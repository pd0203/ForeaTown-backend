from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        # Create a User with the given email & password
        if not email:
            raise ValueError(('Email address required'))
        user = self.model(
            email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
        # Create a SuperUser with the given email & password
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

# Social Login User (NEW) User Model
class User(AbstractUser):
    name = models.CharField(max_length=30, unique=False, default="superuser")
    email = models.CharField(max_length=50, unique=True)
    sns_type = models.CharField(max_length=10)
    status = models.CharField(max_length=10, null=True, blank=False)
    birthday = models.DateField(null=True, blank=False)
    mbti_id = models.ForeignKey(MBTI, related_name='user', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    username = None
    first_name = None
    last_name = None
    date_joined = None

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'Users'
    def __str__(self):
        return self.email

class MBTI(models.Model):
   name = models.CharField(max_length=100)
   description = models.CharField(max_length=200)
   def __str__(self):
        return self.name
   class Meta:
        db_table = 'MBTI'

class Interest(models.Model):
   name = models.CharField(max_length=100)
   description = models.CharField(max_length=200)
   def __str__(self):
        return self.name
   class Meta:
        db_table = 'Interest'

class UserInterest(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   interest = models.ForeignKey(User, on_delete=models.CASCADE)
   def __str__(self):
        return self.name
   class Meta:
        db_table = 'User_Interests'

class Class(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    location = models.CharField(max_length=100)
    ratings = models.FloatField(MBTI, related_name='user', null=True, on_delete=models.CASCADE))
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Classes'