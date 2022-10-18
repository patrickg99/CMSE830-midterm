#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
import holoviews as hv
hv.extension('bokeh')
import streamlit as st
import pandas as pd
gv13 = pd.read_csv('gv_data_2013.csv', nrows = 279, dayfirst = True)

from bokeh.sampledata import us_states
from bokeh.plotting import *
from bokeh.models import HoverTool as hover
from collections import OrderedDict
us_states = us_states.data.copy()


state_xs = [us_states[code]["lons"] for code in us_states]
state_ys = [us_states[code]["lats"] for code in us_states]

source = ColumnDataSource(data={'x': gv13['longitude'],'y': gv13['latitude'], 
                                'state':gv13['state'], 'date':gv13['date'],'number_killed':gv13['n_killed'],
                                'number_injured':gv13['n_injured'], 'state_house_district':gv13['state_house_district'],
                                'state_senate_district':gv13['state_senate_district']})


TOOLTIPS = [('State','@state'), ('Date', '@date'), ('Number killed', '@number_killed'), 
            ('Number injured', '@number_injured'), ('state house district', '@state_house_district'), 
            ('state senate district', '@state_senate_district')]

p = figure(title="Gun Violence in The United States in 2013", toolbar_location="left", plot_width=2800, plot_height=700, 
           tooltips = TOOLTIPS)

p.patches(state_xs, state_ys, fill_alpha=0.0, line_color="#884444", line_width=1.5)

p.circle(x = 'x',y = 'y', size=8, color='green', alpha=0.5, source = source)


st.bokeh_chart(p)





