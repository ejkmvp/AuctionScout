import mysql.connector
import json
from nbt import nbt
import io
import gzip
import base64
import requests
import time

# Selection Strategy. This one just takes the lower quartile
def selectionStrat(itemList):
    itemList.sort()
    return itemList[int(len(itemList)/4)]

MIN_OCCURENCES = 10
MIN_PET_OCCURENCES = 5
MIN_BOOK_OCCURENCES = 5
MIN_TARGET_PRICE = 100000

IGNORE_LIST = []
IGNORE_PET_LIST = [""]


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
petTargetPrice = {}

print("Processing Data from Database")
# first, get a list of itemNames that have more than MIN_OCCURENCES occurences in the db
cursor = mydb.cursor()
cursor.execute(f"SELECT itemName FROM auctionscanner.auctionitems GROUP BY itemName HAVING COUNT(*) > {MIN_OCCURENCES}")

# for each item get all the sell prices and find the lower quartile
for item in cursor.fetchall():
    # pet exception
    if item[0] == "PET":
        cursor = mydb.cursor()
        cursor.execute(f"SELECT petName, petRarity FROM auctionscanner.auctionitems WHERE itemName = 'PET' GROUP BY petName, petRarity HAVING COUNT(*) > {MIN_PET_OCCURENCES}")
        for petInfo in cursor.fetchall():
            cursor.execute(f"SELECT auctionId, sellPrice FROM auctionscanner.auctionitems WHERE petName = '{petInfo[0]}' AND petRarity = '{petInfo[1]}'")
            priceList = []
            for result in cursor.fetchall():
                priceList.append(int(result[1]))
            petTargetPrice[petInfo[0] + "-" + petInfo[1]] = selectionStrat(priceList)
        continue
    cursor = mydb.cursor()
    cursor.execute(f"SELECT auctionId, sellPrice FROM auctionscanner.auctionitems WHERE itemName = '{item[0]}'")
    priceList = []
    for result in cursor.fetchall():
        priceList.append(int(result[1]))
    targetPrice[item[0]] = selectionStrat(priceList)
print("Finished Processing")

#ignore items
for item in IGNORE_LIST:
    if item in targetPrice.keys():
        targetPrice.pop(item)
for item in IGNORE_PET_LIST:
    if "-" in item:
        if item in petTargetPrice.keys():
            petTargetPrice.pop(item)
    else:
        removeKeyList = []
        for petKey in petTargetPrice.keys():
            if item in petKey:
                removeKeyList.append(petKey)
        for petKey in removeKeyList:
            petTargetPrice.pop(petKey)

# remove items below minimum target price
targetPriceKeys = list(targetPrice.keys())
for key in targetPriceKeys:
    if targetPrice[key] < MIN_TARGET_PRICE:
        targetPrice.pop(key)

petTargetPriceKeys = list(petTargetPrice.keys())
for key in petTargetPriceKeys:
    if petTargetPrice[key] < MIN_TARGET_PRICE:
        petTargetPrice.pop(key)

print(targetPrice)
print("\n")
print(petTargetPrice)
print("Begin Scan Phase")



