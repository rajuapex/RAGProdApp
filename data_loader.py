import os
from openai import OpenAI
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072 

# Global Splitter for consistency
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def sync_master_folder(folder_path="./pdfs"):
    """
    Scans the entire folder and returns chunks (nodes) with metadata
    (filename, page number, etc.) automatically attached.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created {folder_path} folder. Drop your PDFs there!")
        return []

    # 1. High-level reader for the whole directory
    reader = SimpleDirectoryReader(input_dir=folder_path)
    
    # 2. Load all documents in the folder
    documents = reader.load_data()
    print(f"Loaded {len(documents)} pages from {folder_path}")
    
    # 3. Parse into chunks (nodes)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"Created {len(nodes)} chunks for the vector database.")
    
    return nodes

def embed_nodes(nodes):
    """
    Extracts text from nodes and gets embeddings from OpenAI.
    """
    texts = [node.get_content() for node in nodes]
    
    # OpenAI allows up to 2048 inputs per request; this handles batching
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    
    # Assign the embeddings back to the nodes for storage
    for i, item in enumerate(response.data):
        nodes[i].embedding = item.embedding
        
    return nodes