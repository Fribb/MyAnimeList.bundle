from common import CommonUtils

class TheMovieDbUtils():
    
    API_MAIN = "https://api.themoviedb.org"
    API_CONFIG = "/3/configuration?api_key={apiKey}"
    API_IMAGES = "/3/{endpoint}/{id}/images?api_key={apiKey}"
    
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
    get the images from TheMovieDB API
    '''
    def requestImages(self, metadata, id, endpoint):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting more Data from TheMovieDB")
        
        apiKey = Prefs["tmdbAPIKey"]
        
        if apiKey is None:
            Log.Error("[" + self.AGENT_NAME + "] " + "TheMovieDB API Key was not available!")
            return            
        
        imageBaseUrl = self.getBaseUrl(apiKey)
        
        if imageBaseUrl is not None:
            images = self.getImages(endpoint, id, apiKey)
            if images is not None:
                self.addImages(images, imageBaseUrl, metadata)
        else:
            Log.Error("[" + self.AGENT_NAME + "] " + "Error retrieving image base URL")
            return None
        
        return
    
    '''
    get the Base URL for the Images
    '''
    def getBaseUrl(self, apiKey):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting the Image Base URL")
        
        configUrl = self.API_MAIN + self.API_CONFIG.format(apiKey=apiKey)
        configResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(url=configUrl))
        
        if configResult is not None:
            images = self.COMMON_UTILS.getJsonValue("images", configResult)
            
            if images is not None:
                return self.COMMON_UTILS.getJsonValue("secure_base_url", images)
        
        return None
    
    '''
    get the images for a specific TheMovieDB ID
    '''
    def getImages(self, endpoint, id, apiKey):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Images for ID: " + str(id))
        
        imagesUrl = self.API_MAIN + self.API_IMAGES.format(endpoint=endpoint, id=id, apiKey=apiKey)
        imagesResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(url=imagesUrl))
        
        if imagesResult is not None:
            return imagesResult
        
        return None
    
    '''
    add the images to the metadata 
    '''
    def addImages(self, images, baseUrl, metadata):
        
        posterSize = Prefs["tmdbPosterSize"]
        backgroundSize = Prefs["tmdbBackgroundSize"]
        backdrops = self.COMMON_UTILS.getJsonValue("backdrops", images)
        posters = self.COMMON_UTILS.getJsonValue("posters", images)
        
        # add all backdrops to the metadata (if they don't exist yet)
        for backdrop in backdrops:
            path = self.COMMON_UTILS.getJsonValue("file_path", backdrop)
            
            backdropUrl = baseUrl + backgroundSize + "/" + path
            
            if metadata.art[str(backdropUrl)] is None:
                image = self.COMMON_UTILS.requestImage(str(backdropUrl))
                if image is not None:
                    metadata.art[str(backdropUrl)] = image #Proxy.Media(HTTP.Request(str(backdropUrl), sleep=2.0).content)
            else:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Background is already present (" + str(backdropUrl) + ")")
        
        # add all poster to the metadata (if they don't exist yet)
        for poster in posters:
            path = self.COMMON_UTILS.getJsonValue("file_path", poster)
            
            posterUrl = baseUrl + posterSize + "/" + path
            
            if metadata.posters[str(posterUrl)] is None:
                image = self.COMMON_UTILS.requestImage(str(posterUrl))
                if image is not None:
                    metadata.posters[str(posterUrl)] = image #Proxy.Media(HTTP.Request(str(posterUrl), sleep=2.0).content)
            else:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Poster is already present (" + str(posterUrl) + ")")
            
        
        return