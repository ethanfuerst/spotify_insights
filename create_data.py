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
Streams
'''
streaming_hist = glob.glob('MyData/StreamingHistory*.json')

streams = pd.DataFrame()
for i in streaming_hist:
    i_df = pd.read_json(i)
    streams = pd.concat([i_df, streams])

# Sort the dataframe by endTime
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
#%%
# Put the data in .csvs


