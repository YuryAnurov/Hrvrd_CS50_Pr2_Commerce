from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("save", views.save, name="save"),
    path("categories", views.categories, name="categories"),
    path("catlistings/<str:catname>", views.catlistings, name="catlistings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("addwatch", views.addwatch, name="addwatch"),
    path("please close", views.close, name="please"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("comment", views.comment, name="comment"),
    path("<int:listing_id>", views.listing, name='listing'),
    # path("bid", views.bid, name='bid')
]
