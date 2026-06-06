# TechNova RAG Assistant

A Retrieval-Augmented Generation (RAG) chatbot for TechNova customer support,
built with LangChain, ChromaDB, and OpenAI.

## Overview

TechNova RAG Assistant is a customer support chatbot that answers questions
about TechNova products, policies, and services using Retrieval-Augmented
Generation (RAG). Instead of relying on general AI knowledge, it retrieves
relevant information directly from TechNova's internal knowledge base and
generates accurate, cited responses.

## Features

- Multi-turn conversation with memory
- Category-based document filtering
- Off-topic question detection
- Source citations for answers
- LLM-based evaluation pipeline

## Project Structure

```
technova_rag_assistant/
├── app.py
├── config.py
├── prompts.py
├── rag/
│ ├── chain.py
│ ├── embeddings.py
│ ├── retriever.py
│ └── loader.py
├── evaluation/
│ ├── evaluator.py
│ ├── questions.json
│ └── eval_results.json
├── knowledge-base/
└── vector_db/
```

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

# Clone the repository

- Download ZIP file
- Unzip it
- cd technova_rag_assistant

# Create and activate virtual environment

```

python -m venv .venv
source .venv/bin/activate # Mac/Linux
.venv\Scripts\activate # Windows

```

# Install dependencies

```

pip install -r requirements.txt

```

### Environment Variables

Create a .env file in the project root:

```

OENAI_API_KEY=sk-your-api-key-here

```

## Usage

Run the App

```

python app.py

```

Then open http://127.0.0.1:7860 in your browser.

Run Evaluation

```

python -m evaluation.evaluator

```

Results will be saved to `evaluation/eval_results.json`.

### Run the App

### Run Evaluation

## Evaluation Results

```
| Metric              | Score    |
| ------------------- | -------- |
| Answer Score Avg    | 4.62 / 5 |
| Retrieval Precision | 0.931    |
| Refused Correctly   | true     |
```

## Tech Stack

- Python 3.11
- LangChain
- ChromaDB
- OpenAI GPT-4.1-nano
- Gradio
# technova_rag_assistant
