# tree README.md

## 1. 방법

---

다른 고객이 함께 본 상품 리스트를 기반으로 `frequency` 를 산정한다. 이는 다른 고객이 함께 본 상품 리스트에 언급된 빈도수를 의미한다. 해당 빈도수를 기준으로 리스트를 재정렬하고, 정렬된 순서대로 노드를 만들어 트리 형태의 네트워크를 그린다. 

 (1) 리스트에 함께 등장한 횟수가 많은 상품일 수록 네트워크 상에서 더 가까운 위치에 나타나고, 다른 상품과 리스트에 함께 등장하지 않았고 그 빈도수가 낮은 상품일 수록 네트워크 외곽에 나타난다. 

 (2) 각 노드는 초록색에 가까울 수록 판매량이 높으며, 검은색에 가까울 수록 판매량이 낮다. 

 (3) 노드의 투명도와 크기는 빈도수를 기준으로 빈도수가 높을 수록 불투명하고 크며, 낮을 수록 투명하고 작다.

 (4) 노드 위의 태그는 `product id` 로, 모든 제품에 대해 유일하다.

## 2. code

---

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

 네크워크를 그리는 코드는 위와 같다. `frequncy_norm` 과 `sold_norm` 은 각각의 리스트를 0부터 1 사이의 값으로 바꾼다. 각 노드의 색상은 이렇게 정규화한 값에 9를 곱하고, 오류를 피하기 위해 1을 더하는 방식으로 구성했다. 색상이 선형으로 바뀌면 변화를 보기 어려웠기에 log 함수를사용한다.

 아래의 노드 크기에도 같은 식을 사용한다.

## 3. 결과

---

 이렇게 저장한 네트워크 이미지들은 모두 `plot_images/` 에 있다.