from utils import *


global COMMON_UTILS
COMMON_UTILS = CommonUtils()

def Start():
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Starting MyAnimeList.net Metadata Agent v" + COMMON_UTILS.getVersion())
    
    return
    
def ValidatePrefs():
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Validating Preferences")
    
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Preferred Title Language: " + str(Prefs["preferredTitle"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Preferred Staff Image: " + str(Prefs["actorImage"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Preferred Staff Language: " + str(Prefs["actorLanguage"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Preferred Image Source for Shows: " + str(Prefs["tvshowImageSource"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "Preferred Image Source for Movies: " + str(Prefs["movieImageSource"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "TheMovieDB API Key: " + "-redacted-") #str(Prefs["tmdbAPIKey"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "TheMovieDB Poster Size: " + str(Prefs["tmdbPosterSize"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "TheMovieDB Background Size: " + str(Prefs["tmdbBackgroundSize"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "TheTVDB API Key: " + "-redacted-") #str(Prefs["tvdbAPIKey"]))
    Log.Info("[" + COMMON_UTILS.getAgentName() + "] " + "TheTVDB API PIN: " + "-redacted-") #str(Prefs["tvdbAPIPIN"]))
    
    return

'''
Class declaration for The TV-Show Agent
'''
class MyAnimeList_TV(Agent.TV_Shows, MyAnimeListAgent):
    # initialize configuration
    name = COMMON_UTILS.getAgentName()
    languages = COMMON_UTILS.getLanguages()
    primary_provider = COMMON_UTILS.getPrimaryProvider()
    accepts_from = COMMON_UTILS.getAcceptsFrom()
    
    MYANIMELIST = MyAnimeListAgent()
    
    TYPE = "show"
    
    def search(self, results, media, lang, manual):
        self.MYANIMELIST.search(results, media, lang, manual, self.TYPE)
        return
    
    def update(self, metadata, media, lang, force):
        self.MYANIMELIST.update(metadata, media, lang, force, self.TYPE)
        return

'''
Class declaration for The Movie Agent
'''
class MyAnimeList_Movie(Agent.Movies, MyAnimeListAgent):
    # initialize configuration
    name = COMMON_UTILS.getAgentName()
    languages = COMMON_UTILS.getLanguages()
    primary_provider = COMMON_UTILS.getPrimaryProvider()
    accepts_from = COMMON_UTILS.getAcceptsFrom()
    
    MYANIMELIST = MyAnimeListAgent()
    
    TYPE = "movie"
    
    def search(self, results, media, lang, manual):
        self.MYANIMELIST.search(results, media, lang, manual, self.TYPE)
        return
    
    def update(self, metadata, media, lang, force):
        self.MYANIMELIST.update(metadata, media, lang, force, self.TYPE)
        return