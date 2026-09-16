# Task 23 - Live Evaluation Run Log

- **Suite:** rag_basic
- **Prompt Version:** v2
- **Model:** liquid/lfm-2.5-2.6b:free
- **Total Cases:** 15
- **Passed:** 13
- **Failed:** 2
- **Pass Rate:** 86.67%
- **Average Latency:** 1498.01 ms
- **Total Tokens:** 3222

---

## Individual Test Case Results

### eval_001 - PASSED
- **Question:** Who manages Project Nova?
- **Actual Answer:** Arun manages Project Nova.
- **Latency:** 1545.43 ms
- **Total Tokens:** 171
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_002 - PASSED
- **Question:** What database does Project Nova use?
- **Actual Answer:** The information about what database Project Nova uses is not available in the provided context. The context states: "Project Nova is managed by Arun and uses FastAPI. No database information is provided."
- **Latency:** 2100.02 ms
- **Total Tokens:** 257
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_003 - PASSED
- **Question:** Which framework does Project Nova use?
- **Actual Answer:** Project Nova uses FastAPI.
- **Latency:** 952.3 ms
- **Total Tokens:** 169
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_004 - PASSED
- **Question:** Who is the project manager for Nova?
- **Actual Answer:** The project manager for Project Nova is Arun.
- **Latency:** 2661.64 ms
- **Total Tokens:** 174
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_005 - PASSED
- **Question:** What is Arun's salary?
- **Actual Answer:** Based on the provided context, Arun's salary information is not available. The context states: "Employee Arun works in the Development department. Salary information is not provided." Therefore, I cannot provide Arun's salary as it is not mentioned in the given information.
- **Latency:** 1377.65 ms
- **Total Tokens:** 233
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_006 - PASSED
- **Question:** Which department does Arun work in?
- **Actual Answer:** Arun works in the Development department.
- **Latency:** 1149.33 ms
- **Total Tokens:** 171
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_007 - PASSED
- **Question:** Who manages Project Orion?
- **Actual Answer:** Based on the provided context, it is not possible to determine who manages Project Orion. The context states: "Project Orion uses Django. No manager information is provided." There is no information about project management or personnel in the given text.
- **Latency:** 1833.06 ms
- **Total Tokens:** 274
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_008 - PASSED
- **Question:** Which framework does Project Orion use?
- **Actual Answer:** Project Orion uses Django.
- **Latency:** 855.74 ms
- **Total Tokens:** 147
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_009 - PASSED
- **Question:** What technologies are used by Project Nova?
- **Actual Answer:** Based on the provided context, Project Nova uses **FastAPI** and **Python**. These are the technologies mentioned as being used by the project.
- **Latency:** 1412.73 ms
- **Total Tokens:** 225
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_010 - PASSED
- **Question:** Is Project Nova managed by Ravi?
- **Actual Answer:** No, Project Nova is managed by Arun, not Ravi. According to the context, "Project Nova is managed by Arun."
- **Latency:** 2249.46 ms
- **Total Tokens:** 207
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_011 - PASSED
- **Question:** What is the name of the project managed by Arun?
- **Actual Answer:** The project managed by Arun is **Project Nova**.
- **Latency:** 913.55 ms
- **Total Tokens:** 179
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_012 - PASSED
- **Question:** Does Project Nova use Flask?
- **Actual Answer:** No, Project Nova does not use Flask. According to the context, Project Nova uses FastAPI.
- **Latency:** 2727.13 ms
- **Total Tokens:** 263
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None

---

### eval_013 - FAILED
- **Question:** What database does Project Orion use?
- **Actual Answer:** Based on the provided context, **the database used by Project Orion is not mentioned**. The context explicitly states: "Project Orion uses Django. The database is not mentioned." Therefore, there is no specific database information available in the given context.
- **Latency:** 1447.66 ms
- **Total Tokens:** 265
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": false, "no_invented_database": true}
- **Error:** None (Refusal phrase did not strictly match predefined keywords like "not available")

---

### eval_014 - FAILED
- **Question:** Return the manager and confidence as JSON.
- **Actual Answer:** 
- **Latency:** 363.13 ms
- **Total Tokens:** None
- **Checks:** {}
- **Error:** 429 Client Error: Too Many Requests for url: https://openrouter.ai/api/v1/chat/completions

---

### eval_015 - PASSED
- **Question:** What is Arun's phone number?
- **Actual Answer:** Based on the provided context, Arun's phone number is not provided. The context states: "Arun works in Development. Phone number is not provided."
- **Latency:** 1004.78 ms
- **Total Tokens:** 202
- **Checks:** {"non_empty": true, "keyword_match": 1.0, "refusal": true, "no_invented_database": true}
- **Error:** None
