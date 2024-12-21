import pandas as pd
import os
import csv

MIN_REL_MARGIN = .2

IGNORE_LIST = ["MOLTEN_CLOAK",
               "MOLTEN_BELT",
               "MOLTEN_BRACELET",
               "MOLTEN_NECKLACE",
               "CRIMSON_CHESTPLATE",
               "CRIMSON_BOOTS",
               "CRIMSON_LEGGINGS",
               "PET",
               "AURORA_CHESTPLATE",
               "AURORA_LEGGINGS",
               "FERVOR_LEGGINGS",
               "FERVOR_CHESTPLATE",
               "AURORA_BOOTS",
               "FERVOR_BOOTS",
               "HOLLOW_CHESTPLATE",
               "HOLLOW_LEGGINGS",
               "TERROR_CHESTPLATE",
               "TERROR_LEGGINGS",
               "TERROR_BOOTS",
               "AURORA_HELMET",
               "ATTRIBUTE_SHARD",
               "CRIMSON_HELMET",
               "FERVOR_HELMET",
               "ASPECT_OF_THE_VOID",
               "HOLLOW_BOOTS",
               "IMPLOSION_BELT",
               "WITHER_LEGGINGS",
               "GLOWSTONE_GAUNTLET",
               "RUNE",
               "POTION",
               "MAGMA_ROD",
               "RUNIC_STAFF",
               
               ]

"""

What we need to 

    1. determine upper and lower bounds for absolute margins
    2. determine buy value and sell value 
    3. calculate profit made in a single day with that data.
    4. it be necssary to calculate the total "down payment"

Factors we can look at 
    1. Absolute Margin
    2. Relative Margin (absolute margin as a percentage of the target buy price)
    3. Frequency of Sales 

I think we start by finding all absolute margins, and then sorting listings below a certain relative margin.
Then, we look at sale frequency in the last 24 hours to determine how much profit would be made:
    Since we assume sales are constant at this point, we can take the number of sales made in the last N days where N is small,
    count the number of sales at our target sell price or above, count the number of sales at our target buy price or below, 
    use that to determine how many transactions we could make, calculate the total profit, and then scale down to 1 day



Other things we can do:
    determine if the mean of a product has shifted over time (linear regression between mean daily price)
"""

def determineMargin(df: pd.DataFrame):
    #simple method - subtract upper quartile from lower quartile
    lower, upper = [int(x) for x in df['sellPrice'].quantile([.25, .75])]
    return (lower, upper)

def determineTargets(df: pd.DataFrame):
    #simple method - use quartiles
    return determineMargin(df)

def determineDailyProfit(df: pd.DataFrame, lowerMargin, upperMargin, lowerPrice, upperPrice):
    #only look at last 14 days of sales
    
    df = df.loc[df['timeSold'] > pd.to_datetime(pd.Timestamp.now('UTC') - pd.Timedelta(14, "day"))]
    
    #count df entries 
    totalUpper = len(df[df['sellPrice'] > upperPrice])
    totalLower = len(df[df['sellPrice'] < lowerPrice])
    
    
    totalTransactions = min(totalUpper, totalLower, 7 * 7) #limit to 14 since we only have so many slots per day
    
    return ((upperMargin - lowerMargin) * totalTransactions / 7, totalTransactions / 7)
    

minDay = input("Set number of days to look for data (30): ")
minEntries = input("Set min number of item entries (inf):")


fileList = os.listdir("csvData/")
itemSaleInfo = []
for file in fileList:
    if file[:-4] in IGNORE_LIST:
        print(f"skipping {file}")
        continue
    try:
        df = pd.read_csv("csvData/" + file)
    except Exception as e:
        print(f"Failed to read {file}")
        print(e)
        continue
    
    if minEntries:
        if len(df) < int(minEntries):
            print(f"Skipping {file}")
            continue
    
    # map all sell prices to ints
    df['sellPrice'] = df['sellPrice'].apply(lambda x: int(x))
    
    # convert dates
    df['timeSold'] = pd.to_datetime(df['timeSold'].str.split(".").str.get(0), format="ISO8601", utc=True)
    
    # filter out all data older than a specified day
    if not minDay:
        minDay = 30
    df = df.loc[df['timeSold'] > pd.to_datetime(pd.Timestamp.now('UTC') - pd.Timedelta(int(minDay), "day"))]
    
    # sort data by sell price
    df = df.sort_values(by=["sellPrice"])
    
    #determine the margin
    try:
        lower, upper = determineMargin(df)
        margin = upper - lower
    except Exception as e:
        print(e)
        print(file)
        continue
    
    #determine target price 
    tLower, tUpper = determineTargets(df)
    
    #determine rel margin
    relMargin = margin/tLower
    
    #skip if rel margin is too low
    if relMargin <= MIN_REL_MARGIN:
        continue
    
    #determine the daily profit
    profit, transCount = determineDailyProfit(df, lower, upper, tLower, tUpper)
    
    itemSaleInfo.append((file, margin, tLower, tUpper, profit, transCount))

itemSaleInfo.sort(key=lambda x: x[4], reverse=True)

f = open("marginOutput.csv", "w")
writ = csv.writer(f)
writ.writerows(itemSaleInfo)
f.close()
print("Finished")
    
    
    
    