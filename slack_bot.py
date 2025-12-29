"""
Slack Bot: Replies with square roots in threads
================================================

Setup:
1. Create a Slack App at https://api.slack.com/apps
2. Enable Socket Mode (Settings → Socket Mode → Enable)
3. Add Bot Token Scopes: channels:history, chat:write
4. Install to workspace
5. Copy tokens and run this script

Environment variables needed:
  SLACK_BOT_TOKEN=xoxb-...
  SLACK_APP_TOKEN=xapp-...
"""

import os
import re
import json
import subprocess
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Config
SQRT_API_URL = "https://sqrt-api-7702501906276199.aws.databricksapps.com"
DATABRICKS_HOST = "https://samsara-biztech-us-west-2.cloud.databricks.com"

# Initialize Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


def get_databricks_token():
    """Get fresh OAuth token from Databricks CLI"""
    result = subprocess.run(
        ["databricks", "auth", "token", "--host", DATABRICKS_HOST],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)["access_token"]


def get_sqrt(number: float) -> dict:
    """Call the sqrt API"""
    token = get_databricks_token()
    response = requests.get(
        f"{SQRT_API_URL}/sqrt/{number}",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()


@app.message(re.compile(r"^-?\d+\.?\d*$"))
def handle_number(message, say):
    """When someone posts a number, reply with its square root"""
    number_str = message["text"].strip()
    
    try:
        number = float(number_str)
        result = get_sqrt(number)
        
        if "sqrt" in result:
            reply = f"√{number} = {result['sqrt']}"
        else:
            reply = f"Error: {result.get('detail', 'Unknown error')}"
            
    except Exception as e:
        reply = f"Error: {str(e)}"
    
    # Reply in thread
    say(text=reply, thread_ts=message["ts"])


@app.event("message")
def handle_other_messages(event, logger):
    """Ignore non-number messages"""
    pass


if __name__ == "__main__":
    print("🤖 Starting Slack Bot...")
    print("   Listening for numbers in channels...")
    print("   Press Ctrl+C to stop\n")
    
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()

