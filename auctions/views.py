from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import *


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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
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

@login_required
def create_listing(request):
    categories = Category.objects.all()

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
            return render(request, "auctions/create_listing.html", {
            "message": "Must fill out all required fields",
            "categories": categories
            })
        if len(title) > 64 or len(description) > 500 or len(image_url) > 500:
            return render(request, "auctions/create_listing.html", {
            "message": "Too many characters",
            "categories": categories
            })
        try:
            starting_bid = int(starting_bid)
        except:
            return render(request, "auctions/create_listing.html", {
            "message": "Bid must be an Integer",
            "categories": categories
            })
        if starting_bid < 0:
            return render(request, "auctions/create_listing.html", {
            "message": "Bid must be a positive Integer",
            "categories": categories
            })
        if category_name and not Category.objects.filter(name=category_name).exists():
            return render(request, "auctions/create_listing.html", {
            "message": "Must be a valid category",
            "categories": categories
            })
        # if ok, save listing
        if category_name:
            category = Category.objects.get(name=category_name)
        else:
            category = None
        new_listing = Listing(title=title, description=description, category=category, starting_bid=starting_bid, image_url=image_url, user=user)
        new_listing.save()

    return render(request, "auctions/create_listing.html", {
        "categories": categories
    })