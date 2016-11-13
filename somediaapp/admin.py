from django.contrib import admin
from somediaapp.models import *


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name']

    class Meta:
        model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'product_name', 'tweet_id',  'tweet']

    class Meta:
        model = Product
admin.site.register(Product, ProductAdmin)


class TweetReplyAdmin(admin.ModelAdmin):
    list_display = ['product', 'reply', 'latitude', 'longitude', 'status']

    class Meta:
        model = TweetReply
admin.site.register(TweetReply, TweetReplyAdmin)
