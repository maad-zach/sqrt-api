# Building a Slack Bot on Databricks Apps

A comprehensive guide to building and deploying a Slack bot that runs on Databricks Apps, using FastAPI and Socket Mode.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Create a Slack App](#step-1-create-a-slack-app)
4. [Step 2: Build the Python App](#step-2-build-the-python-app)
5. [Step 3: Deploy to Databricks Apps](#step-3-deploy-to-databricks-apps)
6. [Step 4: Test and Verify](#step-4-test-and-verify)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌──────────────┐      WebSocket       ┌─────────────────────────┐
│  Slack API   │◄────────────────────►│  Databricks App         │
│              │   (Socket Mode)      │                         │
│  - Messages  │                      │  ┌─────────┐ ┌────────┐ │
│  - Events    │                      │  │ FastAPI │ │ Slack  │ │
│  - Commands  │                      │  │  (HTTP) │ │  Bot   │ │
└──────────────┘                      │  └─────────┘ └────────┘ │
                                      └─────────────────────────┘
```

### Why Socket Mode?

- **No public URL needed**: Bot connects outbound to Slack
- **Works behind Databricks OAuth**: No need for Slack to call your app
- **Firewall friendly**: Only outbound connections required
- **Persistent connection**: Instant message delivery

---

## Prerequisites

### Tools
```bash
# Databricks CLI
brew install databricks

# Authenticate to your workspace
databricks auth login --host https://YOUR-WORKSPACE.cloud.databricks.com
```

### Python Dependencies
```
fastapi==0.115.6
uvicorn[standard]==0.34.0
slack-bolt==1.21.2
requests==2.32.3
```

---

## Step 1: Create a Slack App

### 1.1 Create the App
1. Go to https://api.slack.com/apps
2. Click **Create New App** → **From scratch**
3. Name your app, select your workspace
4. Click **Create App**

### 1.2 Enable Socket Mode
1. Go to **Settings** → **Socket Mode**
2. Toggle **Enable Socket Mode** → ON
3. Create an App-Level Token with scope: `connections:write`
4. **Save the `xapp-...` token**

### 1.3 Add Bot Permissions
1. Go to **OAuth & Permissions**
2. Under **Bot Token Scopes**, add:
   - `channels:history` - Read messages
   - `channels:read` - Get channel info
   - `chat:write` - Send messages
   - `groups:history` - Read private channel messages (optional)

### 1.4 Enable Events
1. Go to **Event Subscriptions**
2. Toggle **Enable Events** → ON
3. Under **Subscribe to bot events**, add:
   - `message.channels` - Messages in public channels
   - `message.groups` - Messages in private channels (optional)
4. Click **Save Changes**

### 1.5 Install to Workspace
1. Go to **Install App**
2. Click **Install to Workspace** → **Allow**
3. **Save the `xoxb-...` Bot Token**

### 1.6 Summary of Tokens

| Token | Format | Where to Find | Used For |
|-------|--------|---------------|----------|
| Bot Token | `xoxb-...` | OAuth & Permissions | API calls (send messages, etc.) |
| App Token | `xapp-...` | Basic Information → App-Level Tokens | Socket Mode connection |

---

## Step 2: Build the Python App

### 2.1 Project Structure

```
your-bot/
├── app.py              # Main app (FastAPI + Slack bot)
├── app.yaml            # Databricks Apps config
├── requirements.txt    # Dependencies
└── README.md
```

### 2.2 The Main App (`app.py`)

```python
"""
FastAPI + Slack Bot running on Databricks Apps
"""

import os
import re
import threading
from fastapi import FastAPI, HTTPException
from slack_bolt import App as SlackApp
from slack_bolt.adapter.socket_mode import SocketModeHandler

# === Configuration ===
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
ALLOWED_CHANNEL = "your-channel-name"  # Optional: restrict to one channel

# === FastAPI App ===
api = FastAPI(title="Your Bot API")

@api.get("/")
def root():
    return {"status": "running"}

@api.get("/health")
def health():
    return {"api": "healthy", "slack_bot": "running"}

# Add your API endpoints here
@api.get("/your-endpoint/{param}")
def your_endpoint(param: str):
    # Your logic here
    return {"result": param}


# === Slack Bot ===
slack_app = SlackApp(token=SLACK_BOT_TOKEN)

# Cache for channel names (optional optimization)
_channel_cache = {}

def get_channel_name(client, channel_id):
    """Get channel name from ID (cached)"""
    if channel_id not in _channel_cache:
        try:
            info = client.conversations_info(channel=channel_id)
            _channel_cache[channel_id] = info["channel"]["name"]
        except:
            _channel_cache[channel_id] = None
    return _channel_cache.get(channel_id)


# Pattern: Respond to messages matching a regex
@slack_app.message(re.compile(r"your-pattern-here"))
def handle_message(message, say, client):
    """Handle messages matching the pattern"""
    
    # Optional: Only respond in specific channel
    channel_name = get_channel_name(client, message["channel"])
    if channel_name != ALLOWED_CHANNEL:
        return
    
    # Get the message text
    text = message["text"]
    
    # Your logic here
    result = f"You said: {text}"
    
    # Reply in thread
    say(text=result, thread_ts=message["ts"])


# Pattern: Respond to app mentions (@your-bot)
@slack_app.event("app_mention")
def handle_mention(event, say):
    """Handle @mentions of the bot"""
    user = event["user"]
    say(f"Hi <@{user}>! How can I help?")


# Pattern: Handle slash commands
@slack_app.command("/your-command")
def handle_command(ack, command, say):
    """Handle /your-command"""
    ack()  # Acknowledge the command
    text = command["text"]
    say(f"You ran the command with: {text}")


# Catch-all for other messages (prevents errors)
@slack_app.event("message")
def handle_other_messages(event, logger):
    pass


# === Start Slack Bot in Background ===
def start_slack_bot():
    if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
        print("🤖 Starting Slack bot...")
        handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
        handler.start()
    else:
        print("⚠️ Slack tokens not set, bot disabled")

if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
    bot_thread = threading.Thread(target=start_slack_bot, daemon=True)
    bot_thread.start()
    print("✅ Slack bot started in background")


# Export for uvicorn
app = api
```

### 2.3 Databricks Config (`app.yaml`)

```yaml
command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
env:
  - name: SLACK_BOT_TOKEN
    value: "xoxb-your-bot-token"
  - name: SLACK_APP_TOKEN
    value: "xapp-your-app-token"
```

⚠️ **Security Note**: Don't commit tokens to GitHub! Store them only in the Databricks workspace version.

### 2.4 Dependencies (`requirements.txt`)

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
slack-bolt==1.21.2
requests==2.32.3
```

---

## Step 3: Deploy to Databricks Apps

### 3.1 Create the App (One-time)

```bash
databricks apps create your-app-name \
  --description "Your bot description" \
  --no-wait
```

### 3.2 Upload Code

```bash
# Upload to Databricks workspace
databricks workspace import-dir ./your-bot /Users/YOUR-EMAIL/your-bot --overwrite
```

### 3.3 Deploy

```bash
databricks apps deploy your-app-name \
  --source-code-path /Workspace/Users/YOUR-EMAIL/your-bot \
  --no-wait
```

### 3.4 Check Status

```bash
# Check if running
databricks apps get your-app-name

# List deployments
databricks apps list-deployments your-app-name
```

### 3.5 Grant Access to All Users (Optional)

```bash
databricks apps update-permissions your-app-name \
  --json '{"access_control_list": [{"group_name": "users", "permission_level": "CAN_USE"}]}'
```

---

## Step 4: Test and Verify

### 4.1 Test the API

```bash
# Get OAuth token
TOKEN=$(databricks auth token --host https://YOUR-WORKSPACE.cloud.databricks.com \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Call your API
curl "https://your-app-URL.databricksapps.com/health" \
  -H "Authorization: Bearer $TOKEN"
```

### 4.2 Test the Slack Bot

1. Invite bot to a channel: `/invite @your-bot`
2. Post a message that matches your pattern
3. Bot should reply in a thread

---

## Common Patterns

### Pattern 1: Respond to Specific Text

```python
@slack_app.message("hello")
def handle_hello(message, say):
    say("Hello! 👋", thread_ts=message["ts"])
```

### Pattern 2: Respond to Regex Pattern

```python
@slack_app.message(re.compile(r"^#(\d+)$"))  # Matches "#123"
def handle_ticket(message, say, context):
    ticket_id = context["matches"][0]
    say(f"Looking up ticket {ticket_id}...", thread_ts=message["ts"])
```

### Pattern 3: Call External API

```python
import requests

@slack_app.message(re.compile(r"^lookup (.+)$"))
def handle_lookup(message, say, context):
    query = context["matches"][0]
    
    # Call your API
    response = requests.get(f"https://api.example.com/search?q={query}")
    result = response.json()
    
    say(f"Found: {result}", thread_ts=message["ts"])
```

### Pattern 4: Interactive Buttons

```python
@slack_app.message("menu")
def show_menu(message, say):
    say(
        blocks=[
            {
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "Option A"}, "action_id": "option_a"},
                    {"type": "button", "text": {"type": "plain_text", "text": "Option B"}, "action_id": "option_b"},
                ]
            }
        ],
        thread_ts=message["ts"]
    )

@slack_app.action("option_a")
def handle_option_a(ack, say):
    ack()
    say("You chose Option A!")
```

### Pattern 5: Scheduled Messages

```python
from datetime import datetime, timedelta

@slack_app.message("remind me")
def set_reminder(message, say, client):
    # Schedule message for 1 hour from now
    future_time = datetime.now() + timedelta(hours=1)
    
    client.chat_scheduleMessage(
        channel=message["channel"],
        post_at=int(future_time.timestamp()),
        text="This is your reminder!"
    )
    
    say("Reminder set for 1 hour from now!", thread_ts=message["ts"])
```

---

## Troubleshooting

### Bot Not Responding

1. **Check bot is running**:
   ```bash
   curl "https://your-app-URL.databricksapps.com/health" -H "Authorization: Bearer $TOKEN"
   # Should return: {"api": "healthy", "slack_bot": "running"}
   ```

2. **Check bot is in channel**: Use `/invite @your-bot`

3. **Check event subscriptions**: Ensure `message.channels` is enabled in Slack App settings

4. **Check tokens**: Verify both `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are set correctly

### Deployment Stuck

```bash
# Check deployment status
databricks apps list-deployments your-app-name

# If stuck, try redeploying
databricks apps deploy your-app-name --source-code-path /Workspace/... --no-wait
```

### Token Expired (for API access)

```bash
# Get fresh token
databricks auth token --host https://YOUR-WORKSPACE.cloud.databricks.com
```

For long-lived programmatic access, ask your admin to create a **service principal**.

---

## Quick Reference Commands

```bash
# Create app
databricks apps create APP_NAME --description "..." --no-wait

# Upload code
databricks workspace import-dir ./local-dir /Users/EMAIL/remote-dir --overwrite

# Deploy
databricks apps deploy APP_NAME --source-code-path /Workspace/Users/EMAIL/dir --no-wait

# Check status
databricks apps get APP_NAME

# View deployments
databricks apps list-deployments APP_NAME

# Set permissions
databricks apps update-permissions APP_NAME --json '{"access_control_list": [{"group_name": "users", "permission_level": "CAN_USE"}]}'

# Get OAuth token
databricks auth token --host https://WORKSPACE.cloud.databricks.com
```

---

## Resources

- [Slack Bolt for Python](https://slack.dev/bolt-python/)
- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

*Generated from the sqrt-api PoC project*

