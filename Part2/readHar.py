import csv
import json

thirdPartyFrequency = {}

with open("top-1m.csv") as f1, open("myHar.har") as f2:
    for (csvRow, harJson) in zip(csv.reader(f1), json.dumps(f2)):
        if (csvRow != harJson["url"]):
            thirdPartyFrequency[]