#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st


#import packages
import pandas as pd
import requests
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio

import numpy as np
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt
import seaborn as sns

import folium
from folium import plugins
from folium.plugins import MarkerCluster



# In[ ]:


#### API populaire koffie


# In[4]:


# API's inladen hot en iced coffees met ingrediënten etc
response_sets = requests.get("https://api.sampleapis.com/coffee/hot")
response_sets1 = requests.get('https://api.sampleapis.com/coffee/iced')

url_hot = 'https://api.sampleapis.com/coffee/hot' #https://sampleapis.com/api-list
response_hot = requests.get(url_hot)
json_hot = response_hot.json()
df_coffee_hot = pd.json_normalize(json_hot)
df_coffee_hot = pd.DataFrame(df_coffee_hot)

url_iced = 'https://api.sampleapis.com/coffee/iced'
response_iced = requests.get(url_iced)
json_iced = response_iced.json()
df_coffee_iced = pd.json_normalize(json_iced)
df_coffee_iced = pd.DataFrame(df_coffee_iced)

# Lege waardes en onnodige kolommen verwijderen
df_coffee_hot.drop(df_coffee_hot.index[20:41], inplace=True)
df_coffee_hot = df_coffee_hot.drop(['idnumber', 'id', 'image', 'description'], axis=1)
df_coffee_iced = df_coffee_iced.drop(['id', 'image', 'description'], axis=1)

# Hot en iced samenvoegen tot één dataframe
df_coffee = df_coffee_hot.append(df_coffee_iced)

# Ingrediënten uit lists in kolom halen
df_coffee_exploded = df_coffee.explode('ingredients')

# Dubbele ingrediënten samenvoegen
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Steamed Milk', 'Milk')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('1oz Milk', 'Milk')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Foamed milk', 'Milk')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Foam', 'Milk')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Long steeped coffee', 'Coffee')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('1oz Espresso', 'Espresso')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('2oz Espresso', 'Espresso')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Short pulled espresso', 'Espresso')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Long pulled espresso', 'Espresso')
df_coffee_exploded['ingredients'] = df_coffee_exploded['ingredients'].str.replace('Blended ice', 'Ice')

df_coffee_exploded = df_coffee_exploded.groupby('ingredients')['title'].count().sort_values(ascending=False).reset_index()

fig1 = px.bar(df_coffee_exploded, x='ingredients', y='title', text='title')
fig1.update_layout( 
    title="<b>Het aantal drankjes bestaande uit ingrediënten</b>",
    yaxis_title="Aantal verschillende drankjes",
    xaxis_title="Ingrediënt"
)
fig1.show()
st.plotly_chart(fig1)


