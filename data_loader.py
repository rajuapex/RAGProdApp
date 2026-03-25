import os
from openai import OpenAI
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072 # Ensure Qdrant matches this!

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)

def load_and_chunk_pdf(file_path: str):
    # 1. Initialize the reader
    reader = PDFReader()
    
    # 2. Load data (this returns a list of Document objects)
    docs = reader.load_data(file=file_path)
    
    # 3. Use the splitter directly on documents to keep metadata
    # This is better than extracting text manually
    nodes = splitter.get_nodes_from_documents(docs)
    
    return nodes

def embed_texts(texts: list[str]) -> list[list[float]]:
    # Batch processing is better for performance
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]