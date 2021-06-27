from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import csv

# set variables
pageURLstring_1 = "https://www.coupang.com/np/categories/" # category = "가구>침대"
category = "184670"
pageURLstring_2 = "?listSize=120&brand=&offerCondition=&filterType=&isPriceRange=false&minPrice=&maxPrice=&page=" # paging size = 120
pageNo = 1
pageURLstring_3 = "&channel=user&fromComponent=N&selectedPlpKeepFilter=&sorter=saleCountDesc&filter=&component=184462&rating=0" # 판매량순 정렬
rank = 0 # 판매량순 정렬 시 랭킹
'''
pageURL example : https://www.coupang.com/np/categories/184562?listSize=120&brand=&offerCondition=&filterType=&isPriceRange=false&minPrice=&maxPrice=&page=1&channel=user&fromComponent=N&selectedPlpKeepFilter=&sorter=saleCountDesc&filter=&component=184462&rating=0
카테고리>가구>침대>판매량순 정렬>120개씩 보기
'''

# 각 csv row의 상세 페이지로 이동하여 정보를 추출하는 함수
def analyzeProductPage(driver, row, csv_file, cap, stackCount):
	if stackCount >= 3: # 3번 이상 재로딩 이후에는 column들을 공란으로 두고 시도 중단
		productElemList_spec = ['', '', [], []]
		for elem in productElemList_spec:
			row.append(elem)
		driver.quit()
		return	
	
	row_temp = row[:] # 임시로 row 정보를 저장
	
	try:
		driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', cap)
		driver.get(str(row[5]))
		wait = WebDriverWait(driver, 10)
		element = wait.until(lambda x: x.find_element_by_css_selector('footer')) # 페이지에서 footer가 로드될 때까지 대기
		
		print('Searching Product ' + str(row[0]) + '\'s Page : ' + str(row[4]))
		
		try:
			brand_name = driver.find_element_by_css_selector('a.prod-brand-name').text # 브랜드 이름
		except:
			brand_name = ""
		
		if row[10] == True:
			shopping_fee = "" # 품절인 경우 배송비를 공란으로 둠
		else:
			shopping_fee = driver.find_element_by_css_selector('div.prod-shipping-fee-message').text # 배송비
			if shopping_fee.find("무료") != -1 : shopping_fee = 0
			elif shopping_fee.find("착불배송") != -1 : shopping_fee = '착불배송'
			else:
				idx1 = shopping_fee.find("배송비 ")+4
				idx2 = shopping_fee.find("원")
				shopping_fee = shopping_fee[idx1:idx2] # 문자열에서 배송비 가격 추출
		
		attributes = driver.find_elements_by_css_selector("li.prod-attr-item") # 내적 특성 리스트
		attribute_list = []
		for attribute in attributes:
			attribute_list.append(attribute.text)
		recommends = driver.find_elements_by_css_selector('li.recommend-widget__item') # 다른 고객이 함께 본 상품 id 리스트
		recommends_list = []
		for recommend in recommends: # 해당 상품의 url에서 상품 id 추출
			target_id = recommend.find_element_by_css_selector('a').get_attribute('href')
			target_id = target_id[target_id.find("products/")+9:target_id.find("?")]
			print(target_id)
			recommends_list.append(target_id)
			
			
		# 각 제품의 상세 페이지에서 추출한 Elements들을 row에 추가
		productElemList_spec = [brand_name, shopping_fee, attribute_list, recommends_list]
		for elem in productElemList_spec:
			row.append(elem)
		driver.quit()
		
	except Exception as e: # "데이터 처리에 실패했습니다. 다시 시도해 주세요" alert 발생 시 페이지를 다시 로드하여 Element 추출
		print("An error occured in product " + str(row[0]) + '\'s Page : ' + 'Failed to get data. trying again..')
		print("Error : ", e)
		time.sleep(2)	# 2초 대기
		analyzeProductPage(driver, row_temp, csv_file, cap, stackCount+1)
		
	return


# set driver and first pageURL string
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless') # Ubuntu에서 script 돌릴 시 주석처리할 것. headless가 기본적용되어 있음
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument("--single-process") # Ubuntu에서 script 돌릴 시 주석처리할 것
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)
capabilities = chrome_options.to_capabilities()
print('Capabilities :',capabilities)
driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', capabilities)
pageURL = pageURLstring_1 + category + pageURLstring_2 + str(pageNo) + pageURLstring_3

# get first URL
start = time.time()  # 시작 시간 저장
driver.get(pageURL)
print("searching started from :", driver.current_url)

# start downloading
while True:
	# open csv file
	f = open('output_' + str(pageNo) + '.csv', 'w', encoding='utf-8', newline='')
	wr = csv.writer(f)
	wr.writerow(['rank', 'category', 'name', 'price', 'product_id', 'baby_product_link', 'isRocket', 'discount_percentage', 'rating', 'rating_total_count', 'is_out_of_stock', 'brand_name', 'shopping_fee', 'attribute_list', 'recommends_list']) # write first row
	csv_rows = []

	# get item infos
	products = driver.find_elements_by_css_selector("li.baby-product.renew-badge") # product 컨테이너들을 가져옴
	for product in products: # 각 product container에 대해
		rank += 1	# 판매량순 정렬 시 랭킹
		product_id = product.find_element_by_css_selector("a.baby-product-link").get_attribute('data-product-id') # 상품 id
		baby_product_link = product.find_element_by_css_selector("a.baby-product-link").get_attribute('href') # 상세 상품 페이지 링크
		isRocket = product.find_element_by_css_selector("a.baby-product-link").get_attribute('data-is-rocket') # 로켓배송 여부
		if len(isRocket) == 0: isRocket = 'false' # 로켓배송 여부가 true가 아니면 false로 설정
		name = product.find_element_by_css_selector("div.name").text	# 상품명
		price = product.find_element_by_css_selector("strong.price-value").text # 가격
		price = price.replace(",", "") # 문자열에서 , 제거
		try:
			discount_percentage = product.find_element_by_css_selector("span.discount-percentage").text # 할인율
			discount_percentage = discount_percentage.replace("%", "") # 문자열에서 % 제거
		except:
			discount_percentage = 0
		try:
			rating = product.find_element_by_css_selector("em.rating").text # 별점
		except:
			rating = None # 별점이 존재하지 않는 경우
		try:
			rating_total_count = product.find_element_by_css_selector("span.rating-total-count").text # 상품평 개수
			rating_total_count = rating_total_count[1:len(rating_total_count)-1] # 문자열에서 양끝의 (, ) 제거
		except:
			rating_total_count = None # 상품평 개수가 존재하지 않는 경우
		try:
			is_out_of_stock = product.find_element_by_css_selector("div.out-of-stock")
			is_out_of_stock = True # 품절 여부
		except:
			is_out_of_stock = False
		
		productElemList = [rank, category, name, price, product_id, baby_product_link, isRocket, discount_percentage, rating, rating_total_count, is_out_of_stock]
		csv_rows.append(productElemList)
		
	driver.quit() # 상품 리스트 페이지 종료
	print("took " + str(time.time() - start) + " sec to get info in product list.")
	
	# 각 csv row의 상세 페이지로 이동하여 정보를 추출
	for row in csv_rows:
		analyzeProductPage(driver, row, wr, capabilities, 0)
		wr.writerow(row) # write row into csv file
	
	# close csv file
	print("Completed Parsing Page " + str(pageNo) + " : took " + str(time.time() - start) + " sec")
	f.close()
	
	# product id, rating_total_count만 따로 저장
	pidf = open('output_pid.csv', 'a', encoding='utf-8', newline='')
	wr_pidf = csv.writer(pidf)
	for row in csv_rows:
		wr_pidf.writerow([row[4],row[9]])
	pidf.close()
	
	# move to the next page
	pageNo += 1
	if pageNo == 10:
		print("Parsing Finished.")
		break
	
	# 쿠팡 서버 측에서 driver로 다른 새로운 url을 호출하면 거부하기 때문에 driver를 close하고 다시 open
	driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', capabilities) 
	pageURL = pageURLstring_1 + category + pageURLstring_2 + str(pageNo) + pageURLstring_3
	start = time.time()  # 시작 시간 저장
	driver.get(pageURL)

