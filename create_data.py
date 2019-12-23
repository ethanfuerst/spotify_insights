#%%
import pandas as pd
import numpy as np
import os
import glob
import json
import datetime
import time
from tzlocal import get_localzone

#%%
'''
Library
    Tracks
    Albums
    Subscriptions
'''
with open('MyData/YourLibrary.json') as data:
    library = json.loads(data.read())
    for i in library:
        if i == 'tracks':
            tracks = pd.DataFrame(library['tracks'])
        elif i == 'albums':
            albums = pd.DataFrame(library['albums'])
        elif i == 'shows':
            subscriptions = pd.DataFrame(library['shows'])
        else:
            pass

#%%
'''
Streams
'''
# List of files containing streaming history
streaming_hist = glob.glob('MyData/StreamingHistory*.json')

# Make a df called streams with all the streaming history
streams = pd.DataFrame()
for i in streaming_hist:
    i_df = pd.read_json(i)
    streams = pd.concat([i_df, streams])

# Sort the df by endTime
streams.sort_values('endTime', inplace=True)
streams.reset_index(drop=True, inplace=True)

# Removing all rows where 0 msPlayed is recorded
streams = streams[streams['msPlayed'] != 0].copy()

# Get local timezone of where script is run
local_tz = str(get_localzone())
# Convert endTime to local timezone
streams['endTime'] = pd.to_datetime(streams["endTime"]).dt.tz_localize('Europe/Stockholm').dt.tz_convert(local_tz)
# Drop timezone 
streams['endTime'] = streams['endTime'].dt.tz_localize(None)

# Convert msPlayed to a Timedelta series called playTime
streams['playTime'] = pd.TimedeltaIndex(streams['msPlayed'], unit='ms')
# Get startTime from endTime - playTime
streams['startTime'] = streams['endTime'] - streams['playTime']

# Create inLibrary column - is true if tracks are saved in library and false if not saved in library
streams['inLibrary'] = (streams['artistName'].isin(tracks['artist']) & streams['trackName'].isin(tracks['track'])).astype(bool)

# Create an audioType column
streams['audioType'] = np.where(streams['artistName'].isin(subscriptions['name']), 'Podcast', "Music")

# Create a date column that I can group by
streams['date'] = streams['startTime'].dt.date

def as_day(i):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[i]

streams['weekday'] = streams['startTime'].dt.dayofweek
streams['weekday'] = streams['weekday'].apply(as_day)

# Reorder columns to look nicer
streams = streams[['date', 'weekday', 'artistName', 'trackName', 'msPlayed', 'playTime', 'startTime', 'endTime', 'inLibrary', 'audioType']]

#%%
# Create a groupby dataframe used for totals
streams_tracks = streams.groupby(['artistName','trackName', 'audioType']).sum().copy()
streams_tracks = pd.DataFrame(streams_tracks.to_records())
streams_tracks['inLibrary'] = streams_tracks['inLibrary'].astype(bool)

# This dataframe shows the sum of listening for each day
streams_days = streams.groupby(['date', 'audioType']).sum().copy()
streams_days.drop('inLibrary', axis=1, inplace=True)
streams_days = streams_days.unstack(level=1)
streams_days = streams_days.fillna(0).astype(int)
streams_days.columns = streams_days.columns.get_level_values(1)
streams_days = pd.DataFrame(streams_days.to_records())
streams_days['weekday'] = pd.to_datetime(streams_days['date']).dt.dayofweek.apply(as_day)

# This dataframe shows the total amount of time per track each day
streams_tracks_days = streams.groupby(['date', 'artistName', 'trackName', 'audioType']).sum().copy()
streams_tracks_days.sort_values(['date', 'artistName', 'msPlayed'], inplace=True)
streams_tracks_days = pd.DataFrame(streams_tracks_days.to_records())
streams_tracks_days.drop('inLibrary', axis=1, inplace=True)
streams_tracks_days['weekday'] = pd.to_datetime(streams_tracks_days['date']).dt.dayofweek.apply(as_day)

# This dataframe shows the total amount of time per artist each day
streams_artists_days = streams_tracks_days.groupby(['date', 'artistName', 'audioType']).sum().copy()
streams_artists_days.sort_values(['date', 'msPlayed'], inplace=True)
streams_artists_days = pd.DataFrame(streams_artists_days.to_records())
streams_artists_days['weekday'] = pd.to_datetime(streams_artists_days['date']).dt.dayofweek.apply(as_day)

# Export to .csvs to work in Tableau
streams.to_csv('streams.csv', index=False)
streams_tracks.to_csv('streams_tracks.csv')
streams_days.to_csv('streams_days.csv')
streams_tracks_days.to_csv('streams_tracks_days.csv')
streams_artists_days.to_csv('streams_artists_days.csv')

#%%
'''
Playlists
'''
# playlist_list = glob.glob('MyData/Playlist*.json')

# playlists = pd.DataFrame()
# for i in playlist_list:
#     i_df = pd.read_json(i)
#     playlists = pd.concat([i_df, playlists])

# caps out at 67792 lines or 1799045 characters
# with open('MyData/Playlist1.json') as data:
#     playlists = json.loads(data.read())

# df = pd.read_json('MyData/Playlist1.json')
# for i in df['playlists']:
#     print(i['name'])
