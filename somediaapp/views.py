from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from somediaapp.models import (
    UserProfile,
    Product,
    TweetReply,
)

from somediaapp.forms import (
    ProductForm,
    UserRegistrationForm,
    UserProfileForm,
    TweetForm,

)


def create_account(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST)
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password2'])
            user.save()
            cd = profile_form.cleaned_data
            company_name = cd['company_name']
            profile = UserProfile.objects.create(
                user=user,
                company_name=company_name
            )
            profile.save()
            message = "account created successfully"
            return HttpResponse(message)
    else:
        user_form = UserRegistrationForm()
        profile_form = UserRegistrationForm()
    return render(request, 'create_account.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        })

@login_required(login_url='/login/')
def add_product(request):
    user = get_object_or_404(User, username=str(request.user))
    profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            cd = product_form.cleaned_data
            product_name = cd['product_name']

            product = Product.objects.create(
                profile=profile,
                product_name=product_name
            )
            product.save()
            message = "product added successfully"
            return HttpResponse(message)
    else:
        product_form = ProductForm()
    return render(request, 'add_product.html', {'product_form': product_form, })


@login_required(login_url='/login/')
def post_tweet(request, product_id=None):
    product = get_object_or_404(Product, id=product_id)
    product_name = str(product.product_name)
    form_initial = {'product_name': product_name}
    if request.method == 'POST':
        tweet_form = TweetForm(request.POST, initial=form_initial)

        if tweet_form.is_valid():
            cd = tweet_form.cleaned_data
            tweet_text = cd['text']
            product.tweet = tweet_text

            # the logic for sending tweet to twitter here
            product.save()
            message = "broadcast sent successfully"
            return HttpResponse(message)
    else:
        tweet_form = TweetForm(initial=form_initial)
    return render(request, 'send_tweet.html', {'tweet_form': tweet_form})








