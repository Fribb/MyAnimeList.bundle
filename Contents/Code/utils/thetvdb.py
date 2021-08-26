from common import CommonUtils

class TheTvDbUtils():
    
    API_MAIN = "https://api4.thetvdb.com/v4"
    API_LOGIN = "/login"
    API_ARTWORKS_TYPE = "/artwork/types"
    API_ARTWORKS = "/{endpoint}/{id}/extended"
    
    COMMON_UTILS = None
    AGENT_NAME = None
    
    '''
    Initialize the Utils
    '''
    def __init__(self):
        self.COMMON_UTILS = CommonUtils()
        self.AGENT_NAME = self.COMMON_UTILS.getAgentName()
        return
    
    '''
    get the images from TheTVDB API
    '''
    def requestImages(self, metadata, id, endpoint):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting more Data from TheTVDB")
        
        token = self.authenticate()
        if token is not None:
            artworkTypes = self.getArtworkTypes(token)
            
            if artworkTypes is not None:
                artworks = self.getArtworks(id, token, endpoint)
                
                # iterate over every artwork of the show
                for artwork in artworks:
                    artworkUrl = self.COMMON_UTILS.getJsonValue("image", artwork)
                    artworkType = self.COMMON_UTILS.getJsonValue("type", artwork)
                    
                    # iterate over each artwork type
                    for type in artworkTypes:
                        typeId = self.COMMON_UTILS.getJsonValue("id", type)
                        typeName = self.COMMON_UTILS.getJsonValue("name", type)
                        
                        # if the type of the artwork of the show equals the id of the type then we have found the correct type
                        if artworkType == typeId:
                            
                            self.addImage(typeName, artworkUrl, metadata)
        return None
    
    '''
    check the response from TheTVDB for the status and return the data value
    '''
    def getData(self, response):
        
        if response is not None:
            status = self.COMMON_UTILS.getJsonValue("status", response)
            
            if status == "success":
                Log.Info("[" + self.AGENT_NAME + "] " + "Status: " + str(status))
                
                data = self.COMMON_UTILS.getJsonValue("data", response)
                
                return data
                
            else:
                message = self.COMMON_UTILS.getJsonValue("message", loginResult)
                Log.Error("[" + self.AGENT_NAME + "] " + "Status: '" + str(status) + "' Reason: " + str(message))
        
        return None
    
    '''
    authenticate against the TheTVDB API to get a token
    '''
    def authenticate(self):
        Log.Info("[" + self.AGENT_NAME + "] " + "authenticating")
        apiKey = str(Prefs["tvdbAPIKey"])
        apiPin = str(Prefs["tvdbAPIPIN"])
        token = None
        
        if len(apiKey) > 0 and len(apiPin) > 0:
            data = JSON.StringFromObject(dict(apikey=apiKey, pin=apiPin))
        
            loginUrl = self.API_MAIN + self.API_LOGIN
            loginResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(url=loginUrl, data=data))
            
            data = self.getData(loginResult)
            
            if data is not None:
                return self.COMMON_UTILS.getJsonValue("token", data)
            else:
                Log.Error("[" + self.AGENT_NAME + "] " + "Could not Authenticate")
        else:
            Log.Error("[" + self.AGENT_NAME + "] " + "TheTVDB API Key and/or PIN were not available!")
                        
        return None
    
    '''
    get the Artwork Types from TheTVDBD
    '''
    def getArtworkTypes(self, token):
        Log.Info("[" + self.AGENT_NAME + "] " + "Retrieving Artwork Types")
        
        artworkTypeUrl = self.API_MAIN + self.API_ARTWORKS_TYPE
        artworkTypeResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(url=artworkTypeUrl, headers={'Authorization': 'Bearer %s' % token}))
        
        data = self.getData(artworkTypeResult)
        
        if data is not None:
            return data
        else:
            Log.Error("[" + self.AGENT_NAME + "] " + "Could not retrieve Artwork types")
        
        return None
    
    '''
    get the Artworks for a specific Id from TheTVDB
    '''
    def getArtworks(self, id, token, endpoint):
        Log.Info("[" + self.AGENT_NAME + "] " + "Retrieving Artworks for ID: " + str(id))
        
        artworkUrl = self.API_MAIN + self.API_ARTWORKS.format(id=id, endpoint=endpoint)
        artworkResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(url=artworkUrl, headers={'Authorization': 'Bearer %s' % token}))
        
        data = self.getData(artworkResult)
        
        if data is not None:
            return self.COMMON_UTILS.getJsonValue("artworks", data)
        else:
            Log.Error("[" + self.AGENT_NAME + "] " + "Could not retrieve Artworks")
        
        return None
    
    '''
    add the image to the metadata
    '''
    def addImage(self, name, url, metadata):
        
        if name == "Banner":
            if metadata.banners[str(url)] is None:
                metadata.banners[str(url)] = Proxy.Media(HTTP.Request(str(url), sleep=2.0).content)
            else:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Banner is already present (" + str(url) + ")")
        
        if name == "Poster":
            if metadata.posters[str(url)] is None:
                metadata.posters[str(url)] = Proxy.Media(HTTP.Request(str(url), sleep=2.0).content)
            else:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Poster is already present (" + str(url) + ")")
        
        if name == "Background":
            if metadata.art[str(url)] is None:
                metadata.art[str(url)] = Proxy.Media(HTTP.Request(str(url), sleep=2.0).content)
            else:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Background is already present (" + str(url) + ")")
        
        return