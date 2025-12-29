# Building Slack Bots on Databricks Apps

**Your Setup Reference Guide**

This guide shows how to create new Slack bots using your existing infrastructure:
- **Databricks Workspace**: `samsara-biztech-us-west-2.cloud.databricks.com`
- **Slack App**: `@maad-testing`

---

## Quick Start: Create a New Bot

### 1. Copy the Template

Create a new directory for your bot:

```bash
mkdir ~/github/my-new-bot
cd ~/github/my-new-bot
```

### 2. Create the Files

**`app.py`** - Your bot logic:

```python
"""
My New Bot - [describe what it does]
"""

import os
import re
import threading
from fastapi import FastAPI, HTTPException
from slack_bolt import App as SlackApp
from slack_bolt.adapter.socket_mode import SocketModeHandler

# === Config ===
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
ALLOWED_CHANNEL = "your-channel-name"  # Change this!

# === FastAPI ===
api = FastAPI(title="My New Bot")

@api.get("/")
def root():
    return {"status": "running", "bot": "my-new-bot"}

@api.get("/health")
def health():
    return {"api": "healthy", "slack_bot": "running"}

# === Slack Bot ===
slack_app = SlackApp(token=SLACK_BOT_TOKEN)

_channel_cache = {}

def get_channel_name(client, channel_id):
    if channel_id not in _channel_cache:
        try:
            info = client.conversations_info(channel=channel_id)
            _channel_cache[channel_id] = info["channel"]["name"]
        except:
            _channel_cache[channel_id] = None
    return _channel_cache.get(channel_id)


# === YOUR BOT LOGIC HERE ===

@slack_app.message(re.compile(r"YOUR_PATTERN_HERE"))
def handle_message(message, say, client):
    # Only respond in allowed channel
    if get_channel_name(client, message["channel"]) != ALLOWED_CHANNEL:
        return
    
    text = message["text"]
    
    # YOUR LOGIC HERE
    result = f"You said: {text}"
    
    say(text=result, thread_ts=message["ts"])


# Catch-all (prevents errors)
@slack_app.event("message")
def handle_other(event, logger):
    pass


# === Start Bot ===
def start_slack_bot():
    if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
        print("🤖 Starting Slack bot...")
        handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
        handler.start()

if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
    threading.Thread(target=start_slack_bot, daemon=True).start()
    print("✅ Slack bot running")

app = api
```

**`app.yaml`** - Databricks config (tokens stored here, NOT in GitHub):

```yaml
command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
env:
  - name: SLACK_BOT_TOKEN
    value: "xoxb-YOUR-BOT-TOKEN"  # Get from: Slack App → OAuth & Permissions
  - name: SLACK_APP_TOKEN
    value: "xapp-YOUR-APP-TOKEN"  # Get from: Slack App → Basic Information → App-Level Tokens
```

> **Note**: The actual tokens for `@maad-testing` are stored in the Databricks workspace version of app.yaml at `/Users/zach.merritt@samsara.com/sqrt-api/app.yaml`. Copy from there when creating new bots.

**`requirements.txt`**:

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
slack-bolt==1.21.2
requests==2.32.3
```

### 3. Deploy to Databricks

```bash
# Create the app (one-time)
databricks apps create my-new-bot --description "My new bot" --no-wait

# Wait ~2 min for compute to start, then...

# Upload code (only essential files, not .git or .venv)
mkdir -p /tmp/my-new-bot-deploy
cp app.py app.yaml requirements.txt /tmp/my-new-bot-deploy/
databricks workspace import-dir /tmp/my-new-bot-deploy /Users/zach.merritt@samsara.com/my-new-bot --overwrite

# Deploy
databricks apps deploy my-new-bot \
  --source-code-path /Workspace/Users/zach.merritt@samsara.com/my-new-bot \
  --no-wait

# Check status (wait ~1-2 min)
databricks apps get my-new-bot
```

### 4. Test It

```bash
# Verify it's running
TOKEN=$(databricks auth token --host https://samsara-biztech-us-west-2.cloud.databricks.com \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl "https://MY-NEW-BOT-URL.aws.databricksapps.com/health" \
  -H "Authorization: Bearer $TOKEN"
```

Then in Slack:
1. `/invite @maad-testing` in your channel
2. Post a message matching your pattern
3. Bot replies in thread!

---

## Common Bot Patterns

### Pattern: Respond to Numbers (like sqrt-api)

```python
@slack_app.message(re.compile(r"^-?\d+\.?\d*$"))
def handle_number(message, say, client):
    if get_channel_name(client, message["channel"]) != ALLOWED_CHANNEL:
        return
    
    number = float(message["text"])
    result = do_something_with(number)
    say(text=f"Result: {result}", thread_ts=message["ts"])
```

### Pattern: Respond to Keywords

```python
@slack_app.message(re.compile(r"(help|info|status)", re.IGNORECASE))
def handle_keywords(message, say, client):
    if get_channel_name(client, message["channel"]) != ALLOWED_CHANNEL:
        return
    
    say(text="Here's some help...", thread_ts=message["ts"])
```

### Pattern: Extract Data from Message

```python
# Matches: "lookup ACME Corp" or "lookup 12345"
@slack_app.message(re.compile(r"^lookup\s+(.+)$", re.IGNORECASE))
def handle_lookup(message, say, client, context):
    if get_channel_name(client, message["channel"]) != ALLOWED_CHANNEL:
        return
    
    query = context["matches"][0]  # The captured group
    
    # Call an external API
    result = call_your_api(query)
    
    say(text=f"Found: {result}", thread_ts=message["ts"])
```

### Pattern: Call External API with Auth

```python
import requests

EXTERNAL_API_URL = "https://api.example.com"
EXTERNAL_API_KEY = os.environ.get("EXTERNAL_API_KEY")

@slack_app.message(re.compile(r"^fetch\s+(\S+)$"))
def handle_fetch(message, say, client, context):
    if get_channel_name(client, message["channel"]) != ALLOWED_CHANNEL:
        return
    
    account_id = context["matches"][0]
    
    response = requests.get(
        f"{EXTERNAL_API_URL}/v1/state/{account_id}",
        headers={"X-API-Key": EXTERNAL_API_KEY}
    )
    
    if response.status_code == 200:
        data = response.json()
        say(text=f"Account: {data}", thread_ts=message["ts"])
    else:
        say(text=f"Error: {response.status_code}", thread_ts=message["ts"])
```

### Pattern: Format Rich Slack Messages

```python
@slack_app.message(re.compile(r"^report\s+(\S+)$"))
def handle_report(message, say, client, context):
    if get_channel_name(client, message["channel"]) != ALLOWED_CHANNEL:
        return
    
    account_id = context["matches"][0]
    data = get_account_data(account_id)
    
    # Rich formatting with blocks
    say(
        blocks=[
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"📊 Report for {account_id}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Status:*\n{data['status']}"},
                    {"type": "mrkdwn", "text": f"*Score:*\n{data['score']}"},
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Summary:*\n{data['summary']}"}
            }
        ],
        thread_ts=message["ts"]
    )
```

---

## Updating an Existing Bot

```bash
# Edit your local files, then:

# Re-upload
cp app.py app.yaml requirements.txt /tmp/my-bot-deploy/
databricks workspace import-dir /tmp/my-bot-deploy /Users/zach.merritt@samsara.com/my-bot --overwrite

# Redeploy
databricks apps deploy my-bot \
  --source-code-path /Workspace/Users/zach.merritt@samsara.com/my-bot \
  --no-wait

# Check deployment status
databricks apps list-deployments my-bot
```

---

## Adding a New Channel to @maad-testing

The Slack app `@maad-testing` is already set up. To use it in a new channel:

1. Go to the channel in Slack
2. Type `/invite @maad-testing`
3. Update your bot's `ALLOWED_CHANNEL` variable
4. Redeploy

---

## Quick Reference

### Your Tokens (for app.yaml)

Get the actual tokens from the Databricks workspace:

```bash
# View the tokens stored in Databricks
databricks workspace export /Users/zach.merritt@samsara.com/sqrt-api/app.yaml
```

Or copy from an existing deployed bot's `app.yaml`.

### Databricks Commands

```bash
# Authenticate (one-time)
databricks auth login --host https://samsara-biztech-us-west-2.cloud.databricks.com

# Create new app
databricks apps create APP_NAME --description "..." --no-wait

# Upload code
databricks workspace import-dir /tmp/deploy-dir /Users/zach.merritt@samsara.com/APP_NAME --overwrite

# Deploy
databricks apps deploy APP_NAME --source-code-path /Workspace/Users/zach.merritt@samsara.com/APP_NAME --no-wait

# Check status
databricks apps get APP_NAME

# List deployments
databricks apps list-deployments APP_NAME

# Grant access to all users
databricks apps update-permissions APP_NAME --json '{"access_control_list": [{"group_name": "users", "permission_level": "CAN_USE"}]}'

# Get OAuth token (for API testing)
databricks auth token --host https://samsara-biztech-us-west-2.cloud.databricks.com
```

### Test API Endpoint

```bash
TOKEN=$(databricks auth token --host https://samsara-biztech-us-west-2.cloud.databricks.com \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl "https://YOUR-APP-URL.aws.databricksapps.com/health" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Architecture Reminder

```
┌──────────────┐     WebSocket      ┌─────────────────────────┐
│    Slack     │◄──────────────────►│   Databricks App        │
│              │   (Socket Mode)    │                         │
│ @maad-testing│                    │  ┌─────────┐ ┌────────┐ │
│              │                    │  │ FastAPI │ │ Slack  │ │
└──────────────┘                    │  │  :8000  │ │  Bot   │ │
                                    │  └─────────┘ └────────┘ │
                                    └─────────────────────────┘
```

- **Socket Mode**: Bot connects outbound (no public URL needed)
- **FastAPI**: Optional HTTP endpoints (health checks, APIs)
- **Thread replies**: `say(text=..., thread_ts=message["ts"])`

---

## Existing Bots

| Bot | Channel | What it does |
|-----|---------|--------------|
| sqrt-api | #sqrt-example | Replies with √number |

---

*Last updated: December 2024*
