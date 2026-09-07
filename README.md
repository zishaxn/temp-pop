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

Complete **all three sections below** before running the agent. Each service needs its own credentials. Work through them in order — OpenRouter and Telegram can be done on your phone or browser; Gmail setup uses Google Cloud Console.

### Setup checklist (complete before first run)

- [ ] OpenRouter account created and `OPENROUTER_API_KEY` added to `.env`
- [ ] Telegram bot created via BotFather and `TELEGRAM_BOT_TOKEN` added to `.env`
- [ ] Your Telegram **Chat ID** copied and `TELEGRAM_CHAT_ID` added to `.env`
- [ ] You have opened your bot in Telegram and pressed **Start** (or sent `/start`) — **required**
- [ ] Google Cloud project created and Gmail API enabled
- [ ] OAuth consent screen configured and your Gmail added as a **Test user**
- [ ] OAuth Desktop credentials downloaded as `credentials.json` in the project folder
- [ ] `.env` file saved with all values filled in

---

### 1. OpenRouter API Key Setup (~5 minutes)

This agent uses [OpenRouter](https://openrouter.ai/) as its LLM provider. OpenRouter routes requests to many AI models through one API — including **free models**, so you can run this project without paying.

#### Step 1: Create an OpenRouter account

1. Open [https://openrouter.ai/](https://openrouter.ai/) in your browser.
2. Click **Sign In** (top right).
3. Sign up with Google, GitHub, or email — whichever you prefer.
4. If prompted, verify your email address before continuing.

#### Step 2: Create an API key

1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys).
2. Click **Create Key** (or **Create API Key**).
3. Give the key a name you will recognize later (e.g. `gmail-inbox-agent`).
4. Click **Create**.
5. **Copy the key immediately** — it usually starts with `sk-or-v1-...`. You may not be able to view the full key again after closing the dialog.

#### Step 3: Add the key to your `.env` file

1. Open the `.env` file in your project folder (create it from `.env.example` if you have not already).
2. Find the line `OPENROUTER_API_KEY=` and paste your key after the `=`:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here
   ```
3. Set the model line (free tier — recommended for this project):
   ```env
   OPENROUTER_MODEL=openrouter/free
   ```
4. Save the file.

#### Free models and limits

| Setting | What it does |
| :--- | :--- |
| `openrouter/free` | OpenRouter automatically picks an available free model for each request. **Recommended default.** |
| `provider/model-name:free` | Pin one specific free model (e.g. `meta-llama/llama-3.3-70b-instruct:free`). Browse at [openrouter.ai/models?q=free](https://openrouter.ai/models?q=free). |

**Free tier limits (OpenRouter):**

- **20 requests per minute**
- **50 requests per day** if you have not purchased credits
- **1,000 requests per day** after at least $10 in lifetime credit purchases

This agent classifies up to **5 emails per run**, so daily limits are usually enough for personal or workshop use.

#### Troubleshooting OpenRouter

| Problem | Fix |
| :--- | :--- |
| `401 Unauthorized` | Key is wrong or missing — check `OPENROUTER_API_KEY` in `.env` with no extra spaces or quotes. |
| `429 Too Many Requests` | Free rate limit hit — wait a minute and try again, or switch to another `:free` model. |
| Empty or bad JSON from the model | Free models vary in quality; try pinning a different `:free` model in `OPENROUTER_MODEL`. |

---

### 2. Telegram Bot Setup (~10 minutes)

The agent sends your inbox brief to Telegram. You need **two values**: a bot token (from BotFather) and your personal chat ID.

> **Important — read this before running the agent**
>
> Telegram bots **cannot message you first**. You must open a chat with your bot and press **Start** (or send `/start`) **before** the agent runs. If you skip this step, you will see an error like `chat not found` when the script tries to send the briefing.

#### Step 1: Create your bot with BotFather

1. Open the **Telegram** app (mobile or desktop).
2. In the search bar, type **`@BotFather`** and open the official bot (blue verified checkmark).
3. Tap **Start** or send:
   ```
   /start
   ```
4. Send:
   ```
   /newbot
   ```
5. BotFather asks for a **display name** — this is what users see in chats (e.g. `My Gmail Agent`).
6. BotFather asks for a **username** — must end in `bot` (e.g. `zishan_gmail_agent_bot`). If the name is taken, try another.
7. BotFather replies with a message containing your **HTTP API token**, for example:
   ```
   7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
8. Copy that entire token.

#### Step 2: Save the bot token in `.env`

1. Open your `.env` file.
2. Set:
   ```env
   TELEGRAM_BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   (Replace with your real token — no quotes, no spaces.)
3. Save the file.

**Keep this token private.** Anyone with it can control your bot.

#### Step 3: Get your Telegram Chat ID

Your chat ID is a numeric ID for *you* (not the bot). The agent uses it to know where to send messages.

1. In Telegram, search for **`@userinfobot`** or **`@raw_data_bot`**.
2. Open the bot and tap **Start** (or send `/start`).
3. The bot replies with your user information. Find the line labeled **Id** (or **Chat Id**) — a number like `123456789`.
4. Copy that number.

#### Step 4: Save your Chat ID in `.env`

1. Open your `.env` file.
2. Set:
   ```env
   TELEGRAM_CHAT_ID=123456789
   ```
   (Use your actual numeric ID — no quotes.)
3. Save the file.

#### Step 5: Start a conversation with **your** bot (required)

This step is easy to miss but **mandatory**:

1. In Telegram search, type the **username** of the bot you created (e.g. `@zishan_gmail_agent_bot`).
2. Open the chat with your bot.
3. Tap **Start** at the bottom **or** send:
   ```
   /start
   ```
4. You should see a welcome message from the bot (or an empty chat — that is fine). What matters is that **you** initiated the conversation.

Until you do this, Telegram blocks the agent from sending you messages.

#### Troubleshooting Telegram

| Problem | Fix |
| :--- | :--- |
| `chat not found` | Open your bot in Telegram and press **Start** / send `/start`, then run the agent again. |
| `Unauthorized` / `401` | `TELEGRAM_BOT_TOKEN` is wrong — copy the token again from BotFather (`/mybots` → your bot → **API Token**). |
| Bot never sends messages | Confirm `TELEGRAM_CHAT_ID` is **your** user ID from `@userinfobot`, not the bot's ID. |
| Wrong chat receives messages | You used someone else's chat ID — re-copy your own Id from `@userinfobot`. |

---

### 3. Gmail API & Google Cloud Setup (~15 minutes)

The agent reads unread emails from Gmail using Google's official OAuth flow. This is **separate from OpenRouter** — Gmail access uses Google Cloud credentials, not an OpenRouter key.

You will:

1. Create a Google Cloud project
2. Enable the Gmail API
3. Configure the OAuth consent screen and add yourself as a **Test user**
4. Create Desktop OAuth credentials and download `credentials.json`

#### Step 1: Open Google Cloud Console and create a project

1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/).
2. Sign in with the **Google account whose Gmail inbox** you want the agent to read.
3. At the top of the page, click the **project dropdown** (next to "Google Cloud").
4. Click **New Project**.
5. Enter a project name (e.g. `Gmail-Agent-Workshop`).
6. Click **Create**.
7. Wait a few seconds, then **select your new project** from the project dropdown at the top so it is active.

#### Step 2: Enable the Gmail API

1. With your project selected, open the left menu (**☰**).
2. Go to **APIs & Services** → **Library**.
3. In the search box, type **Gmail API**.
4. Click **Gmail API** in the results.
5. Click **Enable**.
6. Wait until the API shows as enabled (you may land on the API overview page).

#### Step 3: Configure the OAuth consent screen

While your app is in **Testing** mode, only accounts listed as **Test users** can sign in.

1. Open the left menu (**☰**).
2. Go to **APIs & Services** → **OAuth consent screen**.
3. Choose **User Type**:
   - Select **External** (works for personal Gmail accounts).
   - Click **Create**.
4. **App information** (page 1):
   - **App name:** e.g. `Gmail Inbox Agent`
   - **User support email:** select your email from the dropdown
   - **Developer contact email:** enter your email
   - Click **Save and Continue**
5. **Scopes** (page 2):
   - Click **Save and Continue** (default scopes are fine for now; the app requests Gmail access at login time).
6. **Test users** (page 3) — **do not skip this**:
   - Scroll to the **Test users** section.
   - Click **+ Add Users**.
   - Enter the **exact Gmail address** you will use when the agent logs in (e.g. `you@gmail.com`).
   - Click **Add**.
   - Confirm your email appears in the Test users list.
   - Click **Save and Continue**
7. **Summary** (page 4):
   - Review and click **Back to Dashboard**.

> If you try to log in with a Gmail account that is **not** listed under Test users, Google will block access with an error like *"Access blocked: app has not completed Google verification"* or *"Error 403: access_denied"*.

#### Step 4: Create OAuth Desktop credentials

1. Go to **APIs & Services** → **Credentials**.
2. Click **+ Create Credentials** at the top.
3. Select **OAuth client ID**.
4. If asked to configure the consent screen first, you already did — continue.
5. **Application type:** choose **Desktop app**.
6. **Name:** e.g. `Gmail Agent Desktop`.
7. Click **Create**.
8. A dialog shows your **Client ID**. Click **OK** (you do not need to copy these separately — they are in the JSON file next).

#### Step 5: Download `credentials.json`

1. On the **Credentials** page, find your new OAuth 2.0 Client ID under **OAuth 2.0 Client IDs**.
2. Click the **Download** icon (⬇️) on the right side of that row.
3. A JSON file downloads (often named something like `client_secret_....json`).
4. **Rename** the file to exactly:
   ```
   credentials.json
   ```
5. **Move** `credentials.json` into your project folder (same folder as `main.py`).

Your project folder should now contain:

```text
project/
├── main.py
├── credentials.json    ← you added this
├── .env
└── ...
```

#### Step 6: Point `.env` at your credentials file (optional)

By default the agent looks for `credentials.json` in the project root. If you use a different path or filename, set:

```env
GMAIL_CREDENTIALS_FILE=credentials.json
```

Save `.env` when done.

#### What happens on first Gmail login

The first time you run `python main.py`:

1. A **browser window opens** automatically.
2. Choose the **same Google account** you added as a Test user.
3. Google may show **"Google hasn't verified this app"** — this is normal for personal development projects:
   - Click **Advanced**
   - Click **Go to Gmail Inbox Agent (unsafe)** (wording may vary slightly)
4. Review permissions and click **Allow** / **Continue**.
5. You may see *"The authentication flow has completed"* in the browser — you can close it.
6. The script creates **`token.json`** in your project folder. This stores your refresh token so you **do not need to log in through the browser on every run**.

**Do not commit `credentials.json` or `token.json` to git** — they grant access to your Gmail.

#### Troubleshooting Gmail

| Problem | Fix |
| :--- | :--- |
| `Access blocked` / `403 access_denied` | Add your Gmail under **OAuth consent screen → Test users** (see Step 3 above). |
| Browser does not open | Run `python main.py` from a normal terminal (not a restricted sandbox). On headless servers, complete OAuth locally first and copy `token.json`. |
| `credentials.json` not found | File must be in the project folder or path set in `GMAIL_CREDENTIALS_FILE`. |
| Wrong inbox is read | Log out in browser or delete `token.json` and run again, signing in with the correct Test user account. |
| `token.json` expired issues | Delete `token.json` and run again to re-authenticate. |

---

## 🏃 Running the Agent

Run the script:

```bash
python main.py
```

### What to Expect on First Run

Make sure you completed the [setup checklist](#setup-checklist-complete-before-first-run) — especially **Telegram `/start`** and **Gmail Test users**.

1. Run:
   ```bash
   python main.py
   ```
2. A browser window opens for **Google sign-in** (first run only, unless `token.json` already exists).
3. Select the Gmail account you added as a **Test user**.
4. If you see *"Google hasn't verified this app"*, click **Advanced** → **Go to Gmail Inbox Agent (unsafe)**. This is normal for personal development apps.
5. Click **Allow** to grant Gmail access. The agent can read emails, apply labels, and mark messages as read.
6. A `token.json` file is saved locally — future runs skip the browser login.
7. The agent runs its loop:
   - Fetches up to 5 unread emails from Gmail
   - Sends each to OpenRouter for category and priority
   - Builds an executive brief
   - Sends the brief to your Telegram chat (you must have pressed **Start** on your bot first)
   - Applies Gmail labels and marks processed emails as read

If Telegram fails with **`chat not found`**, open your bot and send `/start`, then run `python main.py` again.

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
