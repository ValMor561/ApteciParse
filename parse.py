import os
import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.proxy import Proxy, ProxyType
import pandas as pd
import requests
import random

proxies = []
with open("proxy.txt", 'r') as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]
for line in lines:
    proxies.append(f"http://{line}")

def init_driver():
    service = Service(ChromeDriverManager().install())
    global proxies
  
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    #options.add_argument('headless')
    options.add_argument('log-level=3')
    options.add_argument(f'--proxy-server={random.choice(proxies)}')

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def download_images(url, output_directory, name, extention, max_images=20):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    count_try = 0
    while count_try != 10:
        try:
            driver = init_driver()
            driver.get(url)
            time.sleep(1)
        except Exception as e:
            if "ERR_PROXY_CONNECTION_FAILED" in str(e):
                count_try += 1
                driver.quit()
        finally:
            break

    image_elements = driver.find_elements(By.TAG_NAME, 'img')

    image_count = 0
    for img in image_elements:
        if image_count >= max_images:
            break

        image_url = img.get_attribute('src')
        if image_url:
            
            image_name = f"{name}({image_count}).{extention}"
            image_filename = os.path.join(output_directory, image_name)
            with open(image_filename, 'wb') as image_file:
                image_file.write(requests.get(image_url).content)
            image_count += 1

    print(f"{image_count} images downloaded successfully. for {name}")

    driver.quit()


def main():
    file_path = "list.xlsx"  


    df = pd.read_excel(file_path)
    
    pngs = df['Имя лого аптеки png']
    i = 0
    for url in df['Поиск лого']:
        download_images(url, f"downloaded_images/png/{pngs[i]}", pngs[i], "png")
        i += 1

    jpgs = df['Имя фото аптеки jpg']
    i = 0
    for url in df['Поиск фото']:
        download_images(url, f"downloaded_images/png/{jpgs[i]}", jpgs[i], "jpg")
        i += 1
    

if __name__ == "__main__":
    main()
