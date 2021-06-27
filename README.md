# Recommend popular trends of furniture category
## Project
이 프로젝트는 쿠팡 가구 쇼핑몰에서 카테고리별로 함께 본 상품과 판매량을 기준으로 트리 그래프를 만들어<br> 
자주 같이 조회된 상품 집단의 최다 공통 특성들을 찾아 해당 카테고리의 인기 트렌드를 추천한다<br>
AWS EC2 상에서 cluster 환경을 구축하여 진행하였다.(1 master & 3 workers)

## Outcome 
---
## `화이트` 컬러를 공략하라!
대표적인 방 인테리어 상품인 **storage, small table, closet**의 분석 결과는 다음과 같습니다. 
* 묶여있는 군집을 대상으로 한 인기 요인

     * 색깔 : 화이트 
     * 재질 : 합성목재 / 원목

* 카테고리 전체를 대상으로 한 인기 요인

     * 색깔 : 베이지(small table), 브라운(storage), closet(그레이) 
     * 재질 : PB + MDF, 원목, 합성목재 등 다양

**화이트 컬러를 선호하는 사람은 유독 방 인테리어를 전부 다 화이트 컬러로 맞추고 싶어하는 경향 존재**
* 화이트를 선호하는 사람들이 유독 화이트 제품만을 자주 보고 골랐고, 그래서 군집되었다.
* 따라서 화이트 제품을 판매하는 판매자의 경우, 다양한 화이트 가구를 추천해줄 수 있게 되면 수익성이 증대될 것
* **전체 리스트를 대상으로 한 인기요인은 부정확할 수 있음** 
* 판매량이 매우 큰 특정 제품의 요인에 크게 영향을 받을 수 있음

## Data infrastructure

---

### pipeline outlook
![image](https://user-images.githubusercontent.com/78855847/121779256-c5af3a80-cbd5-11eb-894a-49ae3d18b721.png)

### ETL process

#### Extract & Ingestion

- 네이버, 쿠팡으로부터 크롤링한 csv, png 데이터를 HDFS에 저장
- 방식 : 로컬에서 HDFS로 직접 업로드

#### Transformation

- **Apache Spark**를 이용하여 raw data를 가공
- **pandas dataframe**으로 변환 후 분석 목적에 맞게 전처리 진행
- **Apache Parquet**로 저장하여 **처리 속도 향상 & 저장공간 63.4% 절약**

#### Load

- **Apache Zeppelin**에서 transformed data를 갖고와 분석 진행
- 데이터 분석 결과 시각화 진행

## Data Acquisition

---

1. 방법
- Selenium Standalone Server와 Chrome Driver를 이용, 쇼핑몰 페이지에서 데이터 추출
- Selenium Standalone Server에 여러 세션을 생성하여, 일괄적으로 크롤링 작업을 진행
- 소비자의 상품 선택 요인에 대한 여러 가설들을 세우고, 가설을 확인하기 위해 필요한 데이터들을 추출하는 방식으로 크롤링을 진행함
- 크롤링 작업은 VirualBox상의 Ubuntu 20.10에서 진행하였음.

 2. 크롤링 과정

- 네이버 쇼핑 및 쿠팡에서 검색 가능한 상품 리스트 및 구매 요인 가설 분석에 필요한 개별 상품 속성을 추출함
- 크롤링 데이터 형식 : 각 상품의 속성을 Column으로 가지는 csv 파일 혹은 이미지 파일

- 네이버 쇼핑
- 1. 선택한 이유
    - 소비자가 상품 선택의 직접적인 지표인 '구매 건수'를 상품별로 확인할 수 있어 Data Acquisition을 위한 Source로 활용
- 2.  크롤링 방법
    - 방식 : 네이버 쇼핑 홈페이지에서 카테고리를 선택한 뒤, 상품을 가격대로 구분하고 네이버 랭킹 순으로 나열함. 그리고 정렬된 리스트의 상품 중 '구매 건수가 표시되어 있는 상품'의 표시된 상품 정보를 가져옴
    - Code : 크롤링을 위해 getData_sel_template_naver.py 스크립트를 작성하여 사용. 스크립트에 크롤링할 카테고리 넘버 및 가격대를 지정하여 여러 스크립트 파일을 동시 실행함
    - Output : output__(최소가격)_(최대가격)_(검색 페이지 넘버).csv의 파일명을 가지는 csv 파일
- 3.  크롤링한 요소

    ![1](https://user-images.githubusercontent.com/80512975/121628141-a4eec400-cab3-11eb-8aed-39189991eea6.png)

    - ['itemName'(상품명), 'itemPrice'(가격), 'itemReviews'(리뷰 수), 'itemPurchases'(구매건수), 'itemZZim'(찜하기 수), 'itemDelivFee'(배송비), 'mallGrade'(판매자 등급)]
- 4.  문제점
    - 각 상품의 세부 정보 페이지가 통일되어 있지 않아 상기 리스트의 정보 외에는 추가적인 정보를 얻기 어려움
    - 구매건수가 표기되어 있는 상품이 많지 않아, 목표인 500MB 이상의 Rawdata를 확보하기 어려움
- 5. Data Acquisition Source 변경 : 네이버 → 쿠팡
    - 상기 문제점으로 인해 Data Acquisition Source를 쿠팡으로 변경하여 다시 크롤링 작업을 진행함

- 쿠팡
- 1. 선택한 이유
    - 소비자 상품 선택의 직접적인 지표인 '구매 건수'를 직접적으로 표시하지는 않으나, 카테고리별 상품 검색 시 판매량순 정렬 기능이 존재
    - 각 상품의 세부 페이지의 형식이 통일되어 있어 검색 리스트에 표기된 정보 외의 정보를 가져기 용이함
- 2. 크롤링 방법
    - 방식 : 쿠팡 홈페이지에서 카테고리를 선택한 뒤, 판매량 순으로 나열함. 그리고 검색 페이지에 표시된 상품 데이터 및 해당 상품의 상세 페이지에서 데이터를 가져옴
        - 프로젝트를 진행하며 가정들이 추가됨에 따라, 해당 가설에 필요한 데이터를 추가로 수집할 필요성이 생김.
        - 따라서 처음에 작성한 getData_sel_template_coupang.py 외에 추가로 스크립트를 작성하여 크롤링에 사용하였음.
    - Code : 크롤링을 위해 다음과 같은 스크립트들을 작성하여 사용. 스크립트에 크롤링할 카테고리 혹은 상품 ID(product_id)를 지정하여 여러 스크립트 파일을 동시 실행함.
        - getData_sel_template_coupang.py : 카테고리 번호를 입력으로 설정하여, 각 카테고리별, 판매량순, 120개씩 보기로 정렬되어 있는 상품 리스트에서 데이터를 추출함. 그리고 각 상품의 세부 페이지로 이동하여 리스트에 표시된 것 이외의 추가 데이터를 추출함. 데이터 추출 작업은 판매량순으로 상위 1080개 상품까지만 진행함.
        - getAlsoViewedItems.py : getData_sel_template_coupang.py의 출력 csv 파일들을 입력으로 받아,  각 상품이 가지고 있는 '다른 고객이 본 상품'리스트를 추출.
        - getProductImage.py : getData_sel_template_coupang.py의 출력 csv 파일들을 입력으로 받아,  각 상품의 리스트에 표시된 이미지를 추출.
        - getReviewData.py : getData_sel_template_coupang.py의 출력 csv 파일들을 입력으로 받아,  각 상품이 가지고 있는 '리뷰에 관련된 정보'를 추출.
- 3. 크롤링한 요소
    - 각 스크립트별로 크롤링한 요소를 나열함.
    - getData_sel_template_coupang.py

        ![2](https://user-images.githubusercontent.com/80512975/121628304-e4b5ab80-cab3-11eb-912b-5f5f34f2d9bf.png)
        ![3](https://user-images.githubusercontent.com/80512975/121628310-e8e1c900-cab3-11eb-9a4d-096a3ca3020b.png)
        ![4](https://user-images.githubusercontent.com/80512975/121628330-f303c780-cab3-11eb-8ae6-1218676f68cf.png)

        - ['rank'(판매량순 정렬 시 랭킹), 'category'(카테고리 넘버), 'name'(상품명), 'price'(상품가격), 'product_id'(상품id), 'baby_product_link'(상품 상세페이지 링크), 'isRocket'(로켓배송 여부), 'discount_percentage'(할인율), 'rating'(별점), 'rating_total_count'(상품평 개수), 'is_out_of_stock'(품절 여부), 'brand_name'(브랜드명), 'shopping_fee'(배송비), 'attribute_list'(내적 특성 리스트), 'recommends_list'(다른 고객이 함께 본 상품 id 리스트)]를 추출하여 output_1.csv부터 output_9.csv 형식으로 저장
        - 상세 상품 페이지에서  'recommends_list'(다른 고객이 함께 본 상품 id 리스트)가 잘 추출되지 않고, 최대 15개까지만 목록이 출력되어 다른 고객이 함께 본 상품 id 리스트는 getReviewData.py 스크립트에서 다시 추출하였음.
    - getAlsoViewedItems.py

        ![5](https://user-images.githubusercontent.com/80512975/121628605-76bdb400-cab4-11eb-85f3-8a021778d2a7.png)

        - ['product_id'(상품id), 'ratings'(리뷰 별점), 'reg_date'(리뷰 등록일), 'article_headline'(리뷰 제목), 'article_content'(리뷰 내용), 'help_count'(N명에게 도움이 됨), 'is_photo_review'(사진리뷰 여부)]를 추출하여 output_alsovieweditems.csv 형식으로 저장
        - getData_sel_template_coupang.py에서 추출한  'product_id'(상품id), 'baby_product_link'(상품 상세페이지 링크) 정보를 이용, 다른 사람이 함께 본 상품 리스트가 저장되어 있는 페이지로 이동함. 그 후 상품당 최대 약 100개의 다른 사람이 함께 본 상품 id를 가져옴.
    - getProductImage.py

        ![6](https://user-images.githubusercontent.com/80512975/121628466-3fe79e00-cab4-11eb-9941-3eab8f83fe8a.png)

        - 각 상품당 세부 페이지에 표시된 첫 번째 상품 이미지 파일을 product_id와 동일한 파일명으로 저장
        - getData_sel_template_coupang.py에서 추출한 'baby_product_link'(상품 상세페이지 링크) 정보를 이용, 다른 사람이 함께 본 상품 리스트가 저장되어 있는 페이지로 이동함. 그 후 가장 첫 번째로 표시된 상품 이미지를 가져옴.
    - getReviewData.py

        ![7](https://user-images.githubusercontent.com/80512975/121628578-660d3e00-cab4-11eb-9252-0293c43673d2.png)

        - ['product_id'(상품id), 'ratings'(리뷰 별점), 'reg_date'(리뷰 등록일), 'article_headline'(리뷰 제목), 'article_content'(리뷰 내용), 'help_count'(N명에게 도움이 됨), 'is_photo_review'(사진리뷰 여부)]를 추출하여 output_review_(product_id).csv 형식으로 저장
        - getData_sel_template_coupang.py에서 추출한 'product_id'(상품 id) 정보를 이용, 상품별 리뷰 정보가 저장되어 있는 페이지로 이동함. 그 후 리뷰 관련 정보를 추출함.
- 4. 트러블슈팅 및 크롤링 코드 성능 개선
    - 쿠팡 측의 크롤러 Blocking 이슈 : Selenium Server에서 생성한 각 세션에서 get 함수를 통해 다른 URL로 이동할 경우 HTTP 403 Forbidden 페이지로 리다이렉트되며 막히는 문제가 발생함. 이에 대한 해결책으로 Selenium Server에서 다른 페이지로 이동할 시 wd hub에서 새로운 포트 번호를 가지는 세션을 생성하여 이동하게 하는 방법을 사용하여 해결함.
    - 크롤링 속도 향상 : Selenium을 이용하여 크롤링을 작업하다 보니 크롤링 속도가 느린 것이 단점으로 부각됨. 이를 해결하기 위해 다음과 같은 방안을 적용함.
        1. 코드에서 중복된 아이템을 검사하여 건너뛰게 함.
        2. Chrome Driver에 이미지를 disable하는 등 속도 향상에 도움을 주는 option 및 capability를 넣어 사용함.
        3. 카테고리별 입력을 달리한 여러 스크립트를 동시에 실행하여  다수의 Chrome Driver 세션을 생성, 시간을 단축함.
    - 페이지에서 특정 Element들이 로딩되지 않는 현상 : 페이지별로 footer가 로딩될 때까지 대기하는 코드를 추가하고, 여러 방안으로도 검색되지 않는 Element는 데이터를 가져올 수 있는 다른 페이지 링크를 찾아내어 그 페이지에서 가져오는 방식을 시도함.

3.  결과

- 크롤링 결과 약 850MB의 상품별 데이터를 확보하였음. 결과는 ./coupang 폴더에 csv 및 이미지 파일로 저장되어 있음.

4. 하위 디렉토리 구성

- ./naver : 네이버에서 크롤링한 Rawdata들을 보관하는 폴더. 데이터는 상품 카테고리별 폴더에 가격대별로 정리되어 있음.
- ./coupang : 쿠팡에서 크롤링한 Rawdata들을 보관하는 폴더. 데이터는 상품 카테고리별 폴더에 정리되어 있음. 각 카테고리별 폴더에는 실제 크롤링 작업에 사용한 getData_sel_coupang.py 스크립트도 포함되어 있음.
- ./coupang/(카테고리별 폴더)/images : 각 상품의 이미지를 보관한 폴더. 이미지명은 상품 ID와 동일함.
- ./chromedriver_linux64.zip : 크롤링 작업에 사용한 크롬 드라이버.
- ./getAlsoViewedItems : 다른 사람이 본 상품 리스트를 추출 작업에 사용한 스크립트. 상단 참조.
- ./getData_sel_coupang_template.py : getData_sel_coupang.py의 양식 코드.
- ./getData_sel_template_naver.py : getData_Sel.py의 양식 코드.
- ./getProductImage.py : 상품 이미지 추출 작업에 사용한 코드. 상단 참조.
- ./getReviewData.py : 상품 리뷰 정보 추출 작업에 사용한 코드. 상단 참조.
- ./selenium-server-standalone.jar : 크롤링 작업에 사용한 Selenium Standalone Server 구동 파일.
- ./selenium_readme.txt : 크롤링 작업을 진행한 환경(VirtualBox/Ubuntu 20.10)에서 Selenium 서버를 구동하고 크롬 드라이버를 실행하여 크롤링 스크립트를 실행할 조건을 만족시키는 절차를 적은 텍스트 파일.

## Data Preprocessing

---

### Function declarations for preprocessing<br>
![image](https://user-images.githubusercontent.com/78855847/121761668-1d18c080-cb6c-11eb-852e-b4d9a07f6180.png)<br>
![function2](https://user-images.githubusercontent.com/78855847/121761672-22760b00-cb6c-11eb-9e33-68080aa0eb0d.png)<br>

### Merge CSV<br>
merge_data paragraph를 실행하기 전에<br>
- path_dir를 가구 카테고리 디렉토리를 담고있는 위치로 설정해준다<br>
![image](https://user-images.githubusercontent.com/78855847/121761835-39692d00-cb6d-11eb-97b3-8cfe41a30c38.png)<br>
- 병합된 데이터 파일들은 각 카테고리 디렉토리안에 "result.csv"로 저장된다<br>
![image](https://user-images.githubusercontent.com/78855847/121762044-8d284600-cb6e-11eb-8a0c-860cb885b3ff.png)<br>

### Split inner attributes to columns
- 각 카테고리에서 추출할 특성들을 미리 지정해준다<br>
![image](https://user-images.githubusercontent.com/78855847/121762184-49820c00-cb6f-11eb-913d-a7057f09b463.png)<br>
- 상품마다 각 특성이 열로 추가된 데이터프레임은 merged_data 디렉토리에 저장된다<br>
![image](https://user-images.githubusercontent.com/78855847/121762280-d927ba80-cb6f-11eb-8340-cce3b286219c.png)<br>

### Set sales column
- 판매량은 다음과 같은 방식으로 산정된다<br>
  1. 최근 1년간의 리뷰 개수가 0개를 제외하고 가장 적은 10개 상품들의 리뷰 개수 평균을 구한다
  2. 위에서 구한 리뷰개수의 평균을 (가장 낮은 판매량 순위 - 각 상품의 판매량 순위)와 곱한다 
  3. 2번에서의 결과와 각 상품의 최근 1년간 리뷰개수의x3 을 더한다<br>
  ![image](https://user-images.githubusercontent.com/78855847/121762483-2b1d1000-cb71-11eb-949c-66ff158ed9f6.png)<br>
- 판매량 열이 추가된 최종 전처리 결과물이 parquet형식의 파일로 result 디렉토리에 저장된다<br>
![image](https://user-images.githubusercontent.com/78855847/121762565-a7afee80-cb71-11eb-8f69-b2509f67bc57.png)

## Data processing

---

### 함께 본 상품 리스트 기반 Tree

다른 고객이 함께 본 상품 리스트를 기반으로 `frequency` 를 산정한다. 이는 다른 고객이 함께 본 상품 리스트에 언급된 빈도수를 의미한다.<br>
해당 빈도수를 기준으로 리스트를 재정렬하고, 정렬된 순서대로 노드를 만들어 트리 형태의 네트워크를 그린다. 

 (1) 리스트에 함께 등장한 횟수가 많은 상품일 수록 네트워크 상에서 더 가까운 위치에 나타나고, 다른 상품과 리스트에 함께 등장하지 않았고 그 빈도수가 낮은 상품일 수록 네트워크 외곽에 나타난다. 

 (2) 각 노드는 초록색에 가까울 수록 판매량이 높으며, 검은색에 가까울 수록 판매량이 낮다. 

 (3) 노드의 투명도와 크기는 빈도수를 기준으로 빈도수가 높을 수록 불투명하고 크며, 낮을 수록 투명하고 작다.

 (4) 노드 위의 태그는 `product id` 로, 모든 제품에 대해 유일하다.

### code


 `[ft-graph.py](http://ft-graph.py)` 는 실행에 걸리는 시간 문제로 로컬 환경에서 실행하도록 구성되어 있다.

```python
frequency_table = {} # id   frequency   (DataFrame)
sorted_list = {} # id: [id list(sorted by frequency)] (Dictionary)
sales_list = {} # id: sales (Dictionary)
```

 각 리스트는 이러한 형태로 구성되며, 다시 카테고리 별 딕셔너리인 `category_frequency_table` , `category_sorted_list` , `category_sales_list` 에 저장된다.

 네트워크는 `networkx` 라이브러리를 사용하며, 구동을 위해선 `pygraphviz` 와 `matplotlib` 역시 필요하다. 

```
sudo apt-get install graphviz graphviz-dev
pip install pygraphviz
```

 `pygraphviz` 가 설치되지 않을 경우 

[](https://pygraphviz.github.io/documentation/stable/install.html)

```python
frequency_norm = 
    [frequency_table.get(n, 0.0)/frequency_table.max() for n in G.nodes()]
sold_norm = 
    [sales_list.get(n, 0.0)/max(sales_list.values()) for n in G.nodes()]
node_colors = 
    [(0, (math.log10(sold_norm[i]*9.0 + 1)), 0, (math.log10(frequency_norm[i]*9.0 + 1))) \
          for i in range(len(G.nodes()))]

pos = graphviz_layout(G, prog="neato")
plt.figure(i, figsize=(100, 100))

nx.draw_networkx(G, pos=pos, node_color=node_colors,\
                edge_color=(0, 0, 0, 0), with_labels=True, font_size=5,\
                node_size=[math.log10(frequency_table.get(n, 0.0)/frequency_table.max() * 9.0 + 1) * 50 \
                            for n in G.nodes()])
```

 네크워크를 그리는 코드는 위와 같다. `frequncy_norm` 과 `sold_norm` 은 각각의 리스트를 0부터 1 사이의 값으로 바꾼다.<br> 
 각 노드의 색상은 이렇게 정규화한 값에 9를 곱하고, 오류를 피하기 위해 1을 더하는 방식으로 구성했다.<br>
 색상이 선형으로 바뀌면 변화를 보기 어려웠기에 log 함수를 사용하였고, 노드 크기에도 같은 식을 사용하였다.<br>
 이렇게 저장한 네트워크 이미지들은 모두 `plot_images/` 에 있다.
 
### Get common features of product list
- set category and product_id list for target group<br>
![image](https://user-images.githubusercontent.com/78855847/121762735-c5318800-cb72-11eb-88e4-54281d0df78e.png)<br>
![image](https://user-images.githubusercontent.com/78855847/121763105-5c4b0f80-cb74-11eb-92dd-cee4d523b252.png)<br>
   - 동일한 특성요소를 가진 상품의 개수를 기준으로 공통요소를 추출하였다

### Get popular features of each category
- execute "카테고리별 인기 요소 추출" paragrapth<br>
![image](https://user-images.githubusercontent.com/78855847/121763169-df6c6580-cb74-11eb-8a43-884b02803975.png)<br>
![image](https://user-images.githubusercontent.com/78855847/121763173-ed21eb00-cb74-11eb-9226-14cff39ee513.png)<br>
   - 각 특성요소별 1개당 판매량을 기준으로 가장 높은 것을 인기요소로 추출하였다
   
## Results & Visualization

---
![visualization1](https://user-images.githubusercontent.com/78855847/121779752-3d7e6480-cbd8-11eb-82e3-af0bc6b89876.png)
- 트리 그래프에서 초록색에 가까울 수록 판매량이 높으며 불투명도가 높을 수록 같이 조회된 횟수가 높다.
- 그래프를 통해 같이 조회된 횟수가 높은 상품들(한 곳에 모여있는 상품들)이 대체적으로 판매량이 높은 것을
확인 할 수 있다.<br>

![visualization2](https://user-images.githubusercontent.com/78855847/121779805-7a4a5b80-cbd8-11eb-9ff0-17a3d17ceae7.png)
- 해당 군집단의 product_id를 공통요소 추출 알고리즘에 입력하여 해당 카테고리의 현 트렌드를 추천한다<br>

![visualization3](https://user-images.githubusercontent.com/78855847/121779827-8fbf8580-cbd8-11eb-8237-9046db30c8e6.png)<br>
- 카테고리 별 전체 상품을 대상으로하고 개당 판매량을 기준으로 한 결과는 위와 같으며<br>
특정 몇 개의 판매량이 높은 상품들이 결과에 매우 큰 영향을 미칠 수 있는 분석이기에 타겟으로 한 군집단의 공통요소와는 다소 차이가 있는 결과가 나올 수 있다.
- 따라서 트리 그래프를 통해 선정한 군집단의 공통 요소들이 보다 전반적인 현재 해당 카테고리의 인기 트랜드라고 추천할 수 있다. 
