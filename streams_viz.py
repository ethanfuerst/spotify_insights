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
from plotly.subplots import make_subplots
from tzlocal import get_localzone
from humanfriendly import format_timespan
from create_data import get_stream_data
df = get_stream_data()

pod = df[df['audio_kind'] == 'Podcast'].copy()
mus = df[df['audio_kind'] == 'Music'].copy()

span_sec = (df['ts_tz'].max() - df['ts_tz'].min()).total_seconds()
span_ms = span_sec * 1000

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
    seconds = (datetime.timedelta(seconds=x//1000)).total_seconds()
    return format_timespan(seconds)

# %%
# - Bar chart grouped by year and month
# - Stacked by audio_type
# todo Change colors

# Shows podcasts/music grouped by month and year
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


#%% 
# - Podcast breakdown
# - Top 5 podcasts
# - Shows list of podcasts as table
pod = df[df['audio_kind'] == 'Podcast'].copy()
top_pod = pod.groupby(['show']).sum().reset_index().sort_values('ms_played', ascending=False).reset_index(drop=True).copy()
# - Podcasts must have 10 or more total minutes of listening to be counted
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


#%%
# - adds text to final html 

def sum_str(df):
    pod = df[df['audio_kind'] == 'Podcast'].copy()
    mus = df[df['audio_kind'] == 'Music'].copy()
    span_sec = (df['ts_tz'].max() - df['ts_tz'].min()).total_seconds()
    span_ms = span_sec * 1000

    final_str = ''

    final_str += 'From {0} to {1}:\n'.format(df['ts_tz'].min().strftime('%B %d, %Y %-I:%M:%S %p'), df['ts_tz'].max().strftime('%B %d, %Y %-I:%M:%S %p'))
    final_str += 'You listened to {} of Spotify.\n'.format(time_label(int(df['ms_played'].sum())))
    final_str +=  '{0}% of that was spent listening to music. ({1})\n'.format(round(int(mus['ms_played'].sum())/int(df['ms_played'].sum()) * 100,2), \
                                                                    time_label(int(mus['ms_played'].sum())))
    final_str += '{0}% of that was spent listening to podcasts. ({1})\n\n'.format(round(int(pod['ms_played'].sum())/int(df['ms_played'].sum()) * 100,2), \
                                                                    time_label(int(pod['ms_played'].sum())))
    final_str += 'Over this time span, {}% of your time was spent listening to Spotify.\n'.format(round((df['ms_played'].sum() / span_ms) * 100, 2))
    final_str += "That's {0}% music and {1}% podcasts.\n".format(round((mus['ms_played'].sum() / span_ms) * 100, 2), round((pod['ms_played'].sum() / span_ms) * 100, 2))

    return final_str

print(sum_str(df))

# %%
# todo
# - Top 10 artists/songs/podcasts in by year, season, month, week

# %%
# todo
# - Listening breakdown by hour of day
# - include difference for work hours
# - Radial bar stacked bar chart
# - Option to group by year
# 

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

#%%
# todo
# - songs most listened to on working hours/weekend
# - use 1m, 6m, ytd rangeselector and rangeslider

#%%
# todo
# - most popular artist by time of day
# - use 1m, 6m, ytd rangeselector and rangeslider

#%%
# todo
# - bar chart of top 50 songs
t_songs = mus.groupby(['artist', 'track']).sum().sort_values('ms_played', ascending=False).reset_index()[['artist', 'track', 'ms_played']]
t_songs['t_format'] = t_songs['ms_played'].apply(time_label)


#%%
# todo
# - Listening breakdown by weekday

# %%
# todo
# - When you first listened to podcast
# - Limit podcasts by min playing time/freq
# ? maybe make in to a table? is there a way to filter with long dropdown?

#%%
# - When you first started listening to artist
# - Limit artists by min playing time/freq
# - Limit to 2 mins or more of playing
# - filer by ms played and first listen
f_art = mus.groupby(['artist']).min().reset_index()[['artist', 'ts_utc']]
art_list = mus.groupby(['artist']).sum().reset_index()[['artist', 'ms_played']]
art_list = art_list[art_list['ms_played'] >= 60000 * 2].copy()
f_art = pd.merge(art_list, f_art, on='artist', how='inner', suffixes=('_first', ''))
f_art = pd.merge(f_art, mus, on=['ts_utc', 'artist'], how='inner', suffixes=('', '_fplay'))[['artist', 'ms_played', 'ts_utc', 'track', 'album', 'week', 'month']]
f_art['date'] = f_art['ts_utc'].dt.strftime('%d %b %Y')
f_art['tot played'] = f_art['ms_played'].apply(time_label)
# - First 50 artists
f_50 = f_art.sort_values('ts_utc', ascending=True).head(50).reset_index(drop=True)
f_50['rank'] = f_50.index + 1
f_50['track_format'] = 'Track: ' + f_50['track'] + '<br>Album: ' + f_50['album']
# - Top 50 artists
t_50 = f_art.sort_values('ms_played', ascending=False).head(50).reset_index(drop=True)
t_50['rank'] = t_50.index + 1
t_50['track_format'] = 'Track: ' + t_50['track'] + '<br>Album: ' + t_50['album']

alt_greys = ['#cccccc', '#e4e4e4'] * 51

fig = make_subplots(rows=2, cols=1, 
                    specs=[[{"type": "table"}],
                            [{"type": "table"}]],
                    vertical_spacing=0.085)

fig.append_trace(go.Table(
    header=dict(values=['Rank of first listen', 'Artist','First Track','First listen',
                        'Total time listened to artist'],
                fill_color='#5C7DAA',
                font_color='white',
                align='left'),
    cells=dict(values=[f_50['rank'], f_50['artist'], f_50['track_format'],f_50['date'],
                        f_50['tot played']],
                fill_color=[alt_greys[:len(f_50)]]*3,
                font_color='black',
                align='left'),
    columnwidth=[125,250,550,150,300]
                ), row=1, col=1)

fig.append_trace(go.Table(
    header=dict(values=['Rank by time listened', 'Artist','First Track','First listen',
                        'Total time listened to artist'],
                fill_color='#5C7DAA',
                font_color='white',
                align='left'),
    cells=dict(values=[t_50['rank'], t_50['artist'], t_50['track_format'],t_50['date'],
                        t_50['tot played']],
                fill_color=[alt_greys[:len(t_50)]]*3,
                font_color='black',
                align='left'),
    columnwidth=[125,250,550,150,300]
                ), row=2, col=1)

fig.update_layout(
    title=dict(
        text='When I discovered artists on Spotify',
        font=dict(
            size=22,
            color='#000000'
        ),
        x=.5
    ),
    width=1000,
    height=1000,
    annotations = [dict(
                        font=dict(
                            size=16,
                            color='black'
                            ),
                        x=.5, y=1.05,
                        showarrow=False,
                        text ='Sorted by first listen and total time listened')]
)

fig.show()

#%%
# todo
# - History of listening to a song
# - Limit songs by min playing time/freq
# ? maybe make in to a table? is there a way to filter with long dropdown?

#%%
# todo
# - Top 100 or 50 artists of all time
# - show top 3 or 5 songs by time and plays
# - grouped together so each row is artist, total time,  song1 - time \n song2 - time \n song3 - time
# todo change column width, not all the same. artist small, last one large

# - num of top songs to include for each artist
num_top = 5
# - num of top artists to include
num_artists = 100

# - sort df by top artists
top_artists = mus[mus != 'Various Artists'].groupby(by=['artist']).sum().reset_index()[['artist', 'ms_played']].sort_values(by='ms_played', ascending=False).head(num_artists).reset_index(drop=True).rename(columns={'ms_played':'tot_lstn'})
# - group mus by artist and track
top_3_from_t_a = mus[(mus['artist'].isin(top_artists['artist'])) & (mus['ms_played'] > 10)].groupby(['artist', 'track']).sum().reset_index()[['artist', 'track', 'ms_played']].sort_values(by=['artist', 'ms_played'], ascending=False).groupby(['artist']).head(num_top)
# - get playcounts from artists and tracks
p_counts = mus[(mus['artist'].isin(top_artists['artist'])) & (mus['ms_played'] > 10)].groupby(['artist', 'track']).count().reset_index()[['artist', 'track', 'username']]
df_ = pd.merge(top_3_from_t_a, p_counts, how='inner', on=['artist', 'track']).rename(columns={'username':'count'})
df_ = pd.merge(df_, top_artists, how='outer', on='artist')
df_['t_format'] = df_['ms_played'].apply(time_label)
df_['count'] = df_['count'].astype(str) + ' plays'
grouped = df_[['track', 'count', 't_format']].agg(' - '.join,1).groupby(df_.artist).agg('<br>'.join).to_frame('track_format').reset_index().copy()
df_['tot_format'] = df_['tot_lstn'].apply(time_label)
df_ = df_[['artist', 'tot_lstn', 'tot_format']].drop_duplicates().sort_values('tot_lstn', ascending=False).reset_index(drop=True)

df_ = pd.merge(df_, grouped, on='artist').sort_values(['tot_lstn'], ascending=False).reset_index(drop=True)
# - Sort by total listening time and then induvidual song
df_['artist'] = (df_.index + 1).astype(str) + '. ' + df_['artist']
# - index+1. artist, track_format, tot_lstn, tot_format
df_ = df_[['artist', 'tot_format', 'track_format']].copy()


fig = go.Figure(data=[go.Table(
    header=dict(values=['Artist', 'Total time listened', 'Top {} songs by time listened'.format(num_top)],
                fill_color='#5C7DAA',
                font_color='white',
                align='left'),
    cells=dict(values=[df_['artist'], df_['tot_format'], df_['track_format']],
                font_color='black',
                align='left'))])

fig.update_layout(
    title=dict(
        text='Top {} artists'.format(num_artists),
        font=dict(
            size=24,
            color='#000000'
        ),
        x=.5
    ),
    width=1000,
    height=700
)

fig.show()

# - Bar chart with top songs of all time
# - df_.sort_values('ms_played', ascending=False).head(50).reset_index(drop=True)[['artist', 'track', 't_format']]

#%%
# todo
# - line chart for each day
# - lines for both podcasts and music
# - use timestamp slider on plotly

#%%
# todo
# - Top albums and songs from albums


#%%
# todo
# - scatterplot of some sort
# - total time song played vs count?


#%%
# todo 
# - music by release year
# * need spotify API for this


#%%
# - Single artist analysis
# todo
# - add counts
# - maybe list on a table and filter by artist?

mus = mus.replace('The Unauthorized Bash Brothers Experience', 'The Lonely Island').copy()
li = mus[mus['artist'] == 'The Lonely Island'].groupby('track').sum().reset_index().sort_values('ms_played')[['track', 'ms_played']]
li['time played'] = li['ms_played'].apply(time_label)
li = li.sort_values('ms_played', ascending=False)[['track', 'time played']].reset_index(drop=True)

trav = mus[mus['artist'] == 'Travis Scott'].groupby('track').sum().reset_index()[['track', 'ms_played']]
trav['time played'] = trav['ms_played'].apply(time_label)
trav = trav.sort_values('ms_played', ascending=False)[['track', 'time played']].reset_index(drop=True)

# %%


