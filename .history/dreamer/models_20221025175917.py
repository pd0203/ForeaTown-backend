from django.db import models

class MBTI(models.Model):
   name = models.CharField(max_length=100)
   description = models.CharField(max_length=200)

   class Meta:
        db_table = 'MBTIs'
   def __str__(self):
        return self.name

class Interest(models.Model):
   name = models.CharField(max_length=100)
   description = models.CharField(max_length=200)

   class Meta:
        db_table = 'Interests'
   def __str__(self):
        return self.name

class UserInterest(models.Model):
   user = models.ForeignKey('users.User', on_delete=models.CASCADE)
   interest = models.ForeignKey('users.User', on_delete=models.CASCADE)

   class Meta:
        db_table = 'User_Interests'
   def __str__(self):
        return self.name

class DreamClass(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    location = models.CharField(max_length=100)
    avg_rating = models.FloatField(MBTI, related_name='user', null=True, on_delete=models.CASCADE)
    mentor = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Dream_Classes'
    def __str__(self):
        return self.subject

class DreamClassReview(models.Model):
    content = models.TextField(max_length=200)
    rating = models.FloatField(MBTI, related_name='user', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    dream_class = models.ForeignKey(DreamClass, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'Dream_Class_Reviews'
    def __str__(self):
        return self.name + "님의 리뷰입니다"

class UserDreamClass(models.Model):
    mentee = models.ForeignKey('users.User', on_delete=models.CASCADE)
    dream_class = models.ForeignKey(DreamClass, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'User_Dream_Classes'
    def __str__(self):
        return self.mentee.name + '님의 수강 클래스 : ' + self.dream_class.subject 