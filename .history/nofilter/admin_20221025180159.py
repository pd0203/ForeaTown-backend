from django.contrib import admin
from .models import Category, Post, PostFile, Comment, Recomment

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(PostFile)
admin.site.register(Comment)
admin.site.register(Recomment)