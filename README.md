# Square Root API

A simple FastAPI that returns the square root of any number, protected by API key authentication.

## Local Development

```bash
pip install -r requirements.txt
API_KEY=my-secret-key uvicorn main:app --reload
```

## Usage

All requests to `/sqrt/{number}` require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: my-secret-key" http://localhost:8000/sqrt/25
```

Response:
```json
{"number": 25.0, "sqrt": 5.0}
```

## Deploy to Render (Recommended)

1. Go to [render.com](https://render.com) and sign up
2. Click **New** → **Web Service**
3. Connect your GitHub repo: `maad-zach/sqrt-api`
4. Render will auto-detect settings from `render.yaml`
5. Add environment variable: `API_KEY` = your secret key
6. Click **Deploy**

## Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign up
2. Click **New Project** → **Deploy from GitHub**
3. Select `maad-zach/sqrt-api`
4. Add environment variable: `API_KEY` = your secret key
5. Railway auto-deploys!

## API Endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /` | None | Welcome message |
| `GET /sqrt/{number}` | API Key | Returns square root |
| `GET /docs` | None | Swagger UI |

## Authentication

Include your API key in the request header:

```
X-API-Key: your-secret-api-key
```
