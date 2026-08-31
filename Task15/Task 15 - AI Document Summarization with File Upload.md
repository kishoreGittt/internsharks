# Task 15 - AI Document Summarization with File Upload

## About the Project

This project extends the AI Summarization API from Task 14.

In Task 14, the API accepted text through a JSON request and generated a summary using an AI model.

In Task 15, the API can also accept `.txt` and `.pdf` files.

The application first extracts text from the uploaded document and then sends the extracted text to the existing AI summarization service.

The AI response is validated using Pydantic before it is returned to the user.

---

## Technologies Used

- Python
- FastAPI
- Pydantic
- OpenRouter API
- PyPDF2
- HTTPX
- python-multipart
- python-dotenv
- Postman

---

## Features

- Upload TXT files
- Upload PDF files
- Validate uploaded files
- Check file size
- Extract text from TXT files
- Extract text from PDF files
- Generate AI summaries
- Support different summary types
- Validate AI-generated responses using Pydantic
- Reuse the existing summarization service
- Handle AI service errors
- Handle invalid files
- Handle PDFs without extractable text

---

## Supported File Types

The API accepts only:

```text
.txt
.pdf
```

Other file types such as:

```text
.docx
.pptx
.jpg
.png
.xlsx
```

are not accepted by the document summarization endpoint.

---

## Maximum File Size

The maximum allowed file size is:

```text
5 MB
```

Files larger than 5 MB are rejected.

---

## Summary Types

The API supports three summary types.

### 1. Brief

Provides a short summary containing the main points.

```text
brief
```

### 2. Detailed

Provides a more complete summary covering the important information in the document.

```text
detailed
```

### 3. Bullet Points

Returns the important information as bullet points.

```text
bullet_points
```

---

## Project Structure

```text
Task15/
│
├── app/
│   ├── routes/
│   │   ├── summarizer.py
│   │   └── document.py
│   │
│   ├── services/
│   │   ├── summarizer_service.py
│   │   └── document_service.py
│   │
│   ├── models/
│   │   └── summarizer.py
│   │
│   ├── prompts/
│   │   └── summarizer_prompt.py
│   │
│   ├── utils/
│   │   └── file_parser.py
│   │
│   ├── config.py
│   └── main.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# How the Application Works

The document summarization flow is:

```text
Upload File
     ↓
FastAPI
     ↓
Validate File
     ↓
Extract Text
     ↓
Summarization Service
     ↓
OpenRouter
     ↓
Validate AI Response
     ↓
Return Response
```

For a PDF:

```text
PDF
 ↓
PyPDF2
 ↓
Extracted Text
 ↓
OpenRouter
 ↓
Summary
```

The PDF is **not directly sent to the text model**.

The application first converts the PDF into text.

---

# Installation

## 1. Create Virtual Environment

Open a terminal inside the project folder.

```bash
python -m venv venv
```

## 2. Activate Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
MODEL_NAME=openai/gpt-4o-mini
```

The API key is used to communicate with OpenRouter.

Do not share or commit your real API key.

---

# Run the Application

Start the FastAPI server using:

```bash
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically provides Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can test the APIs directly from Swagger.

---

# API Endpoints

## 1. Health Check

### Request

```text
GET /health
```

### Response

```json
{
    "success": true,
    "status_code": 200,
    "message": "API is healthy"
}
```

---

# 2. Text Summarization

This endpoint is from the existing Task 14 functionality.

### Request

```text
POST /ai/summarize
```

### Body

Select:

```text
raw
JSON
```

Example:

```json
{
    "text": "FastAPI is a modern Python framework used to build APIs. It provides automatic API documentation and supports asynchronous programming.",
    "summary_type": "brief"
}
```

### Response

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "summary_type": "brief",
        "summary": "FastAPI is a Python framework for building modern APIs with automatic documentation and asynchronous support.",
        "main_topic": "FastAPI",
        "keywords": [
            "Python",
            "FastAPI",
            "API"
        ]
    }
}
```

---

# 3. Document Summarization

This is the main endpoint added in Task 15.

### Request

```text
POST /ai/summarize-document
```

The request uses:

```text
multipart/form-data
```

---

## Postman Testing

Open Postman and create a new request.

Select:

```text
POST
```

Enter:

```text
http://127.0.0.1:8000/ai/summarize-document
```

Go to:

```text
Body
    ↓
form-data
```

Add the following fields:

| Key | Type | Value |
|---|---|---|
| file | File | Select your PDF/TXT file |
| summary_type | Text | brief |

Example:

```text
file          → project_requirements.pdf
summary_type  → brief
```

Then click:

```text
Send
```

---

# TXT File Example

Upload:

```text
requirements.txt
```

Use:

```text
summary_type = brief
```

The application will:

```text
TXT File
   ↓
Read File
   ↓
Decode Text
   ↓
Summarization Service
   ↓
OpenRouter
   ↓
Summary
```

---

# PDF File Example

Upload:

```text
project_requirements.pdf
```

Use:

```text
summary_type = brief
```

The application will:

```text
PDF
 ↓
PyPDF2
 ↓
Extract Text
 ↓
Summarization Service
 ↓
OpenRouter
 ↓
Summary
```

---

# Detailed Summary

In Postman, use:

```text
summary_type = detailed
```

Example:

```text
file          → project_requirements.pdf
summary_type  → detailed
```

---

# Bullet Point Summary

Use:

```text
summary_type = bullet_points
```

Example:

```text
file          → project_requirements.pdf
summary_type  → bullet_points
```

---

# Successful Response

A successful document summarization returns:

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "file_name": "project_requirements.pdf",
        "summary_type": "brief",
        "summary": "The document describes the requirements for a task management backend.",
        "main_topic": "Task Management Backend",
        "keywords": [
            "FastAPI",
            "MongoDB",
            "authentication"
        ]
    }
}
```

---

# Error Handling

The application validates uploaded files before processing them.

## Missing File

If the file is not provided:

```text
400 Bad Request
```

---

## Empty File

If the uploaded file contains no data:

```text
400 Bad Request
```

Example:

```json
{
    "detail": "Uploaded file is empty"
}
```

---

## Unsupported File Type

If a user uploads a file other than TXT or PDF:

```text
415 Unsupported Media Type
```

Example:

```json
{
    "detail": "Unsupported file type. Only .txt and .pdf files are allowed"
}
```

---

## File Too Large

If the file is larger than 5 MB:

```text
413 Request Entity Too Large
```

Example:

```json
{
    "detail": "File size exceeds the 5 MB limit"
}
```

---

## PDF Extraction Failure

If the PDF cannot be processed:

```text
422 Unprocessable Entity
```

---

## PDF Without Extractable Text

Scanned or image-only PDFs are not supported.

If no text can be extracted:

```text
422 Unprocessable Entity
```

Example:

```json
{
    "detail": "No extractable text found in the document"
}
```

OCR is not included in this task.

---

## Invalid Summary Type

Allowed values are:

```text
brief
detailed
bullet_points
```

If another value is provided:

```text
400 Bad Request
```

---

## Invalid API Key

If the OpenRouter API key is invalid:

```text
401 Unauthorized
```

The actual API key or raw OpenRouter error is not returned to the user.

---

## Rate Limit

If the AI service rate limit is reached:

```text
429 Too Many Requests
```

---

## AI Service Failure

If the AI service is unavailable:

```text
503 Service Unavailable
```

---

## Invalid AI Response

If the AI model returns an unexpected response:

```text
502 Bad Gateway
```

The application does not return the raw AI response.

---

# Testing Checklist

The following cases should be tested using Postman.

| Test | Expected Result |
|---|---|
| Valid TXT file | 200 |
| Valid PDF file | 200 |
| Multi-page PDF | 200 |
| Brief summary | 200 |
| Detailed summary | 200 |
| Bullet-point summary | 200 |
| Empty file | 400 |
| Missing file | 4xx |
| Unsupported file | 415 |
| Invalid summary type | 400 |
| PDF with no text | 422 |
| File above 5 MB | 413 |
| Invalid API key | 401 |
| AI service failure | 503 |
| Invalid AI response | 502 |

---

# Reusing Existing AI Logic

The document API does not create a separate AI implementation.

Both APIs use the same summarization service.

```text
                    ┌────────────────────┐
                    │ Summarization      │
                    │ Service            │
                    └─────────┬──────────┘
                              │
                              ↓
                         OpenRouter
                              ↑
                              │
          ┌───────────────────┴──────────────────┐
          │                                      │
     Text API                              Document API
          │                                      │
     JSON text                              PDF / TXT
                                                 │
                                                 ↓
                                           File Parser
                                                 │
                                                 ↓
                                           Extracted Text
```

This avoids duplicate code and makes the application easier to maintain.

---

# Security

Uploaded files are treated as untrusted input.

The application:

- Allows only TXT and PDF files
- Checks the file size
- Does not accept arbitrary file types
- Does not send the original PDF directly to the text model
- Does not expose API keys
- Does not expose raw OpenRouter errors
- Does not expose stack traces
- Does not store uploaded documents permanently

Do not commit the following files or folders:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
uploaded documents
cache files
API keys
secrets
```

---

# Git

Before pushing the project, check that sensitive files are ignored.

```bash
git status
```

Add the changes:

```bash
git add .
```

Commit with a meaningful message:

```bash
git commit -m "Add AI document summarization with file upload"
```

Push:

```bash
git push
```

---

# Task 15 Learning Outcomes

After completing this task, I understood:

- How file uploads work in FastAPI
- How to use `UploadFile`
- How `multipart/form-data` works
- How to validate uploaded files
- How to check file size
- How to read TXT files
- How to extract text from PDFs
- How uploaded files differ from extracted text
- How extracted text can be passed to an LLM
- How to reuse an existing AI service
- How to validate AI output using Pydantic
- How to handle file-processing errors
- How to handle AI service errors
- Why uploaded files should be treated as untrusted input

---

# Important Note

This project does not send PDF files directly to the AI text model.

The actual process is:

```text
PDF
 ↓
Extract Text using PyPDF2
 ↓
Extracted Text
 ↓
Summarization Service
 ↓
OpenRouter
 ↓
Structured AI Response
 ↓
Pydantic Validation
 ↓
Final API Response
```

Scanned and image-only PDFs are not supported because OCR is not part of Task 15.