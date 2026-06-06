# TechNova RAG Assistant — Design Report

## 1. Document Loading and Metadata


- Documents are loaded from `knowledge-base` using Langchain in-built functions. No need to develop helper functions for that task. 
- All Categories based on the directory. Because it helps to maintenance this structure. Easy to scale
- A custom `clean_text()` function always remove whitespace before chunking, removing unnecessary spaces, duplicate spaces. 



## 2. Chunking Strategy

- **Splitter:** `RecursiveCharacterTextSplitter`
- **Chunk size:** 800 tokens
- **Chunk overlap:** 150 tokens

These MD documents have lengthy content. Before it passing to LLM , we need have to split them into small pieces (chunks). So I used langchain in-built `RecursiveCharacterTextSplitter` . 

Because I don't waste developer time for develop this kind of function.  Also , LLM likes to read chunks. It is hard to pass full lengthy content to LLM context. 


## 3. Embedding Model

`text-embedding-3-small` helps us to find high quality semantic similarity. Also its cheap modal.


## 4. Vector Store — ChromaDB

- **Store:** ChromaDB
- **Persistence:** `vector_db/` directory on disk

No need to pay additional charges. It runs on local server . Initial time , it creates new ChromaDB, other wise its loading exsisting ones. 

## 5. Retrieval Design

- **k (chunks retrieved):** 13
- **Out-of-scope threshold:** similarity score > 3.0
- **Category filtering:** Chroma `where=` metadata filter

Retrieving 13 chunks confirm large coverage accross categories. it helps to run complex queries. LLM can get good decision based on that documents. 

If user asks out of scope question, out of scope threshold helps to identify that .  Example: Who is the prime minister in sri lanka ? 

Category Filter , some users need have to select specific types. Eg: policies, faq ,etc. then Retriever can search documents using filtering option. It helps to get fastest results without searching entire vector database. 

Example:

`filter={"category": category}` 

## 6. LLM and System Prompt

- **Model:** `gpt-4.1-nano`
- **Temperature:** 0

`gpt-4.1-nano` -  low cost and fast response time. 

Temperature 0 - no need fancy answers. provide direct answers. 


## 7. Out-of-Scope Refusal

If the best similarity score exceeds 3.0, the system returns:
*"I don't have enough information to answer that question."*

## 8. Source Citations

If user says "Hi" , then this system never provide citations. if any technova related questions. then it shows up source citations . 

## 9. Multi-Turn Chat

Conversation history maintained using several ways. then LLM can provide comprehensive answer according to history . 

## 10. Evaluation Pipeline

It has two parts. summary provides overall idea of the evaluation. 

```
 "summary": {
    "total_questions": 29,
    "retrieval_precision": 0.931,
    "answer_score_avg": 4.76,
    "refused_correctly": true
  },
    "per_question": []
   
```

1. Total Questions:

```
questions = evaluation_data["questions"]
total_question = len(questions)  # → 29


```

2. retrieval_precision: 0.931

For each user question, checks if at least one expected source file appears in the actually retrieved sources. If yes , then counts as a hit.


```
if any(actual.endswith(expected) for expected in expected_sources
                                 for actual in actual_sources):
    retrieval_hits += 1

retrieval_precision = retrieval_hits / total_question
# = 27 hits / 29 questions = 0.931

```

3. refused_correctly: true

If there is out-of-scope question, then it never gives halucinated answer. directly say
"I don't have enough information..." 

if LLM gives false information ,then refused_correctly set to False



## 11. Deployment

Gradio , but we never recommend to use gradio in production environment. 