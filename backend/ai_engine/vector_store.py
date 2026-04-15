import logging
logger = logging.getLogger(__name__)

try:
    import chromadb
except ImportError:
    chromadb = None
    logger.warning("chromadb not installed. Vector store mocked.")

class BookVectorStore:
    def __init__(self):
        if chromadb:
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.client.get_or_create_collection(
                name="books",
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.client = None
            self.collection = None

    def add_book(self, book_id: int, chunks: list[str], embeddings: list[list[float]]):
        """Store book chunks with their embeddings."""
        if not self.collection:
            return
        if not chunks:
            return
            
        ids = [f"book_{book_id}_chunk_{i}" for i in range(len(chunks))]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{"book_id": book_id} for _ in chunks]
        )

    def similarity_search(self, query_embedding: list[float], n_results=5) -> list[dict]:
        """Return top-N most similar chunks with metadata."""
        if not self.collection:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

    def get_book_embeddings(self, book_id: int) -> list:
        """Retrieve all chunks for a specific book."""
        if not self.collection:
            return []
        
        return self.collection.get(
            where={"book_id": book_id},
            include=["embeddings", "documents"]
        )
