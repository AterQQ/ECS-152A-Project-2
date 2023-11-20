from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import csv
import json

# Reference:
# https://github.com/Haroon96/ecs152a-fall-2023/tree/main/week6

# create a browsermob server instance
server = Server(r"C:\Users\clamer\Desktop\ECS152A-Project-2\browsermob-proxy\bin\browsermob-proxy.bat")
server.start()
proxy = server.create_proxy(params=dict(trustAllServers=True))

# create a new chromedriver instance
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
chrome_options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(20)
driver.implicitly_wait(10)
driver.set_script_timeout(20)

# do crawling through 1000 websites
with open("top-1m.csv", 'r') as csvFile, open("ok-website.csv", 'a') as okWebsite:
    i = 0
    
    for row in csv.reader(csvFile):
        # Set up har file
        proxy.new_har("myhar", options={"captureHeaders": True, "captureCookies": True})
        if (i == 1000):
            break
        url = "http://www." + row[1]

        try:
            driver.get(url)
            i += 1
        except:
            continue

        # Construct seperate har file
        harFile = "myhar" + str(i) + ".har"
        with open(harFile, 'w') as f:
            f.write(json.dumps(proxy.har, indent=2))

        # Construct label for success website
        label = str(i) + "," + row[1] + "\n"
        okWebsite.write(label)

# stop server and exit
server.stop()
driver.quit()
