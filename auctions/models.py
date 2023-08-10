from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL, related_name="listings")
    starting_bid = models.IntegerField()
    image_url = models.URLField(blank=True, max_length=500)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"
    
    def highest_bid(self):
        return self.bids.order_by('-bid').first()


class Bid(models.Model):
    bid = models.IntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bid} by {self.user} for {self.listing}"
    
class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")
    listings = models.ManyToManyField(Listing, related_name="watchlist")

    def __str__(self):
        return f"{self.listings} by {self.user}"



class Comment(models.Model):
    comment = models.CharField(max_length=200)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} commented {self.comment} on {self.listing}"
