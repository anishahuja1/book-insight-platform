from django.urls import path
from .views import (
    BookListView, BookDetailView, BookRecommendationsView, GenreListView,
    ChatHistoryView, ScrapeView, UploadBookView, QAApiView,
    RegenerateInsightsView, TaskStatusView
)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/scrape/', ScrapeView.as_view(), name='book-scrape'),
    path('books/upload/', UploadBookView.as_view(), name='book-upload'),
    path('books/genres/', GenreListView.as_view(), name='book-genres'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/recommendations/', BookRecommendationsView.as_view(), name='book-recommendations'),
    path('books/<int:pk>/regenerate-insights/', RegenerateInsightsView.as_view(), name='book-regenerate-insights'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat-history'),
    path('qa/ask/', QAApiView.as_view(), name='qa-ask'),
    path('tasks/<str:task_id>/status/', TaskStatusView.as_view(), name='task-status'),
]
