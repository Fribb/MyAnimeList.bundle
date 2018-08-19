'''
Last update on 26.05.2018

Plex Media Server Metadata Agent for MyAnimeList.net

TODO: Description

@author: Fribb http://coding.fribbtastic.net/
'''
from utils import Utils

'''Constants'''
AGENT_NAME = "MyAnimeList.net"

MYANIMELIST_URL_MAIN = "https://atarashii.fribbtastic.net"
MYANIMELIST_URL_SEARCH = "/web/2.1/anime/search?q={title}"
MYANIMELIST_URL_DETAILS = "/web/2.1/anime/{id}"
MYANIMELIST_URL_EPISODES = "/web/2.1/anime/episodes/{id}"
MYANIMELIST_CACHE_TIME = CACHE_1HOUR * 24

class MyAnimeListUtils():
    
    '''
    Search the Atarashii API for the name of the Anime
    '''
    def search(self, name, results, lang):
        Log.Info("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Searching for Anime: " + str(name))
        
        title = String.Quote(name, usePlus=True)
        searchUrl = MYANIMELIST_URL_MAIN + MYANIMELIST_URL_SEARCH.format(title=title)
        utils = Utils()
        
        try:
            Log.Info("[" + AGENT_NAME + "] [Utils] " + "Fetching URL " + str(searchUrl))
            searchResults = JSON.ObjectFromString(HTTP.Request(searchUrl, sleep=2.0, cacheTime=MYANIMELIST_CACHE_TIME).content)
        except Exception as e:
            Log.Info("[" + AGENT_NAME + "] " + "search results could not be requested " + str(e))
            return
        
        Log.Info("[" + AGENT_NAME + "] [MyAnimeListUtils] " + str(len(searchResults)) + " Results found")
        for series in searchResults:            
            # get the ID if it is available
            apiAnimeId = str(utils.getJSONValue("id", series))
        
            # get the title if it is available
            apiAnimeTitle = str(utils.getJSONValue("title", series))
            
            # get the year if it is available
            apiAnimeYear = str(utils.getJSONValue("start_date", series)).split("-")[0]       
            
            # calculate the match score
            if len(apiAnimeTitle) > 0:
                animeMatchScore = utils.getMatchScore(apiAnimeTitle, name)
            
            # append results to search results
            Log.Debug("[" + AGENT_NAME + "] " + "Anime Found - ID=" + str(apiAnimeId) + " Title=" + str(apiAnimeTitle) + " Year=" + str(apiAnimeYear) + " MatchScore=" + str(animeMatchScore))
            results.Append(MetadataSearchResult(id=apiAnimeId, name=apiAnimeTitle, year=apiAnimeYear, score=animeMatchScore, lang=lang))

        return
    
    '''
    Method to request the details of an AnimeID and add the information to the metadata
    '''
    def getData(self, metadata, type):
        Log.Info("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Requesting Information from MyAnimeList.net")
        
        utils = Utils()
        
        detailUrl = MYANIMELIST_URL_MAIN + MYANIMELIST_URL_DETAILS.format(id=metadata.id)
        
        try:
            Log.Info("[" + AGENT_NAME + "] [Utils] " + "Fetching URL " + str(detailUrl))
            detailResult = JSON.ObjectFromString(HTTP.Request(detailUrl, sleep=2.0, cacheTime=MYANIMELIST_CACHE_TIME).content)
            #detailResult = JSON.ObjectFromString(utils.fetchContent(detailUrl, additionalHeaders=False, cacheTime=MYANIMELIST_CACHE_TIME))
        except Exception as e:
            Log.Error("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "No Detail Information were available " + str(e))
            return
        
        '''Parse the main Elements of the response'''
        apiAnimeId = None               # the ID of the Anime (plex metadata.id, myanimelist id)
        apiAnimeTitle = None            # the Title of the Anime (plex metadata.title, myanimelist title) 
        apiAnimeSummary = None          # the Summary of the Anime (plex metadata.summary, myanimelist synopsis)
        apiAnimeRating = None           # the Rating of the Anime (plex metadata.rating, myanimelist members_score) 
        apiAnimeAvailableAt = None      # the Date of the Anime first aired (plex metadata.originally_available_at, myanimelist start_date)
        apiAnimeContentRating = None    # the Content rating of the Anime (plex metadata.content_rating, myanimelist classification)
        apiAnimeCovers = None           # the Covers of the Anime (plex metadata.posters, myanimelist image_url)
        apiAnimeDuration = None         # the Duration of an Anime Episode (plex metadata.duration, myanimelist duration)
        apiAnimeGenres = None           # the Genres of the Anime (plex metadata.genres, myanimelist genres)
        apiAnimeProducers = None        # the Producers of the Anime (plex metadata.studio, myanimelist producers) ### TODO: Switch to Studios when they are available in the API (or add Producers to metadata when this is possible in Plex) 
        
        if detailResult is not None:
            
            # get the ID if it is available
            apiAnimeId = utils.getJSONValue("id", detailResult)
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "ID: " + str(apiAnimeId))
            if apiAnimeId is not None:
                metadata.id = str(apiAnimeId)
            
            # get the Title if it is available
            apiAnimeTitle = utils.getJSONValue("title", detailResult)
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Title: " + str(apiAnimeTitle))
            if apiAnimeTitle is not None:
                metadata.title = str(apiAnimeTitle)
            
            # get the Summary if it is available
            apiAnimeSummary = utils.getJSONValue("synopsis", detailResult) 
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Summary: " + str(apiAnimeSummary))
            if apiAnimeSummary is not None:
                metadata.summary = str(utils.removeTags(apiAnimeSummary))
            
            # get the Rating if it is available
            apiAnimeRating = utils.getJSONValue("members_score", detailResult)
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Rating: " + str(apiAnimeRating))
            if apiAnimeRating is not None:
                metadata.rating = float(apiAnimeRating)
            
            # get the first aired Date if it is available
            tmpYear = utils.getJSONValue("start_date", detailResult)
            if(tmpYear is not None):
                try:
                    apiAnimeAvailableAt = datetime.strptime(str(tmpYear), "%Y-%m-%d")
                    Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Year: " + str(apiAnimeAvailableAt))
                    if apiAnimeAvailableAt is not None:
                        metadata.originally_available_at = apiAnimeAvailableAt
                except Exception as e:
                    Log.Error("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "There was an Error while adding the Aired Date " + str(e))
            
            # get the content rating if it is available
            apiAnimeContentRating = utils.getJSONValue("classification", detailResult)
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Content Rating: " + str(apiAnimeContentRating))
            if apiAnimeContentRating is not None:
                metadata.content_rating = str(apiAnimeContentRating)
            
            # get the covers if they are available
            apiAnimeCovers = utils.getJSONValue("image_url", detailResult)
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Cover: " + str(apiAnimeCovers))
            if apiAnimeCovers is not None:
                if metadata.posters[str(apiAnimeCovers)] is None:
                    metadata.posters[str(apiAnimeCovers)] = Proxy.Media(HTTP.Request(str(apiAnimeCovers), sleep=2.0).content)
                else:
                    Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Image is already present")
            
            # get the duration if it is available
            tmpDuration = utils.getJSONValue("duration", detailResult)
            if(tmpDuration is not None):
                apiAnimeDuration = tmpDuration * 60000 
                Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Duration: " + str(apiAnimeDuration))
                if apiAnimeDuration is not None:
                    metadata.duration = int(apiAnimeDuration)
            
            # get the genres if they are available
            apiAnimeGenres = utils.getJSONValue("genres", detailResult)
            Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Genres: " + str(apiAnimeGenres))
            if apiAnimeGenres is not None and len(apiAnimeGenres) > 0:
                for genre in apiAnimeGenres:
                    metadata.genres.add(str(genre))
            
            # get the producers if they are available
            # TODO: plex only has Studios currently and the Atarashii API does not provide the Studios from MyAnimeList (yet)
            # When either of those are available this needs to be fixed
            tmpProducers = utils.getJSONValue("producers", detailResult)
            if(tmpProducers is not None):
                Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Producers: " + str(tmpProducers))
                if tmpProducers is not None and len(tmpProducers) > 0:
                    apiAnimeProducers = ""
                    for idx, producer in enumerate(tmpProducers):
                        apiAnimeProducers += str(producer)
                        if idx < len(tmpProducers) - 1:
                            apiAnimeProducers += ", "
                    
                    metadata.studio = str(apiAnimeProducers)
            
            '''
            Add specific data for TV-Shows
            '''
            if type == "tvshow":
                Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Adding TV-Show specific data")
                
                apiAnimeEpisodeCount = None
                episodesUrl = MYANIMELIST_URL_MAIN + MYANIMELIST_URL_EPISODES.format(id=metadata.id)
        
                try:
                    Log.Info("[" + AGENT_NAME + "] [Utils] " + "Fetching URL " + str(episodesUrl))
                    episodeResult = JSON.ObjectFromString(HTTP.Request(episodesUrl, sleep=2.0, cacheTime=MYANIMELIST_CACHE_TIME).content)
                except Exception as e:
                    Log.Info("[" + AGENT_NAME + "] " + "episode results could not be requested " + str(e))
                    return
                
                # get the episode count if it is available
                apiAnimeEpisodeCount = utils.getJSONValue("episodes", detailResult)
                Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Episodes: " + str(apiAnimeEpisodeCount))
                if apiAnimeEpisodeCount is not None:
                    metadata.seasons[1].episode_count = int(apiAnimeEpisodeCount)
                
                for episode in episodeResult:
                    apiEpisodeNumber = None     # the Number of the episode
                    apiEpisodeTitle = None      # the title of the Episode
                    apiEpisodeAirDate = None    # the air date of the Episode
                    
                    # get the episode Number
                    apiEpisodeNumber = utils.getJSONValue("number", episode)
                    
                    # get the episode title
                    apiEpisodeTitle = utils.getJSONValue("title", episode)
                    
                    # get the episode air date
                    apiEpisodeAirDate = utils.getJSONValue("air_date", episode)
                    
                    if apiEpisodeNumber is not None:
                        plexEpisode = metadata.seasons[1].episodes[int(apiEpisodeNumber)]
                        
                        # add the Episode Title if it is available, if not use a default title
                        if apiEpisodeTitle is not None:
                            plexEpisode.title = str(apiEpisodeTitle)
                        else:
                            plexEpisode.title = "Episode: #" + str(apiEpisodeNumber)
                        
                        # add the episode air date if it is available, if not use the current date
                        if apiEpisodeAirDate is not None:
                            plexEpisode.originally_available_at = datetime.strptime(str(apiEpisodeAirDate), "%Y-%m-%d")
                        else:
                            plexEpisode.originally_available_at = datetime.now()
                        
                    Log.Debug("Episode " + str(apiEpisodeNumber) + ": " + str(apiEpisodeTitle) + " - " + str(apiEpisodeAirDate))
            
            '''
            Add specific data for Movies
            '''
            if type == "movie":
                Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "Adding Movie specific data")
                Log.Debug("[" + AGENT_NAME + "] [MyAnimeListUtils] " + "nothing specific to add")
            
        return