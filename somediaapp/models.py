from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, )
    business_name = models.CharField(max_length=64, blank=True, null=True)

    def __unicode__(self):
        return str(self.user)


class Product(models.Model):
    profile = models.ForeignKey(UserProfile, )
    product_name = models.CharField(max_length=32, )
    tweet_id = models.CharField(max_length=128, null=True, blank=True)
    tweet = models.TextField(max_length=140, null=False)

    def __unicode__(self):
        return self.product_name


class TweetReply(models.Model):
    product = models.ForeignKey(Product, )
    reply = models.CharField(max_length=140, null=True, blank=True)
    latitude = models.DecimalField(max_digits=64, decimal_places=10)
    longitude = models.DecimalField(max_digits=64, decimal_places=10)
    latitude = models.DecimalField(max_digits=64, decimal_places=10, null=True, )
    longitude = models.DecimalField(max_digits=64, decimal_places=10, null=True, )
    status = models.CharField(max_length=3)

    def __unicode__(self):
        return "{0} {1}".format(self.product.product_name, self.status)
