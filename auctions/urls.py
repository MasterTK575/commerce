from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create/listing", views.create_listing, name="create_listing"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories/<int:category_id>", views.categories, name="categories"),
    path("my_bids", views.my_bids, name="my_bids")
]
