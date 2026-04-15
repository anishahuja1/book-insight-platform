import logging
import uuid
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from celery.result import AsyncResult

from .models import Book, ChatHistory, BookInsight
from .serializers import (
    BookSerializer, BookDetailSerializer, RecommendedBookSerializer,
    ChatHistorySerializer, ScrapeRequestSerializer, QARequestSerializer
)
from .tasks import scrape_books_task, generate_insights_task
from ai_engine.rag import RAGPipeline
from ai_engine.vector_store import BookVectorStore
from ai_engine.embeddings import generate_embedding

logger = logging.getLogger(__name__)

class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        search = self.request.query_params.get('search', None)
        genre = self.request.query_params.get('genre', None)
        ordering = self.request.query_params.get('ordering', '-scraped_at')

        if search:
            queryset = queryset.filter(title__icontains=search) | queryset.filter(author__icontains=search)
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        
        if ordering:
            queryset = queryset.order_by(ordering)
            
        return queryset

class GenreListView(APIView):
    def get(self, request):
        genres = Book.objects.values_list('genre', flat=True).distinct()
        return Response([g for g in genres if g])

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        book_id = self.kwargs.get('pk')
        try:
            store = BookVectorStore()
            book = Book.objects.get(id=book_id)
            similar = Book.objects.filter(genre=book.genre).exclude(id=book.id)[:4]
            context['recommended_books'] = similar
        except Exception as e:
            logger.error(f"Error getting recommendations for book {book_id}: {e}")
            context['recommended_books'] = []
        return context

class BookRecommendationsView(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.get(id=pk)
            text = f"Title: {book.title} Description: {book.description}"
            emb = generate_embedding(text)
            
            store = BookVectorStore()
            results = store.similarity_search(emb, n_results=10)
            
            recommended = []
            seen = {book.id}
            
            if results and "metadatas" in results and results["metadatas"][0]:
                for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
                    b_id = meta.get("book_id")
                    if b_id and b_id not in seen:
                        seen.add(b_id)
                        try:
                            b = Book.objects.get(id=b_id)
                            b.relevance_score = round(max(0, 1.0 - dist), 2)
                            recommended.append(b)
                        except:
                            pass
                    if len(recommended) >= 5:
                        break
                        
            if not recommended:
                recommended = Book.objects.filter(genre=book.genre).exclude(id=book.id)[:5]
                
            serializer = RecommendedBookSerializer(recommended, many=True)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)

class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatHistorySerializer
    queryset = ChatHistory.objects.all().order_by('-asked_at')

class ScrapeView(APIView):
    def post(self, request):
        serializer = ScrapeRequestSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            pages = serializer.validated_data['pages']
            task = scrape_books_task.delay(url, pages)
            return Response({"task_id": task.id, "status": "queued"}, status=201)
        return Response(serializer.errors, status=400)

class UploadBookView(APIView):
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            generate_insights_task.delay(book.id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class QAApiView(APIView):
    def post(self, request):
        serializer = QARequestSerializer(data=request.data)
        if serializer.is_valid():
            rag = RAGPipeline()
            res = rag.answer(
                serializer.validated_data['question'],
                serializer.validated_data.get('session_id')
            )
            return Response(res)
        return Response(serializer.errors, status=400)

class RegenerateInsightsView(APIView):
    def post(self, request, pk):
        try:
            book = Book.objects.get(id=pk)
            task = generate_insights_task.delay(book.id)
            return Response({"task_id": task.id, "status": "queued"})
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=404)

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        return Response({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        })
