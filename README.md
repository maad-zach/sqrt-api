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

