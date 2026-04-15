from rest_framework import serializers
from .models import Book, BookInsight, ChatHistory

class BookInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInsight
        fields = ['summary', 'genre_predicted', 'sentiment', 'sentiment_score']

class BookSerializer(serializers.ModelSerializer):
    insight = BookInsightSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'rating', 'reviews_count',
            'description', 'book_url', 'cover_image_url', 'genre',
            'price', 'scraped_at', 'insight'
        ]

class RecommendedBookSerializer(serializers.ModelSerializer):
    relevance_score = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Book
        fields = ['id', 'title', 'cover_image_url', 'author', 'rating', 'relevance_score']

class BookDetailSerializer(BookSerializer):
    recommended_books = serializers.SerializerMethodField()

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['recommended_books']

    def get_recommended_books(self, obj):
        recommended = self.context.get('recommended_books', [])
        return RecommendedBookSerializer(recommended, many=True).data

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = '__all__'

class ScrapeRequestSerializer(serializers.Serializer):
    url = serializers.URLField(default="https://books.toscrape.com")
    pages = serializers.IntegerField(default=3, min_value=1)

class QARequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    session_id = serializers.CharField(required=False, allow_blank=True)
