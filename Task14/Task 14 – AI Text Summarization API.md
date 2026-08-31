# Task 14 – AI Text Summarization API

## About the Project

In this task, I created an AI-powered text summarization API using **FastAPI** and **OpenRouter**.

The API accepts a text and a summary type. Based on the selected summary type, the AI generates a different type of summary.

The API supports:

- Brief summary
- Detailed summary
- Bullet-point summary

It also extracts the **main topic** and **important keywords** from the given text.

---

## Technologies Used

- Python
- FastAPI
- Pydantic
- OpenRouter
- HTTPX
- Uvicorn
- Postman

---

## Project Structure

```text
Task14/
│
├── app/
│   ├── routes/
│   │   └── summarizer.py
│   │
│   ├── services/
│   │   └── summarizer_service.py
│   │
│   ├── models/
│   │   └── summarizer.py
│   │
│   ├── prompts/
│   │   └── summarizer_prompt.py
│   │
│   ├── config.py
│   └── main.py
│
├── .env
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## How It Works

The basic flow of the application is:

```text
Postman
   ↓
FastAPI
   ↓
Validate Input
   ↓
Check Summary Type
   ↓
Create AI Prompt
   ↓
OpenRouter
   ↓
AI Model
   ↓
Structured Response
   ↓
Pydantic Validation
   ↓
Final Response
```

---

## API Endpoint

### POST `/ai/summarize`

The API accepts a text and a summary type.

### Request

```json
{
    "text": "The development team is working on a payment API integration. The project is currently blocked because the client has not provided the required credentials.",
    "summary_type": "brief"
}
```

---

## Summary Types

### 1. Brief

Gives a short summary with only the main information.

```text
The payment API integration is currently blocked because the client
has not provided the required credentials.
```

### 2. Detailed

Gives a longer summary and keeps the important details from the original text.

### 3. Bullet Points

Shows the important information as bullet points.

```text
- Payment API integration is in progress.
- Client credentials are required.
- The project is currently blocked.
```

The same API endpoint is used for all three types. The `summary_type` decides how the AI should respond.

---

## AI Prompt

I used a **system prompt** to tell the AI how it should behave.

The system prompt tells the AI to:

- Summarize the given text
- Not make up information
- Find the main topic
- Find important keywords
- Follow the requested summary type
- Return the result in JSON format

The user's text is sent separately as the **user prompt**.

This helps me understand the difference between a system prompt and a user prompt.

---

## AI Response

The AI returns information in a structured format like this:

```json
{
    "summary": "The payment API integration is blocked by missing client credentials.",
    "main_topic": "Payment API Integration",
    "keywords": [
        "payment",
        "API",
        "credentials"
    ]
}
```

The application does not directly return the raw AI response.

Instead, the response is checked using **Pydantic** before sending it to the user.

---

## Environment Variables

The OpenRouter API key and model are stored in the `.env` file.

```env
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=your_model
```

The API key is not written directly inside the Python code.

The `.env` file should not be pushed to GitHub.

---

## Installation

First create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

---

## Run the Project

Run the FastAPI application using:

```powershell
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Postman Testing

I tested the API using Postman.

The main test cases are:

1. Brief summary
2. Detailed summary
3. Bullet-point summary
4. Short text
5. Long text
6. Empty text
7. Missing text
8. Invalid summary type
9. Invalid API key
10. AI service failure

---

## Example Response

```json
{
    "success": true,
    "status_code": 200,
    "data": {
        "summary_type": "brief",
        "summary": "The payment API integration is blocked because client credentials are missing.",
        "main_topic": "Payment API Integration",
        "keywords": [
            "payment",
            "API",
            "credentials"
        ]
    }
}
```

---

## Error Handling

The API also handles errors such as:

- Invalid input
- Empty text
- Invalid summary type
- Invalid API key
- AI service failure
- Model unavailable
- Rate limit
- Invalid AI response

The application returns a proper error message instead of exposing the raw OpenRouter error.

---

## What I Learned

Through this task, I learned:

- How to connect FastAPI with an AI API
- How OpenRouter works
- How to create system and user prompts
- How prompt instructions change AI output
- How one API can support different behaviours
- How to get structured output from an AI model
- How to validate AI responses using Pydantic
- How to handle AI API errors
- How to protect API keys using environment variables
- How to test an AI API using Postman

---

## Task 14 Flow

```text
User sends text
       ↓
Selects summary type
       ↓
FastAPI validates the request
       ↓
Backend creates the prompt
       ↓
OpenRouter sends request to AI model
       ↓
AI generates summary + topic + keywords
       ↓
Pydantic validates AI response
       ↓
FastAPI sends final response
```

The main idea of this task is to understand how **backend input controls AI behaviour** and how an AI response can be converted into useful and structured application data.