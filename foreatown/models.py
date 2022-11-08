from django.db import models

class ForeaTownBannerImage(models.Model):
    subject = models.CharField(max_length=100) 
    img_url = models.URLField(max_length=200, null=True)
    class Meta:
        db_table = 'foreatown_banner_images'
    def __str__(self):
        return self.subject + ' banner - image'

class ForeaTownPolicy(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    img_url = models.URLField(max_length=200, null=True)
    class Meta:
        db_table = 'foreatown_policies'
    def __str__(self):
        return self.subject + ' policy - image'

class GatherRoomCategory(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        db_table = 'gather_room_categories'
    def __str__(self):
        return self.name

class GatherRoom(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField(max_length=200)
    address = models.CharField(max_length=100, null=True) 
    is_online = models.BooleanField()
    avg_rating = models.FloatField(default=0.0)
    user_limit = models.PositiveSmallIntegerField(default=25)
    date_time = models.DateTimeField(null=True)
    creator = models.ForeignKey('users.User', on_delete = models.CASCADE)
    participants = models.ManyToManyField('users.User', related_name='participating_gather_rooms', through='foreatown.UserGatherRoomReservation')
    gather_room_category = models.ForeignKey(GatherRoomCategory, on_delete=models.CASCADE)
    class Meta:
        db_table = 'gather_rooms'
    def __str__(self):
        return self.subject

class GatherRoomImage(models.Model):
    img_url = models.URLField(max_length=200, null=True)
    gather_room = models.ForeignKey(GatherRoom, related_name='gather_room_images', on_delete=models.CASCADE)
    class Meta:
        db_table = 'gather_room_images'
    def __str__(self):
        return self.gather_room.subject + ' - image'

class GatherRoomReview(models.Model):
    content = models.TextField(max_length=200)
    rating = models.FloatField()
    user = models.ForeignKey('users.User', related_name='gather_room_reviews', on_delete=models.CASCADE)
    gather_room = models.ForeignKey(GatherRoom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
    class Meta:
        db_table = 'gather_room_reviews'
    def __str__(self):
        return self.user.name + "님의 리뷰입니다"

class Hashtag(models.Model):
    name = models.CharField(max_length=100) 
    class Meta:
        db_table = 'hashtags'
    def __str__(self):
        return 'hashtag : #' + self.name 

class GatherRoomHashtag(models.Model):
    gather_room = models.ForeignKey(GatherRoom, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)
    class Meta:
        db_table = 'gather_room_hashtags'
    def __str__(self):
        return 'hashtag : #' + self.hashtag.name + ', gather_room: ' + self.gather_room.subject

class UserGatherRoomReservation(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    gather_room = models.ForeignKey(GatherRoom, on_delete=models.CASCADE)
    class Meta:
        db_table = 'user_gather_room_reservations'
    def __str__(self):
        return self.user.name + ' - reserved room: ' + self.gather_room.subject 

class UserGatherRoomLike(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    gather_room = models.ForeignKey(GatherRoom, on_delete=models.CASCADE)
    class Meta:
        db_table = 'user_gather_room_likes'
    def __str__(self):
        return self.user.name + ' - reserved room: ' + self.gather_room.subject 
