import math
import os
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader

app = FastAPI(
    title="Square Root API",
    description="A simple API that returns the square root of any number",
    version="1.0.0"
)

# API Key authentication
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="Missing API Key")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


@app.get("/")
def root():
    return {"message": "Welcome to the Square Root API! Use /sqrt/{number} to get a square root."}


@app.get("/sqrt/{number}")
def sqrt(number: float, api_key: str = Depends(verify_api_key)):
    if number < 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot compute square root of a negative number"
        )
    return {"number": number, "sqrt": math.sqrt(number)}
