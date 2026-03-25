# 📂 RAG Production Intelligence System

A high-performance, asynchronous **Retrieval-Augmented Generation (RAG)** pipeline. This system is engineered for scalability, moving beyond simple scripts into a production-ready environment using **FastAPI** for the backend, **Inngest** for reliable event orchestration, and **Qdrant** for high-dimensional vector search.

---

## 🏗️ Architecture: From Monolith to Distributed
The application is structured as a **three-tier system** to ensure the user interface remains responsive even during heavy AI processing:

1. **The Interface (Streamlit)**: A clean, reactive frontend for document upload and querying.
2. **The Brain (FastAPI / `main.py`)**: A dedicated backend server that hosts the AI logic and embedding engine.
3. **The Orchestrator (Inngest)**: A background worker system that manages long-running tasks (like PDF embedding) so the UI never freezes.

---

## 🛠️ Key Engineering Enhancements

### 1. Unified Vector Alignment
The system is standardized on **OpenAI’s `text-embedding-3-large`** model. 
* **The Challenge**: Standard RAG setups often suffer from "Dimension Mismatches" (e.g., searching 3072-dim data with a 1536-dim query).
* **The Solution**: Forced 3072-dimension consistency across both the **Ingestion** and **Query** layers, ensuring 100% precision in Qdrant retrieval.

### 2. Asynchronous Ingestion Pipeline
By utilizing **Inngest**, the app handles PDF processing as a resilient background "Job."
* **Reliability**: If an API call to OpenAI fails, the system automatically handles retries.
* **Concurrency**: Users can continue querying existing data while new documents are being indexed in the background.

### 3. Isolated Environment Management
The project utilizes a dedicated Python 3.13 virtual environment (`.venv`) with specifically injected LlamaIndex modules (`embeddings-openai`, `llms-openai`) to ensure zero dependency drift and maximum performance.

---

## 🚀 Execution Instructions

To run the full stack, you must have three services running. Open **three separate terminal tabs** and run one command in each:

### Terminal 1: Start the Backend (The "Engine")
```bash
/Users/nagarajukrishnappa/Desktop/RAGProdApp/.venv/bin/python main.py
```

### Terminal 2: Start the Bridge (Inngest)
```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest
```

### Terminal 3: Start the UI (The "Dashboard")
```bash
/Users/nagarajukrishnappa/Desktop/RAGProdApp/.venv/bin/python -m streamlit run streamlit_app.py
```

---

## 📂 Project Structure

* **`main.py`**: The central API and Background Worker host.
* **`data_loader.py`**: Logic for document chunking and vector upserts.
* **`streamlit_app.py`**: The Streamlit user interface.
* **`Qdrant`**: Vector database for persistent, high-speed memory.

---

## 📈 Roadmap

- [ ] **Advanced Reranking**: Implementing a Cross-Encoder layer to prioritize the most relevant document chunks.
- [ ] **Multi-modal Support**: Extraction and querying of charts and images within technical PDFs.
- [ ] **Auto-scaling**: Transitioning background workers to serverless cloud functions.