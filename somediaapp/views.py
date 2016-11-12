from django.shortcuts import render
from somediaapp.models import (
    UserProfile,
    Product,
    TweetReply,
)

from somediaapp.forms import (
ProductForm,
UserRegistrationForm,

)

def create_account(request):
    if request.method == 'POST':
        form =
