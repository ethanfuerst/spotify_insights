#%%
import pandas as pd
pd.set_option('display.max_columns', None)
import numpy as np
import glob
import json
import datetime
import time
from tzlocal import get_localzone

#%%
def get_stream_data():
    '''
    Pulls data from MyData/EndSong.json and returns a df of the data
    '''
    df = pd.read_json('MyData/EndSong.json', lines=True)
    df = df[['ts', 'username', 'ms_played',  'master_metadata_track_name', 'master_metadata_album_artist_name', 'master_metadata_album_album_name',
    'reason_start', 'reason_end', 'shuffle', 'offline', 'incognito_mode', 'episode_name', 'episode_show_name']].copy()

    local_tz = str(get_localzone())
    df['ts_utc'] = pd.to_datetime(df['ts'])
    df['ts_tz'] = df['ts_utc'].dt.tz_convert(local_tz)
    df = df.sort_values('ts_utc').reset_index(drop=True).copy()
    df = df.fillna('').copy()

    df = df.rename(columns=dict(
            master_metadata_track_name='track',
            master_metadata_album_artist_name='artist',
            master_metadata_album_album_name='album',
            episode_show_name='show'
        )).copy()

    # Removes all entries with null tracka and episodes - counts for 1.5 percent of ms_played sum
    # Not sure what these records are
    df = df[(df['track'] != '') | (df['episode_name'] != '')].copy()

    # make audio type column - podcast or music
    def audio_kind(row):
        if row['track'] == '' and row['artist'] == '' and row['album'] == '':
            return 'Podcast'
        elif  row['episode_name'] == '' and row['show'] == '':
            return 'Music'
        else:
            return 'Other'

    df['audio_kind'] = df.apply(lambda row: audio_kind(row), axis=1)

    # make time played column 0-30 (skipped) or 30+ (played) if music and other for podcast
    def skipped(row):
        if row['ms_played'] < 30000:
            return True
        else:
            return False

    df['skipped'] = df.apply(lambda row: skipped(row), axis=1)

    # Create season column
    def season(x):
        if x > 2 and x < 6:
            return 'Spring'
        elif x > 5 and x < 9:
            return 'Summer'
        elif x > 8 and x < 12:
            return 'Fall'
        else:
            return 'Winter'

    df['season'] = df['ts_tz'].dt.month.apply(season)

    df = df[['ts_utc', 'ts_tz'] + list(df.columns[1:-5]) + list(df.columns[-3:])].copy()
    return df

#%%
if __name__ == '__main__':
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

    # List of files containing streaming history
    streaming_hist = glob.glob('MyData/StreamingHistory*.json')

    # Make a df called streams with all the streaming history
    streams = pd.DataFrame()
    for i in streaming_hist:
        i_df = pd.read_json(i)
        streams = pd.concat([i_df, streams])

    # Sort the df by endTime
    # streams.sort_values('endTime', inplace=True)
    # streams.reset_index(drop=True, inplace=True)

    # Removing all rows where 0 msPlayed is recorded
    # streams = streams[streams['msPlayed'] != 0].copy()

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
