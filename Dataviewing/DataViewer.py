import pandas as pd
import os
import sys
import traceback
pd.options.plotting.backend = "plotly"

"""
#fileName = input("Input item name to scan: ")
fileName = "JERRY_TALISMAN_GREEN"
df = pd.read_csv(fileName + ".csv")
df['timeSold1'] = pd.to_datetime(df['timeSold'].str.split(".").str.get(0), format="ISO8601")

maxPrice = int(input("Enter max price or zero to ignore: "))
df = df.loc[df['sellPrice'] < maxPrice]
df = df.sort_values(by=["timeSold1"])
print(df)
pl = df.plot(x="timeSold1", y="sellPrice")

pl.show()
"""


minDay = int(input("Set number of days to look for data (0 for unlimited): "))

pl = 0

#fileList = os.listdir("csvData/")
fileList = [input("Input file name: ")]
for file in fileList:
    try:
        df = pd.read_csv("csvData/" + file)
    except Exception as e:
        print(f"Failed to read {file}")
        print(e)
        continue
    #try:
    # map all sell prices to ints
    df['sellPrice'] = df['sellPrice'].apply(lambda x: int(x))
    
    # if a min day is set, filter out older days
    df['timeSold'] = pd.to_datetime(df['timeSold'].str.split(".").str.get(0), format="ISO8601", utc=True)
    if minDay:
        df = df.loc[df['timeSold'] > pd.to_datetime(pd.Timestamp.now('UTC') - pd.Timedelta(minDay, "day"))]
    
    # remove outliers
    try:
        lower, mid, upper = [int(x) for x in df['sellPrice'].quantile([.25, .5, .75])]
    except Exception as e:
        print(e)
        print(file)
        exit()
        
    iqr = upper - lower
    df = df.loc[df['sellPrice'] < upper + 1.5 * iqr]
    df = df.loc[df['sellPrice'] > lower - 1.5 * iqr]
    
    #get min and max price
    maxPrice = int(df.max(axis=0)['sellPrice'])
    minPrice = int(df.min(axis=0)['sellPrice'])
    
    #normalize between min and max
    #df['sellPrice'] = df['sellPrice'].apply(lambda x: (x - minPrice)/(maxPrice - minPrice))
    
    #sort data
    df = df.sort_values(by=["timeSold"])
    
    #add data to graph
    if pl:
        pl.add_scatter(x=df["timeSold"], y=df["sellPrice"], mode="lines")
    else:
        pl = df.plot(x="timeSold", y="sellPrice", kind="scatter")
"""
    except Exception as e:
        print(f"Failed during processing {file}")
        print(e)
        ifd = sys.exc_info()
        print(traceback.format_tb(ifd[2]))
"""  
pl.show()