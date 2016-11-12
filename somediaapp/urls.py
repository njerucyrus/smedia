__author__ = 'njerucyrus'
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^create-account/', views.create_account, name='create_account'),
    url(r'^post_tweet/(?P<product_id>[0-9])/$', views.post_tweet, name='post_tweet'),
    url(r'^add-product/$', views.add_product, name='add_product'),

]