# Auctions Application

## Overview

The Auctions application is a platform where users can create and bid on listings, akin to auction platforms. Users can also comment on listings, view categories of listings, add listings to a watchlist, and more.

## Key Features

1. **User Authentication**: Users can register, log in, and log out. Only authenticated users can create listings, place bids, and perform other related actions.

2. **Listings**: Users can create new listings with details like title, description, starting bid, category, and an image URL.

3. **Bidding**: Authenticated users can place bids on active listings. They can't bid on their own listings or place a bid that's lower than the current highest bid.

4. **Watchlist**: Users can add and remove listings from their watchlist.

5. **Categories**: Listings can be sorted into categories. Users can view listings by categories.

6. **Comments**: Authenticated users can comment on active listings.

7. **Listing Management**: Listing creators can edit or close their listings. Once a listing is closed, no further bids can be placed on it.

8. **Navbar Information**: Displays count of the user's listings, bids, and watchlist items.

## Tools & Technologies Used

- **Backend**: Django (Python)
- **Database**: Django ORM with SQLite (default)
- **Frontend**: HTML with Django Templates, CSS (Bootstrap)