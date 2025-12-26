"""
Example: Programmatic access to the sqrt-api on Databricks Apps

Prerequisites:
1. Install databricks-sdk: pip install databricks-sdk requests
2. Authenticate: databricks auth login --host https://samsara-biztech-us-west-2.cloud.databricks.com
"""

import json
import subprocess
import requests

# Get OAuth token from Databricks CLI
print("🔐 Getting OAuth token from Databricks CLI...")
result = subprocess.run(
    ["databricks", "auth", "token", "--host", "https://samsara-biztech-us-west-2.cloud.databricks.com"],
    capture_output=True, text=True
)
token_data = json.loads(result.stdout)
token = token_data["access_token"]
print(f"✓ Got token (expires: {token_data['expiry']})")

# Your app URL
APP_URL = "https://sqrt-api-7702501906276199.aws.databricksapps.com"
headers = {"Authorization": f"Bearer {token}"}

# Test the API
print(f"\n📡 Calling the Square Root API...\n")

for number in [25, 144, 2, 1000000]:
    response = requests.get(f"{APP_URL}/sqrt/{number}", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   √{number} = {result['sqrt']}")
    else:
        print(f"   Error for {number}: {response.status_code}")

# Test error handling
print(f"\n📡 Testing error handling (negative number)...")
response = requests.get(f"{APP_URL}/sqrt/-1", headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

print("\n✅ Done!")
