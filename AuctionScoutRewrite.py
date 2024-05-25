import mysql.connector
import json
from nbt import nbt
import io
import gzip
import base64
import requests
import time

MIN_OCCURENCES = 30

#overall goals of this script:
    #1. process data from db to get a list of items to match for
    #2. get rid of all ignored items
    #3. scan loop
    #4. when an item is found, somehow send a signal to the fabric/forge/liquidbounce mod that includes the auction ID and when it becomes available

# attempt connection to database
mydb = mysql.connector.connect(
    host="localhost",
    user="auctionscanner",
    password="auctionpassword",
    database="auctionscanner"
)

targetPrice = {}


# first, get a list of itemNames that have more than MIN_OCCURENCES occurences in the db
cursor = mydb.cursor()
cursor.execute("SELECT itemName FROM auctionscanner.auctionitems GROUP BY itemName HAVING COUNT(*) > 30")

# for each item get all the sell prices and find the lower quartile
for item in cursor.fetchall():
    if item[0] == "PET":
        cursor = mydb.cursor()
        cursor.execute("SELECT petName FROM auctionscanner.auctionitems WHERE itemName = 'PET' GROUP BY petName HAVING COUNT(*) > 5")
        print(cursor.fetchall())
    cursor = mydb.cursor()
    cursor.execute(f"SELECT auctionId, sellPrice FROM auctionscanner.auctionitems WHERE itemName = '{item[0]}'")
    priceList = []
    for result in cursor.fetchall():
        priceList.append(int(result[1]))
    priceList.sort()
    targetPrice[item[0]] = priceList[int(len(priceList)/4)]


print(targetPrice)

