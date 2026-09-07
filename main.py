import base64
import json
import os
import sys
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles so emojis and currency symbols (e.g. ₹) print cleanly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Google Gemini SDK
from google import genai

# Google OAuth & Gmail API Client
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail Modify Scope: allows our agent to read emails and modify labels (like removing UNREAD)
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


# ============================================================================
# 1. OBSERVE: Fetch perception data from the environment (Gmail)
# ============================================================================
def get_unread_emails(max_results=5):
    """
    Connects to Gmail via OAuth and fetches the latest unread emails.
    Extracts sender, subject, and text body for each email.
    Returns a tuple (service, extracted_emails).
    """
    creds = None
    token_file = "token.json"
    credentials_file = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")

    # Step A: Load saved login token if already authorized previously
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, GMAIL_SCOPES)

    # Step B: If no valid token exists, open browser for student to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future runs so we don't have to log in every time
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    # Step C: Build Gmail API client service
    service = build("gmail", "v1", credentials=creds)

    # Step D: Query Gmail for unread emails in inbox
    response = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=max_results
    ).execute()

    messages = response.get("messages", [])
    extracted_emails = []

    for item in messages:
        msg = service.users().messages().get(
            userId="me",
            id=item["id"],
            format="full"
        ).execute()

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])

        # Extract Subject and Sender from headers
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "(Unknown Sender)")
        snippet = msg.get("snippet", "")

        # Extract plain text body from email payload parts
        body = ""
        if "data" in payload.get("body", {}):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
        else:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    break

        # Fallback to snippet if body decoding didn't produce text
        body_text = (body if body else snippet).strip()

        extracted_emails.append({
            "id": item["id"],
            "subject": subject,
            "sender": sender,
            "body": body_text[:1000]  # Limit to first 1000 characters to keep prompt compact
        })

    return service, extracted_emails


# ============================================================================
# 2. THINK & 3. DECIDE: Use Gemini to reason about content & make decisions
# ============================================================================
def classify_email(client, email):
    """
    Sends email details to Gemini to reason (THINK) and determine (DECIDE)
    the category, priority, and rationale.
    """
    prompt = f"""You are an intelligent email triage AI Agent.
Analyze the following email:

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Perform two tasks:
1. Classify category into ONE of: ACTION_REQUIRED, MEETING, OPPORTUNITY, PROMOTION, SPAM
2. Assign priority into ONE of: HIGH, MEDIUM, LOW

Return ONLY a valid JSON object (no markdown, no backticks, no explanations) with this exact schema:
{{
  "category": "ACTION_REQUIRED",
  "priority": "HIGH",
  "reason": "Brief one-sentence reason"
}}
"""
    # THINK: Model processes and reasons over the prompt
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    # DECIDE: Parse the structured decision from the model output
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`").removeprefix("json").strip()

    try:
        decision = json.loads(raw_text)
    except json.JSONDecodeError:
        # Graceful fallback if JSON parsing fails
        decision = {
            "category": "ACTION_REQUIRED",
            "priority": "MEDIUM",
            "reason": "Automated parsing fallback: please review manually."
        }

    return decision


# ============================================================================
# SUMMARY BUILDER: Aggregate decisions into an executive briefing
# ============================================================================
def build_summary(classified_emails):
    """
    Formats the classified emails into a clean, human-readable briefing
    grouped by priority (HIGH, MEDIUM, LOW).
    """
    high_items = []
    medium_items = []
    low_promotions_count = 0
    low_items = []

    for item in classified_emails:
        subject = item["email"]["subject"]
        priority = item["decision"].get("priority", "LOW").upper()
        category = item["decision"].get("category", "").upper()

        if priority == "HIGH":
            high_items.append(f"• {subject}")
        elif priority == "MEDIUM":
            medium_items.append(f"• {subject}")
        else:
            if category in ("PROMOTION", "SPAM"):
                low_promotions_count += 1
            else:
                low_items.append(f"• {subject}")

    # Build final message text
    lines = ["📬 Inbox Brief\n"]

    lines.append("HIGH PRIORITY")
    lines.extend(high_items if high_items else ["• None"])
    lines.append("")

    lines.append("MEDIUM")
    lines.extend(medium_items if medium_items else ["• None"])
    lines.append("")

    lines.append("LOW")
    if low_promotions_count > 0:
        lines.append(f"• {low_promotions_count} promotional/spam emails hidden")
    lines.extend(low_items)
    if low_promotions_count == 0 and not low_items:
        lines.append("• None")

    return "\n".join(lines)


# ============================================================================
# 4. ACT: Execute changes or transmit results into the world (Telegram)
# ============================================================================
def send_telegram_message(token, chat_id, message_text):
    """
    Sends the generated summary to the user's Telegram chat via HTTP API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text
    }
    response = requests.post(url, json=payload, timeout=10)
    data = response.json()
    if not data.get("ok"):
        error_desc = data.get("description", "Unknown error")
        if "chat not found" in error_desc.lower():
            print(f"\n[!] Telegram Error: {error_desc}")
            print("👉 Fix: Open Telegram, search for your bot (e.g. @zishanmailbot), and press 'Start' or send /start.")
            print("   Telegram bots cannot message you first until you initiate the chat!")
        raise RuntimeError(f"Telegram API Error: {error_desc}")
    return data


# ============================================================================
# 5. UPDATE ENVIRONMENT: Organize emails in Gmail (Apply Labels & Mark Read)
# ============================================================================
def organize_emails_in_gmail(service, classified_emails):
    """
    Creates category labels in Gmail if they don't exist, assigns the matching
    category label to each email, and removes the 'UNREAD' label.
    """
    # Step A: Fetch all existing Gmail labels
    results = service.users().labels().list(userId="me").execute()
    existing_labels = results.get("labels", [])
    label_map = {lbl["name"].upper(): lbl["id"] for lbl in existing_labels}

    for item in classified_emails:
        msg_id = item["email"]["id"]
        category = item["decision"].get("category", "OTHER").upper()
        label_name = f"Agent/{category}"

        # Step B: Create the Gmail label if it doesn't exist yet
        if label_name not in label_map:
            try:
                new_label = service.users().labels().create(
                    userId="me",
                    body={
                        "name": label_name,
                        "labelListVisibility": "labelShow",
                        "messageListVisibility": "show"
                    }
                ).execute()
                label_map[label_name] = new_label["id"]
                print(f"  [+] Created Gmail label: '{label_name}'")
            except Exception as e:
                print(f"  [!] Could not create label '{label_name}': {e}")
                continue

        category_label_id = label_map.get(label_name)
        modify_body = {"removeLabelIds": ["UNREAD"]}
        if category_label_id:
            modify_body["addLabelIds"] = [category_label_id]

        # Step C: Update email labels in Gmail
        try:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body=modify_body
            ).execute()
        except Exception as e:
            print(f"  [!] Failed to organize email {msg_id} in Gmail: {e}")


# ============================================================================
# AGENT LOOP: Observe -> Think -> Decide -> Act -> Update Environment
# ============================================================================
def main():
    # Load settings from .env file
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not gemini_key or not bot_token or not chat_id:
        print("[!] Error: Missing required keys in .env file.")
        print("    Make sure GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, and TELEGRAM_CHAT_ID are set.")
        return

    print("========================================")
    print("      GMAIL INBOX AGENT STARTING        ")
    print("========================================")

    # 1. OBSERVE
    print("\n[1. OBSERVE] Reading unread emails from Gmail...")
    service, emails = get_unread_emails(max_results=5)
    print(f"Found {len(emails)} unread email(s).")

    if not emails:
        print("Inbox clear! No unread emails to process.")
        return

    # Initialize Gemini client
    client = genai.Client(api_key=gemini_key)

    classified_emails = []
    for email in emails:
        print(f"\nAnalyzing email: \"{email['subject']}\" from {email['sender']}")

        # 2. THINK & 3. DECIDE
        print("  -> [2. THINK & 3. DECIDE] Gemini evaluating category & priority...")
        decision = classify_email(client, email)
        print(f"     Category: {decision.get('category')} | Priority: {decision.get('priority')}")
        print(f"     Reason:   {decision.get('reason')}")

        classified_emails.append({
            "email": email,
            "decision": decision
        })

    # Prepare Executive Summary
    summary = build_summary(classified_emails)
    print("\n[SUMMARY PREVIEW]")
    print(summary)

    # 4. ACT
    print("\n[4. ACT] Sending briefing to Telegram...")
    send_telegram_message(bot_token, chat_id, summary)
    print("Message successfully sent to Telegram!")

    # 5. UPDATE ENVIRONMENT
    print("\n[5. UPDATE ENVIRONMENT] Organizing emails in Gmail with labels...")
    organize_emails_in_gmail(service, classified_emails)
    print("Emails successfully categorized and marked as read in Gmail!")

    print("\n========================================")
    print("          AGENT LOOP COMPLETE           ")
    print("========================================")


if __name__ == "__main__":
    main()