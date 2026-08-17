# Python API Task 1

A simple FastAPI POST API that accepts JSON input and validates `name`, `email`, and `age`.

## Requirements

- Python 3.10+
- pip

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## Endpoint

### POST `/users`

Example request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25
}
```

Successful response: **201 Created**

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 25
  }
}
```

## Validation

- `name` is required and cannot be empty.
- `email` is required and must be a valid email address.
- `age` is required and must be greater than 18. Therefore, age `18` is rejected.

Invalid input returns **422 Unprocessable Entity** with validation details.

Unexpected server-side errors return **500 Internal Server Error**.

Malformed JSON is handled by FastAPI and results in an appropriate **422** validation response.

## Postman

Import `postman_collection.json` into Postman.

The collection includes:

1. Valid request
2. Missing fields
3. Invalid email
4. Age equal to 18

## Project structure

```text
python_api_task1/
├── main.py
├── requirements.txt
├── postman_collection.json
└── README.md
```
