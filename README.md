# spotifyinsights

My mission for this project is to visualize my Spotify data in multiple ways. I'm interested to see how long I spent listening to my top songs, and how my listening changed between each year. I'd like to do something like [this project I found](https://github.com/luka1199/geo-heatmap) where people can download their own data and visualize it with my code. I think I will use Plotly and Dash to create interactive dashboards.

## Files in this repository

__*create_data.py*__ - .py file that takes data from the MyData folder and creates dataframes. I could add the rest of my code on to here or I could figure out how to take the dataframes directly in to another file where I will create the dashboards.

__*streams.csv*__ - .csv linked to .twb

__*stream_data.twb*__ - .twb where I can plan out visualizations

__*.gitignore*__ - shows github what files to ignore when I commit my changes.

## TODO

- [x] add weekday column to streams
- [ ] learn more about [Spotify Developer API](https://developer.spotify.com/)
- [ ] plan out vizs in tableau
- [ ] learn more about Plotly and Dash and create vis
- [ ] make script to compare two diffrent users streaming data (maybe another repo)
