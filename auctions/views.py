from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *

# TODO:
# add timespan to listings; when date is reached listing will get closed automatically
# add option to modify listings
# add option to modify comments

def index(request):
    active_listings = Listing.objects.filter(active=True).order_by('-created')
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(request, "auctions/login.html", {
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(request, "auctions/register.html", {
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(request, "auctions/register.html", {
            })
        login(request, user)
        messages.success(request, "Registered successfully.")
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    categories = Category.objects.all().order_by('name')

    if request.method == "POST":
        # get the data
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category_name = request.POST["category"]
        user = request.user
        # error checking
        if not title or not description or not starting_bid:
            messages.error(request, "Must fill out all required fields.")
            return render(request, "auctions/create_listing.html", {
            "categories": categories
            })
        if len(title) > 64 or len(description) > 500 or len(image_url) > 500:
            messages.error(request, "Too many characters.")
            return render(request, "auctions/create_listing.html", {
            "categories": categories
            })
        try:
            starting_bid = int(starting_bid)
        except:
            messages.error(request, "Bid must be an Integer.")
            return render(request, "auctions/create_listing.html", {
            "categories": categories
            })
        if starting_bid < 0:
            messages.error(request, "Bid must be a positive Integer.")
            return render(request, "auctions/create_listing.html", {
            "categories": categories
            })
        if category_name and not Category.objects.filter(name=category_name).exists():
            messages.error(request, "Must be a valid category.")
            return render(request, "auctions/create_listing.html", {
            "categories": categories
            })
        # if ok, save listing
        if category_name:
            category = Category.objects.get(name=category_name)
        else:
            category = None
        new_listing = Listing(title=title, description=description, category=category, starting_bid=starting_bid, image_url=image_url, user=user)
        new_listing.save()
        return HttpResponseRedirect(reverse("listing", args=(new_listing.id,)))

    return render(request, "auctions/create_listing.html", {
        "categories": categories
    })

def listing(request, listing_id):
    # get the listing
    try:
        listing = Listing.objects.get(pk=listing_id)
    except:
        messages.error(request, "No such listing exists.")
        return HttpResponseRedirect(reverse("index"))
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Need to be logged in to bid.")
            return HttpResponseRedirect(reverse("login"))
        # error checking the bid
        try:
            bid = int(request.POST["bid"])
        except:
            messages.error(request, "Bid needs to be a positive Integer.")
            return render(request, "auctions/listing.html", {
            "listing": listing
            })
        if listing.user == request.user:
            messages.error(request, "You can't bid on your own listings.")
            return render(request, "auctions/listing.html", {
            "listing": listing
            })
        if listing.bids.all():
            if bid <= listing.highest_bid().bid:
                messages.error(request, "Bid is not high engouh.")
                return render(request, "auctions/listing.html", {
                "listing": listing
                })
        else:
            if bid < listing.starting_bid:
                messages.error(request, "Bid is not high engouh.")
                return render(request, "auctions/listing.html", {
                "listing": listing
                })
        # if ok, commit bid
        new_bid = Bid(bid=bid, user=request.user, listing=listing)
        new_bid.save()
        messages.success(request, "Bid placed successfully.")
    
    return render(request, "auctions/listing.html", {
        "listing": listing
    })

@login_required
def my_listings(request):
    user = request.user
    listings = Listing.objects.filter(user=user).order_by('-created')
    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })

@login_required
def watchlist(request):
    user = request.user
    if request.method == "POST":
        listing_id = request.POST["listing"]
        # error checking
        try:
            listing = Listing.objects.get(pk=listing_id)
        except:
            messages.error(request, "Not a valid listing.")
            return HttpResponseRedirect(reverse("index"))
        if user == listing.user:
            messages.error(request, "Can't add own listings to your watchlist.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        
        # get or create the watchlist for the user
        watchlist, created = Watchlist.objects.get_or_create(user=user)

        # if on watchlist, remove; if not, add
        if user.watchlist.listings.filter(pk=listing_id).exists():
            watchlist.listings.remove(listing)
            messages.error(request, "Removed from your watchlist.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        else:
            watchlist.listings.add(listing)
            messages.success(request, "Added to your watchlist.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    # if user has a watchlist already, get all listings on it
    listings = []
    if hasattr(user, 'watchlist'): 
        listings = user.watchlist.listings.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })