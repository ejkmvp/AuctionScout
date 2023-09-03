import json
from nbt import nbt
import base64
import time
import io
import requests
import gzip
import pyperclip 
import winsound
import pyautogui
import random
def getJson(url):
	try:
		tempRequest = requests.get(url)
	except:
		print("error loading network data")
		return {"status": "error"}
	if tempRequest.status_code != 200:
		print("an error has occured")
		print("Status code = " + str(tempRequest.status_code))
		return {"status": "error"}
	try:
		tempJson = json.loads(tempRequest.text)
	except:
		print("error loading data into Json file")
		return {"status": "error"}
	return tempJson

def randomSleep(delay, deviance):
	time.sleep(delay + random.uniform(-deviance, deviance))
def scanPage(pageNum, recent):	
	itemData = []
	itemPrices = []
	itemIds = []
	firstStart = 0
	startData = []
	while True:
		jsonData = getJson("https://api.hypixel.net/skyblock/auctions?page=" + str(pageNum))
		if "status" in jsonData.keys():
			print("error with initial json call, waiting 20 seconds")
			time.sleep(20)
			continue
		break
	for item in jsonData["auctions"]:
		#check if bin
		if item["bin"] == False:
			continue
		if firstStart == 0:
			firstStart = int(item["start"])
		#check if it just started within last 4 mins
		if time.time()*1000 - int(item["start"]) > 240000 or int(item["start"]) <= recent:
			itemData.append("end")
			break
		startData.append(item["start"])
		itemData.append(item["item_bytes"])
		itemPrices.append(item["starting_bid"])
		itemIds.append(item["uuid"])
	return [itemData, firstStart, itemPrices, itemIds, startData]


#items to ignore 
ignoreList = ["RUNE","ATTRIBUTE_SHARD", "CAKE_SOUL", "POTION", "MOLTEN_CLOAK", "ENCHANTED_BOOK_ultimate_flash_1", "ENCHANTED_BOOK_sharpness_6", "BLAZE_HELMET", "BLAZE_CHESTPLATE", "BLAZE_LEGGINS", "BLAZE_BOOTS", "MOLTEN_NECKLACE", "MIDAS_SWORD", "MAWDUST_DAGGER", "GREAT_SPOOK_HELMET", "EDIBLE_MACE", "LEGGINGS_OF_THE_PACK", "HELMET_OF_THE_PACK", "CHESTPLATE_OF_THE_PACK", "BOOTS_OF_THE_PACK", "PHANTOM_ROD", "ENCHANTED_BOOK_vampirism_6"]
#we have some icky eval shit going on when handling whatever fucking wack format hypixel uses, some
false = False #bruh
true = True #bruh2
pageCount = 0

#Grab auction house data from webserver
ahData = getJson("http://192.168.1.58/ahData.json")
if "status" in ahData.keys():
		print("error with ahData call")
		exit()
print('downloaded ahData.json')
#f = open("ahData.json", "r")
#ahData = json.loads(f.read())
#f.close()

#remove outliers and recalculate means
dataKeys = ahData.keys()
averagePrices = {}
for item in dataKeys:
	sortedNumbers = sorted(ahData[item])
	#mean = ahData[item][2]
	if len(sortedNumbers) == 0:
		continue
	if len(sortedNumbers) % 2 == 0:
		median = round((sortedNumbers[int(len(sortedNumbers)/2)] + sortedNumbers[int(len(sortedNumbers)/2 - 1)])/2)
	else:
		median = sortedNumbers[int((len(sortedNumbers) - 1) / 2)]
	q1 = round(sortedNumbers[int(len(sortedNumbers)/4)])
	q3 = round(sortedNumbers[int(3*len(sortedNumbers)/4)])
	iqr = q3 - q1
	lowerRange = q1 - round(1.5 * iqr)
	upperRange = q3 + round(1.5 * iqr)
	total = 0
	numItems = 0
	for value in ahData[item]:
		if value <= upperRange and value >= lowerRange:
			total += value
			numItems += 1
			
	#ahData[item][2] = round(total / numItems)
	
	averagePrices[item] = int(q1)

		
		
recentTime = 0



while True:
	itemData = []
	priceData = []
	idData = []
	startData = []
	#fetch all itemData into a list to go thru
	while True:
		#print('scanning')
		tempData = scanPage(pageCount, recentTime)
		recentTime = tempData[1]
		if tempData[0][-1] == "end":
			itemData = itemData + tempData[0][:-1]
			priceData = priceData + tempData[2]
			idData = idData + tempData[3]
			startData = startData + tempData[4]
			break
		itemData = itemData + tempData[0]
		priceData = priceData + tempData[2]
		idData = idData + tempData[3]
		startData = startData + tempData[4]
		#print('scanning an extra page')

	for x in range(len(itemData)):
		attribData = nbt.NBTFile(buffer=io.BytesIO(gzip.decompress(base64.b64decode(itemData[x]))))["i"][0]
		itemName = str(attribData["tag"]["ExtraAttributes"]["id"])
		#-------------------------------Conditions Copied from AuctionScanner, I should place this in a function if i extend this in the future-----------
		if itemName == "PET":
			petInfo = eval(str(attribData["tag"]["ExtraAttributes"]["petInfo"]))
			name = str(petInfo["type"]+"_"+petInfo["tier"])
		elif itemName == "ENCHANTED_BOOK":
			if "enchantments" not in attribData["tag"]["ExtraAttributes"].keys():
				continue
			enchantList = attribData["tag"]["ExtraAttributes"]["enchantments"]
			if len(enchantList) > 1:
				continue
			firstEnchant = str(enchantList.keys()[0])
			name = str("ENCHANTED_BOOK_" + firstEnchant + "_" + str(enchantList[firstEnchant]))
		elif "STARRED_" in itemName:
			name = str(itemName)[8:]
		else:
			name = str(itemName)
			
		#------------------------------------------------output: name, which contains product id found in ahData.json---------------------------
		#check if item in ignoreList and ahData or less than 10 are in database
		if name in ignoreList:
			continue
		if name not in ahData:
			continue
		if len(ahData[name]) < 10:
			continue
		#get avg price and item price
		avgPrice = int(averagePrices[name])
		itemPrice = int(priceData[x])
		#do check to see if itemPrice is less than 20% of avgPrice
		#TODO - if time between auction open and now is greater than 5 seconds, print, timer setup, start a timer to click the button a bit before the auction opens
        #TODO - Don't hardcode these values below
		if ((itemPrice < .50*avgPrice and avgPrice < 5000000 and avgPrice > 500000) or (itemPrice < .65*avgPrice and avgPrice > 5000000)) and itemPrice < 45000000:
			#((itemPrice < .50*avgPrice and avgPrice < 5000000 and avgPrice > 500000) or (itemPrice < .65*avgPrice and avgPrice > 5000000)) and itemPrice < 32000000:
			print(name + " going for " + str(itemPrice) + " When avg price is " + str(avgPrice) + ".        Margin=" + str(avgPrice - itemPrice))
			command = "/viewauction " + str(idData[x])
			pyperclip.copy(command)
			pyautogui.press("t")
			randomSleep(0.2, 0.005)
			pyautogui.hotkey('ctrl', 'v', interval=.05)
			time.sleep(.2)
			pyautogui.press("enter")
			winsound.Beep(1000, 200)
			if startData[x] + 19500 > time.time()*1000:
				pyautogui.press("t")
				time.sleep(.15)
				pyautogui.moveTo(1275, 612)
				print('autoclick ready')
				while startData[x] + 20000 > time.time()*1000 - 50: #change this interval to whatever works
					pass
				pyautogui.click()
				print('click sent')
			randomSleep(2, .05)
			pyautogui.press("t")
			randomSleep(.15, .005)
			pyautogui.press("esc")
			randomSleep(.15, .005)
	time.sleep(1)
	
	
	
	

		

