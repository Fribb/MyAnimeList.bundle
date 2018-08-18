'''
Last update on 26.05.2018

Plex Media Server Metadata Agent for MyAnimeList.net

TODO: Description

@author: Fribb http://coding.fribbtastic.net/
'''

from utils import Utils

'''Constants'''
AGENT_NAME = "MyAnimeList.net"

THETVDB_URL_MAIN = "https://www.thetvdb.com"
THETVDB_URL_API_MAIN = "https://api.thetvdb.com"
THETVDB_URL_LOGIN = "/login"
THETVDB_URL_SERIES_IMAGES = "/series/{id}/images"
THETVDB_URL_SERIES_IMAGE_QUERY = "/series/{id}/images/query?keyType={imageType}"
THETVDB_URL_BANNERS = "/banners/{image}"
THETVDB_API_KEY = "CE86D5F59D2835C2"
THETVDB_CACHE_TIME = CACHE_1HOUR * 24

class TheTVDBUtils():
    
    '''
    Mapping to request the image information from TheTVDB.com
    '''
    def getData(self, id, metadata):
        Log.Info("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Requesting Information from TheTVDB.com")
        
        utils = Utils()
        token = None
        
        loginUrl = THETVDB_URL_API_MAIN + THETVDB_URL_LOGIN
        
        try:
            loginResponse = JSON.ObjectFromString(HTTP.Request(loginUrl, data=JSON.StringFromObject(dict(apikey=THETVDB_API_KEY)), headers={'Content-type': 'application/json'}, sleep=2.0, cacheTime=THETVDB_CACHE_TIME).content)
        except Exception as e:
            Log.Error("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Could not retrieve authentication token from TheTVDB.com " + str(e))
            return
        
        if loginResponse is not None:
            if "token" in loginResponse:
                token = loginResponse["token"]
                Log.Debug("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Token is: " + token)
            else:
                Log.Error("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Could not retrieve authentication token from TheTVDB.com") 
                return
        
        imageTypesUrl = THETVDB_URL_API_MAIN + THETVDB_URL_SERIES_IMAGES.format(id=id)
        
        imageTypesResult = JSON.ObjectFromString(HTTP.Request(imageTypesUrl, headers={'Authorization': 'Bearer %s' % token}, sleep=2.0, cacheTime=THETVDB_CACHE_TIME).content)
        
        if "data" in imageTypesResult:
            
            for type in imageTypesResult["data"]:
                imageTypeQueryUrl = THETVDB_URL_API_MAIN + THETVDB_URL_SERIES_IMAGE_QUERY.format(id=id, imageType=type)
                
                if type == "poster" or type == "fanart" or type == "series":
                    
                    imageData = JSON.ObjectFromString(HTTP.Request(imageTypeQueryUrl, headers={'Authorization': 'Bearer %s' % token}, cacheTime=THETVDB_CACHE_TIME, sleep=2.0).content)
                    
                    Log.Info("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Adding " + type + " Images to metadata")
                    for data in imageData["data"]:
                        keyType = data["keyType"]
                        fileName = THETVDB_URL_MAIN + THETVDB_URL_BANNERS.format(image=data["fileName"])
                        
                        Log.Debug("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Image: " + keyType + " - " + fileName)
                        
                        if keyType == "poster":
                            metadata.posters[str(fileName)] = Proxy.Media(HTTP.Request(str(fileName), sleep=2.0).content)
                        
                        if keyType == "fanart":
                            metadata.art[str(fileName)] = Proxy.Media(HTTP.Request(str(fileName), sleep=2.0).content)
                        
                        if keyType == "series":
                            metadata.banners[str(fileName)] = Proxy.Media(HTTP.Request(str(fileName), sleep=2.0).content)
                        
        else:
            Log.Error("[" + AGENT_NAME + "] [TheTVDBUtils] " + "Could not retrieve image information from TheTVDB.com") 
            
        return