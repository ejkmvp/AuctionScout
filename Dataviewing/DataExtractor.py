import psycopg2
import csv
import os

"""
 Todo...
     get list of items with history
     take in selection
     get all data from that item and save as idk yet


mydb = psycopg2.connect(
    host="192.168.1.46",
    dbname="auctionscanner",
    user="auctionscanner",
    password="auctionpassword",
    port="5555"
)
MIN_OCCURENCE = int(input("Enter min occurences: "))
print("getting list of items...")
cursor = mydb.cursor()
cursor.execute(f"SELECT itemName, COUNT(*) FROM auctionitems GROUP BY itemName HAVING COUNT(*) > {MIN_OCCURENCE}")
itemList = cursor.fetchall()
print(f"Found {len(itemList)} items")
itemList = list(itemList)
itemList.sort(key=lambda x: x[1], reverse=True)
for item in itemList:
    print(item)
itemName = input("Choose Item to get data on: ")

print("Getting items...")
cursor = mydb.cursor()
cursor.execute(f"SELECT auctionId, sellPrice, timeSold FROM auctionitems WHERE itemName = '{itemName}'")
allItems = cursor.fetchall()
f = open(itemName + ".json", "w")
writer = csv.writer(f)
writer.writerow(('auctionId', 'sellPrice', 'timeSold'))
writer.writerows(allItems)
f.close()
print("Finished")
"""

mydb = psycopg2.connect(
    host="192.168.1.46",
    dbname="auctionscanner",
    user="auctionscanner",
    password="auctionpassword",
    port="5555"
)

MIN_OCCURENCE = int(input("Enter min occurences: "))
print("getting list of items...")
cursor = mydb.cursor()
cursor.execute(f"SELECT itemName, COUNT(*) FROM auctionitems GROUP BY itemName HAVING COUNT(*) > {MIN_OCCURENCE}")
itemList = cursor.fetchall()
print(f"Found {len(itemList)} items")
itemList = list(itemList)

input("Press enter to continue")

for item in itemList:
    if os.path.exists(f"csvData/{item}.csv"):
        print(f"Skipping {item}, csv data already exists")
        continue
    print(f"Gathering data on {item}")
    
    cursor = mydb.cursor()
    cursor.execute(f"SELECT auctionId, sellPrice, timeSold FROM auctionitems WHERE itemName = '{item}'")
    allItems = cursor.fetchall()
    f = open(f"csvData/{item}.csv", "w")
    writer = csv.writer(f)
    writer.writerow(('auctionId', 'sellPrice', 'timeSold'))
    writer.writerows(allItems)
    f.close()