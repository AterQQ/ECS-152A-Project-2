from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import csv
import json
import os

# Reference:
# https://github.com/Haroon96/ecs152a-fall-2023/tree/main/week6

# Cross-platfrom Path compatibility
bashFile = "browsermob-proxy"
subDirectory = "bin"
targetDirectory = "browsermob-proxy"
currentDirectory = os.getcwd()
proxyBinaryPath = os.path.join(currentDirectory, targetDirectory, subDirectory, bashFile)

# create a browsermob server instance
server = Server(proxyBinaryPath)
server.start()
proxy = server.create_proxy(params=dict(trustAllServers=True))

# do crawling through 1000 websites
with open("top-1m.csv", 'r') as csvFile, open("ok-website.csv", 'a') as okWebsite:
    i = 0
    
    for row in csv.reader(csvFile):
        # create a new chromedriver instance
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
        chrome_options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(20)
        driver.implicitly_wait(10)
        driver.set_script_timeout(20)

        # Set up har file
        proxy.new_har("myhar", options={"captureHeaders": True, "captureCookies": True})
        if (i == 100):
            break
        url = "http://www." + row[1]

        try:
            driver.get(url)
            i += 1

            # Construct label for success website
            label = str(i) + "," + row[1] + "\n"
            okWebsite.write(label)

            # Construct seperate har file
            harFile = "myhar" + str(i) + ".har"
            with open(harFile, 'w') as f:
                f.write(json.dumps(proxy.har, indent=2))
        except:
            pass
        finally:
            driver.quit()
            
# stop server and exit
server.stop()

