import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

load_dotenv()

# --- OpenAI ---
client = OpenAI()
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

# --- Qdrant ---
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "rag_docs"

def ensure_collection():
    try:
        existing = [c.name for c in qdrant.get_collections().collections]
        if COLLECTION_NAME not in existing:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBED_DIM,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created collection: {COLLECTION_NAME}")
    except Exception as e:
        print(f"Qdrant connection error: {e}")

ensure_collection()

# --- Chunking ---
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def sync_master_folder(path="./pdfs"):
    path = Path(path)
    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")

    if path.is_file():
        reader = SimpleDirectoryReader(input_files=[str(path)])
        source = path.name
    else:
        reader = SimpleDirectoryReader(input_dir=str(path))
        source = str(path)

    documents = reader.load_data()
    if not documents:
        return []

    nodes = splitter.get_nodes_from_documents(documents)
    return nodes

def embed_nodes(nodes, source_id=None):
    if not nodes:
        return []

    texts = [node.get_content() for node in nodes]

    # Batch embed
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )

    points = []
    for i, item in enumerate(response.data):
        embedding = item.embedding
        
        # Metadata cleanup
        metadata = nodes[i].metadata or {}
        if source_id:
            metadata["source_id"] = source_id

        # FIX: Use a clean UUID string to avoid "Invalid ID" errors from filenames
        point_id = str(uuid.uuid4())

        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": nodes[i].get_content(),
                    **metadata
                },
            )
        )

    # Final Upsert
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(f"✅ Stored {len(points)} vectors for {source_id}")
    return nodes