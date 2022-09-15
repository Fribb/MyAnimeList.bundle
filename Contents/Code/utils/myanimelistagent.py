from common import CommonUtils
from jikan import JikanApiUtils
from thetvdb import TheTvDbUtils
from themoviedb import TheMovieDbUtils
import socket
import os

class MyAnimeListAgent:

    COMMON_UTILS = None
    JIKAN_UTILS = None
    AGENT_NAME = None
    TVDB_UTILS = None
    TMDB_UTILS = None

    '''
    Initialize the Utils
    '''
    def __init__(self):
        self.COMMON_UTILS = CommonUtils()
        self.JIKAN_UTILS = JikanApiUtils()
        self.AGENT_NAME = self.COMMON_UTILS.getAgentName()
        self.TVDB_UTILS = TheTvDbUtils()
        self.TMDB_UTILS = TheMovieDbUtils()

        socket.setdefaulttimeout(60)

        return

    '''
    Search for an Anime on the Jikan API and add the search results to the MetadataSearchResults
    '''
    def search(self, results, media, lang, manual, type):
        Log.Info("[" + self.AGENT_NAME + "] " + "Searching for Anime")

        mediaFolder = None

        # check the media type because the title is not in the same location
        if type == "show":
            title = self.COMMON_UTILS.removeAscii(media.show)
            mediaFolder = self.COMMON_UTILS.getMediaDirectory(media, "show")
        elif type == "movie":
            title = self.COMMON_UTILS.removeAscii(media.name)
            mediaFolder = self.COMMON_UTILS.getMediaDirectory(media, "movie")
        else:
            Log.Error("[" + self.AGENT_NAME + "] " + "No type defined, don't know which name to pick")

        if mediaFolder is not None:
            matchFileLocation = os.path.join(mediaFolder, ".match")

        if Data.Exists(matchFileLocation):
            Log.Info("[" + self.AGENT_NAME + "] " + ".match file found")
            matchFileDict = self.COMMON_UTILS.readMatchFile(matchFileLocation)

            if "mal-id" in matchFileDict:
                # the MyAnimeList ID is available in the .match file
                title = title + "[mal-" + matchFileDict['mal-id'] + "]"
            elif "title" in matchFileDict:
                # a title is available in the .match file, use that instead of the media title
                title = matchFileDict['title']

        else:
            Log.Debug("[" + self.AGENT_NAME + "] " + "No .match file found")

        self.JIKAN_UTILS.search(title, results, lang)

        Log.Info("[" + self.AGENT_NAME + "] " + "Search finished")
        return

    '''
    Update the metadata for a specific anime with metadata from Jikan, TheTVDB/TheMovieDB
    '''
    def update(self, metadata, media, lang, force, type):
        Log.Info("[" + self.AGENT_NAME + "] " + "Updating Anime " + type + " Metadata")

        # get the details of the Anime and add it to the metadata
        self.JIKAN_UTILS.getDetails(metadata)

        # when it is a tvshow, get the episodes and add them to the metadata
        if type == "show":
            self.JIKAN_UTILS.getEpisodes(metadata)

        # get the Images of the Anime and add them to the metadata        
        self.JIKAN_UTILS.getPictures(metadata)

        # get the Staff of the Anime and add them to the metadata
        self.JIKAN_UTILS.getCharacters(metadata)

        # request additional images from TheTVDB or TheMovieDB
        movieImageSource = str(Prefs["movieImageSource"])
        tvshowImageSource = str(Prefs["tvshowImageSource"])

        if type == "show":
            tvdbEndpoint = "series"
            tmdbEndpoint = "tv"

            if tvshowImageSource == "TheTVDB":
                mappingId = self.COMMON_UTILS.getMapping(metadata.id, "thetvdb")
                if mappingId is not None:
                    self.TVDB_UTILS.requestImages(metadata, mappingId, tvdbEndpoint)
            elif tvshowImageSource == "TheMovieDB":
                mappingId = self.COMMON_UTILS.getMapping(metadata.id, "themoviedb")
                if mappingId is not None:
                    self.TMDB_UTILS.requestImages(metadata, mappingId, tmdbEndpoint)

        if type == "movie":
            tvdbEndpoint = "movies"
            tmdbEndpoint = "movie"

            if movieImageSource == "TheTVDB":
                mappingId = self.COMMON_UTILS.getMapping(metadata.id, "thetvdb")
                if mappingId is not None:
                    self.TVDB_UTILS.requestImages(metadata, mappingId, tvdbEndpoint)
            elif movieImageSource == "TheMovieDB":
                mappingId = self.COMMON_UTILS.getMapping(metadata.id, "themoviedb")
                if mappingId is not None:
                    self.TMDB_UTILS.requestImages(metadata, mappingId, tmdbEndpoint)

        Log.Info("[" + self.AGENT_NAME + "] " + "Update finished")
        return
    