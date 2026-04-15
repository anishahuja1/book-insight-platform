from celery import shared_task
import logging
from .models import Book
from scraper.scraper import BookScraper
from ai_engine.insights import InsightGenerator
from ai_engine.embeddings import generate_batch_embeddings
from ai_engine.vector_store import BookVectorStore
from utils.chunking import semantic_chunk

logger = logging.getLogger(__name__)

@shared_task
def scrape_books_task(url, pages):
    scraper = BookScraper(base_url=url, max_pages=pages)
    new_book_ids = scraper.run()
    
    for book_id in new_book_ids:
        generate_insights_task.delay(book_id)
        generate_embeddings_task.delay(book_id)
        
    return {"scraped_count": len(new_book_ids), "book_ids": new_book_ids}

@shared_task
def generate_insights_task(book_id):
    try:
        book = Book.objects.get(id=book_id)
        generator = InsightGenerator()
        generator.generate_all(book)
        return {"status": "success", "book_id": book_id}
    except Exception as e:
        logger.error(f"Error generating insights for book {book_id}: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def generate_embeddings_task(book_id):
    try:
        book = Book.objects.get(id=book_id)
        text = f"Title: {book.title}\nAuthor: {book.author}\nGenre: {book.genre}\nDescription: {book.description}"
        chunks = semantic_chunk(text)
        
        if chunks:
            embeddings = generate_batch_embeddings(chunks)
            store = BookVectorStore()
            store.add_book(book.id, chunks, embeddings)
            
        return {"status": "success", "book_id": book_id, "chunks": len(chunks)}
    except Exception as e:
        logger.error(f"Error generating embeddings for book {book_id}: {e}")
        return {"status": "error", "message": str(e)}
