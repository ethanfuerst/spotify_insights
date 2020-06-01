# %%
import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import math
import plotly
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import n_colors
import plotly.express as px
import plotly.figure_factory as ff
from tzlocal import get_localzone
from create_data import get_stream_data
df = get_stream_data()

def day_label(i):
    '''
    Used for y axis, will return x day/s when given an int
    Returns ' ' for 0
    '''
    if i == 0:
        return ' '
    elif i != 1:
        return str(i) + ' days'
    else:
        return '1 day'

def time_label(x):
    '''
    Takes ms and converts to string with days, hours mins
    '''
    if x >= 86400000 * 2:
        return str(datetime.timedelta(seconds=x//1000).days) + ' days, '                 + str(datetime.timedelta(seconds=x//1000).seconds//3600) + ' hours and '                 + str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'
    elif x >= 86400000:
        return str(datetime.timedelta(seconds=x//1000).days) + ' day, '                 + str(datetime.timedelta(seconds=x//1000).seconds//3600) + ' hours and '                 + str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'
    else:
        return str(datetime.timedelta(seconds=x//1000).seconds//3600) + ' hours and '                 + str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'


# %%
# Bar chart grouped by year and month
# Stacked by audio_type
# Change colors
print(df.columns)
df_ = df.groupby(by=['month', 'audio_kind']).sum().reset_index().copy()

df_ = pd.merge(df_[df_['audio_kind'] == 'Podcast'], df_[df_['audio_kind'] == 'Music'], on='month', how='outer')
df_ = df_[['month', 'audio_kind_x', 'ms_played_x', 'audio_kind_y', 'ms_played_y']].copy()
df_['total'] = df_['ms_played_x'] + df_['ms_played_y']
df_['month_order'] = df_['month'].apply(lambda x: datetime.datetime.strptime(x, "%b '%y"))
df_['month'] = df_['month_order'].dt.strftime("%B '%y")
df_['days'] = df_['total']/86400000
df_['ms_in_month'] = pd.to_datetime(df_['month_order'].dt.date + relativedelta(months=1) - datetime.timedelta(days=1)).dt.day * 86400000
df_['x_pct_of_month'] = round(round(df_['ms_played_x']/df_['ms_in_month'], 4) * 100, 2)
df_['y_pct_of_month'] = round(round(df_['ms_played_y']/df_['ms_in_month'], 4) * 100, 2)

df_.sort_values('month_order', inplace=True)
df_ = df_.fillna(0).copy()

df_['ms_played_x_format'] = df_['ms_played_x'].apply(time_label)
df_['ms_played_y_format'] = df_['ms_played_y'].apply(time_label)

fig = go.Figure(data=[go.Bar(
                            x=df_['month_order'],
                            y=df_['ms_played_x'],
                            name='Podcasts',
                            hovertemplate=df_['month'] +'</b>'+
                            '<br>' + df_['ms_played_x_format'] + 
                            '<br>' + df_['x_pct_of_month'].astype(str) + '% of the month'
                            ),
                        go.Bar(
                            x=df_['month_order'],
                            y=df_['ms_played_y'],
                            name='Music',
                            hovertemplate=df_['month'] +'</b>'+
                            '<br>' + df_['ms_played_y_format'] + 
                            '<br>' + df_['y_pct_of_month'].astype(str) + '% of the month'
                            )]
                )

fig.update_layout(
    plot_bgcolor='#cccccc',
    barmode='stack',
    title=dict(
        text='Time listened to Spotify by month',
        font=dict(
            size=24,
            color='#000000'
        ),
        x=.5
    ),
    xaxis=dict(
        title='Month',
        range=[df_['month_order'].min() - datetime.timedelta(days=32), df_['month_order'].max() + datetime.timedelta(days=32)]
    ),
    yaxis=dict(
        title='Time',
        range=[0, math.ceil(df_['days'].max()) * 86400000],
        tickvals=[i for i in range(0, math.ceil(df_['days'].max() * 86400000), 86400000)],
        ticktext=[day_label(i) for i in range(0, math.ceil(df_['days'].max()))]
    ),
    width=900,
    height=600
)
fig.show()


# %%
# Top 10 artists/songs/podcasts in a year, season, month, week


# %%
# Listening breakdown by hour of day
# Radial bar stacked bar chart

