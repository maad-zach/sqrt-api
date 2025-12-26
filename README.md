# Square Root API

A simple FastAPI that returns the square root of any number.

## Installation

```bash
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn main:app --reload
```

## Usage

- **Root endpoint**: `GET /` - Welcome message
- **Square root**: `GET /sqrt/{number}` - Returns the square root of the given number

### Example

```bash
curl http://localhost:8000/sqrt/16
```

Response:
```json
{"number": 16.0, "sqrt": 4.0}
```

## Interactive Docs

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deploy to Databricks

This app is configured for **Databricks Apps** deployment.

### Steps:

1. **Upload to Databricks**: Push this repo to a Git provider connected to your Databricks workspace, or upload files to DBFS.

2. **Create a Databricks App**:
   - Go to **Compute** → **Apps** → **Create App**
   - Choose **Custom** and give it a name
   - Click **Create App**

3. **Deploy**:
   - Once compute starts, click **Deploy**
   - Select the directory containing your app files
   - Click **Deploy**

4. **Access your API**:
   ```bash
   curl -X GET "https://<your-databricks-app-url>/sqrt/25" \
     -H "Authorization: Bearer YOUR_DATABRICKS_TOKEN"
   ```

### Generate Access Token

```bash
databricks auth login --host https://<your-workspace-url>
databricks auth token
```

