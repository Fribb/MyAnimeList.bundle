'''
Created on 23.03.2018

Plex Media Server Metadata Agent for MyAnimeList.net

This Agent will look up the title of the Anime and get the Metadata for the ID.
The Metadata will be cached in Plex for 1 Day

@author: Fribb http://coding.fribbtastic.net/
'''
import re
from datetime import datetime

'''
The Constants 
'''
AGENT_NAME = "MyAnimeList.net"
AGENT_VERSION = "v6.0.0"
AGENT_LANGUAGES = [Locale.Language.English]
AGENT_PRIMARY_PROVIDER = True
AGENT_ACCEPTS_FROM = [ 'com.plexapp.agents.localmedia', 'com.plexapp.agents.opensubtitles' ]
AGENT_SEARCH_URL = "https://atarashii.fribbtastic.net/web/2.1/anime/search?q={title}"
AGENT_DETAIL_URL = "https://atarashii.fribbtastic.net/web/2.1/anime/{id}"
AGENT_EPISODE_URL = "https://atarashii.fribbtastic.net/web/2.1/anime/episodes/{id}"
AGENT_CACHE_TIME = CACHE_1DAY

def Start():
    Log.Info("[" + AGENT_NAME + "] " + "Starting MyAnimeList.net Metadata Agent " + AGENT_VERSION)

def ValidatePrefs():
    Log.Info("[" + AGENT_NAME + "] There is nothing to validate")

### Agent Declaration for TV-Shows
class MyAnimeList_TV(Agent.TV_Shows):
    # initialize configuration
    name = AGENT_NAME
    languages = AGENT_LANGUAGES
    primary_provider = AGENT_PRIMARY_PROVIDER
    accepts_from = AGENT_ACCEPTS_FROM
    
    def search(self, results, media, lang, manual):
        doSearch(results, media, lang, "tv")
        return
    
    def update(self, metadata, media, lang, force):
        doUpdateShow(metadata, media, lang)
        return

### Agent declaration for Movies
class MyAnimeList_Movie(Agent.Movies):
    # initialize configuration
    name = AGENT_NAME
    languages = AGENT_LANGUAGES
    primary_provider = AGENT_PRIMARY_PROVIDER
    accepts_from = AGENT_ACCEPTS_FROM
    
    def search(self, results, media, lang, manual):
        doSearch(results, media, lang, "movie")
        return
    
    def update(self, metadata, media, lang, force):
        doUpdateMovie(metadata, media, lang)
        return
    
### Method to search for an Anime on the API 
def doSearch(results, media, lang, mediaType):
    Log.Info("[" + AGENT_NAME + "] " + "Searching for Anime")
    
    # Initialize variables
    mediaName = None
    searchURL = None
    jsonResponse = None
    apiAnimeId = None
    apiAnimeTitle = None
    apiAnimeYear = None
    animeMatchScore = None
    
    # check on mediaType if it is tv or movie
    if mediaType == "tv":
        mediaName = removeASCII(media.show)
    elif mediaType == "movie":
        mediaName = removeASCII(media.name)
    else:
        Log.Error("[" + AGENT_NAME + "] " + "No mediaType defined, don't know which name to pick")
    
    # build search URL
    searchURL = AGENT_SEARCH_URL.format(title=String.Quote(mediaName, usePlus=True))
    Log.Debug("[" + AGENT_NAME + "] " + "Search URL: " + searchURL)
    
    # retrieve Response from API for the Search
    try:
        jsonResponse = JSON.ObjectFromURL(searchURL, sleep=2.0, cacheTime=AGENT_CACHE_TIME)
        
        Log.Debug(jsonResponse)
    except Exception as e:
        Log.Error("[" + AGENT_NAME + "] " + "Error fetching JSON page: " + str(e))
        return
    
    # iterate over responses
    for series in jsonResponse:
        Log.Debug("Matches Found: ")
        # get the ID if it is available
        apiAnimeId = str(getJSONValue("id", series))
        
        # get the title if it is available
        apiAnimeTitle = str(getJSONValue("title", series))
        
        # get the year if it is available
        apiAnimeYear = str(getJSONValue("start_date", series)).split("-")[0]       
        
        # calculate the match score
        if len(apiAnimeTitle) > 0:
            animeMatchScore = int(100 - abs(String.LevenshteinDistance(apiAnimeTitle, mediaName)))
            Log.Debug("Matchscore: " + str(animeMatchScore))
        
        # append results to search results
        Log.Info("[" + AGENT_NAME + "] " + "Anime Found - ID=" + str(apiAnimeId) + " Title=" + str(apiAnimeTitle) + " Year=" + str(apiAnimeYear) + " MatchScore=" + str(animeMatchScore))
        results.Append(MetadataSearchResult(id=apiAnimeId, name=apiAnimeTitle, year=apiAnimeYear, score=animeMatchScore, lang=lang))
        
    Log.Info("[" + AGENT_NAME + "] " + "Anime search completed")
    
    return

### Method to update the Anime Series metadata
def doUpdateShow(metadata, media, lang):
    Log.Info("[" + AGENT_NAME + "] " + "Updating Metadata for Series " + metadata.id)
    
    # initialize variables
    detailURL = None
    episodesURL = None
    jsonResponse = None
    apiAnimeId = metadata.id
    apiAnimeEpisodeCount = None     # the number of Episodes of the Anime (episodes)
    
    '''
    Load Data for Show
    '''
    # build detail URL
    detailURL = AGENT_DETAIL_URL.format(id=metadata.id)
    Log.Debug("[" + AGENT_NAME + "] " + "Detail URL: " + detailURL)
    
    # retrieve Response from the API for the Anime
    try:
        jsonResponse = JSON.ObjectFromURL(detailURL, sleep=2.0, cacheTime=AGENT_CACHE_TIME)
        
        Log.Debug(jsonResponse)
    except Exception as e:
        Log.Error("[" + AGENT_NAME + "] " + "Error fetching JSON page: " + str(e))
        return
    
    # parse the elements of the response
    parseElements(jsonResponse, metadata)
    
    # get the number of episodes if it is available
    apiAnimeEpisodeCount = getJSONValue("episodes", jsonResponse)
    Log.Debug("Episode Count: " + str(apiAnimeEpisodeCount))
    if apiAnimeEpisodeCount is not None:
        metadata.seasons[1].episode_count = int(apiAnimeEpisodeCount)
    
    
    '''
    Load Data for Episodes
    '''
    jsonResponse = None
    
    # build episodes URL
    episodesURL = AGENT_EPISODE_URL.format(id=apiAnimeId)
    Log.Debug("[" + AGENT_NAME + "] " + "Episode URL: " + episodesURL)
    
    # retrieve Response from the API for the Episodes
    try:
        jsonResponse = JSON.ObjectFromURL(episodesURL, sleep=2.0, cacheTime=AGENT_CACHE_TIME)
        
        Log.Debug(jsonResponse)
    except Exception as e:
        Log.Error("[" + AGENT_NAME + "] " + "Error fetching JSON page: " + str(e))
        return
    
    # iterate over all episodes
    for episode in jsonResponse:
        apiEpisodeNumber = None
        apiEpisodeTitle = None
        apiEpisodeAirDate = None
        
        # get the number if it is available
        apiEpisodeNumber = getJSONValue("number", episode)
        Log.Debug("Episode Number: " + str(apiEpisodeNumber))
        
        apiEpisodeTitle = getJSONValue("title", episode)
        Log.Debug("Episode Title: " + str(apiEpisodeTitle))
        
        tmp_airDate = getJSONValue("air_date", episode)
        if tmp_airDate is not None:
            apiEpisodeAirDate = datetime.strptime(str(tmp_airDate), "%Y-%m-%d")
        Log.Debug("Episode Air Date: " + str(apiEpisodeAirDate))
        
        # add metadata only when episode number is available
        if apiEpisodeNumber is not None:
            # get the episode in plex
            plexEpisode = metadata.seasons[1].episodes[int(apiEpisodeNumber)]
            
            # create default title
            default_title = "Episode: " + str(apiEpisodeNumber)
            
            if apiEpisodeTitle is not None:
                plexEpisode.title = apiEpisodeTitle
            else:
                plexEpisode.title = default_title
            
            # create default air date
            default_date = datetime.now()
            
            if apiEpisodeAirDate is not None:
                plexEpisode.originally_available_at = apiEpisodeAirDate
            else :
                plexEpisode.originally_available_at = default_date
        
        Log.Debug("Episode " + str(apiEpisodeNumber) + ": " + str(plexEpisode.title) + " - " + str(plexEpisode.originally_available_at))
    
    Log.Info("Show Update completed")
    return

### Method to update the Anime Movie metadata
def doUpdateMovie(metadata, media, lang):
    Log.Info("[" + AGENT_NAME + "] " + "Updating Metadata for Movie " + metadata.id)
    
    # initialize variables
    detailURL = None
    apiAnimeId = metadata.id
        
    '''
    Load Data for Movie
    '''
    # build detail URL
    detailURL = AGENT_DETAIL_URL.format(id=apiAnimeId)
    Log.Debug("[" + AGENT_NAME + "] " + "Detail URL: " + detailURL)
    
    # retrieve Response from the API for the Anime
    try:
        jsonResponse = JSON.ObjectFromURL(detailURL, sleep=2.0, cacheTime=AGENT_CACHE_TIME)
        
        Log.Debug(jsonResponse)
    except Exception as e:
        Log.Error("[" + AGENT_NAME + "] " + "Error fetching JSON page: " + str(e))
        return
    
    # parse the elements of the response
    parseElements(jsonResponse, metadata)
    
    Log.Info("Movie Update completed")
    
    return

### Method to remove all ASCII from the text
def removeASCII(text):
    return re.sub(r'[^\x00-\x7F]+',' ', text)

### Method to get the JSON value of a key
def getJSONValue(key, json):
    value = None
    
    if key in json:
        value = json[key]
    else:
        Log.Debug(str(key) + ": NA")
    
    return value

### Method to remove all HTML tags from a string
def cleanText(raw):
    regex = re.compile('<.*?>')
    
    cleantext = re.sub(regex, '', raw)
    
    return cleantext

def parseElements(jsonResponse, metadata):
    
    # initialize variables
    apiAnimeId = None               # the ID of the Anime (id)
    apiAnimeTitle = None            # the Title of the Anime (title)
    apiAnimeSummary = None          # the summary of the Anime (synopsis)
    apiAnimeRating = None           # the rating of the Anime (members_score)
    apiAnimeAvailableAt = None      # the original available at date of the Anime (start_date)
    apiAnimeContentRating = None    # the content rating of the Anime (classification)
    apiAnimeCovers = None          # the cover pictures of the Anime (image_url)
    apiAnimeDuration = None         # the duration of the Anime (duration)
    apiAnimeGenres = None           # the genres of Anime (genres)
    apiAnimeProducers = None        # the producers of the Anime (producers)
    
    # get the ID if it is available and distinguish with MAL identifier 
    apiAnimeId = getJSONValue("id", jsonResponse)
    Log.Debug("ID: " + str(apiAnimeId))
    if apiAnimeId is not None:
        metadata.id = str(apiAnimeId)
    
    # get the title if it is available
    apiAnimeTitle = getJSONValue("title", jsonResponse)
    Log.Debug("Title: " + str(apiAnimeTitle))
    if apiAnimeTitle is not None and len(apiAnimeTitle) > 0:
        metadata.title = str(apiAnimeTitle)
    
    # get the synopsis if it is available
    apiAnimeSummary = cleanText(getJSONValue("synopsis", jsonResponse))
    Log.Debug("Summary: " + str(apiAnimeSummary))
    if apiAnimeSummary is not None:
        metadata.summary = str(apiAnimeSummary)
    
    # get the score if it is available
    apiAnimeRating = getJSONValue("members_score", jsonResponse)
    Log.Debug("Rating: " + str(apiAnimeRating))
    if apiAnimeRating is not None:
        metadata.rating = apiAnimeRating
    
    # get the original available at date if it is available
    tmp_year = getJSONValue("start_date", jsonResponse)
    apiAnimeAvailableAt = datetime.strptime(str(tmp_year), "%Y-%m-%d")
    Log.Debug("Year: " + str(apiAnimeAvailableAt))
    if apiAnimeAvailableAt is not None:
        metadata.originally_available_at = apiAnimeAvailableAt
    
    # get the content rating if it is available
    apiAnimeContentRating = getJSONValue("classification", jsonResponse)
    Log.Debug("Content Rating: " + str(apiAnimeContentRating))
    if apiAnimeContentRating is not None:
        metadata.content_rating = str(apiAnimeContentRating)
    
    # get the covers if they are available
    apiAnimeCovers = getJSONValue("image_url", jsonResponse)
    Log.Debug("Cover: " + str(apiAnimeCovers))
    if apiAnimeCovers is not None:
        metadata.posters[str(apiAnimeCovers)] = Proxy.Media(HTTP.Request(str(apiAnimeCovers)).content)
    
    # get the duration if it is available
    tmp_duration = getJSONValue("duration", jsonResponse)
    apiAnimeDuration = tmp_duration * 60000
    Log.Debug("Duration: " + str(apiAnimeDuration))
    if apiAnimeDuration is not None:
        metadata.duration = int(apiAnimeDuration)
    
    # get the genres if they are available
    apiAnimeGenres = getJSONValue("genres", jsonResponse)
    Log.Debug("Genres: " + str(apiAnimeGenres))
    if apiAnimeGenres is not None and len(apiAnimeGenres) > 0:
        for genre in apiAnimeGenres:
            metadata.genres.add(str(genre))
    
    # get the producers if they are available
    tmp_producers = getJSONValue("producers", jsonResponse)
    Log.Debug("Producers: " + str(tmp_producers))
    if tmp_producers is not None and len(tmp_producers) > 0:
        apiAnimeProducers = ""
        for idx, producer in enumerate(tmp_producers):
            apiAnimeProducers += str(producer)
            if idx < len(tmp_producers)-1:
                apiAnimeProducers += ", "
        
        metadata.studio = str(apiAnimeProducers)
    
    # add tags
    # metadata.tags.add("MyAnimeList.net")   
    
    return