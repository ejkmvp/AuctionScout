import mysql.connector
import json
import nbt
import io
import gzip
import base64

def getEndedAuctionData():
    retryCount = 5
    while retryCount != 0:
        auctionRequest = requests.get("https://api.hypixel.net/v2/skyblock/auctions_ended")
        if auctionRequest.status_code != 200:
            print("Error with request: ", auctionRequest.status_code)
            retryCount -= 1
            time.sleep(1)
            continue
        ahData = json.loads(auctionRequest.text)
        return ahData
    return Exception("Request failed after five retries")


# attempt connection to database
mydb = mysql.connector.connect(
    host="localhost",
    user="dbUsername",
    password="dbPassword",
    database="databaseName"
)

# send a request every 40 ish seconds, check if the timestamp is new, and if so, add the data to the database
nextScanTime = time.time() + 40
previousTimestamp = "d"

# main loop
while True:
    # wait for next scan time
    if time.time() < nextScanTime:
        continue

    #attempt to grab json data from endpoint
    print("Attempting to connect to ended auctions endpoint")
    try:
        auctionData = getEndedAuctionData()
    except Exception as e:
        print("Failed to get auction data")
        print(e)
        print("Will try again in 6 seconds")
        time.sleep(6)
        continue

    # check if necessary tags are present
    if "success" not in auctionData.keys() or "lastUpdated" not in auctionData.keys() or "auctions" not in auctionData.keys():
        print("auction data invalid, trying again in 6 seconds")
        time.sleep(6)
        continue

    # check that the success tag is true
    if auctionData["success"] != True:
        print("Auction data indicated an error, retrying in 6 seconds")
        time.sleep(6)
        continue

    # check that the timestamp is newer than the previous request
    currentTimestamp = auctionData["lastUpdated"]
    if currentTimestamp == previousTimestamp:
        print("Timestamps are equal, waiting 10 seconds")
        time.sleep(10)
        continue
    previousTimestamp = currentTimestamp

    # process each item
    for item in auctionData["auctions"]:
        # make sure it's a BIN offer
        if not item["bin"]:
            continue
        auctionId = item["auctionId"]
        sellPrice = item["price"]
        timeSold = item["timestamp"]
        attribData = nbt.NBTFile(buffer=io.BytesIO(gzip.decompress(base64.b64decode(item["item_bytes"]))))["i"][0]
        itemName = str(attribData["tag"]["ExtraAttributes"]["id"])

        # ------------------------------ Item Exclusions -------------------------------------- #

        # exclude items sold with a count greater than 1
        if str(attribData["Count"]) != "1":
            continue

        # handle pets
        if itemName == "PET":
            # exclude if pet level is greater than 10
            if int(str(attribData["tag"]["display"]["Name"]).split("Lvl ")[1].split("]")[0]) > 10:
                continue
            petInfo = eval(str(attribData["tag"]["ExtraAttributes"]["petInfo"]))
            # extract pet name and rarity
            petName = petInfo["type"]
            petRarity = petInfo["tier"]

        # handle enchanted books
        elif itemName == "ENCHANTED_BOOK":
            enchantList = attribData["tag"]["ExtraAttributes"]["enchantments"]
            # skip if the book has more than one enchantment
            if len(enchantList) > 1:
                continue
            firstEnchant = str(enchantList.keys()[0])
            enchantmentName = firstEnchant
            enchantmentLevel = enchantList[firstEnchant]

        # exclude other items that have enchantments
        elif 'enchantments' in attribData["tag"]["ExtraAttributes"].keys():
            continue

        #exclude dungeonized items
        elif 'dungeon_item_level' in attribData["tag"]["ExtraAttributes"].keys():
            # print('dungeon level detected')
            continue

        #exclude items with hot potatos on them
        elif 'hot_potato_count' in attribData["tag"]["ExtraAttributes"].keys():
            # print('hot potato')
            continue

        #exclude items that have recombobulated
        elif 'rarity_upgrades' in attribData["tag"]["ExtraAttributes"].keys():
            # print('hot potato')
            continue

        # run insertion into database
        cursor = mydb.connection.cursor()
        if itemName == "PET":
            # pet insertion
            cursor.execute(f"INSERT INTO auctionscanner.itemsales (auctionId, sellPrice, timeSold, itemName, petName, petRarity) VALUES ('{auctionId}', {sellPrice}, {timeSold}, '{itemName}', '{petName}', '{petRarity}')")
        elif itemName == "ENCHANTED_BOOK":
            cursor.execute(f"INSERT INTO auctionscanner.itemsales (auctionId, sellPrice, timeSold, itemName, enchantmentName, enchantmentLevel) VALUES ('{auctionId}', {sellPrice}, {timeSold}, '{itemName}', '{enchantmentName}', '{enchantmentLevel}')")
        else:
            cursor.execute(f"INSERT INTO auctionscanner.itemsales (auctionId, sellPrice, timeSold, itemName) VALUES ('{auctionId}', {sellPrice}, {timeSold}, '{itemName}')")
        try:
            mydb.connection.commit()
        except Exception as e:
            print("error during database insertion")
            print(e)
            print("skipping iteration")







    

