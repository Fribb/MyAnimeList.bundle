from common import CommonUtils
import re

class JikanApiUtils:
    
    API_MAIN        = "https://jikan.fribbtastic.net/v3"
    API_DETAILS     = "/anime/{id}"
    API_SEARCH      = "/search/anime?q={title}"
    API_EPISODES    = API_DETAILS + "/episodes/{page}"
    API_STAFF       = API_DETAILS + "/characters_staff"
    API_PICTURES    = API_DETAILS + "/pictures"
    API_PERSON      = "/person/{id}/pictures"
    API_CHARACTER   = "/character/{id}/pictures"
    
    COMMON_UTILS = None
    AGENT_NAME = None
    
    def __init__(self):
        self.COMMON_UTILS = CommonUtils()
        self.AGENT_NAME = self.COMMON_UTILS.getAgentName()
        return
    
    '''
    search for the title on the Jikan API
    '''
    def search(self, title, results, lang):
        
        # match the search title for a specific myanimelist-id
        manualId = self.COMMON_UTILS.getRegExMatch("^myanimelist-id:([0-9]+)$", str(title), 1)
        manualMatch = False
        searchUrl = None
        
        # manual match with a myanimelist ID or general search for the title
        if manualId:
            
            Log.Info("[" + self.AGENT_NAME + "] " + "Searching on Jikan for ID: '" + str(manualId) + "'")
            
            manualMatch = True
            searchUrl = self.API_MAIN + self.API_DETAILS.format(id=str(manualId))
        else:
            Log.Info("[" + self.AGENT_NAME + "] " + "Searching on Jikan for name: '" + str(title) + "'")
            
            searchUrl = self.API_MAIN + self.API_SEARCH.format(title=String.Quote(title, usePlus=True))
        
        searchResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(searchUrl))
        
        # manual match request the details page and have a different data Structure
        if manualMatch:
            Log.Debug("[" + self.AGENT_NAME + "] " + "Parsing match with myanimelist ID")
            
            apiMal_id = str(self.COMMON_UTILS.getJsonValue("mal_id", searchResult))
            apiTitle = str(self.COMMON_UTILS.getJsonValue("title", searchResult))
            apiAired = str(self.COMMON_UTILS.getYear("from", searchResult["aired"]))
            matchScore = 100
            
            Log.Debug("[" + self.AGENT_NAME + "] " + "ID=" + str(apiMal_id) + " Title='" + str(apiTitle) + "' Year=" + str(apiAired) + " MatchScore=" + str(matchScore))
            
            results.Append(MetadataSearchResult(id=apiMal_id, name=apiTitle, year=apiAired, score=matchScore, lang=lang))
        else:
            Log.Debug("[" + self.AGENT_NAME + "] " + "Parsing search results")
            resultsArray = searchResult["results"]
            
            Log.Info("[" + self.AGENT_NAME + "] " + str(len(resultsArray)) + " Results found")
            
            for show in resultsArray:
                apiMal_id = str(self.COMMON_UTILS.getJsonValue("mal_id", show))
                apiTitle = str(self.COMMON_UTILS.getJsonValue("title", show))
                apiAired = str(self.COMMON_UTILS.getYear("start_date", show))
                matchScore = self.COMMON_UTILS.calcMatchScore(title, apiTitle)
                
                Log.Debug("[" + self.AGENT_NAME + "] " + "ID=" + str(apiMal_id) + " Title='" + str(apiTitle) + "' Year=" + str(apiAired) + " MatchScore=" + str(matchScore))
                
                results.Append(MetadataSearchResult(id=apiMal_id, name=apiTitle, year=apiAired, score=matchScore, lang=lang))
        
        return
    
    '''
    get the metadata details for the specific MyAnimeList ID from the Jikan API
    '''
    def getDetails(self, metadata):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting detailed Information from Jikan")
        
        detailsUrl = self.API_MAIN + self.API_DETAILS.format(id=metadata.id)
        detailResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(detailsUrl))
        
        if detailResult is not None:
            
            # get the MyAnimeList ID from the JSON response and add it to the metadata
            apiId = self.COMMON_UTILS.getJsonValue("mal_id", detailResult)
            if apiId is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "ID: " + str(apiId))
                metadata.id = str(apiId)
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "ID was not available ")
            
            # get the Title that the user desires from the JSON response and add it to the metadata, if that title isn't available then default to the main
            preferredTitle = str(Prefs["preferredTitle"])
            titleLanguage = None
            
            if preferredTitle == "Japanese":
                titleLanguage = "title_japanese"
            elif preferredTitle == "English":
                titleLanguage = "title_english"
            else:
                titleLanguage = "title"
            
            apiTitle = self.COMMON_UTILS.getJsonValue(titleLanguage, detailResult)
            if apiTitle is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Title (" + preferredTitle + "): " + str(apiTitle))
                metadata.title = str(apiTitle)
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Title was not available ")
            
            # get the summary from the JSON response and add it to the metadata
            apiSummary = self.COMMON_UTILS.getJsonValue("synopsis", detailResult)
            if apiSummary is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Summary: " + str(apiSummary))
                metadata.summary = str(apiSummary)
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Summary was not available ")
            
            # get the rating from the JSON response and add it to the metadata
            apiRating = self.COMMON_UTILS.getJsonValue("score", detailResult)
            if apiRating is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Rating: " + str(apiRating))
                metadata.rating = apiRating
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Rating was not available ")
            
            # get the year when it originally aired from the JSON response and add it to the metadata
            apiYear = self.COMMON_UTILS.getDate("from", detailResult["aired"])
            if apiYear is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Year: " + str(apiYear))
                metadata.originally_available_at = apiYear
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Year was not available ")
            
            # get the content rating from the JSON response and add it to the metadata
            apiContentRating = self.COMMON_UTILS.getJsonValue("rating", detailResult)
            if apiContentRating is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Content Rating: " + str(apiContentRating))
                metadata.content_rating = str(apiContentRating)
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Content Rating was not available ")
            
            # get the main poster from the JSON response and add it to the metadata
            apiMainPoster = self.COMMON_UTILS.getJsonValue("image_url", detailResult)
            if apiMainPoster is not None:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Main Poster: " + str(apiMainPoster))
                if metadata.posters[str(apiMainPoster)] is None:
                    imageContent = self.COMMON_UTILS.getResponse(str(apiMainPoster))
                    
                    metadata.posters[str(apiMainPoster)] = Proxy.Media(imageContent)
                else:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Image is already present (" + str(apiMainPoster) + ")")
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Main Poster was not available ")
            
            # get the duration from the JSON response, parse it, get milliseconds and add it to the metadata
            apiDuration = self.COMMON_UTILS.getJsonValue("duration", detailResult)
            if apiDuration is not None:
                duration = int(self.COMMON_UTILS.getRegExMatch("^(\d*)", str(apiDuration), 1)) * 60000
                Log.Debug("[" + self.AGENT_NAME + "] " + "Duration: " + str(duration))
                metadata.duration = int(duration)
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Duration was not available ")
            
            # get the genres from the JSON response and add it to the metadata
            apiGenres = self.COMMON_UTILS.getJsonValue("genres", detailResult)
            if apiGenres is not None:
                genresArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiGenres)
                Log.Debug("[" + self.AGENT_NAME + "] " + "Genres: " + str(genresArray))
                for genre in genresArray:
                    metadata.genres.add(str(genre))
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Genres were not available ")
            
            # get the producers from the JSON response and add it to the metadata
            # Note: producers are only set on an individual episodes or a Movie, not on a show or season
            #apiProducers= self.COMMON_UTILS.getJsonValue("producers", detailResult)
            #if apiProducers is not None:
            #    producersArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiProducers)
            #    Log.Debug("[" + self.AGENT_NAME + "] " + "Producers: " + str(producersArray))
            #else:
            #    Log.Warn("[" + self.AGENT_NAME + "] " + "Producers were not available ")
            
            # get the studios from the JSON response and add it to the details dictionary
            apiStudios = self.COMMON_UTILS.getJsonValue("studios", detailResult)
            if apiStudios is not None:
                studiosArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiStudios)
                Log.Debug("[" + self.AGENT_NAME + "] " + "Studios: " + str(studiosArray))
                
                metadata.studio = ', '.join(studiosArray)
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Studios were not available ")
            
        return
    
    '''
    get the episodes for a specific MyAnimeList ID
    '''
    def getEpisodes(self, metadata):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Episodes from Jikan")
        
        firstPage = 1
        
        episodesUrl = self.API_MAIN + self.API_EPISODES.format(id=metadata.id,page=firstPage)
        episodesResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(episodesUrl))
        
        if episodesResult is not None:
            maxPages = self.COMMON_UTILS.getJsonValue("episodes_last_page", episodesResult)
            
            # parse the first page and add them to the metadata
            self.parseEpisodePage(metadata, firstPage, maxPages, episodesResult)
            
            # if there are more pages, parse them too and add them to the metadata
            for currentPage in range(firstPage + 1, maxPages + 1):
                
                nextPageUrl = self.API_MAIN + self.API_EPISODES.format(id=metadata.id,page=currentPage)
                nextPageResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(nextPageUrl))
                
                if nextPageResult is not None:
                    self.parseEpisodePage(metadata, currentPage, maxPages, nextPageResult)
            
        else:
            Log.Warn("[" + self.AGENT_NAME + "] " + "Episodes were not available")
            
        return
    
    '''
    parse the specific page of episodes and add the information to the metadata
    '''
    def parseEpisodePage(self, metadata, current, max, page):
        Log.Info("[" + self.AGENT_NAME + "] " + "Parsing Episodes page " + str(current) + "/" + str(max))
        
        episodes = self.COMMON_UTILS.getJsonValue("episodes", page)
        
        for episode in episodes:
            # get the episode number and title of the episode
            # both the number and title are required on MyAnimeList and define that an episode even exist.
            number = self.COMMON_UTILS.getJsonValue("episode_id", episode)
            title = self.COMMON_UTILS.getJsonValue("title", episode)
            
            # get the aired date of the episode
            # unlike the number and title, the aired date can be unavailable (null on the jikan API)
            # plex needs a valid date so that the episode can be considered for "next episode"
            try:
                aired = self.COMMON_UTILS.getDate("aired", episode)
            except:
                aired = self.COMMON_UTILS.getNowDate()
            
            Log.Debug("[" + self.AGENT_NAME + "] Episode " + str(number) + ": " + str(title) + " - " + str(aired))
            
            plexEpisode = metadata.seasons[1].episodes[int(number)]
            plexEpisode.title = str(title)
            plexEpisode.originally_available_at = aired
                
        return
    
    '''
    get the pictures of the anime
    Note: Pictures on MyAnimeList can contain Pictures that could be either a Poster or a Background image
    '''
    def getPictures(self, metadata):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Pictures from Jikan")
        
        picturesUrl = self.API_MAIN + self.API_PICTURES.format(id=metadata.id)
        picturesResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(picturesUrl))
        
        if picturesResult is not None:
            
            picArr = self.COMMON_UTILS.getJsonValue("pictures", picturesResult)
            pictures = self.COMMON_UTILS.getArrayFromJsonValue("large", picArr)
            
            for picture in pictures:
                Log.Debug("[" + self.AGENT_NAME + "] " + "Poster: " + str(picture))
                
                if metadata.posters[str(picture)] is None:
                    imageContent = self.COMMON_UTILS.getResponse(str(picture))
                    
                    metadata.posters[str(picture)] = Proxy.Media(imageContent)
                else:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Image is already present (" + str(picture) + ")")
                    
        return
    
    '''
    get the Character of the anime
    Note: a single Character can have multiple Voice Actors
          since there is not necessarily a distinction between those Voice Actors in terms of a different Character Picture
          the method will return the first VA for that selected preferred language
    '''
    def getCharacters(self, metadata):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Staff information from Jikan")
        
        preferredVaLanguage = str(Prefs["actorLanguage"])
        preferredCharacterImage = str(Prefs["actorImage"])
        
        staffUrl = self.API_MAIN + self.API_STAFF.format(id=metadata.id)
        staffResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(staffUrl))
        
        metadata.roles.clear()
        
        if staffResult is not None:
            
            charactersArr = self.COMMON_UTILS.getJsonValue("characters", staffResult)
            
            for character in charactersArr:
                #Log.Debug("[" + self.AGENT_NAME + "] " + "Character: " + str(character))
                
                charId = self.COMMON_UTILS.getJsonValue("mal_id", character)
                charName = self.COMMON_UTILS.getJsonValue("name", character)
                charImage = self.COMMON_UTILS.getJsonValue("image_url", character)
                vaId = None
                vaName = None
                vaLanguage = None
                vaImage = None
                
                voiceActors = self.COMMON_UTILS.getJsonValue("voice_actors", character)
                
                for voiceActor in voiceActors:
                    vaLang = self.COMMON_UTILS.getJsonValue("language", voiceActor)
                    
                    if vaLang == preferredVaLanguage:
                        vaId = self.COMMON_UTILS.getJsonValue("mal_id", voiceActor)
                        vaName = self.COMMON_UTILS.getJsonValue("name", voiceActor)
                        if preferredCharacterImage == "Voice Actor":
                            vaImage = self.getPersonImage(vaId)
                        vaLanguage = vaLang
                        break
                
                Log.Debug("[" + self.AGENT_NAME + "] " 
                          + "Character: #" + str(charId) + " - " 
                          + str(charName) + " - " 
                          + str(charImage) + " - " 
                          + str(vaId) + " - "
                          + str(vaName) + " - "
                          + str(vaLanguage) + " - "
                          + str(vaImage))
                
                newRole = metadata.roles.new()
                newRole.name = vaName
                newRole.role = charName
                if preferredCharacterImage == "Voice Actor":
                    newRole.photo = vaImage
                else:
                    newRole.photo = charImage
        
        return
    
    '''
    get the image for a person
    '''
    def getPersonImage(self, id):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Person image from Jikan")
        
        personUrl = self.API_MAIN + self.API_PERSON.format(id=id)
        personResult = JSON.ObjectFromString(self.COMMON_UTILS.getResponse(personUrl))
        
        if personResult is not None:
            picArr = self.COMMON_UTILS.getJsonValue("pictures", personResult)
            pictures = self.COMMON_UTILS.getArrayFromJsonValue("large", picArr)
        
        if len(pictures) > 0:
            return pictures[0]
        else:
            return None