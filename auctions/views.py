from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.forms import ModelForm
import datetime
from django.db.models import Max #added for current_price, not needed as updated on Bid, then added again
#from django.utils.translation import gettext_lazy as _ #added to make value look like Your bid
from .models import User, Listing, Bid, Comment, Category
from django.core import validators
from django.core.exceptions import ValidationError
from decimal import *


"""class CreateListingForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label='Description')
    starting_bid = forms.DecimalField(label='Starting bid', max_digits=10, decimal_places=2, min_value=0)
    photo = forms.ImageField(label='Photo')
#    category = forms.ComboField(label='Category')
"""

class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
#        fields = ['title', 'description', 'starting_bid', 'photo', 'category']
        exclude = ['user', 'created', 'current_price', 'current_bid', 'current_bidder', 'status'] 


""" 
class MakeBidForm(forms.Form):
    value = forms.DecimalField(max_digits=10, decimal_places=2)
эту форму сначала хотел унаследовать из модели, но оказалось, что нужно передавать листинг и решил что лучше вручную
возможно лучше сделать форму из forms.Form, хоть и не унаследованную - для проверки значений при вводе
class MakeBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['value']
        labels = {
            'value': _('Your bid'),
        }"""


def create(request):
    return render(request, "auctions/create.html", {"createform":CreateListingForm()})


def wtchlisted(request):
    if request.user.is_authenticated:
        wtchlisted = request.user.watchlist.all().count()
    else:
        wtchlisted = ''
    return(wtchlisted)


def index(request):
    return render(request, "auctions/index.html", {"listings":Listing.objects.all(), "wtch":wtchlisted(request)}) # listings - added


def categories(request):
    return render(request, "auctions/categories.html", {"categories":Category.objects.all(), "wtch":wtchlisted(request)})


def catlistings(request, catname):
    return render(request, "auctions/catindex.html", {"listings":Listing.objects.filter(category__catname = catname), "wtch":wtchlisted(request), 'catname':catname})


def watchlist(request):#повторил render index с доп атрибутом watchlist
    return render(request, "auctions/index.html", {"listings":request.user.watchlist.all(), 'watchlist':1})


def save(request):
    f = CreateListingForm(request.POST)
    new_listing = Listing()
    if f.is_valid():
        new_listing.title = f.cleaned_data['title']
        new_listing.description = f.cleaned_data['description']
        new_listing.starting_bid = f.cleaned_data['starting_bid']
        new_listing.photo = f.cleaned_data['photo']
        new_listing.category = f.cleaned_data['category']
        new_listing.current_price = new_listing.starting_bid
        new_listing.user = request.user
        new_listing.created = datetime.datetime.now()
#    new_listing = f.save() # использовал, когда модель = форме, но работало и без new_listing, досточно было f.save()
    new_listing.save()
#    return index(request) так сделал сначала и все работало, но вроде бы правильней как ниже:
    return HttpResponseRedirect(reverse("index"))


def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id) #сделал с передачей listing_id чз url, в отличие от других функций
    f = request.user
    if listing.user == f:
        listing.status = False
#        listing.winner = listing.current_bid.user - иногда возникали какие-то конфликты, отказался от поля
        listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
#    return listing(request, listing_id) - здесь меня обругали, говорят Listing not callable
#    return render(request, "auctions/listing.html", {"listing":listing, "comments":Comment.objects.filter(listing=listing), "addwatch":True})

    
def addwatch(request):
    if request.method == "POST":
        listing_id = int(request.POST.get('list'))
        listing = Listing.objects.get(pk=listing_id)
        f = request.user
        if listing in f.watchlist.all(): # даже проголосовать не смог из-за 0 репутации на stackoverflow за хороший ответ
            f.watchlist.remove(listing)
        else:
            f.watchlist.add(listing)
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

"""
def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    f = request.user
    if f.is_authenticated:
        if listing in f.watchlist.all(): # даже проголосовать не смог из-за 0 репутации на stackoverflow за хороший ответ
            addwatch = False
        else:
            addwatch = True
    else:
        addwatch = True
    return render(request, "auctions/listing.html", {"listing":listing, "comments":Comment.objects.filter(listing=listing), "addwatch":addwatch, "wtch":wtchlisted(request)})"""
"""def bid(request):
    if request.method == "POST":
        madebid = request.POST.get('entry')
        listing_id = int(request.POST.get('list'))
        listing = Listing.objects.get(pk=listing_id)
        f = Bid()
#        f.user = User.objects.get(pk=1) попробую request.user
        madebid = Decimal(madebid).quantize(Decimal('1.00'))
        curbd = Decimal(listing.current_bid.value).quantize(Decimal('1.00'))
        if madebid <= curbd:
            raise ValidationError('Your bid should be bigger than current bid if any or equal of bigger than starting bid')            
        f.user = request.user
        f.value = madebid
        f.listing = listing
        f.save()
        listing.current_bid = f
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        if listing.current_bid.value > 0:
            if madebid <= listing.current_bid.value:
                raise ValidationError('Your bid should be bigger than current bid if any or equal of bigger than starting bid')
        elif madebid < listing.starting_bid:
            raise ValidationError('Your bid should be at least equal starting bid')
        else:
            f.save()
#        current_price = Decimal(Bid.objects.filter(target=listing_id).aggregate(Max('value'))['value__max']).quantize(Decimal('1.00'))
            a = float(f.value) + 0.01
            listing.current_price = Decimal(a).quantize(Decimal('1.00'))
            listing.current_bid = f
            listing.save()"""        


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    f = request.user
    if f.is_authenticated:
        if listing in f.watchlist.all(): # даже проголосовать не смог из-за 0 репутации на stackoverflow за хороший ответ
            addwatch = False
        else:
            addwatch = True
    else:
        addwatch = True
    if request.method == "POST":
        madebid = request.POST.get('entry')
        listing = Listing.objects.get(pk=listing_id)
        f = Bid()
        madebid = Decimal(madebid).quantize(Decimal('1.00'))
        if listing.current_bid:
            curbd = Decimal(listing.current_bid.value).quantize(Decimal('1.00'))
            if madebid <= curbd:
#            raise ValidationError('Your bid should be bigger than current bid if any or equal of bigger than starting bid')            
                mssg='Your bid should be bigger than current bid'
                return render(request, "auctions/listing.html", {"listing":listing, "comments":Comment.objects.filter(listing=listing), "addwatch":addwatch, "wtch":wtchlisted(request), "message":mssg}) 
        elif madebid < listing.starting_bid:
            mssg='Your bid should be at least equal starting bid'
            return render(request, "auctions/listing.html", {"listing":listing, "comments":Comment.objects.filter(listing=listing), "addwatch":addwatch, "wtch":wtchlisted(request), "message":mssg}) 
        f.user = request.user
        f.value = madebid
        f.listing = listing
        f.save()
        listing.current_bid = f
        listing.current_price = f.value
        listing.save()
    return render(request, "auctions/listing.html", {"listing":listing, "comments":Comment.objects.filter(listing=listing), "addwatch":addwatch, "wtch":wtchlisted(request)}) 


def comment(request):
    if request.method == "POST":
        content = request.POST.get('content')
        listing_id = int(request.POST.get('list'))
        listing = Listing.objects.get(pk=listing_id)
        f = Comment()
        f.user = request.user
        f.content = content
        f.listing = listing
        f.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
