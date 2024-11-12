# Auction Scout
A set of tools for hypixel skyblock to collect auction data and automatically perform purchases on items sold significantly below average price

## AuctionScanner.py
This script requests auction data from Hypixel's auctions_ended endpoint every minute and stores most Buy-It-Now sales into a timescaledb database. This script is intended to run constantly on some sort of machine. A raspberry pi would probably work as long as you have 8+gb of storage. The database will grow to about 6gb after 5ish months of collecting data.

## AuctionScout.py
This script first builds a list of target prices for every item with more than MIN_OCCURENCES entries in the database. The target price will usually be Then, it begins constantly scanning Hypixel's auctions endpoint to get new buy-it-now offers. When an item sale is detected that is below the target price, it will write the item's auction ID into a file for IPC with the minecraft mod

## mod
Source Code for a forge mod. The mod detects where you are in hypixel skyblock. If you are in the main hub near the auction house and it detects data in the IPC file, it will automatically attempt to purchase the item. The script will also try to mitigate afk issues by warping back to the hub when the player's location changes

## Instructions

1. Let AuctionScanner.py run for a few days in order to build up a good amount of data for various items.
2. Launch minecraft with the mod enabled and go to the hypixel skyblock lobby
3. Run /toggleModEnable
4. Run AuctionScout.py

