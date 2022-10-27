from django.db import models

class Class(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    location = models.CharField(max_length=100)
    ratings = models.FloatField(MBTI, related_name='user', null=True, on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Classes'
    def __str__(self):
        return self.name