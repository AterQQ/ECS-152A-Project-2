import csv
import json
from collections import Counter

HARCOUNT = 1000

def populateWebList() -> list:
    webList = []
    with open("ok-website.csv", "r") as f:
        for row in csv.reader(f):
            webList.append(row[1])
    return webList

def __getDomainName(url: str) -> str:
    domainName = url.split('/')[2]
    domainName = domainName.split('.')
    if len(domainName) > 2:
        domainName = domainName[1:]
        
    stringDOMName = ""
    listSize = len(domainName)
    for i in range(listSize):
        stringDOMName += domainName[i]
        if i != listSize - 1:
            stringDOMName += '.'
    return stringDOMName

def __getCookies(cookieList: list) -> list:
    cookies = []
    for cookie in cookieList:
        cookies.append(cookie["name"])
    return cookies

def populateFrequencies(webList: list) -> tuple[dict, dict]:
    websites = {}
    cookies = {}

    for i in range(HARCOUNT): # Todo: Change to HARCOUNT later
        myHarFile = "myhar" + str(i + 1) + ".har"
        with open(myHarFile, "r") as f:
            data = json.load(f)

            for elem in data["log"]["entries"]:
                domNameMatched = False
                for site in webList:
                    if site in elem["request"]["url"]:
                        domNameMatched = True
                
                if domNameMatched:
                    continue
                else:
                    domName = __getDomainName(elem["request"]["url"])
                    try:
                        websites[domName] += 1
                    except KeyError:
                        websites[domName] = 1

                    reqCookies = __getCookies(elem["request"]["cookies"])
                    resCookies = __getCookies(elem["request"]["cookies"])
                    
                    for (reqCookie, resCookie) in zip(reqCookies, resCookies):
                        # Request cookies
                        try:
                            cookies[reqCookie] += 1
                        except KeyError:
                            cookies[reqCookie] = 1
                        # Response cookies
                        try:
                            cookies[resCookie] += 1
                        except KeyError:
                            cookies[resCookie] = 1
                        
    return websites, cookies

def main():
    websiteList = populateWebList()
    thirdPartySiteFreq, thirdPartyCookieFreq = populateFrequencies(websiteList)
    print("Third Party Websites")
    print(thirdPartySiteFreq)
    print("")
    print("Top 10 Third Party Websites")
    print(Counter(thirdPartySiteFreq).most_common(10))
    print("")
    print("Cookies: ")
    print(thirdPartyCookieFreq)
    print("")
    print("Top 10 Third Party Cookies")
    print(Counter(thirdPartyCookieFreq).most_common(10))
    print("")

if (__name__ == "__main__"):
    main()