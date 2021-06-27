import pandas as pd
import copy
from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

csv_rows = []
target_link_string1 = 'https://m.coupang.com/vm/'
target_link_string2 = '/recommendations/search/also-viewed/show-more?'
target_link_string3 = '&auth=true&pushEvent=true&tab=Y&event=recommendation_app_sdp_seemore_001'

# output_n.csv 파일에서 세부 페이지 url 추출하여 다른사람이 본 상품 리스트 url 리스트로 재가공
for index in range(1, 10):
	filename = "output_" + str(index) + ".csv"
	df = pd.read_csv("./" + filename, encoding = 'utf-8')
	links = copy.deepcopy(df["baby_product_link"])
	
	''' url example
	https://m.coupang.com/vm/products/10755024/recommendations/search/also-viewed/show-more?vendorItemId=3005964162&itemId=46602774&auth=true&pushEvent=true&tab=Y&event=recommendation_app_sdp_seemore_001
	'''
	
	for link in links:
		productIdString = link[ link.find('products/') : link.find('?') ]
		productId = productIdString[ productIdString.find('/')+1 : ]
		vendorItemIdstring = link[ link.find('vendor') : link.find('source')-1 ]
		itemIdString = link[ link.find('itemId') : link.find('vendor') -1 ]
		
		target_link_string = target_link_string1 + productIdString + target_link_string2 + vendorItemIdstring + '&' + itemIdString + target_link_string3
		csv_rows.append([productId, target_link_string])
		
# 상기 작업을 거치면 output_1부터 output_9까지의 [productId, target_link_string]이 csv_row에 저장되어 있는 상태


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
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)
capabilities = chrome_options.to_capabilities()
print('Capabilities :',capabilities)
driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', capabilities)

# 페이지 url로 이동하여 다른 사람이 본 상품 id 리스트 추출
for row in csv_rows:
	recItemIdList = []
	driver.get(row[1])
	time.sleep(0.5)
	recItemList = driver.find_elements_by_css_selector("div.recommend-item")
	print('now parsing page - prouctId : ' + str(row[0]) + '... ' + str(len(recItemList)) + ' items found.')
	
	for recItem in recItemList:
		hrefString = recItem.find_element_by_css_selector('a.recommend-item-link').get_attribute('href')
		recItemIdList.append(hrefString[ hrefString.find('products/')+9 : hrefString.find('?') ]) # 상품 id
	
	#target_link_string을 다른 사람이 본 상품 id 리스트로 바꾸기
	row[1] = recItemIdList

# csv 파일에 처리한 데이터 쓰기
f = open('output_alsovieweditems.csv', 'w', encoding='utf-8', newline='')
wr = csv.writer(f)
wr.writerow(['product_id', 'also_viewed_item_prouduct_id']) # write first row
for row in csv_rows:
	wr.writerow(row)

f.close()
driver.quit()
	
print('All done.')
		
