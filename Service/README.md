# Simple Flask Web Application

A simple Flask web application that serves multiple endpoints for testing and demonstration purposes.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python simple_python_server.py
```

The server will start on `http://localhost:5000`


## Available Endpoints

- **GET /** - Home endpoint with welcome message and endpoint list
- **GET /docufy** - (if implemented) or **POST /docufy** - Accepts multipart/form-data with `filename`, `diff` (file), and `content` (file). Returns a patch or updated file content.

## Example Usage


### Using curl:

```bash
# Home endpoint
curl http://localhost:5000/

# Health check
curl http://localhost:5000/api/health

# Server info
curl http://localhost:5000/api/info

# Echo GET with query parameters
curl "http://localhost:5000/api/echo?name=test&value=123"

# Echo POST with JSON data
curl -X POST http://localhost:5000/api/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello World", "data": [1, 2, 3]}'

# Docufy endpoint (POST multipart/form-data)
curl -X POST http://localhost:5000/docufy \
  -F "filename=yourfile.py" \
  -F "diff=@/path/to/diff.patch" \
  -F "content=@/path/to/yourfile.py"
```


### Using Python requests:

```python
import requests

# GET request
response = requests.get('http://localhost:5000/api/info')
print(response.json())

# POST request
data = {"name": "DocuBuddy", "type": "test"}
response = requests.post('http://localhost:5000/api/echo', json=data)
print(response.json())

# Docufy endpoint (multipart/form-data)
with open("yourfile.py", "rb") as content_file, open("diff.patch", "rb") as diff_file:
    files = {
        "filename": (None, "yourfile.py"),
        "diff": ("diff.patch", diff_file),
        "content": ("yourfile.py", content_file)
    }
    response = requests.post('http://localhost:5000/docufy', files=files)
    print(response.text)
```

## Features

- JSON responses for all endpoints
- Error handling with custom 404 and 500 error pages
- Support for both GET and POST methods
- Query parameter handling
- JSON request body parsing
- Comprehensive documentation with docstrings
