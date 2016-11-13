__author__ = 'njerucyrus'
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^create-account/', views.create_account, name='create_account'),
    url(r'^post_tweet/(?P<product_id>[0-9])/$', views.post_tweet, name='post_tweet'),
    url(r'^add-product/$', views.add_product, name='add_product'),
    url(r'^my-products/$', views.display_my_products, name='my_products'),
    url(r'^analyse-tweet/(?P<product_id>[0-9])/$', views.analyse_product_tweet, name='analyse_product_tweet'),

]