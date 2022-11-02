#!/usr/bin/env python
# coding: utf-8

# In[ ]:

#import packages
import streamlit as st

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
import streamlit_folium as st_folium
from streamlit_folium import folium_static

from PIL import Image

st.title('2022-2023 sem-1 VA: Dashboard')
st.header('Starbucks')
st.subheader('Annika & Estelle')

# # API populaire koffie's met ingrediënten
st.subheader(" API populaire koffie's met ingrediënten")

# In[19]:


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

lijst_ingredienten_totaal = df_coffee_exploded['ingredients'].unique()
lijst_ingredienten_totaal = pd.DataFrame(lijst_ingredienten_totaal)
# print(lijst_ingredienten_totaal)

st.dataframe(lijst_ingredienten_totaal)

st.markdown('Van de dataset met de meest populaire koffiesoorten van koude en warme dranken is één dataset gemaakt. Alle ingrediënten staan op een rijtje, maar sommige kwamen overeen, slechts met een andere hoeveelheid of bewerking. Deze zijn samengevoegd om een beeld te creeeren van de meest benodigde ingrediënten. Deze zijn te zien in het staafdiagram hieronder.')

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


# # Map
st.subheader("Map")
# In[4]:
st.markdown('Om de map te maken is er gebruik gemaakt van de directory.csv bestand. Hierin zijn er onder andere gegevens te vinden over; Store Number, Store Name, Ownership Type, Street Address,Country, Coordinaten etc.')

world_wide = pd.read_csv('directory.csv')
world_wide.notnull().sum()
world_wide.dropna()
world_wide.notnull().sum()
world_wide.City.value_counts().head(20)
wereld_dataset =world_wide.iloc[-5:]

st.dataframe(wereld_dataset)

# In[20]:


df_world_count = world_wide.groupby(['Country'], dropna=False)['Postcode'].count().sort_values(ascending=False).reset_index()
df_world_count = df_world_count.head(10)

st.markdown('In de figuur hieronder is een staafdiagram geschetst met de top 10 landen met de meeste Starbucks stores. Hieruit valt op te merken dat de koploper US 13 duizend Starbucks stores heeft. Op de tweede plek staat China met ongeveer 2200 store. Dat is aanzienlijk minder dan de koploper.')

# print(df_world_count)
fig2 = px.bar(df_world_count, x='Country', 
             y='Postcode',
             text="Postcode",
            # color='status',
             labels={
                 "Postcode": "Aantal stores",
                 "Country": "Landcode"
             },
                title="<b>Top 10 landen met de meeste Starbucks Stores</b>"
            )
fig2.show()
st.plotly_chart(fig2)

## nog top 10 maken


# In[6]:


world_wide = pd.read_csv('directory.csv')
world_wide=world_wide.dropna(subset=['Longitude'])
world_wide=world_wide.dropna(subset=['Latitude'])

combined_zip = zip(world_wide['Latitude'], world_wide['Longitude'],world_wide['Country'],world_wide['Store Name'], world_wide['Ownership Type']  )
points = [*combined_zip]
df_points = pd.DataFrame(points, columns=['LAT','LNG','COUNTRY','NAME','TYPE'])


# In[31]:
st.markdown('Om de map te maken is er gebruik gemaakt van de gevraagde gegevens, deze zijn vervolgens omgezet in een gecombined zip die in een nieuwe lijst wordt gezet. Dit is vervolgens door de packages Folium ondersteund. Doormiddel van de checkbox kunnen de Starbucks Stores in Nederland of de wereld aan of uit worden gezet. Door op de pop-up te klikken komt er informatie ter beschikking over de store gegevens.')

mymap = folium.Map(location=[52.489797, 4.879391], 
               tiles='CartoDB positron',
               zoom_start=7.4)



mCluster_nl = MarkerCluster(name="nl").add_to(mymap)
mCluster_wereld = MarkerCluster(name="wereld").add_to(mymap)


for row in df_points.itertuples():
    location = row[1], row[2]
    icon=folium.Icon(color='green', icon='glyphicon glyphicon-star-empty', prefix='glyphicon')
    html = '''Land: ''' + row[3] + '''<br>Locatie store: ''' + row[4] +  '''<br> Type eigendom: ''' + row[5]
    iframe = folium.IFrame(html, width=200, height=100)
    popup = folium.Popup(iframe, max_width=300)
    marker = folium.Marker(location=location, popup=popup, icon=icon)
    if row[3] == 'NL':
        mCluster_nl.add_child(marker)
#     elif row[3] != 'NL':
#         mCluster_wereld.add_child(marker)
        

folium.LayerControl().add_to(mymap);

# mymap
st_data = folium_static(mymap)


# # Starbucks ingredienten
st.subheader("Starbucks ingredienten")

# In[8]:


starbucks_drinkMenu = pd.read_csv('starbucks_drinkMenu_expanded.csv')
# VERWIJDEREN VAN DUBBELE WAARDES
starbucks_drinkMenu.duplicated().sum()
starbucks_drinkMenu.drop_duplicates(inplace=True)

#CONTROLE nul waardes in colom 
starbucks_drinkMenu.isnull().sum() ##1 missende waarde

#### verwijderen van missende waarde 
starbucks_drinkMenu.dropna()

starbucks_drinkMenu["Sugars"] = starbucks_drinkMenu[" Sugars (g)"].astype(int)
starbucks_drinkMenu["Sodium"] = starbucks_drinkMenu[" Sodium (mg)"].astype(int)

print(starbucks_drinkMenu.head())
print(starbucks_drinkMenu.dtypes)


# In[21]:


# data students performance
st.markdown('In onderstaand figuur zijn per categorie drankjes van Starbucks alle drankjes weergegeven. De count die hierbij staat geeft het aantal formaten weer die mogelijk zijn per drankje.')

df = px.data.tips()
fig3 = px.sunburst(starbucks_drinkMenu,
                  path=['Beverage_category', 'Beverage'])
fig3.update_layout(title_text="<b> Starbucks drankjes per catergorie<b>", 
             #     titlefont={'size': 24, 'family':'Serif'},
                  width=750, 
                  height=750,
                 )
fig3.show()
st.plotly_chart(fig3)


# In[22]:


aantal_drinks_per_catergorie = starbucks_drinkMenu.groupby(['Beverage_category'])['Beverage_prep'].count().sort_values(ascending=False).reset_index()

fig4 = px.bar(aantal_drinks_per_catergorie, x='Beverage_category', y='Beverage_prep', text = "Beverage_prep")

fig4.update_layout( 
    title="<b>Het aantal drankjes en formaten beschikbaar per drankcategorie</b>",
    yaxis_title="Aantal",
    xaxis_title="Drankcategorie"
    )

fig4.show()
st.plotly_chart(fig4)


# In[23]:


#starbucks_drinkMenu.sort_values("Calories", ascending=False)
fig5 = px.box(starbucks_drinkMenu, x='Calories', y='Beverage')
fig5.update_layout( 
    title="<b>Het aantal calorieën per drankje</b>",
    yaxis_title="Type drankje",
    xaxis_title="Aantal calorieën"
)

fig5.show()
st.plotly_chart(fig5)


# In[25]:


df = px.data.tips()
fig6 = px.histogram(starbucks_drinkMenu, x="Calories", marginal="box")

fig6.update_layout( 
    title="<b>Spreiding calorieën</b>",
    yaxis_title="Frequentie",
    xaxis_title="Calorieën"
)

fig6.show()
st.plotly_chart(fig6)


# In[26]:


df = px.data.tips()
fig7 = px.box(starbucks_drinkMenu, 
x=" Sugars (g)", 
color='Beverage_category', 
hover_name = 'Beverage_category'
)

dropdown_buttons = [
{'label': "Totaal", 'method': "update", 'args': [{"visible": [True,True,True,True,True,True,True,True,True]}, {'title': 'Spreiding calorieën per categorie drankje'}]},
{'label': "Coffee", 'method': "update", 'args': [{"visible": [True,False,False,False,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Classic Espresso Drinks", 'method': "update", 'args': [{"visible": [False,True,False,False,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Signature Espresso Drinks", 'method': "update", 'args': [{"visible": [False,False,True,False,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Tazo Tea Drinks", 'method': "update", 'args': [{"visible": [False,False,False,True,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Shaken Iced Beverages", 'method': "update", 'args': [{"visible": [False,False,False,False,True,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Smoothies", 'method': "update", 'args': [{"visible": [False,False,False,False,False,True,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Frappucino's", 'method': "update", 'args': [{"visible": [False,False,False,False,False,False,True,True,True]}, {'title': "Spreiding calorieën per categorie drankje"}]}
]

fig7.update_layout(
    {    'updatemenus':[{
            'type': 'dropdown',
            'x': 1.40, 'y': 1.1,
            'buttons': dropdown_buttons
            }]},
    title="<b>Spreiding suiker per soort drankje</b>",
    yaxis_title="Frequentie",
    xaxis_title="Suiker (g)",
    legend_title="Categorie drankje"
)

fig7.show()
st.plotly_chart(fig7)


# In[27]:


df = px.data.tips()
fig8 = px.histogram(starbucks_drinkMenu, x=" Sugars (g)", marginal="box")

fig8.update_layout( 
    title="<b>Spreiding suiker</b>",
    yaxis_title="Frequentie",
    xaxis_title="Suiker"
)

fig8.show()
st.plotly_chart(fig8)


# In[28]:



fig9 = px.scatter(starbucks_drinkMenu, 
x="Calories", 
y=" Sugars (g)", 
color="Beverage_category",
symbol="Beverage_category",
trendline='ols',
trendline_scope="overall", 
labels={ "OLS Trendline ": "Trendline" }
)

dropdown_buttons = [
{'label': "Totaal", 'method': "update", 'args': [{"visible": [True,True,True,True,True,True,True,True,True]}, {'title': 'Spreiding calorieën per categorie drankje'}]},
{'label': "Coffee", 'method': "update", 'args': [{"visible": [True,False,False,False,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Classic Espresso Drinks", 'method': "update", 'args': [{"visible": [False,True,False,False,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Signature Espresso Drinks", 'method': "update", 'args': [{"visible": [False,False,True,False,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Tazo Tea Drinks", 'method': "update", 'args': [{"visible": [False,False,False,True,False,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Shaken Iced Beverages", 'method': "update", 'args': [{"visible": [False,False,False,False,True,False,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Smoothies", 'method': "update", 'args': [{"visible": [False,False,False,False,False,True,False,False,False]}, {'title': "Spreiding calorieën per categorie drankje"}]},
{'label': "Frappucino's", 'method': "update", 'args': [{"visible": [False,False,False,False,False,False,True,True,True]}, {'title': "Spreiding calorieën per categorie drankje"}]}
]


fig9.update_layout(
    {    'updatemenus':[{
            'type': 'dropdown',
            'x': 1.40, 'y': 1.1,
            'buttons': dropdown_buttons
            }]},
    title="<b>Spreiding calorieën per categorie drankje</b>",
    yaxis_title="Suikers (g)",
    xaxis_title="Aantal calorieën",
    legend_title="Categorie drankje"
)

fig9.show()
st.plotly_chart(fig9)


# In[29]:


df = pd.DataFrame(starbucks_drinkMenu)

fig10 = plt.figure()
corr_matrix = starbucks_drinkMenu.corr()
print(corr_matrix)
sns.heatmap(corr_matrix, annot=True)

plt.title("Correlatie onderling de variabelen")

plt.show()
st.pyplot(fig10)


# In[32]:
st.subheader("Regressie op variabelen ingredienten")

st.markdown('Allereerst hebben we gekeken naar de samenhang tussen zout en het aantal calorieën. Hierbij is geen duidelijke correlatie op te maken. Wel lijkt het door de trendlijn zo dat de hoeveelheid calorieën toeneemt naarmate de hoeveelheid zout toeneemt. De R-squared van 0.150 (zie onderstaand schema) bevestigt dit, want de variabele zout voegt niet veel toe aan het model met deze variabele. Er is dus weinig samenhang te vinden tussen de twee variabelen.')
regressie1 = ols(formula="Calories ~ Sodium", data=starbucks_drinkMenu).fit()
explanatory_data1 = pd.DataFrame({"Sodium": np.arange(40, 60)})
prediction_data1 = explanatory_data1.assign(Calories=regressie1.predict(explanatory_data1))
fig11 = plt.figure()
ax1 = sns.regplot(x="Sodium",y="Calories",ci=None,data=starbucks_drinkMenu,)
ax2 = sns.scatterplot(x="Sodium", y="Calories",data=prediction_data1,color="red",marker="s")
ax1.set(xlabel='Zout (g)', ylabel="Aantal calorieën")
ax1.set(title="Voorspelling aantal calorieën per hoeveelheid zout in grammen")
plt.show()
# print(regressie1.summary())
# regressie1.summary(print_fn=lambda x: st.text(x))
image1 = Image.open('Regressie ZOUT.PNG')
col1, col2 = st.columns([1,1])
with col1:
    st.pyplot(fig11, 
              #figsize=(5, 5)
             )
with col2:
    st.image(image1, caption='Summary zout'
             #, width=60
            )

st.markdown('Vervolgens zijn we gaan kijken naar de samenhang tussen de hoeveelheid suikers en het aantal calorieën. Hier is duidelijk wel een correlatie in waar te nemen. Het is duidelijk te zien dat hoe meer suiker er in een drankje zit, hoe hoger het aantal calorieën dat deze bevat is. Ook de R-squared is in dit geval hoog, dus bij een model voor de berekening en voorspelling van het aantal calorieën, zou de variabele suiker erg goed gebruikt kunnen worden. Dit dus in tegenstelling tot die van zout.')
regressie2 = ols(formula="Calories ~ Sugars", data=starbucks_drinkMenu).fit()
explanatory_data2 = pd.DataFrame({"Sugars": np.arange(83, 100)})
prediction_data2 = explanatory_data2.assign(Calories=regressie2.predict(explanatory_data2))
fig12 = plt.figure()
ax3 = sns.regplot(x="Sugars",y="Calories",ci=None,data=starbucks_drinkMenu,)
ax4 = sns.scatterplot(x="Sugars", y="Calories",data=prediction_data2,color="red",marker="s")
ax3.set(xlabel='Suiker (g)', ylabel="Aantal calorieën")
ax3.set(title="Voorspelling aantal calorieën per hoeveelheid suiker in grammen")
plt.show()
st.pyplot(fig12)
# print(regressie2.summary())
# regressie2.summary(print_fn=lambda x: st.text(x))
image2 = Image.open('Regressie SUIKER.PNG')
st.image(image2, caption='Summary suiker')

st.header('Bronnen')
st.markdown('API populairste koffie-drankjes: https://sampleapis.com/api-list')

# <a style='text-decoration:none;line-height:16px;display:flex;color:#5B5B62;padding:10px;justify-content:end;' href='https://deepnote.com?utm_source=created-in-deepnote-cell&projectId=35ad6ba8-4d16-4527-85ba-cb0e5bb1ec9c' target="_blank">
# <img alt='Created in deepnote.com' style='display:inline;max-height:16px;margin:0px;margin-right:7.5px;' src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iODBweCIgaGVpZ2h0PSI4MHB4IiB2aWV3Qm94PSIwIDAgODAgODAiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayI+CiAgICA8IS0tIEdlbmVyYXRvcjogU2tldGNoIDU0LjEgKDc2NDkwKSAtIGh0dHBzOi8vc2tldGNoYXBwLmNvbSAtLT4KICAgIDx0aXRsZT5Hcm91cCAzPC90aXRsZT4KICAgIDxkZXNjPkNyZWF0ZWQgd2l0aCBTa2V0Y2guPC9kZXNjPgogICAgPGcgaWQ9IkxhbmRpbmciIHN0cm9rZT0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIxIiBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPgogICAgICAgIDxnIGlkPSJBcnRib2FyZCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTEyMzUuMDAwMDAwLCAtNzkuMDAwMDAwKSI+CiAgICAgICAgICAgIDxnIGlkPSJHcm91cC0zIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMjM1LjAwMDAwMCwgNzkuMDAwMDAwKSI+CiAgICAgICAgICAgICAgICA8cG9seWdvbiBpZD0iUGF0aC0yMCIgZmlsbD0iIzAyNjVCNCIgcG9pbnRzPSIyLjM3NjIzNzYyIDgwIDM4LjA0NzY2NjcgODAgNTcuODIxNzgyMiA3My44MDU3NTkyIDU3LjgyMTc4MjIgMzIuNzU5MjczOSAzOS4xNDAyMjc4IDMxLjY4MzE2ODMiPjwvcG9seWdvbj4KICAgICAgICAgICAgICAgIDxwYXRoIGQ9Ik0zNS4wMDc3MTgsODAgQzQyLjkwNjIwMDcsNzYuNDU0OTM1OCA0Ny41NjQ5MTY3LDcxLjU0MjI2NzEgNDguOTgzODY2LDY1LjI2MTk5MzkgQzUxLjExMjI4OTksNTUuODQxNTg0MiA0MS42NzcxNzk1LDQ5LjIxMjIyODQgMjUuNjIzOTg0Niw0OS4yMTIyMjg0IEMyNS40ODQ5Mjg5LDQ5LjEyNjg0NDggMjkuODI2MTI5Niw0My4yODM4MjQ4IDM4LjY0NzU4NjksMzEuNjgzMTY4MyBMNzIuODcxMjg3MSwzMi41NTQ0MjUgTDY1LjI4MDk3Myw2Ny42NzYzNDIxIEw1MS4xMTIyODk5LDc3LjM3NjE0NCBMMzUuMDA3NzE4LDgwIFoiIGlkPSJQYXRoLTIyIiBmaWxsPSIjMDAyODY4Ij48L3BhdGg+CiAgICAgICAgICAgICAgICA8cGF0aCBkPSJNMCwzNy43MzA0NDA1IEwyNy4xMTQ1MzcsMC4yNTcxMTE0MzYgQzYyLjM3MTUxMjMsLTEuOTkwNzE3MDEgODAsMTAuNTAwMzkyNyA4MCwzNy43MzA0NDA1IEM4MCw2NC45NjA0ODgyIDY0Ljc3NjUwMzgsNzkuMDUwMzQxNCAzNC4zMjk1MTEzLDgwIEM0Ny4wNTUzNDg5LDc3LjU2NzA4MDggNTMuNDE4MjY3Nyw3MC4zMTM2MTAzIDUzLjQxODI2NzcsNTguMjM5NTg4NSBDNTMuNDE4MjY3Nyw0MC4xMjg1NTU3IDM2LjMwMzk1NDQsMzcuNzMwNDQwNSAyNS4yMjc0MTcsMzcuNzMwNDQwNSBDMTcuODQzMDU4NiwzNy43MzA0NDA1IDkuNDMzOTE5NjYsMzcuNzMwNDQwNSAwLDM3LjczMDQ0MDUgWiIgaWQ9IlBhdGgtMTkiIGZpbGw9IiMzNzkzRUYiPjwvcGF0aD4KICAgICAgICAgICAgPC9nPgogICAgICAgIDwvZz4KICAgIDwvZz4KPC9zdmc+' > </img>
# Created in <span style='font-weight:600;margin-left:4px;'>Deepnote</span></a>


