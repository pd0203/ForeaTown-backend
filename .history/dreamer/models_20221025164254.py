from django.db import models
from users.models import MBTI, User

class DreamClass(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    location = models.CharField(max_length=100)
    avg_rating = models.FloatField(MBTI, related_name='user', null=True, on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Classes'
    def __str__(self):
        return self.name

class DreamClassReview(models.Model):
    content = models.TextField(max_length=200)
    rating = models.FloatField(MBTI, related_name='user', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dream_class = models.ForeignKey(DreamClass, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
    
    class Meta:
        db_table = 'Classes'
    def __str__(self):
        return self.name