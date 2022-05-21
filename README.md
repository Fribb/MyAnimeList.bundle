MyAnimeList.bundle
==================

## Description

This project is to provide a Metadata Agent for the [Plex Media Server (PMS)](https://www.plex.tv/) to add Metadata to an Anime Library retrieved from [MyAnimelist.net](https://myanimelist.net/)

## Features

The MyAnimeList Metadata Agent interacts with the [Jikan API](https://jikan.moe/) to request the necessary information that will be added to the Library.

### Privacy

The accessed Jikan API is running on my own server which will log the access with your IP and the API endpoints for each request, this is necessary for security reasons.
The Log files are being rotated daily and those rotations will only contain anonymized IP-Addresses. That means that the server only stores your IP address for a day.

### Metadata Information being used

The MyAnimeList Agent will retrieve the Metadata from the Jikan API and add them to the Library Item that should be updated.
The requested metadata are as follows:

#### Searching for a title (creating search results)

The Agent will create search results based on the metadata the search will respond with.

* ID: The MyAnimeList ID for identification and Update
* Title: The main Title of the Anime
* Aired Date: The Year at which the Show Aired
* Match Score: A calculated value between the name of the library item and the title from the search result on a 1-100 scale
* language: the language set in the search options (does not have an effect)

#### Updating a library item

After a search is being done the best search result (the first search result with the highest score) will be used to update the library item

* ID: the MyAnimeList ID
* Title: the Title of the Anime (2)
* Synopsis: The summary of the anime and what it is about
* Score: The Score Rating
* Aired date: the date on which the Anime aired the first time
* Age Rating: the content Rating
* Posters: the Main Poster used on the Website
* Duration: The duration of the Anime (episode or movie)
* Genres: the genres
* Studio: The Studio(s) that created the Anime
* Episodes:
    * ID: The ID of the episode
    * Title: The title of the Episode
    * Aired Date: The date the episode aired (1)
* Pictures: The additional pictures from MyAnimeList
* Staff:
    * ID: the ID of the character on MyAnimeList
    * Name: The name of the Voice Actor (3)
    * Role: The role that the Voice Actor voiced
    * Photo: The Photo for the Character (4)


----
**Note:**

(1) The Aired date for an Episode does not necessarily exist. If it doesn't the Agent will use the current date. Without an aired date Plex will not consider the episode for "up-next".

Some metadata can be configured through the Metadata Agent Settings:

(2) The Title used for the Library item can be set to either the main title (default), English or Japanese.

(3) The Name of the Voice Actor can be selected based on the Language English or Japanese. This will add the Voice actor for a specific language to the metadata

(4) The Photo of the Role can be set to be either the Voice actor that voiced the role or the character

For some roles, a character was voiced by multiple voice actors (for example, at different ages).
However, there is no distinction between those characters and their voice actors with, for example, a dedicated image.
So there is no way to tell which Character image would be related to a certain voice actor. Therefore, the agent will just pick the first one.

Since the Roles in Plex are shared across the whole library and not specifically for the Library item (probably to allow you to click on the Role and then have a filter for every Library item that this Actor played in) Character Photos will be overwritten by the last instance you ran a metadata refresh.
For example: Ono Daisuke voiced  Vanno Clemente in '91 Days' but also William Vangeance in 'Black Clover'.
When you Refrehs the Metadata on '91 Days' then the character image will be for Vanno Clemente, if you then refresh 'Black clover' then you get the image for William Vangeance but this will also be changed for Vanno Clemente again.

There is nothing I can do about that behaviour.

----

Additionally to the base Metadata from MyAnimeList, the MyAnimeList Metadata Agent can also retrieve additional Images from other sources TheTVDB and TheMovieDB.

To use those sources you will have to enable the "Source for additional images in" in the Metadata Agents settings (disabled by default).
Since those sources require an API Key **the user has to provide those themselves and are not provided by the Agent or myself**

The reason for this is that TheTVDB has (or will be soon) switched to a subscription Model in which you have to pay to use the API.
I think it is fair to say that if you want to use Images from TheTVDB you should also support them by subscribing.

TheMovieDB is still free to use but I decided that the user should provide their own API key for this as well.

#### How do you get an API key

you will need to have an Account for both TheTVDB and TheMovieDB

##### TheTVDB

1. Create and Login to TheTVDB and go to your Dashboard.
2. under Account -> Subscription you can subscribe to TheTVDB which will give you an "Subscriber PIN"
3. Add the "Subscriber PIN" to the Metadata Agent Settings "TheTVDB - API PIN"
4. Back in TheTVDB go to Account -> API Keys and "create a v4 Api Key"
    * Project Name: Plex metadata Agent
    * Project Description: A Metadata Agent for the Plex Media Server
5. Enter whatever in the "Company Information" fields.
6. Select End-User Subscription in "Funding"
7. Agree to the Terms
8. Add the API key (should look something like xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) to the Agents settings in the "TheTVDB - API Key" field
9. Save the settings


##### TheMovieDB

1. Create or Login to TheMovieDB and go to your Account Settings
2. in the navigation bar to the left click on API
3.  create an API key and add that to the Agents Settings in the "TheMovieDB - API Key"
4. Save the settings

#### Accept from other Metadata Agents

The MyAnimeList Agent also allows that other Metadata Agents provide Metadata to a Library Item. This is based on a list of Priority of the Metadata Agents in you Agents list in the Server settings.
The Agent accepts the following Metadata Agents:

* Local Media Assets
* [OpenSubtitles](https://github.com/oncleben31/OpenSubtitles.bundle) (Archived)
* [Subzero](https://github.com/plexinc-agents/Sub-Zero.bundle)
* [XBMCnfoMoviesImporter](https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle)
* [XBMCnfoTVImporter](https://github.com/gboudreau/XBMCnfoTVImporter.bundle)
* [HTTP Anidb Metadata Agent (HAMA)](https://github.com/ZeroQI/Hama.bundle/)

Please note that not every Agent is necessarily compatible with each other.

### Mapping:

To provide a way to get the additional images from TheTVDB and/or TheMovieDB the agent will use a list of IDs of mappings between different websites.

See my [anime-list Project](https://github.com/Fribb/anime-lists) for more information and contribution.

## Installation

### The Agent

Download the Agent from the [Releases page](https://github.com/Fribb/MyAnimeList.bundle/releases)

Installation is straight forward, place the MyAnimeList.bundle folder into the directories (depending on your OS) listed below and restart your Plex Media Server (Note: Plex only loads the Agent on restart!).

Directories:

* Linux: /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins/
* Windows: %LOCALAPPDATA%\Plex Media Server\Plug-ins

[More information](https://support.plex.tv/articles/201106098-how-do-i-find-the-plug-ins-folder/)

### The Scanners

Anime usually rely on an absolute episode numbering format instead of organizing them through seasons.
Therefore I recommend using scanners that follow this format:

* [Better ABsolute Scanner (BABS)](https://forums.plex.tv/discussion/31081/better-absolute-scanner-babs/p1)
* [Absolute Series Scanner](https://github.com/ZeroQI/Absolute-Series-Scanner)

Which scanner you use is up to you but there are some things that you should know:

The 'Better Absolute Scanner (BABS)' is not able to identify episodes with a 4 digit episode number, episodes above and including 1000 would not be added to your library.
The 'Absolute Series Scanner (ASS)', on the other hand, will add those episodes with 4 digit episode number to your library, but it will also remove anything in brackets like `(TV)` from the title.

This can lead to a matching problem. An example:

* Big Order (TV) - MAL-ID=31904
* Big Order - MAL-ID=30137

As you can see, those are two different releases one (30137) being the OVA version while the other (31904) is the TV version.
If you now would have your folder named according to my recommendation `Big Order (TV)` the following would happen:

* By using BABS a new Library item with the title `Big Order (TV)` would be created and matched to the correct MAL-ID 31904
* By using ASS a new Library item with the title `Big Order` would be created and matched to the incorrect MAL-ID 30137

The result of this would be that you would still have a somewhat similar Show metadata in Plex but no Episode title.

#### Force a Match

To circumvent the Problem described above, the Absolute Series Scanner offers the ability to leave GUIDs in the show title.
This will enable you to add the MyAnimeList ID to the folder directly which is then used to match the Anime specifically to that release

This also includes the manual match in which the notation is the same, the notation is as follows

`[mal-<mal_id>]`

Example:

The Anime `91 Days` has the ID `32998` the correct name for your folder or a manual search/match would then be `91 Days [mal-32998]`

## Support:

For all support related or general questions please use the [thread in the official plex forums](https://forums.plex.tv/discussion/105054/release-myanimelist-net-metadata-agent/p1)

For any issues like bugs, unintended behaviour please create a new Issue on the [github issue tracker](https://github.com/Fribb/MyAnimeList.bundle/issues)

For development stages, release information, download link or anything else you can visit my [dev Blog here](https://fribbtastic.net/projects/myanimelistagent/)

[See the Wiki Page for the FAQ](https://github.com/Fribb/MyAnimeList.bundle/wiki/Frequently-Asked-Questions)

We also have a [Discord Server](https://discord.gg/drHgfgC6)