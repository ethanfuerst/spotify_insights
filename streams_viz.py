# %%
import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import math
import calendar
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
        return str(datetime.timedelta(seconds=x//1000).days) + ' days, ' \
             + str(datetime.timedelta(seconds=x//1000).seconds//3600) + ' hours and ' \
                  + str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'
    elif x >= 86400000:
        return str(datetime.timedelta(seconds=x//1000).days) + ' day, ' \
             + str(datetime.timedelta(seconds=x//1000).seconds//3600) + ' hours and ' \
                  + str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'
    elif x >= 3600000:
        return str(datetime.timedelta(seconds=x//1000).seconds//3600) + ' hours and ' \
             + str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'
    else:
        return str((datetime.timedelta(seconds=x//1000).seconds//60)%60) + ' minutes'

# %%
# Bar chart grouped by year and month
# Stacked by audio_type
# Change colors

def monthly_hist(df):
    '''
    Shows podcasts/music grouped by month and year
    '''
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

    return fig

#%% 
# Podcast breakdown
# Top 5 podcasts
def pod_list(df):
    '''
    Shows list of podcasts as table
    '''
    pod = df[df['audio_kind'] == 'Podcast'].copy()
    top_pod = pod.groupby(['show']).sum().reset_index().sort_values('ms_played', ascending=False).reset_index(drop=True).copy()
    # Podcasts must have 10 or more total minutes of listening to be counted
    top_pod = top_pod[top_pod['ms_played'] >= 600000].copy()
    top_pod['tot_format'] = top_pod['ms_played'].apply(time_label)
    top_pod['rank'] = top_pod.index + 1
    top_pod = top_pod[['show', 'ms_played', 'tot_format', 'rank']].copy()

    pod_ep_count = pod.groupby(['show','episode_name']).count().reset_index().sort_values('username', ascending=False)[['show', 'username']].groupby('show').sum().reset_index().sort_values('username', ascending=False).copy()
    pod_ep_count.columns = ['show', 'ep_count']

    merged = pd.merge(top_pod, pod_ep_count, on='show').copy()

    med_ep = pod.groupby(['show', 'episode_name']).sum().reset_index()[['show', 'ms_played']].groupby('show').median().reset_index().copy()

    merged = pd.merge(merged, med_ep, on='show', suffixes=('_tot', '_ep_med')).copy()
    merged['med_ep_format'] = merged['ms_played_ep_med'].apply(time_label)

    alt_greys = ['#cccccc', '#e4e4e4'] * len(df)
    fig = go.Figure(data=[go.Table(
        header=dict(values=['Rank', 'Podcast', 'Total time listened', '# episodes listened to', 'Median time per listen'],
                    fill_color='#5C7DAA',
                    font_color='white',
                    align='left'),
        cells=dict(values=[merged['rank'], merged['show'], merged['tot_format'], merged['ep_count'], merged['med_ep_format']],
                    fill_color=[alt_greys[:len(top_pod)]]*3,
                    font_color='black',
                    align='left'))])

    fig.update_layout(
        title=dict(
            text='My podcast listening history on Spotify',
            font=dict(
                size=22,
                color='#000000'
            ),
            x=.5
        ),
        width=700,
        height=1000,
        annotations = [dict(
                            font=dict(
                                size=16,
                                color='black'
                                ),
                            x=.5, y=1.05,
                            showarrow=False,
                            text ='from {0} to {1}'.format(df['ts_tz'].min().strftime('%B %d, %Y'), df['ts_tz'].max().strftime('%B %d, %Y')))]
    )
    fig.show()

    return fig

pod_list(df)

# %%
# Top 10 artists/songs/podcasts in a year, season, month, week


# %%
# Listening breakdown by hour of day
# Radial bar stacked bar chart
# Option to group by year



#%%
# Listening breakdown by weekday
# 

#%%
# df_ = df.groupby('weekday_#').mean().reset_index()[['weekday_#', 'ms_played']].copy()
# df_['weekday'] = df_['weekday_#'].apply(lambda x: list(calendar.day_name)[x])
# df_['theta'] = (df_['weekday_#'] + 1) * (360/7)

# fig = go.Figure(
#     go.Scatterpolar(
#         r = df_['ms_played'],
#         theta = df_['theta'],
#         mode = 'lines',
#         name = 'Average listening by weekday'
#     )
# )

# fig.show()

# %%
# When you first listened to podcast
# Limit podcasts by min playing time/freq

#%%
# When you first started listening to artist
# Limit artists by min playing time/freq

#%%
# Given date range

def insights(df):
    pod = df[df['audio_kind'] == 'Podcast'].copy()
    mus = df[df['audio_kind'] == 'Music'].copy()
    span_sec = (df['ts_tz'].max() - df['ts_tz'].min()).total_seconds()
    span_ms = span_sec * 1000

    monthly_hist(df)

    print('From {0} to {1}:'.format(df['ts_tz'].min().strftime('%B %d, %Y %-I:%M:%S %p'), df['ts_tz'].max().strftime('%B %d, %Y %-I:%M:%S %p')))
    print('You listened to {} of Spotify'.format(time_label(int(df['ms_played'].sum()))))
    print('{0}% of that was spent listening to music ({1})'.format(round(int(mus['ms_played'].sum())/int(df['ms_played'].sum()) * 100,2), \
                                                                    time_label(int(mus['ms_played'].sum()))))
    print('{0}% of that was spent listening to podcasts ({1})\n'.format(round(int(pod['ms_played'].sum())/int(df['ms_played'].sum()) * 100,2), \
                                                                    time_label(int(pod['ms_played'].sum()))))

    print('Over this time span, {}% of your time was spent listening to Spotify'.format(round((df['ms_played'].sum() / span_ms) * 100, 2)))
    print("That's {0}% music and {1}% podcasts".format(round((mus['ms_played'].sum() / span_ms) * 100, 2), round((pod['ms_played'].sum() / span_ms) * 100, 2)))
    
    print('Music\n')
    

    print('Podcasts')
    pod_list(df)

insights(df)

# %%


