from django.contrib import admin
from .models import User, Nofilter_highschool, Nofilter_highschool_rating, Nofilter_user_info

admin.site.register(User)
admin.site.register(Nofilter_highschool)
admin.site.register(Nofilter_highschool_rating)
admin.site.register(Nofilter_user_info)