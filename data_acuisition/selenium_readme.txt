# 실행 환경 : VirtualBox 6.1 / Ubuntu 20.10

# 필요한 라이브러리 : xvfb

# 셀레니움 스탠드얼론 서버 시작
selenium-server-standalone.jar가 위치한 디렉토리에서 다음 명령 실행
xvfb-run java -Dwebdriver.chrome.driver=/usr/bin/chromedriver -jar selenium-server-standalone.jar 

# Headless ChromeDriver 시작
/usr/bin에 chromedriver 드라이버 파일을 이동시키고 나서 다음 명령 실행
chromedriver --url-base=/wd/hub 

#파이썬에서 셀레니움 실행이 정상적으로 진행되었는지 테스트하는 코드 
from selenium import webdriver 
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities 

driver = webdriver.Remote('http://127.0.0.1:4444/wd/hub', DesiredCapabilities.CHROME) 
driver.get("https://www.naver.com") 

print(driver.page_source)

# 이상의 작업은 다음 링크에서 상세하게 확인할 수 있음
https://oslinux.tistory.com/33
