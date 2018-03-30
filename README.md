MyAnimeList.bundle
==================

### Description:
[Plex Media Server (PMS)](https://www.plex.tv/) Metadata Agent for MyAnimelist.net

This Metadata Agent loads the metadata into your Plex Media Server from the Anime website [MyAnimeList.net](https://myanimelist.net/). The Agent will request all data from a standalone installation of the [atarashii API](https://bitbucket.org/animeneko/atarashii-api)

### Features:
Those features will only be added if the corresponding Data is available

* Search for the Title of the Anime (taken from the scanners file name)
* Request the detailed data of the Anime found while searching for the title (Plex will use any title similarity of 80% and above)
* The entry in your library will be filled with Anime ID, Title, Summary, User Rating, Air Date, Content Rating, Cover image, the average duration of an episode, genres, producers
* The Episodes listed in your library will be filled with the Episode Title and the Date it aired (if there is no Title or Date available a Default value will be used which is for the Title "Episode: #" and for the Date it will use the current date at which the agent tried to add the metadata)

### Scanners:
Anime rely normally on the absolute numbering format and I recommend the following Scanners to use them for adding Anime
* [Better ABsolute Scanner (BABS)](https://forums.plex.tv/discussion/31081/better-absolute-scanner-babs/p1)
* [Absolute Series Scanner](https://github.com/ZeroQI/Absolute-Series-Scanner)

### What this Agent won't do:
This agent won't pull any data from somewhere else (unlike the previous versions).
With the shift from my own API that provides the data to another API I have no influence on what the API provides anymore but gain a fully working API with a lot more functionality and "stableness". That means there won't be any Background or additional Cover images from TheTVDB.com that my own API provided in a previous version of the Agent.

The problem with this was that there was and is not an easy way to match something confidently between MyAnimeList.net and TheTVDB.com if I would want that I would need a mapping between those two websites which is additional work (maybe in a future update).

### Support:

For all support related or general questions please use the [thread in the official plex forums](https://forums.plex.tv/discussion/105054/release-myanimelist-net-metadata-agent/p1)
For any issues like bugs, unintended behaviour please create a new Issue on the [github issue tracker](https://github.com/Fribb/MyAnimeList.bundle/issues)
For development stages, release information, download link or anything else you can visit my [dev Blog here](https://coding.fribbtastic.net/projects/myanimelistagent/)
