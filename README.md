

# RAG Chat System 

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline with:

* **Python (FastAPI)** → Core RAG logic, embeddings, data ingestion, and LLM inference.
* **Node.js Backend** → Can consume the exposed FastAPI endpoints and integrate with a frontend or other services.
* **MongoDB Atlas + AWS S3** → Knowledge base and document storage.
* **OpenAI & Serper API** → For embeddings, completions, and web search augmentation.

---

## 🚀 Features

* Chat API with Perplexity-style answers (`/chat`).
* Categorized web + knowledge base sources (`/websource`).
* Follow-up suggestions (`/related`).
* Health endpoint (`/health`).
* Ingestion pipeline: fetches docs from **MongoDB** and **S3**, chunks them, embeds via OpenAI, and stores embeddings in MongoDB Atlas.
* Persistent chat history in MongoDB.

---

## 📦 Installation



### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env` with your credentials:

```env
MONGODB_URI="your-mongo-uri"
DATABASE_NAME="daysdemo"
COLLECTION_NAME="embedding"
MONGO_VECTOR_INDEX_NAME="vector_index"
MONGO_HISTORY_COLLECTION_NAME="chathistory"

AWS_ACCESS_KEY_ID="your_aws_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret"
AWS_REGION="ap-south-1"
S3_BUCKET_NAME="your-s3-bucket"

OPENAI_API_KEY="your-openai-key"
SERPER_API_KEY="your-serper-key"

EMBEDDING_MODEL="text-embedding-ada-002"
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
BATCH_SIZE=10
DEFAULT_K=5
```

---

## ▶️ Running Services

### 1. Start FastAPI Server

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Now your API is available at:

```
http://localhost:8000
```

### 2. Test Endpoints

* **Chat**

  ```bash
  curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"query":"What is Retrieval-Augmented Generation?"}'
  ```
* **Sources** → `GET /websource`
* **Related prompts** → `GET /related`
* **Health check** → `GET /health`

---

## 📊 Code Flow

Here’s how the system works:

### 1. **Ingestion (`ingest.py`)**

* Loads documents from **S3 JSON files** & **MongoDB records**.
* Splits them into chunks using `RecursiveCharacterTextSplitter`.
* Embeds each chunk with **OpenAI Embeddings**.
* Stores embeddings + metadata back into MongoDB Atlas.

### 2. **Data Service (`data.py`)**

* Connects to MongoDB and retrieves relevant chunks via `$vectorSearch`.
* Collects sources (KB + categorized web links).
* Saves chat history in MongoDB.
* Integrates with **Serper API** for web search.

### 3. **Chat Orchestration (`chat.py`)**

* Takes a user query.
* Retrieves knowledge base + web context.
* Sends both to **OpenAI GPT model** for answer generation.
* Generates **related prompts**.
* Returns: `{query, answer, sources, related_prompts}`.

### 4. **API Layer (`api.py`)**

* **`/chat`** → Runs full pipeline, returns **answer**.
* **`/websource`** → Returns last query’s sources.
* **`/related`** → Returns last query’s related prompts.
* **`/health`** → API health check.

### 5. **Node.js Integration**

* Your Node.js backend can call the FastAPI endpoints just like any REST API:

  ```js
  const axios = require("axios");
  const response = await axios.post("http://localhost:8000/chat", { query: "Hello AI" });
  console.log(response.data.answer);
  ```

---

## 🧪 Testing MongoDB Connection

```bash
python test_mongo.py
```

If successful:

```
✅ Connected successfully!
```

---


## 📌 Summary

* **Python handles AI & data pipelines (FastAPI + RAG pipeline).**
* **Node.js backend calls FastAPI endpoints and serves clients.**
* **MongoDB + S3 act as persistent knowledge sources.**


