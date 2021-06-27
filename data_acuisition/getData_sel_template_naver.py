from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 
import time
import csv

# set variables
urlstring_1 = "https://search.shopping.naver.com/search/category?catId=50001239&frm=NVSHPRC&" # category = "chair"
maxPrice = 100000
minPrice = 0
pagingIndex=1
urlstring_2 = "&pagingSize=80&productSet=total&query&sort=rel&timestamp=&viewType=list" # paging size = 80
'''
url example : https://search.shopping.naver.com/search/category?catId=50001239&frm=NVSHPRC&maxPrice=100000&minPrice=0&origQuery&pagingIndex=1&pagingSize=80&productSet=total&query&sort=rel&timestamp=&viewType=list
'''

# set url string
url = urlstring_1 + "maxPrice=" + str(maxPrice) + "&minPrice=" + str(minPrice) + "&origQuery&pagingIndex=" + str(pagingIndex) + "&pagingSize=80&productSet=total&query&sort=rel&timestamp=&viewType=list"

driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', DesiredCapabilities.CHROME)

# get url page
driver.get(url)
print("searching started from :", driver.current_url)

while True:
	# 화면 최하단으로 스크롤 다운
	SCROLL_PAUSE_TIME = 2
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	
	# 페이지 로드를 기다림
	time.sleep(SCROLL_PAUSE_TIME)
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight-50);")
	time.sleep(SCROLL_PAUSE_TIME)
	
	# Calculate new scroll height and compare with last scroll height
	new_height = driver.execute_script("return document.body.scrollHeight")
	last_height = new_height
	
	# 새로운 높이가 이전 높이와 변하지 않았을 경우 스크롤 종료
	if new_height == last_height:
		break
		
	# 스크롤 다운이 된다면 스크롤 다운이 된 후의 창 높이를 새로운 높이로 갱신
	last_height = new_height
	
	
while True:
	# open csv file
	f = open('output_' + '_' + str(minPrice) + '_' + str(maxPrice) + '_' + str(pagingIndex) + '.csv', 'w', encoding='utf-8', newline='')
	wr = csv.writer(f)
	
	# get item infos
	items = driver.find_elements_by_css_selector("li.basicList_item__2XT81")
	for item in items:
		etcBox = item.find_element_by_css_selector("div.basicList_etc_box__1Jzg6")
		attributes_href = etcBox.find_elements_by_css_selector('a')
		itemReviews = 0
		itemPurchases = -1
		for a in attributes_href:
			if a.text.find("리뷰") != -1:
				itemReviews = a.find_element_by_css_selector("em.basicList_num__1yXM9").text
			elif a.text.find("구매건수") != -1:
				itemPurchases = a.find_element_by_css_selector("em.basicList_num__1yXM9").text
		
		# if there is no itemPurchases info, skip
		if itemPurchases == -1:
			continue
				
		itemName = item.find_element_by_css_selector("a.basicList_link__1MaTN").get_attribute('title')
		#itemLink = item.find_element_by_css_selector("a.basicList_link__1MaTN").get_attribute('href')
		itemPrice = item.find_element_by_css_selector("span.price_num__2WUXn").text
			
		itemZZim = etcBox.find_element_by_css_selector("button.basicList_btn_zzim__2MGkM").find_element_by_css_selector("em.basicList_num__1yXM9").text
	
		try:
			itemDelivFee = item.find_element_by_css_selector("em.basicList_option__3eF2s").text
		except:
			itemDelivFee = -1
		
		try:
			mallGrade = item.find_element_by_css_selector("span.basicList_grade__LMHXE").text
		except:
			mallGrade = "noData"
	
		itemElemList = [itemName, itemPrice, itemReviews, itemPurchases, itemZZim, itemDelivFee, mallGrade]
		wr.writerow(itemElemList)
	
	# close csv file
	f.close()
	print("Completed Parsing Page " + str(pagingIndex))
	
	# move to the next page
	try:
		next_btn = driver.find_element_by_class_name('pagination_next__1ITTf')
		next_btn.click()
		time.sleep(2)
		pagingIndex += 1
	except:
		print("Data Aquisition Done.")
		break
	
driver.close()
