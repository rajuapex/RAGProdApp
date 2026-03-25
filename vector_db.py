from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from custom_types import RAGUpsertResult, RAGSearchResult

class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=3072):
        """
        Initializes the Qdrant client and ensures the collection exists.
        """
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection  # Defined as self.collection
        
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids: list[str], vectors: list[list[float]], payloads: list[dict]) -> RAGUpsertResult:
        """
        Pushes PointStructs to the Qdrant instance.
        """
        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) 
            for i in range(len(ids))
        ]
        
        self.client.upsert(self.collection, points=points)
        return RAGUpsertResult(ingested=len(points))

    def search(self, query_vector: list[float], top_k: int = 5) -> RAGSearchResult:
        """
        Searches using self.collection to match the __init__ definition.
        """
        # Changed collection_name=self.collection_name to self.collection
        results = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k
        ).points
        
        contexts = []
        sources = set()

        for r in results:
            payload = r.payload if r.payload else {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            
            if text:
                contexts.append(text)
            if source:
                sources.add(source)

        return RAGSearchResult(
            contexts=contexts, 
            sources=list(sources)
        )