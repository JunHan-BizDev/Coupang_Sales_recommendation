import pandas as pd
import copy
from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os
import urllib.request
import time


def getProductImage(driver, row, cap, stackCount):
	# 페이지 url로 이동하여 상품 이미지 추출
	
	if stackCount >= 3: # 3번 이상 시도 이후에는 중단
		return
	
	try:
		driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', cap) 
		driver.get(row[1])
		wait = WebDriverWait(driver, 5)
		element = wait.until(lambda x: x.find_element_by_css_selector('footer')) # 페이지에서 footer가 로드될 때까지 대기
		try:
			print('downloading image ' + str(row[0]) + '.. ')
			image_link = driver.find_element_by_css_selector('img.prod-image__detail').get_attribute('src')
			ext = '.jpg'
			if image_link.find('.png') != -1 : ext = '.png'
			urllib.request.urlretrieve(image_link, './images/'+ str(row[0]) + ext)
		except Exception as e:
			print(image_link)
			print('failed to download image. Error : ', e)
			
		driver.quit()
	except Exception as err:
		print("Error : ", err)
		time.sleep(2)	# 2초 대기
		driver.quit()
		getProductImage(driver, row, cap, stackCount+1) # 페이지를 다시 로드
			

csv_rows = []

# output_n.csv 파일에서 세부 페이지 url 추출
for index in range(1, 10):
	filename = "output_" + str(index) + ".csv"
	df = pd.read_csv("./" + filename, encoding = 'utf-8')
	links = copy.deepcopy(df["baby_product_link"])
	
	for link in links:
		productIdString = link[ link.find('products/') : link.find('?') ]
		productId = productIdString[ productIdString.find('/')+1 : ]
		csv_rows.append([productId, link])

# 이미지들을 저장할 하위 디렉토리 생성
directory = './images'		
try:
	if not os.path.exists(directory):
		os.makedirs(directory)
except OSError:
        print ('Creating directory.. ' +  directory)


# selenium driver 설정
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless') # Ubuntu에서 script 돌릴 시 주석처리할 것. headless가 기본적용되어 있음
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("--single-process") # Ubuntu에서 script 돌릴 시 주석처리할 것
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
chrome_options.add_argument("--dns-prefetch-disable");
#prefs = {"profile.managed_default_content_settings.images":2}
#chrome_options.add_experimental_option("prefs",prefs)
capabilities = chrome_options.to_capabilities()
print('Capabilities :',capabilities)
driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', capabilities)

for row in csv_rows:
	getProductImage(driver, row, capabilities, 0)
	
print('All done.')
		
