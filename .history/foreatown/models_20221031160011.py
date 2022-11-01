from django.db import models
from users.models import User

class DreamClass(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    location = models.CharField(max_length=100)
    avg_rating = models.FloatField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Dream_Classes'
    def __str__(self):
        return self.subject

class DreamClassReview(models.Model):
    content = models.TextField(max_length=200)
    rating = models.FloatField()
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    dream_class = models.ForeignKey(DreamClass, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'Dream_Class_Reviews'
    def __str__(self):
        return self.name + "님의 리뷰입니다"

class UserDreamClass(models.Model):
    mentee = models.ForeignKey(User, on_delete=models.CASCADE)
    dream_class = models.ForeignKey(DreamClass, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'User_Dream_Classes'
    def __str__(self):
        return self.mentee.name + '님의 수강 클래스 : ' + self.dream_class.subject 

class Country(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        db_table = 'countries'
    def __str__(self):
        return self.name 
