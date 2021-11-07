# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 13:14:18 2021

@author: krasimirk
"""
import plotly.graph_objects as go
# pio.renderers.default = "browser"
import pandas as pd

#%%
# https://plotly.com/python/sankey-diagram/

fig = go.Figure(data=[go.Sankey(
    node = dict(
      line = dict(color = "black", width = 0.5),
      label = ["A1", "A2", "B1", "B2", "C1", "C2"],

    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A2, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2],
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()

#%%



d = {'LJU':
         {'idx':0,
          'dest_cnt:':
              {}}
     
     
     
     }

fig = go.Figure(data=[go.Sankey(
    node = dict(
      line = dict(color = "black", width = 0.5),
      label = ["LJU",'ZAG','TRI', "NL","IT",'BE', "AMS", "EIN", 'NPL','VEN','BRU'],

    ),
    link = dict(
      source = [0, 3, 3, 1, 4, 1, 3, 2, 5], 
      target = [3, 6, 7, 4, 8, 3, 7, 5, 10],
      value =  [10, 5, 5, 5, 5, 5, 5, 5, 5],
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()