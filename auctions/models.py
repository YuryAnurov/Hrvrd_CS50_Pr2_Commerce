from unicodedata import bidirectional
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
#from django.db.models import Max #added for current_price
#from decimal import * # added for crurrent price


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name='watchlist')


class Category(models.Model):
    catname = models.CharField(max_length=64)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return f'{self.catname}'

    
class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=128)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.URLField(editable=True, blank=True)
#    category = models.CharField(max_length=64, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    current_bid = models.OneToOneField('Bid', null=True, blank=True, on_delete=models.CASCADE, related_name='current_bid')
    #current_bidder = models.OneToOneField('User', null=True, blank=True, on_delete=models.CASCADE, related_name='current_bidder')
    status = models.BooleanField(default=True)
#    winner = models.OneToOneField('User', null=True, blank=True, on_delete=models.CASCADE, related_name='winner')
#    current_price = models.DecimalField(max_digits=10, decimal_places=2, default= 100.00) - deleted, to check
    def __str__(self):
        return f'{self.id}:{self.title}'
#Create Listing: Users should be able to visit a page to create a new listing. They should be able to specify a title for the listing, a text-based description, and what the starting bid should be. Users should also optionally be able to provide a URL for an image for the listing and/or a category (e.g. Fashion, Toys, Electronics, Home, etc.).


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    #нужно доделать либо админ либо лист, я save для админа не прописал, а от этого current_price у листинга зависит
    def __str__(self):
        return f'{self.value} $, madeby {self.user} for {self.listing}'
 

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, default='')
    def __str__(self):
        return f'madeby {self.user} for {self.listing} : {self.content}'


