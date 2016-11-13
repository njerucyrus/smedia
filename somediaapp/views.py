from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
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
    LoginForm,

)


# print before
import collections
from datetime import datetime
from nltk import metrics  # for defining function precision_recall(.., ..)
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.corpus import movie_reviews
from nltk.corpus import reuters
from nltk.classify import NaiveBayesClassifier
from nltk.classify.util import accuracy  # for later testing the accuracy of the classifier
from nltk.tokenize import word_tokenize  # for word_tokenize method
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk import PorterStemmer


def index(request):
    return render(request, 'index.html', {})


def user_login(request):
    user = request.user
    next_url = request.GET.get('next', '')
    if user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if next_url == '':
                        return HttpResponseRedirect('/')
                    elif next_url:
                        return HttpResponseRedirect(next_url)
            else:

                message = 'Wrong username or password'
                form = LoginForm()
                return render(request, 'login.html', {'form': form, 'message': message, })
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, })


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return render(request, 'logout_then_login.html', {})


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


import tweepy
from django.conf import settings
import json


def get_api():
    consumer_key = str(settings.SOCIAL_AUTH_TWITTER_KEY)
    secret_key = str(settings.SOCIAL_AUTH_TWITTER_SECRET)
    access_token = str(settings.TWITTER_ACCESS_TOKEN)
    access_token_secret = str(settings.TWITTER_ACCESS_TOKEN_SECRET)
    auth = tweepy.OAuthHandler(consumer_key, secret_key)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


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
            try:
                api = get_api()
                status = api.update_status(status=tweet_text)
                # the logic for sending tweet to twitter here
                product.tweet_id = str(status.id_str)

                product.save()

                print str(status.id_str)
                print str(status.in_reply_to_status_id_str)

                message = "broadcast sent successfully"
                return HttpResponse(message)
            except Exception, e:
                return HttpResponse("error occured {0}".format(str(e)))

    else:
        tweet_form = TweetForm(initial=form_initial)
    return render(request, 'send_tweet.html', {'tweet_form': tweet_form})


def high_information_words(labelled_words, score_fn=BigramAssocMeasures.chi_sq, min_score=5):
    word_fd = FreqDist()
    label_word_fd = ConditionalFreqDist()
    for label, words in labelled_words:
        for word in words:
            word_fd.inc(word)
            label_word_fd[label].inc(word)
        n_xx = label_word_fd.N()
        high_info_words = set()
        for label in label_word_fd.conditions():
            n_xi = label_word_fd[label].N()
            word_scores = collections.defaultdict(int)
        for word, n_ii in label_word_fd[label].iteritems():
            n_ix = word_fd[word]
            score = score_fn(n_ii, (n_ix, n_xi), n_xx)
            word_scores[word] = score
        bestwords = [word for word, score in word_scores.iteritems() if score >= min_score]
        high_info_words |= set(bestwords)
    return high_info_words


# classifier

# precision_recall function is one which calculates the precision and recall of the clssifier
def precision_recall(classifier, testfeats):
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)

    for i, (feats, label) in enumerate(testfeats):
        refsets[label].add(i)
    precisions = {}
    recalls = {}

    for label in classifier.labels():
        precisions[label] = metrics.precision(refsets[label], testsets[label])
        recalls[label] = metrics.recall(refsets[label], testsets[label])
    return precisions, recalls


def bag_of_words(words):
    return dict([(word, True) for word in words])


def bag_of_words_not_in_set(words, badwords):
    # words - this is the original words of the set
    # badwords - are part words but to be discarded(stopwords probably)
    return bag_of_words(set(words) - set(badwords))  # delete badwords from original set of words


def bag_of_non_stopwords(words, stopfile='english'):
    # we are getting rid of english stopwords that are in the the set of words
    badwords = stopwords.words(stopfile)
    return bag_of_words_not_in_set(words, badwords)


def bag_of_bigrams_words(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    # finds words that often occur togther
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return bag_of_words(words + bigrams)


def label_feats_from_corpus(corp, feature_detector=bag_of_words):
    label_feats = collections.defaultdict(list)
    for label in corp.categories():
        for fileid in corp.fileids(categories=[label]):
            feats = feature_detector(corp.words(fileids=[fileid]))
            label_feats[label].append(feats)
    return label_feats


def split_label_feats(lfeats, split=0.75):
    train_feats = []
    test_feats = []
    for label, feats in lfeats.iteritems():
        cutoff = int(len(feats) * split)
        train_feats.extend([(feat, label) for feat in feats[:cutoff]])
        test_feats.extend([(feat, label) for feat in feats[cutoff:]])
    return train_feats, test_feats

lfeats = label_feats_from_corpus(movie_reviews)
# print lfeats

train_feats, test_feats = split_label_feats(lfeats)

# Define the classifier to analyse the emotion of the input sentence
nb_classifier = NaiveBayesClassifier.train(train_feats)
# nb_classifier.show_most_informative_features()


# Some tests
# def a():
#     while True:
#         print "\nplease enter a sentense to be analysed:"
#         sentence = raw_input('--> ')
#         start = datetime.now().microsecond
#         print "starting to analyse..."
#
#         sent = word_tokenize(sentence)
#         posfeat = bag_of_words(sent)
#
#         result = nb_classifier.classify(posfeat)
#         after = datetime.now().microsecond
#         print "analyse finished..."
#         print "result:", result
#         timeconsuming = after - start
#         print "It takes ", timeconsuming, "milliseconds to analyse the sentence"


def analyse_product_tweet(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    tweet_id = str(product.tweet_id)
    fetched_replies = []
    ips = []
    api = get_api()
    timeline = api.search(q="@Smart_Ad_")
    for tweet in timeline:
        if tweet.in_reply_to_status_id_str:
            print tweet.id_str
            reply = tweet.text
            print reply
            fetched_replies.append(reply)

<<<<<<< HEAD
    # get the ip
    return HttpResponse('analysis completed')

@login_required(login_url='/login/')
def get_stats(request, p_id=None):
    user = get_object_or_404(User, username=str(request.user))
    profile = get_object_or_404(UserProfile, user=user)
    product = Product.objects.filter(profile=profile,)


    return
=======
    for sentence in fetched_replies:
        sent = word_tokenize(sentence)
        feature = bag_of_words(sent)
        status = nb_classifier.classify(feature)
        try:
            TweetReply.objects.bulk_create(
                [
                TweetReply(
                    product = product,
                    reply = sentence,
                    status = status
                )
                ]
            )
        except Exception as e:
            raise

    return HttpResponse('Analyzed complete')
>>>>>>> a4d2c47aab685c752c4fc463b6b3e63bb5e11cba


@login_required(login_url='/login/')
def display_my_products(request):
    user = get_object_or_404(User, username=str(request.user))
    profile = get_object_or_404(UserProfile, user=user)
    products = Product.objects.filter(profile=profile)
    return render(request, 'products.html', {'products': products, })
