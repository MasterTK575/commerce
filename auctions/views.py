from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *


def get_pilldata_navbar(request):
    user = request.user
    pilldata = []
    if user.is_authenticated:
        my_listings_count = Listing.objects.filter(user=user).count()
        my_bids_count = Listing.objects.filter(bids__user=user).distinct().count()
        try:
            watchlist_count = user.watchlist.listings.all().count()
        except:
            watchlist_count = 0
        pilldata.append(my_listings_count)
        pilldata.append(my_bids_count)
        pilldata.append(watchlist_count)
    return pilldata


def index(request):
    pilldata = get_pilldata_navbar(request)
    active_listings = Listing.objects.filter(active=True).order_by('-modified')
    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "pilldata": pilldata
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

    # if GET
    pilldata = get_pilldata_navbar(request)
    return render(request, "auctions/create_listing.html", {
        "categories": categories,
        "pilldata": pilldata
    })

@login_required
def edit_listing(request, listing_id):
    user = request.user
    try:
        listing = Listing.objects.get(pk=listing_id)
    except:
        messages.error(request, "No such listing exists.")
        return HttpResponseRedirect(reverse("index"))
    if listing.user != user:
        messages.error(request, "Can only edit your own listings.")
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    # if listing is edited
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category_name = request.POST["category"]
        # error checking
        if not title or not description or not starting_bid:
            messages.error(request, "Must fill out all required fields.")
            return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))
        
        if len(title) > 64 or len(description) > 500 or len(image_url) > 500:
            messages.error(request, "Too many characters.")
            return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))
        
        try:
            starting_bid = int(starting_bid)
        except:
            messages.error(request, "Bid must be an Integer.")
            return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))
        
        if starting_bid < 0:
            messages.error(request, "Bid must be a positive Integer.")
            return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))
        
        if category_name and not Category.objects.filter(name=category_name).exists():
            messages.error(request, "Must be a valid category.")
            return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))
        
        # no changing the starting bid if there have already been bids
        if listing.bids.exists() and listing.starting_bid != starting_bid:
            messages.error(request, "Can't edit the starting_bid if bids have already been placed.")
            return HttpResponseRedirect(reverse("edit_listing", args=(listing_id,)))
        
        # if all okay, update listing
        listing.title = title
        listing.description = description
        listing.starting_bid = starting_bid
        listing.image_url = image_url
        if category_name:
            category = Category.objects.get(name=category_name)
            listing.category = category
        else:
            listing.category = None
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    
    # if GET
    else:
        pilldata = get_pilldata_navbar(request)
        categories = Category.objects.all().order_by('name')
        return render(request, "auctions/edit_listing.html", {
        "listing": listing,
        "categories": categories,
        "pilldata": pilldata
        })

def listing(request, listing_id):
    # get the listing
    try:
        listing = Listing.objects.get(pk=listing_id)
    except:
        messages.error(request, "No such listing exists.")
        return HttpResponseRedirect(reverse("index"))
    
    # if user submits a form
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Need to be logged in.")
            return HttpResponseRedirect(reverse("login"))
        
        # if user closed/ opened the listing
        if request.POST['form_type'] == 'close_listing_form':
            if request.user != listing.user:
                messages.error(request, "Can only edit your own listings.")
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            # if listing is active, close it; if it's closed, reopen it
            if listing.active == True:
                listing.active = False
                messages.success(request, "Listing closed successfully.")
            else:
                listing.active = True
                messages.success(request, "Listing reopened successfully.")
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            
        # if user placed a bid
        if request.POST['form_type'] == 'bid_form':
            if listing.active == False:
                messages.error(request, "Can only bid on active listings.")
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            # error checking the bid
            try:
                bid = int(request.POST["bid"])
            except:
                messages.error(request, "Bid needs to be a positive Integer.")
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            if listing.user == request.user:
                messages.error(request, "You can't bid on your own listings.")
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            if listing.bids.exists():
                if bid <= listing.highest_bid().bid:
                    messages.error(request, "Bid is not high engouh.")
                    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                if bid < listing.starting_bid:
                    messages.error(request, "Bid is not high engouh.")
                    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            # if ok, commit bid
            new_bid = Bid(bid=bid, user=request.user, listing=listing)
            new_bid.save()
            messages.success(request, "Bid placed successfully.")
    
    pilldata = get_pilldata_navbar(request)
    comments = Comment.objects.filter(listing=listing).order_by('-created')
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments" : comments,
        "pilldata": pilldata
    })

@login_required
def my_listings(request):
    user = request.user
    pilldata = get_pilldata_navbar(request)
    listings = Listing.objects.filter(user=user).order_by('-modified')
    return render(request, "auctions/my_listings.html", {
        "listings": listings,
        "pilldata": pilldata
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
    pilldata = get_pilldata_navbar(request)
    if hasattr(user, 'watchlist'): 
        listings = user.watchlist.listings.all().order_by('-modified')
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "pilldata": pilldata
    })

def categories(request, category_id):
    categories = Category.objects.all()
    pilldata = get_pilldata_navbar(request)
    # if category page is requested
    if category_id == 0:
        return render(request, "auctions/categories.html", {
            "categories": categories,
            "pilldata": pilldata
        })
    # else if specific category
    try:
        category = Category.objects.get(pk=category_id)
    except:
        messages.error(request, "No such category exists.")
        return render(request, "auctions/categories.html", {
            "categories": categories,
            "pilldata": pilldata
        })
    listings = category.listings.filter(active=True).order_by('-modified')
    return render(request, "auctions/category.html", {
            "category": category,
            "listings": listings,
            "pilldata": pilldata
        })

@login_required
def my_bids(request):
    pilldata = get_pilldata_navbar(request)
    user = request.user
    # bids is the related name; bids__user means we access the user attribute of the Bid model
    listings_withbid = Listing.objects.filter(bids__user=user).distinct().order_by('-modified')
    return render(request, "auctions/my_bids.html", {
            "listings": listings_withbid,
            "pilldata": pilldata
        })

@login_required
def comment(request):
    if request.method == "POST":
        user = request.user
        listing_id = request.POST['listing']
        try:
            listing = Listing.objects.get(pk=listing_id)
        except:
            messages.error(request, "Not a valid listing.")
            return HttpResponseRedirect(reverse("index"))
        text = request.POST['comment']
        if listing.active == False:
            messages.error(request, "Can't comment on closed listings.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        if not text:
            messages.error(request, "Must provide a comment.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        if len(text) > 200:
            messages.error(request, "Comment is too long.")
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        # if ok, save comment
        comment = Comment(comment=text, user=user, listing=listing)
        comment.save()
        messages.success(request, "Comment placed successfully.")
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

    return HttpResponseRedirect(reverse("index"))