'''
Last update on 26.05.2018

Plex Media Server Metadata Agent for MyAnimeList.net

This Agent will look up the title of the Anime and get the Metadata for the ID.
The Metadata will be cached in Plex for 1 Day

@author: Fribb http://coding.fribbtastic.net/
'''
import re
from datetime import datetime
from myanimelist import MyAnimeListUtils
from theTVDB import TheTVDBUtils
from theMovieDB import TheMovieDbUtils
from utils import Utils

'''The Constants'''
AGENT_NAME = "MyAnimeList.net Agent"
AGENT_VERSION = "v6.0.0"
AGENT_LANGUAGES = [Locale.Language.English]
AGENT_PRIMARY_PROVIDER = True
AGENT_ACCEPTS_FROM = [ 'com.plexapp.agents.localmedia', 'com.plexapp.agents.opensubtitles' ]
AGENT_CACHE_TIME = CACHE_1HOUR * 24

AGENT_MAPPING_URL = "https://atarashii.fribbtastic.net/mapping/animeMapping_full.json"
AGENT_MAPPING_CACHE_TIME = CACHE_1HOUR * 24

AGENT_UTILS = None
AGENT_MYANIMELIST = None
AGENT_THETVDB = None
AGENT_THEMOVIEDB = None

def Start():
    Log.Info("[" + AGENT_NAME + "] " + "Starting MyAnimeList.net Metadata Agent " + AGENT_VERSION)
    
    # Initialize Utils
    global AGENT_UTILS
    AGENT_UTILS = Utils()
    global AGENT_MYANIMELIST
    AGENT_MYANIMELIST = MyAnimeListUtils()
    global AGENT_THETVDB
    AGENT_THETVDB = TheTVDBUtils()
    global AGENT_THEMOVIEDB
    AGENT_THEMOVIEDB = TheMovieDbUtils()
    

def ValidatePrefs():
    Log.Info("[" + AGENT_NAME + "] " + "Validating Preferences")
    
    Log.Debug("[" + AGENT_NAME + "] " + "Fetch TheMovieDB images: " + str(Prefs["getTheMovieDbImages"]))
    Log.Debug("[" + AGENT_NAME + "] " + "Fetch TheTVDB images: " + str(Prefs["getTheTVDBImages"]))
    Log.Debug("[" + AGENT_NAME + "] " + "TheMovieDB Background Image size: " + Prefs["theMovieDbBackgroundSize"])
    Log.Debug("[" + AGENT_NAME + "] " + "TheMovieDB Poster Image size: " + Prefs["theMovieDbPosterSize"])
    
    Log.Info("[" + AGENT_NAME + "] " + "Validation Complete")

'''
Class declaration for The Agent
'''
class MALAgent:
    '''
    Method to search for an Anime TV-Show on the API
    '''
    def searchAnime(self, results, media, lang, type):
        Log.Info("[" + AGENT_NAME + "] " + "Searching for Anime")
        
        # check on mediaType if it is tv or movie
        if type == "tv":
            title = AGENT_UTILS.removeASCII(media.show)
        elif type == "movie":
            title = AGENT_UTILS.removeASCII(media.name)
        else:
            Log.Error("[" + AGENT_NAME + "] " + "No type defined, don't know which name to pick")
        
        AGENT_MYANIMELIST.search(title, results, lang)
    
        Log.Info("[" + AGENT_NAME + "] " + "Search Complete")
        return

    '''
    Method to update the metadata information of an Anime TV-Show
    '''
    def updateTvShow(self, metadata, media, lang):
        Log.Info("[" + AGENT_NAME + "] " + "Updating TV-Show Anime with ID: " + metadata.id)
        
        AGENT_MYANIMELIST.getData(metadata, "tvshow", media)
        
        if Prefs["getTheTVDBImages"] == True:
            Log.Debug("[" + AGENT_NAME + "] " + "Fetching TheTVDB Mapping")
            mappingId = self.getMapping(metadata.id, "thetvdb")
            
            if mappingId is not None:
                Log.Debug("[" + AGENT_NAME + "] " + "Fetching TheTVDB Information")
                AGENT_THETVDB.getData(mappingId, metadata)
    
        Log.Info("[" + AGENT_NAME + "] " + "Update Complete")
        return

    '''
    Method to update the metadata information of an Anime Movie
    '''
    def updateMovie(self, metadata, media, lang):
        Log.Info("[" + AGENT_NAME + "] " + "Updating Movie Anime with ID: " + metadata.id)
        
        AGENT_MYANIMELIST.getData(metadata, "movie", media)
        
        if Prefs["getTheMovieDbImages"] == True:
            Log.Debug("[" + AGENT_NAME + "] " + "Fetching TheMovieDB Mapping")
            mappingId = self.getMapping(metadata.id, "themoviedb")
            
            if mappingId is not None:
                Log.Debug("[" + AGENT_NAME + "] " + "Fetching TheMovieDB Information")
                AGENT_THEMOVIEDB.getData(mappingId, metadata)
    
        Log.Info("[" + AGENT_NAME + "] " + "Update Complete")
        return
    
    '''
    Method to get the Mapping for a given ID
    '''
    def getMapping(self, id, key):
        
        mappingFull = None
        
        try:
            Log.Info("[" + AGENT_NAME + "] [Utils] " + "Fetching URL " + str(AGENT_MAPPING_URL))
            mappingFull = JSON.ObjectFromString(HTTP.Request(AGENT_MAPPING_URL, sleep=2.0, cacheTime=AGENT_MAPPING_CACHE_TIME).content)
        except Exception as e:
            Log.Info("[" + AGENT_NAME + "] " + "Mapping could not be requested " + str(e))
        
        if mappingFull is None:
            Log.Error("[" + AGENT_NAME + "] " + "Mapping could not be loaded")
            return None
        else:
            Log.Info("[" + AGENT_NAME + "] " + "Searching for mapping for ID " + id)
        
        mappingString = str(key) + "_id"
        mappingId = None
        
        for mapping in mappingFull:
            if "mal_id" in mapping:
                malId = AGENT_UTILS.getJSONValue("mal_id", mapping)
                
                if str(malId) == id:
                    mappingId = AGENT_UTILS.getJSONValue(mappingString, mapping)
                    
                    if mappingId == -1:
                        Log.Info("[" + AGENT_NAME + "] " + "Mapping entry was available but ID is not a valid TheTVDB or TheMovieDB ID")
                        return None
                    else:                    
                        Log.Info("[" + AGENT_NAME + "] " + "Mapping entry for ID found: " + str(key) + " = " + str(mappingId))
                        return mappingId # don't need to search further if I already got the ID
        return mappingId

'''
Class declaration for The TV-Show Agent
'''
class MyAnimeList_TV(Agent.TV_Shows, MALAgent):
    # initialize configuration
    name = AGENT_NAME
    languages = AGENT_LANGUAGES
    primary_provider = AGENT_PRIMARY_PROVIDER
    accepts_from = AGENT_ACCEPTS_FROM
    
    def search(self, results, media, lang, manual):
        self.searchAnime(results, media, lang, "tv")
        return
    
    def update(self, metadata, media, lang, force):
        self.updateTvShow(metadata, media, lang)
        return

'''
Class declaration for The Movie Agent
'''
class MyAnimeList_Movie(Agent.Movies, MALAgent):
    # initialize configuration
    name = AGENT_NAME
    languages = AGENT_LANGUAGES
    primary_provider = AGENT_PRIMARY_PROVIDER
    accepts_from = AGENT_ACCEPTS_FROM
    
    def search(self, results, media, lang, manual):
        self.searchAnime(results, media, lang, "movie")
        return
    
    def update(self, metadata, media, lang, force):
        self.updateMovie(metadata, media, lang)
        return