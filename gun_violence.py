#!/usr/bin/env python
# coding: utf-8
import numpy as np
import streamlit as st
import pandas as pd

from bokeh.sampledata import us_states
from bokeh.plotting import *
from bokeh.models import LogColorMapper, ColorBar
from bokeh.palettes import Viridis6 as palette


# Initilaizing state and county borders
us_states = us_states.data.copy()

state_xs = [us_states[code]["lons"] for code in us_states]
state_ys = [us_states[code]["lats"] for code in us_states]

state_names = [us_states['name'] for us_states in us_states.values()]

# Initializing tools for Bokeh
TOOLS = "pan,wheel_zoom,reset,hover,save"
palette = tuple(reversed(palette))
color_mapper = LogColorMapper(palette=palette)

# Read in data
pop_df = pd.read_csv('pop_data.csv')
pop_df_sorted = pop_df.sort_values(['State'], ascending=True)
prov_13 = pd.read_csv('prov.csv', skiprows = 1101, nrows = 50, header=None,
                      usecols=[0,135], names = ['state','#_prov'])

gv13 = pd.read_csv('gv_data_2013.csv', nrows = 52133, dayfirst = True)
gv13c = gv13.groupby('state')
state_group13 = gv13c.describe()
pop_2013 = pd.Series.tolist(pop_df_sorted['Pop2013'].astype(float))
occurence_2013 = pd.Series.tolist(state_group13['incident_id','count'])

gv13nk = gv13.where(gv13['n_killed'] > 0).dropna()
gv13ni = gv13.where(gv13['n_injured'] > 0).dropna()
gv13_cleaned = pd.concat([gv13ni,gv13nk])

gv13nks = gv13c['n_killed'].sum()
gv13nis = gv13c['n_injured'].sum()

gv13nif = gv13nis.to_frame()
gv13_scatter = gv13nks.to_frame()
gv13_scatter['n_injured'] = gv13nif['n_injured']
prov_13.loc[7.5] = ['District of Columbia', 50]
prov_13 = prov_13.sort_index().reset_index(drop=True)
gv13_scatter = gv13_scatter.set_index(prov_13.index)
gv13_scatter['n_provision'] = prov_13['#_prov']
gv13_scatter['state'] = prov_13['state']
prov_13_sum = prov_13['#_prov'].sum()

col_names = ['incident_id','date','state','city_or_county','address','n_killed','n_injured',           'incident_url','source_url','incident_url_fields_missing','congressional_district','gun_stolen',
'gun_type','incident_characteristics','latitude','location_description','longitude','n_guns_involved',
'notes','participant_age','participant_age_group','participant_gender','participant_name','participant_relationship',
'participant_status','participant_type','sources','state_house_district','state_senate_district']
gv21 = pd.read_csv('gv_data_2013.csv',skiprows = 53577, nrows =53578, names = col_names)
gv21c = gv21.groupby('state')
state_group21 = gv21c.describe()
pop_2021 = pd.Series.tolist(pop_df_sorted['Pop2021'].astype(float))
occurence_2021 = pd.Series.tolist(state_group21['incident_id','count'])
prov_21 = pd.read_csv('prov.csv', skiprows = 1301, nrows = 50, header=None,
                      usecols=[0,135], names = ['state','#_prov'])


gv21nk = gv21.where(gv21['n_killed'] > 0).dropna()
gv21ni = gv21.where(gv21['n_injured'] > 0).dropna()
gv21_cleaned = pd.concat([gv21ni,gv21nk])

gv21nks = gv21c['n_killed'].sum()
gv21nis = gv21c['n_injured'].sum()

gv21nif = gv21nis.to_frame()
gv21_scatter = gv21nks.to_frame()
gv21_scatter['n_injured'] = gv21nif['n_injured']
prov_21.loc[7.5] = ['District of Columbia', 64]
prov_21 = prov_21.sort_index().reset_index(drop=True)
gv21_scatter = gv21_scatter.set_index(prov_21.index)
gv21_scatter['n_provision'] = prov_21['#_prov']
gv21_scatter['state'] = prov_21['state']
prov_21_sum = prov_21['#_prov'].sum()
gv_bar = gv13_scatter
gv_bar['n_killed_2021'] = gv21_scatter['n_killed']
gv_bar['n_injured_2021'] = gv21_scatter['n_injured']
gv_bar['n_provision_2021'] = gv21_scatter['n_provision']

### Gun Violence in 2013 & 2021 ###

## Scatter_plot
source13 = ColumnDataSource(
    data={
        'state':gv13_scatter['state'], 
        'number_killed':gv13_scatter['n_killed'], 
        'number_injured':gv13_scatter['n_injured']})
source21 = ColumnDataSource(
    data={
        'state':gv21_scatter['state'], 
        'number_killed':gv21_scatter['n_killed'], 
        'number_injured':gv21_scatter['n_injured']})

s13 = figure(
    title="Gun Violence in The United States in 2021", 
    toolbar_location="left", 
    plot_width=1400, 
    plot_height=700, 
    tooltips = [('State','@state'), 
                ('Number killed', '@number_killed'), 
                ('Number injured', '@number_injured')],
    tools = TOOLS,
    background_fill_color="#333344")

s13.circle(
    x = 'number_killed',
    y = 'number_injured', 
    size=8, 
    color='red', 
    alpha=0.5, 
    source = source13,
    legend_label = '2013: 1347 Provisions')
s13.circle(
    x = 'number_killed',
    y = 'number_injured', 
    size=8, 
    color='green', 
    alpha=0.5, 
    source = source21,
    legend_label = '2021: 1432 Provisions')
s13.xaxis.axis_label = 'Number Killed (Total Per State)'
s13.yaxis.axis_label = 'Number Injured (Total Per State)'
s13.title.text = "Total Gun Violence in Each State: 2013-2021"
s13.title.align = "left"
s13.title.text_font_size = "25px"
s13.xaxis.axis_label_text_font_size = "15px"
s13.yaxis.axis_label_text_font_size = "15px"
s13.legend.location = 'top_left'
s13.grid.grid_line_color = None

## Choropleth Map

# Loop to calculate per capita
pc = dict()
for i in range(len(state_group13)):
    pc[i] = occurence_2013[i] / (pop_2013[i] / 1000) * 100  # Out of every 1000 people
per_capita = pd.Series(pc)

source_c = dict(x = state_xs, 
                y = state_ys, 
                percapita = per_capita, 
                names = state_names)

c13 = figure(
    title="per capita gun violence", 
    tools=TOOLS, 
    x_axis_location=None, 
    y_axis_location=None,
    tooltips=[("Name", "@names"), ("per capita", "@percapita")],
    plot_width=2000, 
    plot_height=700,
    background_fill_color="#333344",
    toolbar_location="left")

c13.grid.grid_line_color = None
c13.hover.point_policy = "follow_mouse"

c13.patches(
    'x', 
    'y', 
    source=source_c,
    fill_color={'field': 'percapita', 'transform': color_mapper},
    fill_alpha=0.7, 
    line_color="white", 
    line_width=0.5)

color_bar = ColorBar(
    color_mapper=color_mapper,
    location="bottom_left", orientation="horizontal",
    title="Incedents per 1000 Individules",
    title_text_font_size="16px", title_text_font_style="bold",
    title_text_color="lightgrey", major_label_text_color="lightgrey",
    background_fill_alpha=0.0)
c13.add_layout(color_bar)

c13.circle(
    x = gv13_cleaned['longitude'],
    y = gv13_cleaned['latitude'], 
    size=8, 
    color='red', 
    alpha=0.5,
    legend_label = 'Large Incidents')

c13.title.text = "Gun Incidents Per 1000 People: 2013"
c13.title.align = "left"
c13.title.text_font_size = "25px"
c13.legend.location = 'top_left'

### Gun Violence in 2021 ###

## Choropleth Map
gv21c = gv21.groupby('state')
state_group21 = gv21c.describe()

pop_2021 = pd.Series.tolist(pop_df_sorted['Pop2021'].astype(float))
occurence_2021 = pd.Series.tolist(state_group21['incident_id','count'])

# Loop to calculate per capita
pc21 = dict()
for i in range(len(state_group21)):
    pc21[i] = occurence_2021[i] / (pop_2021[i] / 1000) * 100 # Out of every 1000 people
per_capita21 = pd.Series(pc21)

source_c21 = dict(x = state_xs, 
                y = state_ys, 
                percapita21 = per_capita21, 
                names = state_names)

c21 = figure( 
    tools=TOOLS, 
    x_axis_location=None, 
    y_axis_location=None,
    tooltips=[("Name", "@names"), ("per capita", "@percapita21")],
    plot_width=2000, 
    plot_height=700,
    background_fill_color="#333344",
    toolbar_location="left")

c21.grid.grid_line_color = None
c21.hover.point_policy = "follow_mouse"

c21.patches(
    'x', 
    'y', 
    source=source_c21,
    fill_color={'field': 'percapita21', 'transform': color_mapper},
    fill_alpha=0.7, 
    line_color="white", 
    line_width=0.5)

color_bar = ColorBar(
    color_mapper=color_mapper,
    location="bottom_left", orientation="horizontal",
    title="Incedents per 1000 Individules",
    title_text_font_size="16px", title_text_font_style="bold",
    title_text_color="lightgrey", major_label_text_color="lightgrey",
    background_fill_alpha=0.0)
c21.add_layout(color_bar)

c21.circle(
    x = gv21_cleaned['longitude'],
    y = gv21_cleaned['latitude'], 
    size=8, 
    color='red', 
    alpha=0.5,
    legend_label = 'Large Incidents')

c21.title.text = "Gun Incidents Per 1000 People: 2021"
c21.title.align = "left"
c21.title.text_font_size = "25px"
c21.legend.location = 'top_left'


# Streamlit Tools

options = st.selectbox(
    'What data would you like to see?',
    ['Per Capita Gun Violence 2013: Choropleth', 
     'Per Capita Gun Violence 2021: Choropleth', 
     'Gun Violence 2013-2021: Scatter'])

if (options == 'Per Capita Gun Violence 2013: Choropleth'):
    st.bokeh_chart(c13)
elif (options == 'Per Capita Gun Violence 2021: Choropleth'):
    st.bokeh_chart(c21)
elif (options == 'Gun Violence 2013-2021: Scatter'):
    st.bokeh_chart(s13)
    st.bar_chart(data = gv_bar,x = 'state', y = ['n_provision_2021','n_provision'])





