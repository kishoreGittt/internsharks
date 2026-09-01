# Task 16 - Context-Aware AI Chat Assistant

## About

This project is a simple AI chatbot built using FastAPI and OpenRouter.

The main purpose of this task is to understand how an AI chatbot can remember previous messages.

The application stores conversation history in memory using a Python dictionary.

Each conversation has a separate session ID.

## Technologies Used

- Python
- FastAPI
- Pydantic
- OpenRouter
- HTTPX
- Python-dotenv

## Project Structure

```text
app/
├── routes/
│   └── chat.py
├── services/
│   ├── chat_service.py
│   └── ai_service.py
├── models/
│   └── chat.py
├── prompts/
│   └── chat_prompt.py
├── storage/
│   └── chat_memory.py
├── config.py
└── main.py