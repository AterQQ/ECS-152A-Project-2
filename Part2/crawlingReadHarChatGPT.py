import csv
import os
import json
from selenium import webdriver
from browsermobproxy import Server
from collections import Counter
from urllib.parse import urlparse

def start_proxy_server():
    server = Server(r"C:\Users\clamer\Desktop\ECS152A-Project-2\browsermob-proxy\bin\browsermob-proxy.bat")
    server.start()
    return server

def create_browser_with_proxy(proxy):
    proxy_options = webdriver.ChromeOptions()
    proxy_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
    proxy_options.add_argument('--ignore-certificate-errors')
    browser = webdriver.Chrome(options=proxy_options)
    return browser

def get_base_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def crawl_websites(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        websites = list(csv.reader(csv_file))

    proxy_server = start_proxy_server()
    proxy = proxy_server.create_proxy()
    proxy.new_har(options={'captureHeaders': True, 'captureCookies': True})
    main_website_base_domain = None

    for website_id, url in websites:
        full_url = f"http://www.{url}"
        browser = create_browser_with_proxy(proxy)

        try:
            # Get the base domain of the main website
            main_website_base_domain = get_base_domain(full_url)

            # Open the website
            browser.get(full_url)

            # Wait for the page to load with a timeout (adjust as needed)
            browser.set_page_load_timeout(30)

        except Exception as e:
            print(f"Error crawling {full_url}: {e}")

        finally:
            # Close the browser
            try:
                browser.quit()
            except:
                pass

  

    # Extract data from the last HAR file
    har_data = json.loads(json.dumps(proxy.har, ensure_ascii=False))
    proxy_server.stop()

    return har_data

def analyze_har_data(har_data):
    # Extract third-party websites and cookies
    third_party_websites = set()
    cookies = {'request': Counter(), 'response': Counter()}

    for entry in har_data['log']['entries']:
        url = entry['request']['url']
        third_party_websites.add(url)

        for cookie in entry.get('request', {}).get('cookies', []):
            cookies['request'][cookie['name']] += 1

        for cookie in entry.get('response', {}).get('cookies', []):
            cookies['response'][cookie['name']] += 1

    # Print the top 10 most common third-party websites and their cookies
    print("Top 10 Most Common Third-Party Websites:")
    for website, count in Counter(third_party_websites).most_common(10):
        print(f"{website}: {count} requests")

    print("\nTop 10 Most Common Cookies (Requests):")
    for cookie, count in cookies['request'].most_common(10):
        print(f"{cookie}: {count} requests")

    print("\nTop 10 Most Common Cookies (Responses):")
    for cookie, count in cookies['response'].most_common(10):
        print(f"{cookie}: {count} responses")

if __name__ == "__main__":
    csv_file_path = "websites.csv"  # Replace with the path to your CSV file

    har_data = crawl_websites(csv_file_path)
    analyze_har_data(har_data)
