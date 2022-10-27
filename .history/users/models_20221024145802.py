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
        return self.name + " - " + self.email


class Nofilter_highschool(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Nofilter_Highschools'


class Nofilter_highschool_rating(models.Model):
    nofilter_highschool_id = models.ForeignKey(
        Nofilter_highschool, on_delete=models.CASCADE, related_name='rating')
    item = models.CharField(max_length=10)
    user_count = models.PositiveIntegerField(default=0)
    total_score = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.item) + " " + str(self.average_score)

    class Meta:
        db_table = 'Nofilter_Highschool_Ratings'


class Nofilter_user_info(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    nofilter_highschool = models.ForeignKey(
        Nofilter_highschool, null=True, blank=False, on_delete=models.CASCADE, related_name="userinfo")
    status = models.CharField(max_length=10, null=True, blank=False)
    # is_verified = models.BooleanField(default=False)
    birthday = models.DateField(null=True, blank=False)
    # ID_image = models.URLField(null=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        db_table = 'Nofilter_User_Infos'
