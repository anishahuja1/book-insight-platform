import json
import logging
from books.models import Book, BookInsight
from .llm_client import get_llm_response
from utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)

class InsightGenerator:
    def _check_cache(self, book_id, insight_type):
        return get_cache(f"insight:{book_id}:{insight_type}")

    def _set_cache(self, book_id, insight_type, value):
        set_cache(f"insight:{book_id}:{insight_type}", value, timeout=86400) # 24h

    def generate_summary(self, book: Book) -> str:
        cached = self._check_cache(book.id, "summary")
        if cached:
            return cached
            
        system_prompt = "You are an expert book reviewer. Provide a concise 2-3 sentence summary based on the given book title and description."
        user_message = f"Title: {book.title}\nDescription: {book.description}"
        response = get_llm_response(system_prompt, user_message)
        
        self._set_cache(book.id, "summary", response)
        return response

    def classify_genre(self, book: Book) -> str:
        cached = self._check_cache(book.id, "genre")
        if cached:
            return cached
            
        system_prompt = "You are a book genre classifier. Predict the primary genre from the description. Return ONLY ONE of these exact categories: Fiction, Mystery, Romance, Sci-Fi, Fantasy, Non-Fiction, Biography, Self-Help, Thriller, Children's, Other"
        user_message = f"Description: {book.description}"
        response = get_llm_response(system_prompt, user_message).strip()
        
        self._set_cache(book.id, "genre", response)
        return response

    def analyze_sentiment(self, book: Book) -> tuple[str, float]:
        cached = self._check_cache(book.id, "sentiment")
        if cached:
            return cached
            
        system_prompt = "Analyze the sentiment of the book description. Return JSON format: {\"label\": \"positive\"|\"negative\"|\"neutral\", \"score\": float between -1.0 and 1.0}"
        user_message = f"Description: {book.description}"
        response = get_llm_response(system_prompt, user_message)
        
        try:
            clean_json = response.strip().strip('```json').strip('```').strip()
            data = json.loads(clean_json)
            result = (data.get('label', 'neutral'), float(data.get('score', 0.0)))
        except Exception as e:
            logger.error(f"Error parsing sentiment JSON: {e} - Response was: {response}")
            result = ("neutral", 0.0)
            
        self._set_cache(book.id, "sentiment", result)
        return result

    def generate_all(self, book: Book) -> BookInsight:
        summary = self.generate_summary(book)
        genre = self.classify_genre(book)
        sentiment_label, sentiment_score = self.analyze_sentiment(book)
        
        insight, created = BookInsight.objects.update_or_create(
            book=book,
            defaults={
                "summary": summary,
                "genre_predicted": genre,
                "sentiment": sentiment_label,
                "sentiment_score": sentiment_score,
                "model_used": "auto"
            }
        )
        return insight
