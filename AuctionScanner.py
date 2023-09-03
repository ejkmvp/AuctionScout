#TODO Incorporate rarity for all items to account for reforges
import requests
import time
import json
import gzip
from nbt import nbt
import io
import base64
#Dict struct will be key = id (except for pets, where it will be petInfo["type"]+_+petInfo["tier"], with data being [total, numSold, avg]
#we have some icky eval shit going on when handling whatever fucking wack format hypixel uses, some
false = False #bruh
true = True #bruh2
name = ""
file = open("ahData.json", "r")
ahStored = json.load(file)
file.close()
currentIDs = []
newIDs = []
#ahStored
def runScan():
	count = 0
	global currentIDs
	global newIDs
	keyList = ahStored.keys()
	while count < 6:
		request = requests.get("https://api.hypixel.net/skyblock/auctions_ended")
		if request.status_code == 200:
			break
		else:
			print(request.status_code)
			#print(request.text)
		count += 1
		time.sleep(0.5)
	if count > 5:
		print("somehow failed after multiple attempts, gonna wait 5 mins before try again")
		time.sleep(300)
	ahData = json.loads(request.text)
	for item in ahData["auctions"]:
		#check for bin
		if(item["bin"] == False):
			continue
		id = item["auction_id"]
		if id in currentIDs:
			#print('duplicate')
			newIDs.append(id)
			continue
		attribData = nbt.NBTFile(buffer=io.BytesIO(gzip.decompress(base64.b64decode(item["item_bytes"]))))["i"][0]
		itemName = str(attribData["tag"]["ExtraAttributes"]["id"])
		"""CONDITIONS*********************************************************************************"""
		if str(attribData["Count"]) != "1":
			continue
		if itemName == "PET":
			#print("pet detected")
			#print(item["auction_id"])
			if int(str(attribData["tag"]["display"]["Name"]).split("Lvl ")[1].split("]")[0]) > 10:
				continue
			petInfo = eval(str(attribData["tag"]["ExtraAttributes"]["petInfo"]))
			name = str(petInfo["type"]+"_"+petInfo["tier"])
			#+"_"+attribData["tag"]["display"]["Name"].split("Lvl ")[1].split("]")[0])
		elif itemName == "ENCHANTED_BOOK":
			#print("book detected")
			enchantList = attribData["tag"]["ExtraAttributes"]["enchantments"]
			if len(enchantList) > 1:
				continue
			firstEnchant = str(enchantList.keys()[0])
			name = str("ENCHANTED_BOOK_" + firstEnchant + "_" + str(enchantList[firstEnchant]))
		elif 'enchantments' in attribData["tag"]["ExtraAttributes"].keys():
			#print('enchantments detected')
			continue
		elif 'dungeon_item_level' in attribData["tag"]["ExtraAttributes"].keys():
			#print('dungeon level detected')
			continue
		elif 'hot_potato_count' in attribData["tag"]["ExtraAttributes"].keys():
			#print('hot potato')
			continue
		elif 'rarity_upgrades' in attribData["tag"]["ExtraAttributes"].keys():
			#print('hot potato')
			continue
		else:
			name = str(itemName)
		#Append item and id to our lists
		if name in keyList:
			total = ahStored[name][0] + int(item["price"])
			numSold = ahStored[name][1] + 1
			ahStored[name] = [total, numSold, round(total/numSold), ahStored[name][3]]
			ahStored[name][3].append(int(item["price"]))
			if len(ahStored[name][3]) > 150:
				ahStored[name][3].pop(0)
			
		else:
			ahStored[name] = [int(item["price"]), 1, int(item["price"]), [int(item["price"])]]
		newIDs.append(id)
	currentIDs = newIDs
	newIDs = []

while True:
	startTime = time.time() + 60
	print("starting scan")
	runScan()
	print("finished scan")
	#print(ahStored)
	file = open("ahData.json", "w")
	file.seek(0)
	file.truncate()
	json.dump(ahStored, file)
	file.close()
	while startTime > time.time():
		pass








