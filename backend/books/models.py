from django.db import models

class Book(models.Model):
    title           = models.CharField(max_length=500)
    author          = models.CharField(max_length=300, blank=True)
    rating          = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    reviews_count   = models.IntegerField(default=0)
    description     = models.TextField(blank=True)
    book_url        = models.URLField(max_length=1000, unique=True)
    cover_image_url = models.URLField(max_length=1000, blank=True)
    genre           = models.CharField(max_length=200, blank=True)
    price           = models.CharField(max_length=50, blank=True)
    scraped_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scraped_at']

    def __str__(self):
        return self.title

class BookInsight(models.Model):
    book            = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='insight')
    summary         = models.TextField(blank=True)
    genre_predicted = models.CharField(max_length=200, blank=True)
    sentiment       = models.CharField(max_length=50, blank=True)
    sentiment_score = models.FloatField(null=True)
    generated_at    = models.DateTimeField(auto_now_add=True)
    model_used      = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Insight for {self.book.title}"

class ChatHistory(models.Model):
    session_id  = models.CharField(max_length=100)
    question    = models.TextField()
    answer      = models.TextField()
    sources     = models.JSONField(default=list)
    asked_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.session_id} - {self.question[:30]}"
