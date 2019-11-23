MyAnimeList.bundle
==================

## Privacy:

The Agents accesses an API that is running on my own server, the log files contain the IP-Address and API endpoint of each request, this is necessary for security reasons. Those log files are being rotated daily and those rotations will contain anonymized IP-Addresses. 

## Description:
[Plex Media Server (PMS)](https://www.plex.tv/) Metadata Agent for [MyAnimelist.net](https://myanimelist.net/)

This Metadata Agent loads the information from the Anime Website [MyAnimeList.net](https://myanimelist.net/) into your Plex Media Server Anime Library.

## Metadata Sources:
The Agent will request the following information from the various sources.

### MyAnimeList.net
The MyAnimeList.net is the main source for the information and the agent relies on a stand-alone installation of the [atarashii API](https://bitbucket.org/animeneko/atarashii-api) which provides the following information:

* ID
* Title
* Synopsis (Plex: Summary)
* Member Score (Plex: rating)
* Start Date (Plex: originally available at)
* Classification (Plex: Content Rating)
* Cover and Pictures (Plex: Posters)
* Duration (Plex: Duration)
* Genres (Plex: Genres)
* Producers (Plex: Studio) (Currently the Atarashii API does not provide the Studios available and plex does not provide a way to store Producers)
* Episode Number
* Episode Title
* Episode Air Date

### TheTVDB.com
TheTVDB.com is used to request more image information for episodic Anime. You can enable or disable this feature to pull image information as well as set the image size in the Agent Settings.

* Posters (Plex: Posters)
* Fanart (Plex: Art)
* Series (Plex: Banners)

### TheMovieDB.org
TheMovieDB is used to request more image information for Anime Movies. You can enable or disable this feature to pull image information as well as set the image size in the Agent Settings.

* Posters (Plex: Posters)
* Backdrops (Plex: Art)

### Other Sources
The Agent also accepts information from other Agents like "Local Media Assets (TV/Movie)" and "OpenSubtitles.org"

## Mapping:
To Provide a way to get additional image information from TheTVDB or TheMovieDB the Agent needs to lookup those places for the informations but the IDs don't match across those websites. Therefore a mapping is needed to map the MyAnimeList ID to the TheTVDB or TheMovieDB to each other.

See my [anime-list Project](https://github.com/Fribb/anime-lists) for more information and contribution. 

## Scanners:
Anime usually rely on the absolute episode numbering format instead of seasons. Therefore I recommend using scanners that follow this format like the following

* [Better ABsolute Scanner (BABS)](https://forums.plex.tv/discussion/31081/better-absolute-scanner-babs/p1)
* [Absolute Series Scanner](https://github.com/ZeroQI/Absolute-Series-Scanner)

Scanners need to be placed in the following Directories for a TV-Show Scanner (if those folders don't exist, create them):

* Linux: /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Scanners/Series
* Windows: %LOCALAPPDATA%\Plex Media Server\Scanners\Series

[More Information to Scanners](https://support.plex.tv/articles/200241548-scanners/)

## Installation:
Installation is straight forward, place the MyAnimeList.bundle folder into the directories (depending on your OS) listed below and restart your Plex Media Server (Note: Plex only loads the Agent on restart!).  

Directories:
* Linux: /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins/
* Windows: %LOCALAPPDATA%\Plex Media Server\Plug-ins

[More information](https://support.plex.tv/articles/201106098-how-do-i-find-the-plug-ins-folder/)

## Update:
I recommend to disable the feature to fetch image information from TheTVDB and TheMovieDB initially or the match process will be extremely long. Any mismatches will pull additional images that might be wrong.

1. Stop Plex 
2. Download the Agent and extract it into your Plug-ins folder
3. Check permissions
4. Start Plex
5. Go to the Agent Settings and disable "Fetch Images for TV-Shows/Movies"
6. match your library and fix matches that were wrongly or not matched at all
7. activate "Fetch Images for..." again
8. refresh metadata and go do something else, this will take some time

## Support:

For all support related or general questions please use the [thread in the official plex forums](https://forums.plex.tv/discussion/105054/release-myanimelist-net-metadata-agent/p1)

For any issues like bugs, unintended behaviour please create a new Issue on the [github issue tracker](https://github.com/Fribb/MyAnimeList.bundle/issues)

For development stages, release information, download link or anything else you can visit my [dev Blog here](https://coding.fribbtastic.net/projects/myanimelistagent/)

[See the Wiki Page for the FAQ](https://github.com/Fribb/MyAnimeList.bundle/wiki/Frequently-Asked-Questions)