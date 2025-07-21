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
- **GET /api/health** - Health check endpoint
- **GET /api/info** - Server information endpoint
- **GET /api/echo** - Echo endpoint for GET requests
- **POST /api/echo** - Echo endpoint for POST requests (expects JSON data)

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
```

## Features

- JSON responses for all endpoints
- Error handling with custom 404 and 500 error pages
- Support for both GET and POST methods
- Query parameter handling
- JSON request body parsing
- Comprehensive documentation with docstrings
