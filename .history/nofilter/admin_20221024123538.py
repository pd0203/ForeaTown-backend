from django.contrib import admin
from .models import Category, Post, PostFile, PostRating, Comment, Recomment

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostFile)
admin.site.register(PostRating)
admin.site.register(Comment)
admin.site.register(Recomment)