import sys
import os
import urllib2
import base64
import difflib
from datetime import datetime

SEARCH_URL = "http://daraku-mal-api.net/services/v2/search/"
DETAIL_URL = "http://daraku-mal-api.net/services/v2/anime/"

def Start():
  Log("[MyAnimeList]: Starting MyAnimeList.net Agent")
  HTTP.CacheTime = CACHE_1DAY

def doSearch(results, media, lang, mediaType):

  Log("[MyAnimeList]: Entered doSearch")
  Log("[MyAnimeList]: Searching for Anime...")
  
  # Init variables
  if mediaType == "tvshow":
    showName = media.show.encode('unicode_escape').encode('ascii').replace("\u2605", " ")
  elif mediaType == "movie":
    showName = media.name
  animeId = None
  animeTitle = None
  animeYear = None
  animeMatchScore = None
  
  # Build URL
  searchURL = SEARCH_URL + String.Quote(showName, usePlus=True)
  Log("[MyAnimeList]: Requesting results from: " + searchURL)
  
  # Request Data  
  xmlResults = XML.ObjectFromURL(searchURL)
  
  # parse Data and add to results
  for i in range(len(xmlResults.xpath("//anime"))):
    Log("[MyAnimeList]: ---- Search Entry ----")

    try:
      animeId = xmlResults.xpath("//anime[%i]/id//text()" % (i + 1) )[0]
      Log("[MyAnimeList]: Anime ID: " + animeId)
    except:
      animeId = None
      Log("[MyAnimeList]: Anime ID: Not Available") 

    try:
      animeTitle = xmlResults.xpath("//anime[%i]/title//text()" % (i + 1) )[0]
      Log("[MyAnimeList]: Anime Title: " + animeTitle)
    except:
      animeTitle = None
      Log("[MyAnimeList]: Anime Title: Not Available")
    
    try:
      animeYear = xmlResults.xpath("//anime[%i]/airedStart//text()" % (i + 1) )[0].split("-")[0]
      Log("[MyAnimeList]: Anime Year: " + animeYear)
    except:
      animeYear = None
      Log("[MyAnimeList]: Anime Year: Not Available")
    
    try:
      animeMatchScore = int(100 - abs(String.LevenshteinDistance(animeTitle, showName)))
      Log("[MyAnimeList]: Anime Match Score: " + str(animeMatchScore))
    except:
      animeMatchScore = None
      Log("[MyAnimeList]: Anime Match Score: Not Available")
    
    Log("[MyAnimeList]: ---- Entry End ----")

    Log("[MyAnimeList]: Add Entry to Results")
    results.Append(MetadataSearchResult(id = animeId, name = animeTitle, year = animeYear, score = animeMatchScore, lang = Locale.Language.English))
  
  Log("[MyAnimeList]: Search Completed")
  
  return

# ---------- TV_Shows ----------

def doUpdateTVShow(metadata, media, lang):

  Log("[MyAnimeList]: Entered doUpdateTVShow")
  Log("[MyAnimeList]: Requesting Data for Anime: " + metadata.id)
  
  # Init variables
  anime = None				# root object
  animeId = None			# metadata.id
  animeTitle = None			# metadata.title
  animeSynopsis = None		# metadata.summary
  animeScore = None			# metadata.rating
  animeAired = None			# metadata.originally_available_at
  animeRating = None		# metadata.content_rating
  animeCovers = None		# metadata.posters
  animeDuration = None		# metadata.duration
  animeGenres = None		# metadata.genres
  animeProducers = None		# metadata.studio
  animeBackgrounds = None	# metadata.art
  animeEpisodes = None		# metadata.seasons[*].episodes
  animeBanners = None		# metadata.banners
  
  # Build URL
  detailURL = DETAIL_URL + String.Quote(metadata.id, usePlus=True)
  Log("[MyAnimeList]: Request Results from: " + detailURL)
  
  # Request Data
  xmlResults = XML.ObjectFromURL(detailURL)

  # Parse Data and add to Metadata
  for i in range(len(xmlResults.xpath("//anime"))):

    Log("[MyAnimeList]: ---- Anime Entry ----")
    
    anime = xmlResults.xpath("//anime[%i]" % (i+1))[0]

    # parse and add anime id
    try:
      animeId = str(anime['id'])
      Log("[MyAnimeList]: ID: " + animeId)
      metadata.id = animeId
    except Exception, e:
      Log("[MyAnimeList]: ID Not Available or could not add to metadata")
      Log("[MyAnimeList]: ID ERROR: " + str(e))

    # parse and add anime title
    try:
      animeTitle = anime['title']
      Log("[MyAnimeList]: Title: " + animeTitle)
      metadata.title = animeTitle
    except Exception, e:
      Log("[MyAnimeList]: Title: Not Available or could not add to metadata")
      Log("[MyAnimeList]: TITLE ERROR: " + str(e))

    # parse and add anime synopsis
    try:
      animeSynopsis = anime['synopsis']
      Log("[MyAnimeList]: Synopsis: " + animeSynopsis)
      metadata.summary = animeSynopsis
    except Exception, e:
      Log("[MyAnimeList]: Synopsis: Not Available or could not add to metadata")
      Log("[MyAnimeList]: SYNOPSIS ERROR: " + str(e))

    # parse and add anime score
    try:
      animeScore = float(anime['score'])
      Log("[MyAnimeList]: Score: " + str(animeScore))
      metadata.rating = animeScore
    except Exception, e:
      Log("[MyAnimeList]: Score: Not Available or could not add to metadata")
      Log("[MyAnimeList]: SCORE ERROR: " + str(e))

    # parse and add anime date
    try:
      animeAired = datetime.strptime(str(anime['airedStart']).split("T")[0], "%Y-%m-%d")
      Log("[MyAnimeList]: Aired: " + str(animeAired))
      metadata.originally_available_at = animeAired
    except Exception, e:
      Log("[MyAnimeList]: Aired: Not Available or could not add to metadata")
      Log("[MyAnimeList]: AIRED ERROR: " + str(e))

    # parse and add anime rating
    try:
      animeRating = anime['rating']
      Log("[MyAnimeList]: Rating: " + animeRating)
      metadata.content_rating = animeRating
    except Exception, e:
      Log("[MyAnimeList]: Rating: Not Available or could not add to metadata")
      Log("[MyAnimeList]: RATING ERROR: " + str(e))

    # parse and add anime covers
    try:
      animeCovers = anime['cover']['url']
      coverPrefs = Prefs['cover']
      Log("[MyAnimeList]: Download Cover Images: " + coverPrefs)
      
      i = 0
      for cover in animeCovers:
        if i != coverPrefs or coverPrefs == "all available":
          Log("[MyAnimeList]: Cover: " + cover)
          metadata.posters[str(cover)] = Proxy.Media(HTTP.Request(str(cover)).content)
        i += 1
    except Exception, e:
      Log("[MyAnimeList]: Cover: Not Available or could not add to metadata")
      Log("[MyAnimeList]: COVER ERROR: " + str(e))

    # parse and add anime duration
    try:
      animeDuration = int(anime['duration'])
      Log("[MyAnimeList]: Duration: " + str(animeDuration))
      metadata.duration = animeDuration
    except Exception, e:
      Log("[MyAnimeList]: Duration: Not Available or could not add to metadata")
      Log("[MyAnimeList]: DURATION ERROR: " + str(e))

    # parse and add anime genres
    try:
      animeGenres = anime['genre']['name']
      for genre in animeGenres:
        Log("[MyAnimeList]: Genre: " + genre)
        metadata.genres.add(genre)
    except Exception, e:
      Log("[MyAnimeList]: Genres: Not Available or could not add to metadata")
      Log("[MyAnimeList]: GENRES ERROR: " + str(e))

    # parse and add anime producers
    try:
      animeProducers = anime['producer']['name']
      animeStudio = ""
      for producer in animeProducers:
        if animeStudio != "":
          animeStudio += ", "
        Log("[MyAnimeList]: Producer: " + producer)
        animeStudio += producer
      metadata.studio = animeStudio
    except Exception, e:
      Log("[MyAnimeList]: Producers: Not Available or could not add to metadata")
      Log("[MyAnimeList]: PRODUCERS ERROR: " + str(e))

    # parse and add anime backgrounds
    try:
      animeBackgrounds = anime['background']['url']
      backgroundPrefs = Prefs['background']
      Log("[MyAnimeList]: Download Background Images: " + backgroundPrefs)
      
      i = 0
      for background in animeBackgrounds:
        if i != backgroundPrefs or backgroundPrefs == "all available":
          Log("[MyAnimeList]: Background: " + background)
          metadata.art[str(background)] = Proxy.Media(HTTP.Request(str(background)).content)
        i += 1
    except Exception, e:
      Log("[MyAnimeList]: Backgrounds: Not Available or could not add to metadata")
      Log("[MyAnimeList]: BACKGROUNDS ERROR: " + str(e))

    # parse and add anime banner
    try:
      animeBanners = anime['banner']['url']
      bannerPrefs = Prefs['banner']
      Log("[MyAnimeList]: Download Banner Images: " + bannerPrefs)
      
      i = 0
      for banner in animeBanners:
        if i != bannerPrefs or bannerPrefs == "all available":
          Log("[MyAnimeList]: Banners " + banner)
          metadata.banners[str(banner)] = Proxy.Media(HTTP.Request(str(banner)).content)
        i += 1
    except Exception, e:
      Log("[MyAnimeList]: Banners: Not Available or could not add to metadata")
      Log("[MyAnimeList]: BANNERS ERROR: " + str(e))

    # parse and add anime episodes
    try:
      animeEpisodes = anime['episodeList']['episodes']
      Log("[MyAnimeList]: Episodes: " + str(len(animeEpisodes)))
      for ep in animeEpisodes:
        episode = metadata.seasons[1].episodes[int(ep['number'])]
        episode.originally_available_at = datetime.strptime(str(ep['aired']), "%Y-%m-%d")
        episode.title = ep['name']
    except Exception, e:
      Log("[MyAnimeList]: Episodes: Not Available or could not add to metadata")
      Log("[MyAnimeList]: EPISODES ERROR: " + str(e))
      Log("[MyAnimeList]: using airedStart date as episode originally_available_at date")
      for seasonNumber in media.seasons:
        for episodeNumber in media.seasons[seasonNumber].episodes:
          episode = metadata.seasons[seasonNumber].episodes[episodeNumber]
          episode.originally_available_at = animeAired
          episode.title = "Episode " + episodeNumber

    Log("[MyAnimeList]: ---- Entry End ----")

  return

# ---------- Movies ----------

def doUpdateMovies(metadata, media, lang):

  Log("[MyAnimeList]: Entered doUpdateMovies")
  Log("[MyAnimeList]: Requesting Data for Anime: " + metadata.id)
  
  # Init variables
  animeId = None			# metadata.id
  animeTitle = None			# metadata.title
  animeSynopsis = None		# metadata.summary
  animeScore = None			# metadata.rating
  animeAired = None			# metadata.originally_available_at
  animeRating = None		# metadata.content_rating
  animeCovers = None		# metadata.posters
  animeDuration = None		# metadata.duration
  animeGenres = None		# metadata.genres
  animeProducers = None		# metadata.studio
  animeBackgrounds = None	# metadata.art
  animeBanners = None		# metadata.banners
  
  # Build URL
  detailURL = DETAIL_URL + String.Quote(metadata.id, usePlus=True)
  Log("[MyAnimeList]: Request Results from: " + detailURL)
  
  # Request Data
  xmlResults = XML.ObjectFromURL(detailURL)
  
  # Parse Data and add to Metadata
  for i in range(len(xmlResults.xpath("//anime"))):

    Log("[MyAnimeList]: ---- Anime Entry ----")
    
    anime = xmlResults.xpath("//anime[%i]" % (i+1))[0]

    # parse and add anime id
    try:
      animeId = str(anime['id'])
      Log("[MyAnimeList]: ID: " + animeId)
      metadata.id = animeId
    except Exception, e:
      Log("[MyAnimeList]: ID Not Available or could not add to metadata")
      Log("[MyAnimeList]: ID ERROR: " + str(e))

    # parse and add anime title
    try:
      animeTitle = anime['title']
      Log("[MyAnimeList]: Title: " + animeTitle)
      metadata.title = animeTitle
    except Exception, e:
      Log("[MyAnimeList]: Title: Not Available or could not add to metadata")
      Log("[MyAnimeList]: TITLE ERROR: " + str(e))

    # parse and add anime synopsis
    try:
      animeSynopsis = anime['synopsis']
      Log("[MyAnimeList]: Synopsis: " + animeSynopsis)
      metadata.summary = animeSynopsis
    except Exception, e:
      Log("[MyAnimeList]: Synopsis: Not Available or could not add to metadata")
      Log("[MyAnimeList]: SYNOPSIS ERROR: " + str(e))

    # parse and add anime score
    try:
      animeScore = float(anime['score'])
      Log("[MyAnimeList]: Score: " + str(animeScore))
      metadata.rating = animeScore
    except Exception, e:
      Log("[MyAnimeList]: Score: Not Available or could not add to metadata")
      Log("[MyAnimeList]: SCORE ERROR: " + str(e))

    # parse and add anime date
    try:
      animeAired = datetime.strptime(str(anime['airedStart']).split("T")[0], "%Y-%m-%d")
      Log("[MyAnimeList]: Aired: " + str(animeAired))
      metadata.originally_available_at = animeAired
    except Exception, e:
      Log("[MyAnimeList]: Aired: Not Available or could not add to metadata")
      Log("[MyAnimeList]: AIRED ERROR: " + str(e))

    # parse and add anime rating
    try:
      animeRating = anime['rating']
      Log("[MyAnimeList]: Rating: " + animeRating)
      metadata.content_rating = animeRating
    except Exception, e:
      Log("[MyAnimeList]: Rating: Not Available or could not add to metadata")
      Log("[MyAnimeList]: RATING ERROR: " + str(e))

    # parse and add anime covers
    try:
      animeCovers = anime['cover']['url']
      coverPrefs = Prefs['cover']
      Log("[MyAnimeList]: Download Cover Images: " + coverPrefs)
      
      i = 0
      for cover in animeCovers:
        if i != coverPrefs or coverPrefs == "all available":
          Log("[MyAnimeList]: Cover: " + cover)
          metadata.posters[str(cover)] = Proxy.Media(HTTP.Request(str(cover)).content)
        i += 1
    except Exception, e:
      Log("[MyAnimeList]: Cover: Not Available or could not add to metadata")
      Log("[MyAnimeList]: COVER ERROR: " + str(e))

    # parse and add anime duration
    try:
      animeDuration = int(anime['duration'])
      Log("[MyAnimeList]: Duration: " + str(animeDuration))
      metadata.duration = animeDuration
    except Exception, e:
      Log("[MyAnimeList]: Duration: Not Available or could not add to metadata")
      Log("[MyAnimeList]: DURATION ERROR: " + str(e))

    # parse and add anime genres
    try:
      animeGenres = anime['genre']['name']
      for genre in animeGenres:
        Log("[MyAnimeList]: Genre: " + genre)
        metadata.genres.add(genre)
    except Exception, e:
      Log("[MyAnimeList]: Genres: Not Available or could not add to metadata")
      Log("[MyAnimeList]: GENRES ERROR: " + str(e))

    # parse and add anime producers
    try:
      animeProducers = anime['producer']['name']
      animeStudio = ""
      for producer in animeProducers:
        if animeStudio != "":
          animeStudio += ", "
        Log("[MyAnimeList]: Producer: " + producer)
        animeStudio += producer
      metadata.studio = animeStudio
    except Exception, e:
      Log("[MyAnimeList]: Producers: Not Available or could not add to metadata")
      Log("[MyAnimeList]: PRODUCERS ERROR: " + str(e))

    # parse and add anime backgrounds
    try:
      animeBackgrounds = anime['background']['url']
      backgroundPrefs = Prefs['background']
      Log("[MyAnimeList]: Download Background Images: " + backgroundPrefs)
      
      i = 0
      for background in animeBackgrounds:
        if i != backgroundPrefs or backgroundPrefs == "all available":
          Log("[MyAnimeList]: Background: " + background)
          metadata.art[str(background)] = Proxy.Media(HTTP.Request(str(background)).content)
        i += 1
    except Exception, e:
      Log("[MyAnimeList]: Backgrounds: Not Available or could not add to metadata")
      Log("[MyAnimeList]: BACKGROUNDS ERROR: " + str(e))

    # parse and add anime banner
    try:
      animeBanners = anime['banner']['url']
      bannerPrefs = Prefs['banner']
      Log("[MyAnimeList]: Download Banner Images: " + bannerPrefs)
      
      i = 0
      for banner in animeBanners:
        if i != bannerPrefs or bannerPrefs == "all available":
          Log("[MyAnimeList]: Banners " + banner)
          metadata.banners[str(banner)] = Proxy.Media(HTTP.Request(str(banner)).content)
        i += 1
    except Exception, e:
      Log("[MyAnimeList]: Banners: Not Available or could not add to metadata")
      Log("[MyAnimeList]: BANNERS ERROR: " + str(e))
    
  return

class MyAnimeListAgentTV(Agent.TV_Shows):
  name = "MyAnimeList.net"
  languages = [Locale.Language.English]
  primary_provider = True
  accepts_from = [ 'com.plexapp.agents.localmedia', 'com.plexapp.agents.opensubtitles', 'com.plexapp.agents.thetvdb' ]
  
  def search(self, results, media, lang):
    doSearch(results, media, lang, "tvshow")
    return
  
  def update(self, metadata, media, lang):
    doUpdateTVShow(metadata, media, lang)
    return


class MyAnimeListAgentMovies(Agent.Movies):
  name = "MyAnimeList.net"
  languages = [Locale.Language.English]
  primary_provider = True
  accepts_from = [ 'com.plexapp.agents.localmedia', 'com.plexapp.agents.opensubtitles', 'com.plexapp.agents.themoviedb' ]
  
  def search(self, results, media, lang):
    doSearch(results, media, lang, "movie")
    return
  
  def update(self, metadata, media, lang):
    doUpdateMovies(metadata, media, lang)
    return