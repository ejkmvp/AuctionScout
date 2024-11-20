import mysql.connector
import psycopg2
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

def writeToIpcFile(uuid, timestamp):
    print("item will be available in", (timestamp / 1000) - time.time() + 17, "seconds")
    ipcData = uuid + "," + str(timestamp + 17000)
    # wait for file to be empty
    sendIpcDataMessage = True
    while os.path.getsize(ipcFile) != 0:
        if sendIpcDataMessage:
            sendIpcDataMessage = False
            print("IPC file has data! waiting for it to clear")
    print("IPC file is empty, adding data")
    f = open(ipcFile, "w")
    f.write(ipcData)
    f.close()
    winsound.Beep(600, 400)


targetPrice = {}
petTargetPrice = {}

if os.path.exists("overrides.json"):
    print("Overrides detected, applying")
    f = open("overrides.json")
    try:
        overridesJson = json.load(f)
        print(f"{len(overridesJson.keys())} overrides found")
        for overrideKey in overridesJson.keys():
            if overrideKey in targetPrice.keys():
                targetPrice[overrideKey] = max(targetPrice[overrideKey], overridesJson[overrideKey])
            else:
                targetPrice[overrideKey] = overridesJson[overrideKey]
    except Exception as e:
        print("Failed to open overrides json")
        print(e)
        print("Skipping...")
else:
    print("No overrides.json detected")

shouldBackSearch = input("Perform an initial long search? (6 hours or 50 pages, whatever comes first) (y\\N)")
if shouldBackSearch == "y":
    print("Will perform back search")
    minTime = 6 * 3600 * 1000
else:
    minTime = 59000
print("Beginning scanning")

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
    print("Scanning Page")
    retryCount = 0
    nextScanTime += 60

    # Now that we verified we are looking at new data, scan pages until we find one with a start time outside of the last minute
    continueScanning = True
    pageNum = 1
    itemCandidates = []
    while continueScanning:
        if pageNum != 1:
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

            # skip if has attributes
            if "attributes" in attribData["tag"]["ExtraAttributes"].keys():
                continue

            # check if item is a pet
            if itemName == "PET":
                petInfo = json.loads(str(attribData["tag"]["ExtraAttributes"]["petInfo"]))
                petName = petInfo["type"]
                petRarity = petInfo["tier"]
                fullPetName = petName + "-" + petRarity
                if fullPetName not in petTargetPrice.keys():
                    continue
                if itemPrice < petTargetPrice[fullPetName]:
                    itemCandidates.append([item["uuid"], item["start"]])
            else:
                if itemName not in targetPrice.keys():
                    continue
                if itemPrice < targetPrice[itemName]:
                    itemCandidates.append([item["uuid"], item["start"]])
        if earliestStart > auctionData["lastUpdated"] - minTime and pageNum < 100:
            print(f"Scanning page {pageNum}")
        else:
            continueScanning = False
    print("found", len(itemCandidates),"candidates")
    minTime = 59000
    itemCandidates.sort(key=lambda item: item[1], reverse=True)
    for item in itemCandidates:
        writeToIpcFile(item[0], item[1])
    print(f"Scanning again in {nextScanTime - time.time()} seconds")
