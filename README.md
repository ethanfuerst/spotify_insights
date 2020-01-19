# spotify_insights

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

## More resources

[Spotify for Developers](https://developer.spotify.com/discover/) has given programmers the tools to create some really innovative projects that help people find new music, look deeper in to their favorite songs, visuualize your taste in music and more! Here are some of my favorite projects.

[__*Organize Your Music* by Spotify__](http://organizeyourmusic.playlistmachinery.com/) - Analyze the danceability, positivty, energy of a playlist and more

[__*Spotify Audio Analysis* by Hugh Rawlinson__](https://spotify-audio-analysis.glitch.me/) - See the rhythm sections of a song

[__*Musicscape* by Nadia Campo Woytuk__](https://musicscapes.herokuapp.com/) - Get a cool visualization of your current taste in music

[__*Discover Quickly* by Aliza Aufrichtig and Edward Lee__](https://discoverquickly.com/) - Wish you could listen to your whole Discover Weekly in a few minutes? You'll love this tool.
