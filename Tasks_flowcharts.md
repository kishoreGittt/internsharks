# Flowcharts for Tasks

## Task 1 -- Basic FastAPI Validation

``` text
START
  ↓
Create FastAPI Application
  ↓
Create POST /user API
  ↓
Define Pydantic Model
(name, email, age)
  ↓
Validate Email and Age
  ↓
Receive User Request
  ↓
Check Validation
  ├── Invalid → Return 422 Error
  └── Valid
        ↓
     Return Response
        ↓
       END
```



## Task 2 -- Student CRUD

``` text
START
  ↓
Create Student Model
  ↓
Create In-Memory Student List
  ↓
POST /students
(Add Student)
  ↓
GET /students
(Get All Students)
  ↓
GET /students/{id}
(Get One Student)
  ↓
PUT /students/{id}
(Update Student)
  ↓
DELETE /students/{id}
(Delete Student)
  ↓
Return Response
  ↓
END
```



## Task 3 -- Search \& Filtering

``` text
START
  ↓
Receive Search Request
  ↓
Add Query Parameters
  ↓
Search by Student Name
  ↓
Filter by Course
  ↓
Check Matching Students
  ├── No Match → Return No Results
  └── Match Found
        ↓
     Return Filtered Students
        ↓
       END
```



## Task 4 -- JSON File Persistence

``` text
START
  ↓
Create JSON File
  ↓
Create Read JSON Function
  ↓
Create Save JSON Function
  ↓
Load Data at Application Startup
  ↓
Perform CRUD Operation
  ↓
Update Student Data
  ↓
Save Updated Data to JSON
  ↓
Return Response
  ↓
END
```



## Task 5 -- MongoDB Integration

``` text
START
  ↓
Install Motor
  ↓
Configure MongoDB Connection
  ↓
Connect FastAPI to MongoDB
  ↓
Create Database and Collection
  ↓
Create Models
  ↓
Implement CRUD Operations
  ↓
Separate Routes / Models / Services / Database
  ↓
Test MongoDB APIs
  ↓
END
```



## Task 6 -- User Authentication

``` text
START
  ↓
Create Register API
  ↓
Receive User Details
  ↓
Check Duplicate Email
  ├── Exists → Return Error
  └── Not Exists
        ↓
     Hash Password
        ↓
     Store User in MongoDB
        ↓
     Create Login API
        ↓
     Verify Email \& Password
        ↓
     Create /me Profile API
        ↓
       END
```



## Task 7 -- JWT Authentication

``` text
START
  ↓
User Login
  ↓
Verify Email and Password
  ↓
Generate JWT Access Token
  ↓
Return Access Token
  ↓
Client Sends Bearer Token
  ↓
Protected API Receives Token
  ↓
Validate JWT
  ├── Invalid/Expired → Return 401
  └── Valid
        ↓
     Allow Access
        ↓
       END
```



## Task 8 -- RBAC \& User Management

``` text
START
  ↓
User Logs In
  ↓
Get User Role
  ↓
Check Role
  ├── USER → Allow User Operations
  └── ADMIN → Allow Admin Operations
                 ↓
              Manage Users
                 ↓
          Change Active Status
                 ↓
               END
```



## Task 9 -- Refresh Tokens

``` text
START
  ↓
User Login
  ↓
Generate Access Token
  ↓
Generate Refresh Token
  ↓
Set Different Expiration Times
  ↓
Return Both Tokens
  ↓
Access Token Expires
  ↓
Send Refresh Token
  ↓
POST /auth/refresh
  ↓
Validate Refresh Token
  ├── Invalid → Return Error
  └── Valid
        ↓
     Generate New Access Token
        ↓
     Logout / Revoke Token
        ↓
       END
```



## Task 10 -- Task Management Backend

``` text
START
  ↓
Create Task Model
  ↓
User Authentication
  ↓
Create Task
  ↓
Set Status \& Priority
  ↓
Assign Task to User
  ↓
Set Due Date
  ↓
View / Update / Delete Task
  ↓
Add Search \& Filtering
  ↓
Add Pagination
  ↓
Check User Authorization
  ↓
Return Task Response
  ↓
END


```

## Task 11 -- Production Hardening

``` text
START
  ↓
Add Centralized Exception Handling
  ↓
Create Consistent Error Responses
  ↓
Add Application Logging
  ↓
Add Request Logging Middleware
  ↓
Add Health Check
  ↓
Add Environment Configuration
  ↓
Protect Sensitive Information
  ↓
Create Pytest Tests
  ↓
Run Automated Tests
  ↓
END
```



## Task 12 -- Basic AI Text Assistant

``` text
START
  ↓
Configure AI API Key
  ↓
Create /ai/generate Endpoint
  ↓
Receive User Prompt
  ↓
Send Prompt to AI Model
  ↓
AI Generates Response
  ↓
Return AI Response
  ↓
Handle API Errors
  ↓
END
```



## Task 13 -- Structured AI Output

``` text
START
  ↓
Create /ai/analyze Endpoint
  ↓
Receive User Text
  ↓
Create AI Prompt
  ↓
Send Text to AI Model
  ↓
Generate:
Summary
Category
Priority
Sentiment
Keywords
  ↓
Validate AI Response with Pydantic
  ├── Invalid → Return Error
  └── Valid
        ↓
     Return Structured Output
        ↓
       END
```



## Task 14 -- AI Summarization

``` text
START
  ↓
Configure OpenRouter
  ↓
Create /ai/summarize Endpoint
  ↓
Receive Text
  ↓
Select Summary Type
  ├── Brief
  ├── Detailed
  └── Bullet Points
        ↓
     Send Prompt to AI
        ↓
     Generate Summary
        ↓
     Validate Response
        ↓
     Return Summary
        ↓
       END
```



## Task 15 -- AI Document Summarization

``` text
START
  ↓
Upload Document
  ↓
Check File Type
  ├── Invalid → Return Error
  └── TXT/PDF
        ↓
     Extract Text
        ↓
     Check Extracted Content
        ↓
     Send Text to AI Model
        ↓
     Generate Summary
        ↓
     Validate AI Response
        ↓
     Return Document Summary
        ↓
       END
```



## Task 16 -- Context-Aware AI Chat

``` text
START
  ↓
Receive session\_id
  ↓
Receive User Message
  ↓
Check Chat History
  ↓
Add User Message to History
  ↓
Get Recent Messages
  ↓
Send History + New Message to AI
  ↓
AI Generates Response
  ↓
Store Assistant Response
  ↓
Return AI Response
  ↓
GET Chat History
  OR
DELETE Chat History
  ↓
END
```



## Task 17 -- RAG / Knowledge Retrieval

``` text
START
  ↓
Add Documents
  ↓
Extract Document Text
  ↓
Split Text into Chunks
  ↓
Create Embeddings
  ↓
Store Knowledge
  ↓
Receive User Question
  ↓
Create Query Embedding
  ↓
Retrieve Relevant Chunks
  ↓
Add Retrieved Context to AI Prompt
  ↓
Send Prompt to AI
  ↓
Generate Knowledge-Based Answer
  ↓
Return Answer
  ↓
END
```

## Task 18 -- AI Tool Calling

``` text
START
  ↓
Receive User Request
  ↓
Send Request + Available Tools to AI
  ↓
AI Understands Request
  ↓
Does AI Need a Tool?
  ├── NO
  │    ↓
  │  Generate Normal Response
  │    ↓
  │   END
  │
  └── YES
       ↓
    Select Tool
       ↓
    Validate Tool Arguments
       ↓
    Execute Registered Tool
       ↓
    Get Tool Result
       ↓
    Send Tool Result Back to AI
       ↓
    AI Generates Final Response
       ↓
      END
```

```

