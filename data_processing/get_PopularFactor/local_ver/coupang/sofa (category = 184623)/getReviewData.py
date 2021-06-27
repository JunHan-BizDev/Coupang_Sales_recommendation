from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import csv

# 각 product의 리뷰 정보를 추출하는 함수
def analyzeProductReview(product_id, rating_total_count, driver, cap):
	rf = open('output_review_' + str(product_id) + '.csv', 'w', encoding='utf-8', newline='')
	rv_wr = csv.writer(rf)
	rv_wr.writerow(['product_id', 'ratings', 'reg_date', 'article_headline', 'article_content', 'help_count', 'is_photo_review']) # write first row
		
	totpage = int(int(rating_total_count)/100 + 1)
	revURLString_1 = 'https://www.coupang.com/vp/product/reviews?productId='
	revURLString_2 = '&page='
	revURLString_3 = '&size=100&sortBy=DATE_DESC&ratings='
	revURLString_4 = '&q=&viRoleCode=2&ratingSummary=true'
	for ratings in range(1,6): # 별점 1점부터 5점까지
		for pageno in range(1,totpage+1): # 1페이지부터 끝까지
			revURL = revURLString_1 + product_id + revURLString_2 + str(pageno) + revURLString_3 + str(ratings) + revURLString_4
			driver.get(revURL)
			print('now parsing review page - prouctId : ' + str(product_id) + ', page ' + str(pageno) + ', rating ' + str(ratings) + '...')
			
			try:
				no_article_string = driver.find_element_by_css_selector('body > div.sdp-review__article__no-review.sdp-review__article__no-review--active').text
				break
			except:
				pass
			
			articles = driver.find_elements_by_css_selector('article')
			
			for article in articles:
				reg_date = article.find_element_by_css_selector('div.sdp-review__article__list__info > div.sdp-review__article__list__info__product-info > div.sdp-review__article__list__info__product-info__reg-date').text # 리뷰 등록일
				try:
					article_headline = article.find_element_by_css_selector('div.sdp-review__article__list__headline').text # 리뷰 제목
				except:
					article_headline = ''
				try:
					article_content = article.find_element_by_css_selector('div.sdp-review__article__list__review.js_reviewArticleContentContainer > div').text # 리뷰 본문
				except:
					article_content = ''
				try:
					help_count = article.find_element_by_css_selector('div.sdp-review__article__list__help.js_reviewArticleHelpfulContainer > div.sdp-review__article__list__help__count > strong > span').text # 'N명에게 도움이 됨'의 수
				except:
					help_count = 0
				try:
					img = article.find_element_by_class_name('sdp-review__article__list__attachment__img js_reviewArticleListImage js_reviewArticleCrop')
					is_photo_review = True # 상품 사진이 포함된 리뷰인지 여부
				except:
					is_photo_review = False
				rv_wr.writerow([product_id, ratings, reg_date, article_headline, article_content, help_count, is_photo_review])
	rf.close()
	print('Done.')
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
chrome_options.add_argument("--dns-prefetch-disable");
#prefs = {"profile.managed_default_content_settings.images":2}
#chrome_options.add_experimental_option("prefs",prefs)
capabilities = chrome_options.to_capabilities()
print('Capabilities :',capabilities)
driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', capabilities)

pidf = open('output_pid.csv', 'r', encoding='utf-8', newline='')
reader_pidf = csv.reader(pidf)
for row in reader_pidf:
	product_id = row[0]
	rating_total_count = row[1]
	if row[1] == '' : rating_total_count = '1000'
	analyzeProductReview(product_id, rating_total_count, driver, capabilities) # pass product_id, rating_total_count
pidf.close()
driver.quit()
