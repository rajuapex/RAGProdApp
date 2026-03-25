import os
from fastapi import FastAPI
import inngest
import inngest.fast_api
from dotenv import load_dotenv

# Query specific imports
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from qdrant_client import QdrantClient

# Ensure these match your data_loader.py exactly
from data_loader import sync_master_folder, embed_nodes

load_dotenv()

# 1. Initialize FastAPI app
app = FastAPI(title="RAG Production API")

# 2. Initialize Inngest Client
inngest_client = inngest.Inngest(app_id="rag_prod_app", is_production=False)

# --- FUNCTION 1: Ingest PDFs ---
@inngest_client.create_function(
    fn_id="ingest_pdf_workflow",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"), 
)
async def rag_ingest_pdf(ctx: inngest.Context):
    pdf_path = ctx.event.data.get("pdf_path")
    source_id = ctx.event.data.get("source_id", "unknown")

    if not pdf_path:
        return {"status": "error", "message": "No pdf_path provided"}

    def run_ingestion():
        nodes = sync_master_folder(pdf_path)
        if not nodes:
            return 0
        embed_nodes(nodes, source_id=source_id)
        return len(nodes)

    try:
        count = await ctx.step.run("ingest_to_qdrant", run_ingestion)
        return {"status": "success", "source": source_id, "node_count": count}
    except Exception as e:
        print(f"Pipeline Error: {str(e)}")
        raise e

# --- FUNCTION 2: Handle Queries ---
@inngest_client.create_function(
    fn_id="query_pdf_workflow",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"), 
)
async def handle_query(ctx: inngest.Context):
    question = ctx.event.data.get("question")
    
    def perform_search():
        # Force the embed model to match the 3072 dimensions in Qdrant
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-large")
        
        # Connect to your local Qdrant
        client = QdrantClient(host="localhost", port=6333)
        vector_store = QdrantVectorStore(client=client, collection_name="rag_docs")
        
        # Query logic
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        query_engine = index.as_query_engine(similarity_top_k=5)
        response = query_engine.query(question)
        
        # Extract metadata
        sources = list(set([n.metadata.get("source_id", "Unknown") for n in response.source_nodes]))
        
        return {
            "answer": str(response),
            "sources": sources
        }

    return await ctx.step.run("search_qdrant", perform_search)

# 4. Mount BOTH functions to FastAPI
inngest.fast_api.serve(
    app,
    inngest_client,
    [rag_ingest_pdf, handle_query],
)

# 5. Run with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)