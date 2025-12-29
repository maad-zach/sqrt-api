"""
Square Root API + Slack Bot
Runs as a Databricks App
"""

import os
import re
import math
import threading
from fastapi import FastAPI, HTTPException, Request
from slack_bolt import App as SlackApp
from slack_bolt.adapter.socket_mode import SocketModeHandler

# === FastAPI App ===
api = FastAPI(
    title="Square Root API",
    description="A simple API that returns the square root of any number",
    version="1.0.0"
)

@api.get("/")
def root():
    return {"message": "Welcome to the Square Root API! Use /sqrt/{number} to get a square root."}

@api.get("/sqrt/{number}")
def sqrt(number: float):
    if number < 0:
        raise HTTPException(status_code=400, detail="Cannot compute square root of a negative number")
    return {"number": number, "sqrt": math.sqrt(number)}

@api.get("/whoami")
def whoami(request: Request):
    user = request.headers.get("X-Forwarded-User", "unknown")
    email = request.headers.get("X-Forwarded-Email", "unknown")
    return {"user": user, "email": email}

@api.get("/health")
def health():
    return {"status": "healthy", "slack_bot": "running"}


# === Slack Bot ===
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

slack_app = SlackApp(token=SLACK_BOT_TOKEN)

@slack_app.message(re.compile(r"^-?\d+\.?\d*$"))
def handle_number(message, say):
    """When someone posts a number, reply with its square root"""
    number_str = message["text"].strip()
    
    try:
        number = float(number_str)
        if number < 0:
            reply = f"❌ Cannot compute square root of negative number: {number}"
        else:
            result = math.sqrt(number)
            reply = f"√{number} = {result}"
    except Exception as e:
        reply = f"❌ Error: {str(e)}"
    
    say(text=reply, thread_ts=message["ts"])

@slack_app.event("message")
def handle_other_messages(event, logger):
    pass


def start_slack_bot():
    """Start Slack bot in background thread"""
    if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
        print("🤖 Starting Slack bot...")
        handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
        handler.start()
    else:
        print("⚠️ Slack tokens not configured, bot disabled")


# Start Slack bot in background when module loads
if SLACK_BOT_TOKEN and SLACK_APP_TOKEN:
    bot_thread = threading.Thread(target=start_slack_bot, daemon=True)
    bot_thread.start()
    print("✅ Slack bot started in background")
else:
    print("⚠️ Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN to enable Slack bot")


# For running with uvicorn
app = api

