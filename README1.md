# Knowledge Graph AI - Graph RAG POC

## Overview

This project demonstrates a **Proof-of-Concept (POC)** for building a **Knowledge Graph (KG)** combined with **Retrieval-Augmented Generation (RAG)**.  

We are using a dataset of **prompt-response pairs related to Apple products** and creating a graph where:

- **Prompt nodes** hold the text + embedding (semantic vector)  
- **Metadata nodes** (Topic, Theme, Mention, Citation, Region, Model) store structured information  
- Relationships connect Prompt nodes to metadata for easy filtering and analytics  

This setup allows us to **ask new questions** and retrieve relevant responses from the graph efficiently using **vector embeddings**.

---

## Target / Goal

- Build a **graph database** with prompts as main nodes and metadata as supporting nodes  
- Generate **embeddings** for semantic search and RAG retrieval  
- Allow **filtered search** based on metadata (Topic, Theme, Region, Model)  
- Demonstrate a **mini knowledge base** POC for portfolio, learning, or interview purposes  

---

## Folder Structure

Knowledge-graph-ai/
├─ data/ # JSON datasets
│ ├─ apple_prompt_response_1000.jsonl
│ ├─ apple_prompt_response_1000_realistic.jsonl
│ └─ data.json
├─ scripts/ # Python scripts for data processing, graph ingestion, RAG queries
│ └─ generate_records.py
├─ notebooks/ # Optional Jupyter notebooks for demos
├─ README.md # Project documentation
└─ requirements.txt # Python dependencies



---

## Dataset

The dataset contains records like:

```json
{
  "run_id": "r0001",
  "created_at": "2024-08-01T09:01:00Z",
  "prompt_id": "p0001",
  "prompt": "Why does iPhone have issue related to Privacy?",
  "mentions": ["iPhone 13"],
  "prompt_type": "open-ended",
  "response": "This issue can be caused by factors related to privacy.",
  "citations": ["https://site2.com"],
  "themes": ["Security"],
  "topics": ["Privacy"],
  "region": "India",
  "model": "Gemini",
  "tags": ["apple", "branded"]
}


Notes:

run_id, prompt_id → unique identifiers

prompt + response → used to generate embeddings for semantic search

mentions, topics, themes, citations, region, model → metadata nodes in the graph

Graph Ontology
Nodes
Node	Attributes / Properties
Prompt	run_id, prompt_id, prompt, response, embedding, prompt_type, created_at, tags
Topic	name
Theme	name
Mention	name
Citation	name
Region	name
Model	name
Relationships
From Node	To Node	Relationship
Prompt	Topic	HAS_TOPIC
Prompt	Theme	HAS_THEME
Prompt	Mention	MENTIONS
Prompt	Citation	CITED_IN
Prompt	Region	IN_REGION
Prompt	Model	GENERATED_BY
Steps to Build the Solution
Step 1: Setup environment
pip install -r requirements.txt


Install Neo4j (local or Aura free)

Start Neo4j and remember credentials

Step 2: Load JSON data
import json

with open("data/apple_prompt_response_1000_realistic.jsonl") as f:
    data = [json.loads(line) for line in f]

Step 3: Generate embeddings (Prompt node only)
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

for record in data:
    text = record["prompt"] + " " + record["response"]
    record["embedding"] = model.encode(text).tolist()


Combines prompt + response for one embedding per record

Embedding stored in Prompt node

Step 4: Ingest graph into Neo4j

Create Prompt nodes with embedding

Create metadata nodes (Topic, Theme, Mention, Citation, Region, Model)

Connect Prompt → metadata nodes with relationships

Python snippet example:

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j","password"))

def create_graph(tx, record):
    tx.run("""
    MERGE (p:Prompt {id:$run_id})
    SET p.prompt=$prompt, p.response=$response, p.embedding=$embedding
    WITH p
    UNWIND $topics AS t
        MERGE (topic:Topic {name:t})
        MERGE (p)-[:HAS_TOPIC]->(topic)
    UNWIND $themes AS th
        MERGE (theme:Theme {name:th})
        MERGE (p)-[:HAS_THEME]->(theme)
    UNWIND $mentions AS m
        MERGE (mention:Mention {name:m})
        MERGE (p)-[:MENTIONS]->(mention)
    UNWIND $citations AS c
        MERGE (citation:Citation {name:c})
        MERGE (p)-[:CITED_IN]->(citation)
    MERGE (region:Region {name:$region})
    MERGE (p)-[:IN_REGION]->(region)
    MERGE (model:Model {name:$model})
    MERGE (p)-[:GENERATED_BY]->(model)
    """, record)

with driver.session() as session:
    for rec in data:
        session.write_transaction(create_graph, rec)

Step 5: RAG Retrieval

User enters a query → generate embedding

Use FAISS or Neo4j GDS to find nearest Prompt nodes

Retrieve response + metadata

Example:

import faiss
import numpy as np

dim = len(data[0]['embedding'])
index = faiss.IndexFlatL2(dim)
embeddings = np.array([rec['embedding'] for rec in data], dtype='float32')
index.add(embeddings)

query = "Why does iPhone battery drain quickly?"
query_emb = model.encode(query).astype('float32')
D, I = index.search(np.array([query_emb]), k=5)

for i in I[0]:
    print(data[i]["prompt"], data[i]["response"])

Step 6: Metadata filtering

Filter prompts before or after vector search by Topic, Theme, Region, or Model

Example: only prompts where Topic=Battery and Region=US

Step 7: Test & validate

Run sample queries

Check retrieved prompts, responses, and metadata

Ensure relevance and correctness

Step 8: Commit & document

Organize repo: data/, scripts/, notebooks/

Commit changes to GitHub:

git add .
git commit -m "Reorganized folder structure + graph ingestion setup"
git push origin main


Add screenshots or Neo4j diagrams if desired

Sample Query Output
User Query	Prompt Retrieved	Response	Topic	Theme	Region	Model
Why does iPhone battery drain?	Why does iPhone have issue related to Battery?	Battery may drain faster due to background apps	Battery	Hardware	US	ChatGPT
Next Steps / Enhancements

Add Streamlit/Gradio interface for interactive queries

Integrate Neo4j GDS for vector search instead of FAISS

Add analytics dashboard for prompts/topics/themes

Scale dataset to 10k+ prompts



 This README:

1. Explains **what we are building**  
2. Shows **folder structure**  
3. Details **step-by-step instructions**  
4. Includes **sample data and query example**  
5. Mentions **next enhancements**  