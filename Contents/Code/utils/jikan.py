from common import CommonUtils
import re
import time

class JikanApiUtils:

    API_MAIN        = "https://api.jikan.moe/v4"
    API_DETAILS     = "/anime/{id}"
    API_SEARCH      = "/anime?q={title}"
    API_EPISODES    = API_DETAILS + "/episodes?page={page}"
    API_STAFF       = API_DETAILS + "/characters"
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
        manualId = self.COMMON_UTILS.getRegExMatch("\[mal-([0-9]+)\]$", str(title), 1)

        manualMatch = False
        searchUrl = None

        # get the Title in the language the user prefers
        preferredTitle = "Default"
        if not Prefs["excludePreferredTitleFromSearch"]:
            preferredTitle = str(Prefs["preferredTitle"])

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
            Log.Debug("[" + self.AGENT_NAME + "] " + "Parsing match with specific MyAnimeList ID")

            data = searchResult['data']

            apiMal_id = str(self.COMMON_UTILS.getJsonValue("mal_id", data))
            apiTitle = self.COMMON_UTILS.getTitle(self.COMMON_UTILS.getJsonValue("titles", data), preferredTitle)
            apiAired = str(self.COMMON_UTILS.getYear("from", data["aired"]))
            matchScore = 100

            Log.Debug("[" + self.AGENT_NAME + "] " + "ID=" + str(apiMal_id) + " Title='" + str(apiTitle) + "' Year=" + str(apiAired) + " MatchScore=" + str(matchScore))

            results.Append(MetadataSearchResult(id=apiMal_id, name=apiTitle, year=apiAired, score=matchScore, lang=lang))
        else:
            Log.Debug("[" + self.AGENT_NAME + "] " + "Parsing search results")
            resultsArray = searchResult["data"]

            Log.Info("[" + self.AGENT_NAME + "] " + str(len(resultsArray)) + " Results found")

            for show in resultsArray:
                apiMal_id = str(self.COMMON_UTILS.getJsonValue("mal_id", show))
                apiTitle = self.COMMON_UTILS.getTitle(self.COMMON_UTILS.getJsonValue("titles", show), preferredTitle)
                apiAired = str(self.COMMON_UTILS.getYear("from", show["aired"]))
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
        detailResponse = self.COMMON_UTILS.getResponse(detailsUrl)

        if detailResponse is not None:
            detailResult = JSON.ObjectFromString(detailResponse)
            data = detailResult['data']

            if data is not None:
                # get the MyAnimeList ID from the JSON response and add it to the metadata
                apiId = self.COMMON_UTILS.getJsonValue("mal_id", data)
                if apiId is not None:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "ID: " + str(apiId))
                    metadata.id = str(apiId)
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "ID was not available ")

                # get the Title in the language the user prefers
                preferredTitle = str(Prefs["preferredTitle"])

                apiTitle = self.COMMON_UTILS.getTitle(self.COMMON_UTILS.getJsonValue("titles", data), preferredTitle)
                Log.Debug("[" + self.AGENT_NAME + "] " + "Title (" + preferredTitle + "): " + str(apiTitle))
                metadata.title = str(apiTitle)

                # get the summary from the JSON response and add it to the metadata
                apiSummary = self.COMMON_UTILS.getJsonValue("synopsis", data)
                if apiSummary is not None:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Summary: " + str(apiSummary))
                    metadata.summary = str(apiSummary)
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Summary was not available ")

                # get the rating from the JSON response and add it to the metadata
                apiRating = self.COMMON_UTILS.getJsonValue("score", data)
                if apiRating is not None:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Rating: " + str(apiRating))
                    metadata.rating = float(apiRating)
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Rating was not available ")

                # get the year when it originally aired from the JSON response and add it to the metadata
                apiYear = self.COMMON_UTILS.getDate("from", data["aired"])
                if apiYear is not None:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Year: " + str(apiYear))
                    metadata.originally_available_at = apiYear
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Year was not available ")

                # get the content rating from the JSON response and add it to the metadata
                apiContentRating = self.COMMON_UTILS.getJsonValue("rating", data)
                if apiContentRating is not None:
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Content Rating: " + str(apiContentRating))
                    metadata.content_rating = str(apiContentRating)
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Content Rating was not available ")

                # get the main poster from the JSON response and add it to the metadata
                images = self.COMMON_UTILS.getJsonValue("images", data)
                apiMainPoster = self.COMMON_UTILS.getJsonValue("large_image_url", images["jpg"])
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
                apiDuration = self.COMMON_UTILS.getJsonValue("duration", data)
                if apiDuration is not None:
                    duration = int(self.COMMON_UTILS.getRegExMatch("^(\d*)", str(apiDuration), 1)) * 60000
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Duration: " + str(duration))
                    metadata.duration = int(duration)
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Duration was not available ")

                # get the genres from the JSON response and add it to the metadata
                apiGenres = self.COMMON_UTILS.getJsonValue("genres", data)
                if apiGenres is not None:
                    genresArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiGenres)
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Genres: " + str(genresArray))
                    for genre in genresArray:
                        metadata.genres.add(str(genre))
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Genres were not available ")

                # get the themes from the JSON response and add it to the metadata
                apiThemes = self.COMMON_UTILS.getJsonValue("themes", data)
                if apiThemes is not None:
                    themesArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiThemes)
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Theme: " + str(themesArray))
                    for theme in themesArray:
                        metadata.genres.add(str(theme))
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Themes were not available ")

                # get the demographic from the JSON response and add it to the metadata
                apiDemographic = self.COMMON_UTILS.getJsonValue("demographics", data)
                if apiDemographic is not None:
                    demographicArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiDemographic)
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Demographic: " + str(demographicArray))
                    for demographic in demographicArray:
                        metadata.genres.add(str(demographic))
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Demographics were not available ")

                # get the producers from the JSON response and add it to the metadata
                # Note: producers are only set on an individual episodes or a Movie, not on a show or season
                #apiProducers= self.COMMON_UTILS.getJsonValue("producers", data)
                #if apiProducers is not None:
                #    producersArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiProducers)
                #    Log.Debug("[" + self.AGENT_NAME + "] " + "Producers: " + str(producersArray))
                #else:
                #    Log.Warn("[" + self.AGENT_NAME + "] " + "Producers were not available ")

                # get the studios from the JSON response and add it to the details dictionary
                apiStudios = self.COMMON_UTILS.getJsonValue("studios", data)
                if apiStudios is not None:
                    studiosArray = self.COMMON_UTILS.getArrayFromJsonValue("name", apiStudios)
                    Log.Debug("[" + self.AGENT_NAME + "] " + "Studios: " + str(studiosArray))

                    metadata.studio = ', '.join(studiosArray)
                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Studios were not available ")


            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Jikan API returned no data")

        else:
            Log.Warn("[" + self.AGENT_NAME + "] " + "There was an error requesting a response from the Jikan API")

        return

    '''
    get the episodes for a specific MyAnimeList ID
    '''
    def getEpisodes(self, metadata):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Episodes from Jikan")

        page = 1
        nextPage = True

        # iterate each page if there is a next page
        while nextPage == True:
            ## reset nextPage to prevent an endless loop
            nextPage = False
            ## Wait 0.5 seconds to not go beyond the rate limit of the Jikan API
            time.sleep(0.5)

            episodesUrl = self.API_MAIN + self.API_EPISODES.format(id=metadata.id,page=page)
            episodesResponse = self.COMMON_UTILS.getResponse(episodesUrl)
            if episodesResponse is not None:
                episodesResult = JSON.ObjectFromString(episodesResponse)
                pagination = episodesResult["pagination"]
                data = episodesResult["data"]

                if data is not None:
                    nextPage = pagination["has_next_page"]

                    # parse episode page
                    self.parseEpisodePage(metadata, data, page)

                    page = page + 1

                else:
                    Log.Warn("[" + self.AGENT_NAME + "] " + "Jikan API returned no data")
                    break

            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Episodes were not available or there was an error retrieving them")
                break
        return

    '''
    parse the specific page of episodes and add the information to the metadata
    '''
    def parseEpisodePage(self, metadata, episodes, page):
        Log.Info("[" + self.AGENT_NAME + "] " + "Parsing Episodes page " + str(page))

        for episode in episodes:
            # get the episode number and title of the episode
            # both the number and title are required on MyAnimeList and define that an episode even exist.
            number = self.COMMON_UTILS.getJsonValue("mal_id", episode)
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

        ## Wait 0.5 seconds to not go beyond the rate limit of the Jikan API
        time.sleep(0.5)

        picturesUrl = self.API_MAIN + self.API_PICTURES.format(id=metadata.id)
        pictureResponse = self.COMMON_UTILS.getResponse(picturesUrl)

        if pictureResponse is not None:
            picturesResult = JSON.ObjectFromString(pictureResponse)
            data = picturesResult["data"]

            if data is not None:
                for picture in data:
                    image = self.COMMON_UTILS.getJsonValue("large_image_url", picture["jpg"])

                    Log.Debug("[" + self.AGENT_NAME + "] " + "Poster: " + str(image))

                    if metadata.posters[str(image)] is None:
                        imageContent = self.COMMON_UTILS.getResponse(str(image))
                        metadata.posters[str(image)] = Proxy.Media(imageContent)
                    else:
                        Log.Debug("[" + self.AGENT_NAME + "] " + "Image is already present (" + str(image) + ")")
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Jikan API returned no data")

        else:
            Log.Warn("[" + self.AGENT_NAME + "] " + "Pictures were not available or there was an error retrieving them")

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

        ## Wait 0.5 seconds to not go beyond the rate limit of the Jikan API
        time.sleep(0.5)

        charactersUrl = self.API_MAIN + self.API_STAFF.format(id=metadata.id)
        charactersResponse = self.COMMON_UTILS.getResponse(charactersUrl)

        if charactersResponse is not None:
            charactersResult = JSON.ObjectFromString(charactersResponse)
            data = charactersResult["data"]

            if data is not None:
                metadata.roles.clear()

                for item in data:
                    char = self.COMMON_UTILS.getJsonValue("character", item)
                    charId = self.COMMON_UTILS.getJsonValue("mal_id", char)
                    charName = self.COMMON_UTILS.getJsonValue("name", char)
                    images = self.COMMON_UTILS.getJsonValue("images", char)
                    charImage = self.COMMON_UTILS.getJsonValue("image_url", images["jpg"])

                    voiceActors = self.COMMON_UTILS.getJsonValue("voice_actors", item)
                    vaId = None
                    vaName = None
                    vaLanguage = None
                    vaImage = None

                    # iterate over all voice actors for that character
                    for voiceActor in voiceActors:
                        vaLang = self.COMMON_UTILS.getJsonValue("language", voiceActor)

                        if vaLang == preferredVaLanguage:
                            person = self.COMMON_UTILS.getJsonValue("person", voiceActor)
                            vaId = self.COMMON_UTILS.getJsonValue("mal_id", person)
                            vaName = self.COMMON_UTILS.getJsonValue("name", person)
                            if preferredCharacterImage == "Voice Actor":
                                images = self.COMMON_UTILS.getJsonValue("images", person)
                                vaImage = self.COMMON_UTILS.getJsonValue("image_url", images["jpg"])
                            vaLanguage = vaLang
                            break

                    Log.Debug("[" + self.AGENT_NAME + "] "
                              + "Character: #" + str(charId) + " - "
                              + str(charName) + " - "
                              + str(charImage) + " - "
                              + str(vaId) + " - "
                              + str(vaName) + " - "
                              + str(vaLanguage) + " - "
                              + str(vaImage)
                              )

                    # add a new role to the metadata
                    newRole = metadata.roles.new()
                    newRole.name = vaName
                    newRole.role = charName
                    if preferredCharacterImage == "Voice Actor":
                        newRole.photo = vaImage
                    else:
                        newRole.photo = charImage
            else:
                Log.Warn("[" + self.AGENT_NAME + "] " + "Jikan API returned no data")
        else:
            Log.Warn("[" + self.AGENT_NAME + "] " + "Pictures were not available or there was an error retrieving them")

        return