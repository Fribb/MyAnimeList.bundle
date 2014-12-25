MyAnimeList.bundle
==================

Plex Media Server Metadata Agent for MyAnimeList.net

Support Thread can be found <a href="https://forums.plex.tv/index.php/topic/105054-release-myanimelistnet-metadata-agent/">here</a><br>
Also visit my Blog on new development stages, release information <a href="http://devvsbugs.net/projects/pms-malagent/">here</a><br>
<br>
This Project loads metadata into your Plex Media Server from the Anime website <a href="myanimelist.net">MyAnimeList.net</a>.<br>
With the help of my for this project developed API you will get Data not only from MyAnimeList but also Series Information from TheTVDB,<br>
like additional cover images, background and banner images and a list of episodes with Episode Number, Title and the date it aired.<br>
<br>
<h3>Better ABsolute Scanner (BABS)</h3>
Since Anime in general use absolute numbering I recommend this scanner to scan your Anime. This scanner can be found <a href="https://forums.plex.tv/index.php/topic/31081-better-absolute-scanner-babs/">here</a>.<br>
<br>
<h3>Installation</h3>
Download the newest version from my <a href="https://sourceforge.net/projects/malagent/files/latest/download?source=files">here</a> (Source: SourceForge)<br>
Like every other Plugin or Agent for Plex you need to extract it into your Plugins folder the exact location for different systems can be found <a href="https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-">here</a><br>
<br>
<h3>Known Issues</h3>
1. Anime with many Episodes like Naruto, Bleach, One Piece will take longer to cache and respond from my API so it could be possible that you wont get any data because of a request timeout
2. To get additional data from TheTVDB I implemented a name matching method to match the names which were found on TheTVDB with the name you have in your DB if this match is over 85% you will get the data from TheTVDB
3. The list of Episodes is in absolute numbering so you won't get any data for your Episodes if you don't use absolute episode numbering in your anime (BABS will help you with that)
