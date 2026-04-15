import hashlib
from .vector_store import BookVectorStore
from .embeddings import generate_embedding
from .llm_client import get_llm_response
from utils.cache import get_cache, set_cache
from books.models import ChatHistory, Book

class RAGPipeline:
    def __init__(self):
        self.vector_store = BookVectorStore()

    def build_prompt(self, question: str, context_chunks: list[str]) -> tuple[str, str]:
        system = """You are a knowledgeable book assistant. Answer the user's question
        based ONLY on the provided book context. Always cite the book title and author
        when referencing information. If the context doesn't contain enough information
        to answer, say so clearly. Be concise but thorough."""

        context = "\n\n---\n\n".join(context_chunks)
        return system, f"Context:\n{context}\n\nQuestion: {question}"

    def answer(self, question: str, session_id: str = None) -> dict:
        q_hash = hashlib.md5(question.encode('utf-8')).hexdigest()
        cached = get_cache(f"rag:{q_hash}")
        if cached:
            if not session_id:
                import uuid
                session_id = str(uuid.uuid4())
            ChatHistory.objects.create(
                session_id=session_id,
                question=question,
                answer=cached.get('answer'),
                sources=cached.get('sources')
            )
            return {"answer": cached.get('answer'), "sources": cached.get('sources'), "session_id": session_id}

        q_emb = generate_embedding(question)
        results = self.vector_store.similarity_search(q_emb, n_results=5)
        
        chunks = []
        sources = []
        book_ids = set()
        
        if results and "documents" in results and results["documents"] and results["documents"][0]:
            docs = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for doc, meta, dist in zip(docs, metadatas, distances):
                chunks.append(doc)
                b_id = meta.get("book_id")
                if b_id and b_id not in book_ids:
                    book_ids.add(b_id)
                    try:
                        book = Book.objects.get(id=b_id)
                        sources.append({
                            "book_id": book.id,
                            "title": book.title,
                            "relevance_score": round(max(0, 1.0 - dist), 2)
                        })
                    except Book.DoesNotExist:
                        pass

        system_prompt, user_msg = self.build_prompt(question, chunks)
        llm_answer = get_llm_response(system_prompt, user_msg)
        
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            
        ans_data = {"answer": llm_answer, "sources": sources}
        set_cache(f"rag:{q_hash}", ans_data, 86400)
        
        ChatHistory.objects.create(
            session_id=session_id,
            question=question,
            answer=llm_answer,
            sources=sources
        )
        
        return {
            "answer": llm_answer,
            "sources": sources,
            "session_id": session_id
        }
