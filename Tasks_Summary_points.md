Tasks

Task 1 -- Basic FastAPI Validation

1.  Created a basic FastAPI application.
2.  Created a POST API for user details.
3.  Used Pydantic for request validation.
4.  Validated name, email, and age.
5.  Added email format and age validation.
6.  Learned basic API request and response handling.

Task 2 -- Student CRUD

1.  Created a Student Management API.
2.  Added students using POST.
3.  Retrieved students using GET.
4.  Updated students using PUT.
5.  Deleted students using DELETE.
6.  Used Pydantic models and an in-memory list.

Task 3 -- Search & Filtering

1.  Added student search functionality.
2.  Used query parameters in FastAPI.
3.  Added search by student name.
4.  Added filtering by course.
5.  Learned query parameters and path parameters.
6.  Handled cases where no matching student exists.

Task 4 -- JSON File Persistence

1.  Added permanent data storage using JSON.
2.  Created functions to read JSON data.
3.  Created functions to save JSON data.
4.  Updated JSON after CRUD operations.
5.  Loaded existing data when the application starts.
6.  Learned basic file-based data persistence.

Task 5 -- MongoDB Integration

1.  Connected FastAPI with MongoDB.
2.  Used Motor for asynchronous database operations.
3.  Created MongoDB collections.
4.  Stored and retrieved data from MongoDB.
5.  Separated routes, models, services, and database logic.
6.  Learned how backend applications work with databases.

Task 6 -- User Authentication

1.  Created user registration and login APIs.
2.  Stored users in MongoDB.
3.  Added password hashing using bcrypt.
4.  Prevented duplicate email registration.
5.  Created a user profile endpoint.
6.  Learned secure authentication basics.

Task 7 -- JWT Authentication

1.  Added JWT-based authentication.
2.  Generated access tokens during login.
3.  Protected API routes using JWT.
4.  Used Bearer tokens in requests.
5.  Added token expiration handling.
6.  Created a protected `/me` endpoint.

Task 8 -- RBAC & User Management

1.  Added user and admin roles.
2.  Implemented role-based access control.
3.  Restricted admin-only operations.
4.  Added user management functionality.
5.  Added active and inactive user status.
6.  Prevented normal users from changing their own role.

Task 9 -- Refresh Tokens

1.  Added refresh token functionality.
2.  Separated access and refresh tokens.
3.  Added different expiration times.
4.  Created a refresh-token API.
5.  Added logout and token revocation.
6.  Learned the complete JWT token lifecycle.

Task 10 -- Task Management Backend

1.  Created a production-style task management API.
2.  Added task creation, update, view, and delete.
3.  Added task status and priority.
4.  Added task assignment and due dates.
5.  Added authentication and authorization.
6.  Added pagination, search, and filtering.

Task 11 -- Production Hardening

1.  Added centralized exception handling.
2.  Created consistent JSON error responses.
3.  Added application and request logging.
4.  Added health-check functionality.
5.  Added environment-based configuration.
6.  Added automated API testing using pytest.

Task 12 -- Basic AI Text Assistant

1.  Integrated an AI API with FastAPI.
2.  Initially used Groq for AI generation.
3.  Created the `/ai/generate` endpoint.
4.  Sent user prompts to the AI model.
5.  Added API-key configuration using environment variables.
6.  Added validation and AI error handling.

Task 13 -- Structured AI Output

1.  Created an AI text analysis API.
2.  Added summary generation.
3.  Added category and priority detection.
4.  Added sentiment and keyword extraction.
5.  Used prompt engineering for consistent output.
6.  Validated AI responses using Pydantic.

Task 14 -- AI Summarization

1.  Integrated OpenRouter for AI summarization.
2.  Created the `/ai/summarize` endpoint.
3.  Added brief summarization.
4.  Added detailed summarization.
5.  Added bullet-point summarization.
6.  Returned structured summary information.

Task 15 -- Document Summarization

1.  Added document upload support.
2.  Accepted TXT and PDF files.
3.  Extracted text from uploaded documents.
4.  Sent extracted content to the AI model.
5.  Generated summaries using OpenRouter.
6.  Added file validation and error handling.

Task 16 -- Context-Aware AI Chat

1.  Created a session-based AI chat system.
2.  Stored conversation history in memory.
3.  Sent previous messages as context.
4.  Used system, user, and assistant roles.
5.  Limited the conversation context to recent messages.
6.  Added APIs to view and delete chat history.

Task 17 -- RAG / Knowledge Retrieval

1.  Learned Retrieval-Augmented Generation concepts.
2.  Stored documents as searchable knowledge.
3.  Created embeddings for document content.
4.  Retrieved relevant information for user questions.
5.  Added retrieved information to the AI prompt.
6.  Improved AI answers using external knowledge.

Task 18 -- AI Tool Calling

1.  Created an AI action assistant.
2.  Implemented AI tool/function calling.
3.  Added calculator operations such as add, subtract, multiply, and
    divide.
4.  Added current-date and task-lookup tools.
5.  Validated tool arguments before execution.
6.  Sent tool results back to the AI for the final response.


