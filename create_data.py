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

# Reorder columns to look nicer
streams = streams[['artistName', 'trackName', 'msPlayed', 'playTime', 'startTime', 'endTime']]

# Create inLibrary column - is true if tracks are saved in library and false if not saved in library
streams['inLibrary'] = (streams['artistName'].isin(tracks['artist']) & streams['trackName'].isin(tracks['track'])).astype(bool)

# Create an audioType column
streams['audioType'] = np.where(streams['artistName'].isin(subscriptions['name']), 'Podcast', "Music")

# Create a groupby dataframe used for totals
streams_sum = streams.groupby(['artistName','trackName', 'msPlayed']).sum().copy()
# streams_sum.drop(['inLibrary'], inplace=True)

streams.to_csv('streams.csv', index=False)
streams_sum.to_csv('streams_sum.csv')

# Get rid of inLibrary column
streams_sum = pd.read_csv('streams_sum.csv')
streams_sum.drop('inLibrary', axis = 1, inplace=True)
streams_sum = pd.read_csv('streams_sum.csv')

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
