# from django.db import models

# class Category(models.Model):
#     name = models.CharField(max_length=20)
#     class Meta:
#         db_table = 'Categories'
#     def __str__(self):
#         return self.name

# class Post(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#     subject = models.CharField(max_length=30)
#     content = models.TextField()
#     view = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(null=True)
#     class Meta:
#         db_table = 'Posts'
#     def __str__(self):
#         return self.subject

# class UserPostLikes(models.Model):
#     user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     likes = models.BooleanField(default=False)
#     class Meta:
#         db_table = 'User_Post_Likes'
#     def __str__(self):
#         return 'like: (' + self.user.name + ', ' + self.post.subject + ')'  

# class PostFile(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     file_url = models.URLField(max_length=2000)
#     class Meta:
#         db_table = 'Post_Files'
#     def __str__(self):
#         return self.file_url

# class Comment(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     class Meta:
#         db_table = 'Comments'
#     def __str__(self):
#         return self.content

# class Recomment(models.Model):
#     user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
#     comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     class Meta:
#         db_table = 'Recomments'
#     def __str__(self):
#         return self.content