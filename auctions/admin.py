from django.contrib import admin
from .models import Listing, Comment, Bid, Category

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'starting_bid', 'category', 'user', 'created')

admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Category)

# Register your models here.
