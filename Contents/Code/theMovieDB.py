'''
Last update on 26.05.2018

Plex Media Server Metadata Agent for MyAnimeList.net

TODO: Description

@author: Fribb http://coding.fribbtastic.net/
'''

from utils import Utils

'''Constants'''
AGENT_NAME = "MyAnimeList.net"

THEMOVIEDB_URL_MAIN = "https://api.themoviedb.org"
THEMOVIEDB_URL_CONFIGURATION = "/3/configuration?api_key={api_key}"
THEMOVIEDB_URL_MOVIE_IMAGES = "/3/movie/{id}/images?api_key={api_key}"
THEMOVIEDB_API_KEY = "f42adc8664ab008c7ea99b720c576213"
THEMOVIEDB_CACHE_TIME = CACHE_1HOUR * 24 * 7

class TheMovieDbUtils():
    
    '''
    Method to request the image information from TheMovieDB.org
    '''
    def getData(self, id, metadata):
        Log.Info("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "Requesting Information from TheMovieDB.org")
        
        utils = Utils()
        
        imageBase = None
        
        ### Request the TheMovieDB configuration for the image base URL
        if imageBase is None:
            theMovieDBConfigUrl = THEMOVIEDB_URL_MAIN + THEMOVIEDB_URL_CONFIGURATION.format(api_key=THEMOVIEDB_API_KEY)
        
            try:
                Log.Info("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "Fetching URL " + str(theMovieDBConfigUrl))
                configResult = JSON.ObjectFromString(HTTP.Request(theMovieDBConfigUrl, sleep=2.0, cacheTime=THEMOVIEDB_CACHE_TIME).content)
            except Exception as e:
                Log.Error("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB configuration could not be requested " + str(e))
                return
            
            if configResult is not None:
                if "images" in configResult:
                    if "base_url" in configResult["images"]:
                        imageBase = configResult["images"]["base_url"]
                    else:
                        Log.Error("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB Image config is not available")
                        return
                else:
                    Log.Error("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB Image config is not available")
                    return
            else:
                Log.Error("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB Image config is not available")
                return
        
        theMovieDBUrl = THEMOVIEDB_URL_MAIN + THEMOVIEDB_URL_MOVIE_IMAGES.format(id=id, api_key=THEMOVIEDB_API_KEY)
        
        ### Request the TheMovieDB information by ID
        
        try:
            Log.Info("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "Fetching URL " + str(theMovieDBUrl))
            movieResult = JSON.ObjectFromString(HTTP.Request(theMovieDBUrl, sleep=2.0, cacheTime=THEMOVIEDB_CACHE_TIME).content)
        except Exception as e:
            Log.Error("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "TheMovieDB image result could not be requested " + str(e))
            return
        
        if movieResult is not None:
            
            if "backdrops" in movieResult:
                backdrops = movieResult["backdrops"]
                for backdrop in backdrops:
                    url = imageBase + Prefs["theMovieDbBackgroundSize"] + "/" + backdrop["file_path"]
                    Log.Debug("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB Background Image Url=" + url)
                    
                    if metadata.art[str(url)] is None:
                        metadata.art[str(url)] = Proxy.Media(HTTP.Request(str(url), sleep=2.0).content)
                    else:
                        Log.Debug("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "Image is already present")
            else:
                Log.Warn("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "There were no backdrops")
            
            if "posters" in movieResult:
                posters = movieResult["posters"]
                for poster in posters:
                    url = imageBase + Prefs["theMovieDbBackgroundSize"] + "/" + poster["file_path"]
                    Log.Debug("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB Poster Image Url=" + url)
                    
                    if metadata.posters[str(url)] is None:
                        metadata.posters[str(url)] = Proxy.Media(HTTP.Request(str(url), sleep=2.0).content)
                    else:
                        Log.Debug("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "Image is already present")
            else:
                Log.Warn("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "There were no posters")
                
        else:
            Log.Error("[" + AGENT_NAME + "] [TheMovieDbUtils] " + "TheMovieDB Image Information are not available")
            return
        
        return