# Square Root API

A simple FastAPI deployed on Databricks Apps that returns the square root of any number.

**Live URL**: https://sqrt-api-7702501906276199.aws.databricksapps.com

## Quick Start (Python)

### One-time setup

```bash
# Install Databricks CLI
brew install databricks

# Login (opens browser)
databricks auth login --host https://samsara-biztech-us-west-2.cloud.databricks.com

# Install Python dependency
pip install requests
```

### Use the API

```python
import json, subprocess, requests

# Get token from Databricks CLI
token = json.loads(subprocess.run(
    ["databricks", "auth", "token", "--host", "https://samsara-biztech-us-west-2.cloud.databricks.com"],
    capture_output=True, text=True
).stdout)["access_token"]

# Call the API
def sqrt(n):
    r = requests.get(f"https://sqrt-api-7702501906276199.aws.databricksapps.com/sqrt/{n}",
                     headers={"Authorization": f"Bearer {token}"})
    return r.json()["sqrt"]

# Try it
print(sqrt(25))   # 5.0
print(sqrt(144))  # 12.0
```

## Use in Databricks Notebook

```python
import requests

token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

response = requests.get(
    "https://sqrt-api-7702501906276199.aws.databricksapps.com/sqrt/25",
    headers={"Authorization": f"Bearer {token}"}
)

print(response.json())  # {'number': 25.0, 'sqrt': 5.0}
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message |
| `GET /sqrt/{number}` | Returns square root |
| `GET /whoami` | Shows authenticated user |
| `GET /docs` | Swagger UI |

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deploy to Databricks Apps

```bash
# Upload code
databricks workspace import-dir . /Users/<your-email>/sqrt-api --overwrite

# Deploy
databricks apps deploy sqrt-api --source-code-path /Workspace/Users/<your-email>/sqrt-api
```
