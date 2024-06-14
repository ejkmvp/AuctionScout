import mysql.connector
import json
from nbt import nbt
import io
import gzip
import base64
import requests
import time
import os
from datetime import datetime
import winsound

ipcFile = "X:/Users/ethan/Desktop/Minecraft/Hypixel/ipcFile"
def getAuctionData(pageNum):
    retryCount = 5
    while retryCount != 0:
        auctionRequest = requests.get("https://api.hypixel.net/v2/skyblock/auctions?page=" + str(pageNum))
        if auctionRequest.status_code != 200:
            print("Error with request: ", auctionRequest.status_code)
            retryCount -= 1
            time.sleep(1)
            continue
        ahData = json.loads(auctionRequest.text)
        return ahData
    raise Exception("Request failed after five retries")

# Selection Strategy. This one just takes the lower quartile
def selectionStrat(itemList):
    itemList.sort()
    return itemList[int(len(itemList)/4)]


def writeToIpcFile(uuid, timestamp):
    print("item will be available in", (timestamp / 1000) - time.time() + 20, "seconds")
    ipcData = uuid + "," + str(timestamp + 19900)
    # wait for file to be empty
    while os.path.getsize(ipcFile) != 0:
        print("IPC file has data! waiting for it to clear")
    print("IPC file is empty, adding data")
    f = open(ipcFile, "w")
    f.write(ipcData)
    f.close()
    winsound.Beep(600, 400)


MIN_OCCURENCES = 30
MIN_PET_OCCURENCES = 25
MIN_TARGET_PRICE = 100000

IGNORE_LIST = ["ATTRIBUTE_SHARD", "FERVOR_HELMET", "FERVOR_CHESTPLATE", "FERVOR_LEGGINGS", "FERVOR_BOOTS", "CRIMSON_HELMET", "CRIMSON_CHESTPLATE", "CRIMSON_LEGGINGS", "CRIMSON_BOOTS",
               "AURORA_HELMET", "AURORA_CHESTPLATE", "AURORA_LEGGINGS", "AURORA_BOOTS", "HOLLOW_HELMET", "HOLLOW_CHESTPLATE", "HOLLOW_LEGGINGS", "HOLLOW_BOOTS",
               "RAMPART_HELMET", "RAMPART_CHESTPLATE", "RAMPART_LEGGINGS", "RAMPART_BOOTS", "REKINDLED_EMBER_HELMET", "REKINDLED_EMBER_CHESTPLATE", "REKINDLED_EMBER_LEGGINGS", "REKINDLED_EMBER_BOOTS",
               "TERROR_HELMET", "TERROR_CHESTPLATE", "TERROR_LEGGINGS", "TERROR_BOOTS",
               "MAGMA_NECKLACE", "SHOWCASE_BLOCK", "STONE_SLAB2", "GHAST_CLOAK", "JERRY_STAFF", "DIGESTED_MOSQUITO"]
IGNORE_PET_LIST = ["JERRY"]

ALLOWED_LIST = []
ALLOWED_PET_LIST = []


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
timer = time.time()

# check if cache exist and decide if to use it
if not os.path.exists("datacache"):
    shouldCache = "n"
else:
    shouldCache = input("Use cached results database data? (y/N)")
if shouldCache == "y":
    # load data from file
    print("loading data from cache")
    f = open("datacache")
    data = json.load(f)
    targetPrice = data["targetPrice"]
    petTargetPrice = data["petTargetPrice"]
    f.close()
else:
    print("Processing Data from Database")
    # first, get a list of itemNames that have more than MIN_OCCURENCES occurences in the db
    cursor = mydb.cursor()
    cursor.execute(f"SELECT itemName FROM auctionscanner.auctionitems WHERE timeSold > FROM_UNIXTIME({int(time.time()) - 604800}) GROUP BY itemName HAVING COUNT(*) > {MIN_OCCURENCES}")

    # for each item get all the sell prices and find the lower quartile
    for item in cursor.fetchall():
        # pet exception
        if item[0] == "PET":
            cursor = mydb.cursor()
            cursor.execute(f"SELECT petName, petRarity FROM auctionscanner.auctionitems WHERE itemName = 'PET' AND timeSold > FROM_UNIXTIME({int(time.time()) - 604800}) GROUP BY petName, petRarity HAVING COUNT(*) > {MIN_PET_OCCURENCES}")
            for petInfo in cursor.fetchall():
                cursor.execute(f"SELECT auctionId, sellPrice FROM auctionscanner.auctionitems WHERE petName = '{petInfo[0]}' AND petRarity = '{petInfo[1]}' AND timeSold > FROM_UNIXTIME({int(time.time()) - 604800})")
                priceList = []
                for result in cursor.fetchall():
                    priceList.append(int(result[1]))
                petTargetPrice[petInfo[0] + "-" + petInfo[1]] = selectionStrat(priceList)
            continue
        cursor = mydb.cursor()
        cursor.execute(f"SELECT auctionId, sellPrice FROM auctionscanner.auctionitems WHERE itemName = '{item[0]}' AND timeSold > FROM_UNIXTIME({int(time.time()) - 604800})")
        priceList = []
        for result in cursor.fetchall():
            priceList.append(int(result[1]))
        targetPrice[item[0]] = selectionStrat(priceList)
    print(f"Finished Processing, took {time.time() - timer} seconds")

    if len(ALLOWED_LIST) != 0:
        print("Item Whitelist detected! Ignoring Item Ignorelist. Applying...")
        newTargetPrice = {}
        for item in ALLOWED_LIST:
            if item in targetPrice.keys():
                newTargetPrice[item] = targetPrice[item]
        targetPrice = newTargetPrice
    else:
        print("Applying Item Ignorelist")
        # ignore items
        for item in IGNORE_LIST:
            if item in targetPrice.keys():
                targetPrice.pop(item)

    if len(ALLOWED_PET_LIST) != 0:
        print("Pet Whitelist detected! Ignoring Pet Ignorelist. Applying...")
        newPetTargetPrice = {}
        for item in ALLOWED_PET_LIST:
            if "-" in item:
                if item in petTargetPrice.keys():
                    newPetTargetPrice[item] = petTargetPrice[item]
            else:
                addKeyList = []
                for petKey in petTargetPrice.keys():
                    if item == petKey.split("-")[0]:
                        addKeyList.append(petKey)
                for item in addKeyList:
                    newPetTargetPrice[item] = petTargetPrice[item]
        petTargetPrice = newPetTargetPrice
    else:
        print("Applying Pet Ignorelist")
        #ignore pets
        for item in IGNORE_PET_LIST:
            if "-" in item:
                if item in petTargetPrice.keys():
                    petTargetPrice.pop(item)
            else:
                removeKeyList = []
                for petKey in petTargetPrice.keys():
                    if item == petKey.split("-")[0]:
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

    print("Finished fetching data. Writing to cache")
    f = open("datacache", "w")
    f.truncate(0)
    data = {"targetPrice": targetPrice, "petTargetPrice": petTargetPrice}
    json.dump(data, f)
    f.close()

print("Begin Scan Phase")


scanDelay = -3.6
nextScanTime = time.time() + 60 - int(datetime.utcnow().strftime('%S')) + scanDelay
previousTimeStamp = "d"
retryCount = 0
while True:
    if retryCount >= 5:
        print("failed after 5+ retries, waiting till next cycle")
        nextScanTime += 60
        retryCount = 0
        continue
    if time.time() < nextScanTime:
        continue
    try:
        auctionData = getAuctionData(0)
    except Exception as e:
        print("Failed to grab auction data")
        print(e)
        print("Trying again in 2 seconds")
        time.sleep(2)
        retryCount += 1
        continue

    if nextScanTime - (auctionData['lastUpdated'] / 1000) > 20:
        print("looking at old data, waiting 0.5 seconds")
        time.sleep(0.5)
        retryCount += 1
        continue

    retryCount = 0
    nextScanTime += 60

    # Now that we verified we are looking at new data, scan pages until we find one with a start time outside of the last minute
    continueScanning = True
    pageNum = 0
    itemCandidates = []
    while continueScanning:
        if pageNum != 0:
            try:
                auctionData = getAuctionData(pageNum)
            except Exception as e:
                print("Failed to grab auction data")
                print(e)
                print("Trying again in 2 seconds")
                time.sleep(2)
                retryCount += 1
                continue
        pageNum += 1
        earliestStart = time.time() * 1000
        for item in auctionData["auctions"]:
            # skip non bins
            if not item["bin"]:
                continue

            # skip already purchased
            if item["highest_bid_amount"] != 0:
                continue

            earliestStart = min(earliestStart, item["start"])

            attribData = nbt.NBTFile(buffer=io.BytesIO(gzip.decompress(base64.b64decode(item["item_bytes"]))))["i"][0]
            itemName = str(attribData["tag"]["ExtraAttributes"]["id"])
            itemPrice = item["starting_bid"]

            # check if item is a pet
            if itemName == "PET":
                petInfo = json.loads(str(attribData["tag"]["ExtraAttributes"]["petInfo"]))
                petName = petInfo["type"]
                petRarity = petInfo["tier"]
                fullPetName = petName + "-" + petRarity
                if fullPetName not in petTargetPrice.keys():
                    continue
                if itemPrice < 0.25 * petTargetPrice[fullPetName]:
                    itemCandidates.append([item["uuid"], item["start"]])
            else:
                if itemName not in targetPrice.keys():
                    continue
                if itemPrice < 0.25 * targetPrice[itemName]:
                    itemCandidates.append([item["uuid"], item["start"]])
        if earliestStart > auctionData["lastUpdated"] - 60:
            print("Scanning another page")
        else:
            continueScanning = False
    print("found", len(itemCandidates),"candidates")
    itemCandidates.sort(key=lambda item: item[1], reverse=True)
    for item in itemCandidates:
        writeToIpcFile(item[0], item[1])


