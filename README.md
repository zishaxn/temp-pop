# 📬 Gmail Inbox AI Agent

> A beginner-friendly educational project for first-year students introducing the core concept of **AI Agents**.

---

## 🎯 What is an AI Agent?

Traditional software follows rigid, hard-coded rules:
```
If input == X then do Y
```

An **AI Agent**, however, interacts dynamically with its environment. It uses a Large Language Model (LLM) to perceive the world, reason about what it perceives, make decisions, and take real-world actions.

Every AI Agent operates in a continuous or triggered feedback loop known as the **Agent Loop**:

```
 ┌────────────────────────────────────────────────────────┐
 │                      THE AGENT LOOP                    │
 │                                                        │
 │     [1. OBSERVE] ──────► [2. THINK] ──────► [3. DECIDE] │
 │           ▲                                     │      │
 │           │                                     ▼      │
 │           └──────────────── [4. ACT] ◄──────────┘      │
 └────────────────────────────────────────────────────────┘
```

---

## 🔄 How the Agent Loop Works in This Project

In this project, our agent monitors your Gmail inbox and delivers an executive brief directly to your phone via Telegram.

| Stage | Action in Our Agent | Code Function |
| :--- | :--- | :--- |
| **1. OBSERVE** | Agent reads recent unread emails (Subject, Sender, Body) from Gmail. | `get_unread_emails()` |
| **2. THINK** | Agent feeds email content into OpenRouter (LLM), reasoning about its context and urgency. | `classify_email()` |
| **3. DECIDE** | Agent determines the category (`ACTION_REQUIRED`, `MEETING`, etc.) and priority (`HIGH`, `MEDIUM`, `LOW`). | `classify_email()` |
| **4. ACT** | Agent compiles the briefing and sends a live message to your Telegram chat. | `send_telegram_message()` |

---

## 📁 Project Structure

This project contains only **4 files** to ensure you can understand the entire codebase in under 20 minutes:

```text
project/
│
├── main.py            # The entire agent logic (~200 lines, fully commented)
├── requirements.txt   # Python dependencies
├── .env.example       # Example file for API keys and configuration
└── README.md          # Complete setup guide and documentation
```

---

## 🚀 Quickstart Guide

### Step 1: Clone or Download the Project

Open your terminal or command prompt in the project folder:
```bash
cd project
```

### Step 2: Create and Activate a Python Virtual Environment

```bash
# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create your own `.env` file from the provided `.env.example`:

```bash
# On macOS / Linux:
cp .env.example .env

# On Windows:
copy .env.example .env
```

Now open `.env` and fill in your keys (see instructions below for each key).

---

## 🔑 API Setup Instructions

### 1. OpenRouter API Key Setup (Takes 2 minutes)

This agent uses [OpenRouter](https://openrouter.ai/) as its LLM provider. OpenRouter gives you access to many models through one API — including **free models** with no credit card required.

1. Go to [OpenRouter](https://openrouter.ai/) and sign up or log in.
2. Open [openrouter.ai/keys](https://openrouter.ai/keys) and click **Create Key**.
3. Copy the generated key.
4. In your `.env` file, paste it:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=openrouter/free
   ```

**Free models:** The default `openrouter/free` automatically picks an available free model for each request. You can also pin a specific free model (any ID ending in `:free`) — browse options at [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free).

**Free tier limits:** 20 requests/minute; 50 requests/day without purchased credits, or 1,000/day after at least $10 in lifetime credits. This agent processes up to 5 emails per run, so daily limits are usually enough for personal use.

---

### 2. Telegram Bot Setup (Takes 3 minutes)

#### A. Create your Bot:
1. Open Telegram and search for `@BotFather`.
2. Click **Start** or send `/start`.
3. Send `/newbot` and follow the prompts to choose a name and username for your bot.
4. BotFather will give you an **API Token** (e.g. `7123456789:AAF...`).
5. In your `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_from_botfather
   ```

#### B. Get your Chat ID:
1. In Telegram, search for `@userinfobot` or `@raw_data_bot` and click **Start**.
2. It will reply with your numeric **Id** (e.g., `123456789`).
3. Now search for your *own new bot* that you created in step A and click **Start** (this allows the bot to message you).
4. In your `.env` file:
   ```env
   TELEGRAM_CHAT_ID=your_numeric_chat_id
   ```

---

### 3. Gmail API Setup (Takes 5 minutes)

Our agent uses Google's official OAuth desktop flow to read unread emails securely. (This is separate from OpenRouter — Gmail access uses Google Cloud OAuth, not an LLM API key.)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `Gmail-Agent-Workshop`).
3. Enable the Gmail API:
   - Navigate to **APIs & Services** > **Library**.
   - Search for **Gmail API** and click **Enable**.
4. Configure the OAuth Consent Screen:
   - Go to **APIs & Services** > **OAuth consent screen**.
   - Choose **External** and click **Create**.
   - Fill in an App name (e.g. `Gmail Agent`) and your email address. Click **Save and Continue**.
   - Under **Test Users**, add your personal Gmail address (the one you want the agent to read).
5. Create OAuth Credentials:
   - Go to **APIs & Services** > **Credentials**.
   - Click **Create Credentials** > **OAuth client ID**.
   - Application type: **Desktop app**.
   - Name: `Gmail Agent Desktop`.
   - Click **Create**.
6. Download Credentials JSON:
   - Click the download icon (⬇️) next to your newly created OAuth Client ID.
   - Rename the downloaded file to `credentials.json` and place it inside the project directory.

---

## 🏃 Running the Agent

Run the script:

```bash
python main.py
```

### What to Expect on First Run:
1. A browser window will open automatically asking you to log in to your Google Account.
2. Select the Gmail account you added as a test user.
3. If you see an *"Unverified app"* warning, click **Advanced** -> **Go to Gmail Agent (unsafe)**. This is normal for development apps created in your own Google Cloud account.
4. Allow read-only access.
5. A `token.json` file will be saved locally so you won't need to log in again.
6. The agent will run its loop:
   - Fetches unread emails.
   - Prompts OpenRouter to categorize each email and assign priority.
   - Builds an executive brief.
   - Sends the brief directly to your Telegram chat!

---

## ⚙️ GitHub Actions (Optional)

The repo includes a scheduled workflow (`.github/workflows/agent.yml`) that runs the agent every 2 hours. Add these repository secrets:

| Secret | Description |
| :--- | :--- |
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your numeric Telegram chat ID |
| `GMAIL_CREDENTIALS_JSON` | Full contents of `credentials.json` |
| `GMAIL_TOKEN_JSON` | Full contents of `token.json` (after first local OAuth login) |

Optionally set `OPENROUTER_MODEL` in the workflow env if you want a specific model instead of the code default (`openrouter/free`).

---

## 📱 Example Telegram Output

```text
📬 Inbox Brief

HIGH PRIORITY
• Assignment due tomorrow
• Interview invitation received

MEDIUM
• Club meeting on Friday
• Hackathon registration

LOW
• 8 promotional/spam emails hidden
```

---

## 🧠 Discussion Points for the Workshop

1. **Autonomy vs. Control**: Where does the agent make decisions independently, and where are strict constraints enforced?
2. **Perception**: What happens if an email contains only an image or a PDF attachment? How would you extend `OBSERVE`?
3. **Action Safety**: Why did we choose a read-only Gmail scope instead of allowing the agent to automatically delete or send emails?
4. **Model Choice**: How does switching `OPENROUTER_MODEL` (e.g. `openrouter/free` vs a pinned `:free` model) affect cost, speed, and classification quality?
