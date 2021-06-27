
# In[1]:

"""
#class Node:
    def __init__(self, id, frequency=0):
        self.id = id
        self.frequency = frequency
        self.children = []

    def addChild(self, c):
        self.children.append(c)
        self.addFrequency()

    def addFrequency(self):
        self.frequency += 1

class Tree:
    def __init__(self):
        self.root = None

    def makeRoot(self, node):
        if self.root == None:
            self.root = node

    #초기값 : start = root
    def addNodes(self, nodes, start, current=0):
        if len(start.children) == 0:
            for n in nodes[current:]:
                    start.addChild(n)
                    start = n
        else: # root에서부터 내려가며 일치하는 route가 있는지 탐색
            for candidate in start.children:
                if candidate == nodes[current]:
                    current += 1
                    candidate.addFrequency()
                    start = candidate
                # 없을 경우 새로운 route 추가
                else:
                    for n in nodes[current:]:
                        start.addChild(n)
                        start = n
"""

from PIL import Image
import os

def open_image(path):
    images = {}
    files = os.listdir(path)
    for file in files:
        images[int(file.replace(".jpg", "").replace(".png", ""))] = Image.open(path + "/" + file)
    return images

## local test code
# In[3]:

import pandas as pd
import numpy as np

images_folder = 'data_images/'
also_viewed_folder = 'data_with_also_viewed/'
sold_folder = 'data_with_sold/'

category = ['bed', 'bedtray', 'chair', 'closet', 'drawers', 'dressingtable,console',\
           'hanger,doorhook', 'hanger', 'livingbox', 'livingroom table', 'mattress', 'outdoor furniture',\
           'partition', 'recliner', 'safe', 'shoes shelf', 'smalltable', 'sofa',\
           'storage', 'table']
category_frequency_table = {}
category_sorted_list={}
category_sales_list = {}

for c in category:
    also_viewed = also_viewed_folder + c + '.csv'
    sold = sold_folder + c + '.csv'
    
    df_also_viewed = pd.read_csv(also_viewed)
    df_sold = pd.read_csv(sold)
    
    # frequency를 count 하기 위한 모든 frequency list
    all_list = []

    frequency_table = {} # id: frequency (dict)
    sorted_list = {} # id: [id list(sorted by frequency)] (dict)
    sales_list = {} # id: sales (dict)

    # 데이터 전처리
    for i in range(len(df_also_viewed)):
        li = df_also_viewed.loc[i:i, ['also_viewed_item_prouduct_id']].values.tolist()
        li = li[0][0].replace("\'", "").replace("[", "").replace("]", "").replace(" ", "").split(',')
        sorted_list[df_also_viewed.iloc[i,0]] = map(int, li)
        for l in li:
            if l == '':
                continue
            all_list.append(int(l))

    frequency_table = pd.Index([all for all in all_list]).value_counts()
    
    for i in range(len(df_sold)):
        prod_id = df_sold.loc[i:i, ['product_id']].values.tolist()
        prod_id = prod_id[0][0]
        if prod_id == 0:
            continue
        sales = df_sold.loc[i:i, ['sales']].values.tolist()
        sales = sales[0][0]
        sales_list[int(prod_id)] = float(sales)
        

    # 데이터 sort
    for id, list in sorted_list.items():
        try:
            list = sorted(list, key=lambda idx: frequency_table.get(idx, 0), reverse=True)
        except:
            continue
        try: sorted_list[id] = list[:20]
        except: sorted_list[id] = list[:10]
        for listed_id in sorted_list[id]:
            if frequency_table.get(listed_id, 0) == 0:
                sorted_list[id].remove(listed_id)
    
    category_frequency_table[c] = frequency_table
    category_sorted_list[c] = sorted_list
    category_sales_list[c] = sales_list

## Make ft-graph
# In[4]:

#images_list = open_image(images_folder + 'bed')

## Tree
# In[5]:

import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import pandas as pd
import pygraphviz
import math
import pandas as pd
import matplotlib.pyplot as plt

i = 1
for c in category:
    frequency_table = category_frequency_table[c]
    sorted_list = category_sorted_list[c]
    sales_list = category_sales_list[c]

    G = nx.DiGraph()
    for id, li in sorted_list.items():
        nx.add_path(G, li)


    #값 normalize
    frequency_norm = [frequency_table.get(n, 0.0)/frequency_table.max() for n in G.nodes()]
    sold_norm = [sales_list.get(n, 0.0)/max(sales_list.values()) for n in G.nodes()]
    node_colors = [(0, (math.log10(sold_norm[i]*9.0 + 1)), 0, (math.log10(frequency_norm[i]*9.0 + 1))) \
                for i in range(len(G.nodes()))]


    pos = graphviz_layout(G, prog="neato")

    plt.figure(i, figsize=(100, 100))

    
    nx.draw_networkx(G, pos=pos, node_color=node_colors,\
                    edge_color=(0, 0, 0, 0), with_labels=True, font_size=5,\
                    node_size=[math.log10(frequency_table.get(n, 0.0)/frequency_table.max() * 9.0 + 1) * 50 \
                                for n in G.nodes()])

    
    """
    images_list = open_image(images_folder + c)

    plt.figure(2, figsize=(100,100))
    ax = plt.gca()
    fig = plt.gcf()
    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    imsize = 1
    
    for n in G.nodes():
        (x, y) = pos[n]
        xx, yy = trans((x, y))
        xa, ya = trans2((xx, yy))
        a = plt.axes([xa-imsize/2.0,ya-imsize/2.0, imsize, imsize ])
        try: image = images_list[n]
        except: continue
        else: a.imshow(images_list[n])
        a.set_aspect('equal')
        a.axis('off') 
        """


    plt.savefig(c + ".png", dpi = 300)
    plt.show()


    i += 1

## Plot
# In[6]:

print(sorted_list)


