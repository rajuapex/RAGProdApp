import qdrant_client
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from data_loader import sync_master_folder  # Using your folder scanner

# 1. Connect to your Qdrant Docker container
client = qdrant_client.QdrantClient(url="http://localhost:6333")

def build_and_store_index(collection_name="master_records"):
    # 2. Get the processed chunks from your data_loader
    # This automatically picks up all PDFs in your ./pdfs folder
    nodes = sync_master_folder("./pdfs")
    
    if not nodes:
        print("No PDFs found to index.")
        return
    
    # 3. Initialize the Vector Store
    # We set the EMBED_DIM to 3072 to match your 'text-embedding-3-large'
    vector_store = QdrantVectorStore(
        client=client, 
        collection_name=collection_name
    )
    
    # 4. Storage Context (The 'Brain' that links storage to the index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 5. Build the Index (This triggers the OpenAI embeddings)
    print(f"Indexing {len(nodes)} chunks into Qdrant... Please wait.")
    index = VectorStoreIndex(
        nodes, 
        storage_context=storage_context,
        show_progress=True
    )
    
    print(f"✅ Success! Your master records are now stored in Qdrant.")
    return index

if __name__ == "__main__":
    build_and_store_index()