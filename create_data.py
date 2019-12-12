#%%
import pandas as pd
import numpy as np
import os
import glob
import json
import datetime

#%%
'''
Streams
'''
streaming_hist = glob.glob('MyData/StreamingHistory*.json')

streams = pd.DataFrame()
for i in streaming_hist:
    i_df = pd.read_json(i)
    streams = pd.concat([i_df, streams])

streams["endTime"] = pd.to_datetime(streams["endTime"])
streams.sort_values('endTime', inplace=True)
streams.reset_index(drop=True, inplace=True)


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


'''
Playlists
'''
# playlist_list = glob.glob('MyData/Playlist*.json')

# playlists = pd.DataFrame()
# for i in playlist_list:
#     i_df = pd.read_json(i)
#     playlists = pd.concat([i_df, playlists])

# caps out at 67792 lines or 1799045 characters
with open('MyData/Playlist1.json') as data:
    playlists = json.loads(data.read())

df = pd.read_json('MyData/Playlist1.json')
for i in df['playlists']:
    print(i['name'])
#%%
# Put the data in .csvs


