#!/usr/bin/env python
#
#
from os.path import dirname, join
import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, RangeSlider, Select, TextInput
from bokeh.io import curdoc

# import rankings
data_fn = '../data/drucker_rankings_2017.csv.gz'
companies = pd.read_csv(data_fn)

axis_list = companies.columns.drop('Company')

sorted_comp = sorted(companies['Company'].tolist(), key=lambda s: s.lower())

desc = Div(text=open(join(dirname(__file__), "description.html")).read(),
           width=800)

# Create Input controls
range_sliders = []
for col in companies.columns.drop('Company'):
    range_sliders.append(RangeSlider(start=np.floor(companies[col].min()),
                                   end=np.ceil(companies[col].max()),
                                   value=(np.floor(companies[col].min()),
                                          np.ceil(companies[col].max())),
                                   step=1, title=col))
focus = Select(title="Company", value="Weyerhaeuser",
               options=sorted_comp)
x_axis = Select(title="X Axis", options=sorted(axis_list),
                value="Ranking")
y_axis = Select(title="Y Axis", options=sorted(axis_list),
                value="Customer Satisfaction")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], company=[], satisfaction=[],
                                    engagement=[], innovation=[],
                                    responsibility=[], strength=[],
                                    effectiveness=[], color=[], ranking=[]))

hover = HoverTool(tooltips=[
    ("Company", "@company"),
    ("Ranking", "@ranking"),
    ("Effectiveness", "@effectiveness")
])

p = figure(plot_height=600, plot_width=700, title="",
           toolbar_location=None, tools=[hover])
p.circle(x="x", y="y", source=source, size=7, line_color=None, color='color')

def select_companies():
    # Filter by ranges
    selected = companies
    selected['color'] = 'grey'
    for col,slider in zip(axis_list,range_sliders):
        min_val, max_val = slider.value
        selected = selected[(selected[col] >= min_val) &
                            (selected[col] < max_val)]
    selected.loc[companies['Company'] == focus.value, 'color'] = 'green'
    return selected

def update():
    df = select_companies()
    x_name = x_axis.value
    y_name = y_axis.value
    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d companies selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        ranking=df['Ranking'],
        company=df['Company'],
        satisfaction=df['Customer Satisfaction'],
        engagement=df['Employee Engagement and Development'],
        innovation=df['Innovation'],
        responsibility=df['Social Responsibility'],
        strength=df['Financial Strength'],
        effectiveness=df['EFFECTIVENESS'],
    )

controls = range_sliders
controls.extend([focus,x_axis,y_axis])
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Drucker Company Rankings"
