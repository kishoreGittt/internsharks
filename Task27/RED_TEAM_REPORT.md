# Red Team Report

| Test ID | Category                        
| ------- | ---------------------- 
| TC-01   | RAG hallucination      
| TC-02   | Wrong retrieval        
| TC-03   | Cross-user leakage    
| TC-04   | Document injection     
| TC-05   | Image injection        
| TC-06   | Invalid tool arguments 
| TC-07   | Unnecessary tool       
| TC-08   | Live backend tool      
| TC-09   | Duplicate action       
| TC-10   | Unknown tool          
| TC-11   | OpenRouter failure     
| TC-12   | Malformed output       
| TC-13   | Huge upload           
| TC-14   | Invalid upload      
| TC-15   | OpenRouter timeout    
| TC-16   | Context confusion      
| TC-17   | Unauthorized document  
| TC-18   | Document failure     
| TC-19   | Worker restart         
| TC-20   | Conversation isolation 
| TC-21   | RAG isolation          
| TC-22   | Sensitive logging      
| TC-23   | Vision hallucination  
| TC-24   | RAG + tool failure     
| TC-25   | Failed request trace   
| TC-26   | Empty message          
| TC-27   | Memory vs backend      
| TC-28   | RAG/backend conflict   
| TC-29   | Invalid conversation   
| TC-30   | Invalid vision file    
| TC-31   | Missing vision file    
| TC-32   | Sensitive prompt       
| TC-33   | Invalid document       
| TC-34   | Unauthorized chat      
| TC-35   | Health/dependency      

# Mandatory Test Cases

The project instructions identify these as mandatory for the remaining work:

- TC-08 — Tool required for live backend data
- TC-10 — Unknown tool rejection
- TC-15 — OpenRouter timeout
- TC-18 — Document processing failure
- TC-19 — Restart during document processing
- TC-27 — Conversation memory vs current backend data
- TC-28 — RAG data vs backend data conflict
- TC-32 — Sensitive prompt must not appear in logs/traces
- TC-40 — Vision hallucination
- TC-43 — Combined RAG + tool partial failure
- TC-46 — Failed request must still create trace

Drawbacks:
 
 couldn't able to track the previous fastly.
 for the 15-20 test cases responce or correct and other are not camed.
 by the uses of access token it is very difficulty to handle the all test cases.
 
Advantages:
    The more testcase can give the best quality of product
