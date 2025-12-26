import math
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(
    title="Square Root API",
    description="A simple API that returns the square root of any number",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Welcome to the Square Root API! Use /sqrt/{number} to get a square root."}


@app.get("/sqrt/{number}")
def sqrt(number: float):
    if number < 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot compute square root of a negative number"
        )
    return {"number": number, "sqrt": math.sqrt(number)}


@app.get("/whoami")
def whoami(request: Request):
    """Shows who is authenticated (useful for debugging)"""
    user = request.headers.get("X-Forwarded-User", "unknown")
    email = request.headers.get("X-Forwarded-Email", "unknown")
    return {"user": user, "email": email}
