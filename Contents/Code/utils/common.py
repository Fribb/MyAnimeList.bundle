import urllib
import os
import re
import sys
import urllib2
import ssl
import difflib

class CommonUtils:
    ''' the path to the VERSION file '''
    VERSIONFILEPATH = os.path.join(Core.bundle_path, "VERSION")

    ''' the name of the Agent '''
    AGENT_NAME = "MyAnimeList.net"
    ''' the library languages '''
    AGENT_LANGUAGES = [Locale.Language.English, 'fr', 'zh', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'cs', 'ko', 'sl', 'hr']
    ''' is the agent a primary provider of the metadata '''
    AGENT_PRIMARY_PROVIDER = True
    ''' allows other agents to provide metadata '''
    AGENT_ACCEPTS_FROM = [ 'com.plexapp.agents.localmedia', 'com.plexapp.agents.opensubtitles', 'com.plexapp.agents.subzero', 'com.plexapp.agents.xbmcnfo', 'com.plexapp.agents.xbmcnfotv', 'com.plexapp.agents.hama' ]
    ''' caching time for requests '''
    AGENT_CACHE_TIME = CACHE_1HOUR * 24
    ''' mapping file '''
    AGENT_MAPPING_URL = "https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-list-full.json"
    ''' headers '''
    AGENT_HEADERS = {'Content-type': 'application/json'}

    '''
    return the name of the Agent
    '''
    def getAgentName(self):
        return self.AGENT_NAME

    '''
    return the supported languages
    '''
    def getLanguages(self):
        return self.AGENT_LANGUAGES

    '''
    return the Primary Provider variable
    '''
    def getPrimaryProvider(self):
        return self.AGENT_PRIMARY_PROVIDER

    '''
    return the agents that are accepted to provide additional metadata
    '''
    def getAcceptsFrom(self):
        return self.AGENT_ACCEPTS_FROM

    '''
    return the the time a request should be cached (default 24 hours)
    '''
    def getCacheTime(self):
        return self.AGENT_CACHE_TIME

    '''
    return the url for the mapping file
    '''
    def getMappingUrl(self):
        return self.AGENT_MAPPING_URL

    '''
    load the Version file and add the keys to a dictionary
    '''
    def loadVersionFile(self):
        separator = "="
        keys = {}

        data = Core.storage.load(self.VERSIONFILEPATH)

        for line in data.splitlines():
            if separator in line:
                name, value = line.split(separator, 1)
                keys[name.strip()] = value.strip()

        return keys

    '''
    get the current Version
    '''
    def getVersion(self):
        keys = self.loadVersionFile()
        version = keys["major.number"] + "." + keys["minor.number"] + "." + keys["build.number"]

        return version

    '''
    remove all ASCII characters from the name
    '''
    def removeAscii(self, name):
        return re.sub(r'[^\x00-\x7F]+', ' ', name)

    '''
    get response from a given URL with or without POST data
    '''
    def getResponse(self, url, data=None, headers={}):
        Log.Debug("[" + self.AGENT_NAME + "] " + "Requesting response from '" + url + "'")

        header = self.AGENT_HEADERS.copy()

        for h in headers:
            header[h] = headers[h]

        try:
            request = urllib2.Request(url, data, header)
            response = urllib2.urlopen(request, context=ssl.SSLContext(ssl.PROTOCOL_SSLv23), timeout=60)

            return response.read()
        except Exception as e:
            Log.Error("[" + self.AGENT_NAME + "] " + "Error getting response '" + str(e) + "'")
            return None

    '''
    return the JSON value for a key
    '''
    def getJsonValue(self, key, json):
        value = None

        if key in json:
            value = json[key]

        return value

    '''
    get an array from a JSON Array that only contains the individual keys as elements
    '''
    def getArrayFromJsonValue(self, key, json):
        elemArr = []

        for elem in json:
            elemName = self.getJsonValue(key, elem)
            elemArr.append(elemName)

        return elemArr

    '''
    calculate the match score between the two titles
    '''
    def calcMatchScore(self, title1, title2):
        #result = int(100 - abs(String.LevenshteinDistance(title1, title2)))
        result = int(difflib.SequenceMatcher(None, title1, title2).ratio() * 100)

        return result

    '''
    parse the Date from a JSON value
    '''
    def parseDateFromJson(self, key, json):
        date = None
        value = self.getJsonValue(key, json)

        if value is not None:
            date = Datetime.ParseDate(value)

        return date

    '''
    get only the year from the datetime
    '''
    def getYear(self, key, json):
        date = self.parseDateFromJson(key, json)
        if date is not None:
            return date.year
        else:
            return None

    '''
    get the date from the datetime
    '''
    def getDate(self, key, json):
        date = self.parseDateFromJson(key, json)

        return date.date()

    '''
    get the current Date
    '''
    def getNowDate(self):
        return Datetime.Now().date()

    '''
    get the regular expression match from a string
    '''
    def getRegExMatch(self, pattern, string, group):
        match = re.search(pattern, string)

        if match is not None:
            return match.group(group)
        else:
            return None

    '''
    get the mapping between MyAnimeList and TheTVDB/TheMovieDB
    '''
    def getMapping(self, id, key):
        Log.Info("[" + self.AGENT_NAME + "] " + "Requesting Mapping file")

        mappingFull = JSON.ObjectFromString(self.getResponse(self.getMappingUrl()))

        if mappingFull is not None:
            mappingkey = str(key) + "_id"
            mappingId = None

            for mapping in mappingFull:
                if "mal_id" in mapping:
                    malId = self.getJsonValue("mal_id", mapping)

                    if str(malId) == id:
                        mappingId = self.getJsonValue(mappingkey, mapping)

                        if mappingId == -1 or mappingId is None:
                            Log.Info("[" + self.AGENT_NAME + "] " + "Mapping was available for mal_id=" + str(malId) + " but ID for '" + str(key) + "' was not valid or did not exist")
                            return None
                        else:
                            Log.Info("[" + self.AGENT_NAME + "] " + "Mapping found: " + str(key) + " = " + str(mappingId))
                            return mappingId

            return mappingId
        else:
            Log.Error("[" + self.AGENT_NAME + "] " + "Mapping file could not be requested")
            return None

    '''
    request the image
    '''
    def requestImage(self, url):

        try:
            media = Proxy.Media(HTTP.Request(str(url), sleep=2.0).content)
            return media
        except Exception as e:
            Log.Error("[" + self.AGENT_NAME + "] " + "Image could not be requested: " + str(e))
            return None

    '''
    Get the specific title for the selected language from the available titles list
    '''
    def getTitle(self, titlesJsonArray, preferred):

        defaultTitle = ""

        # get the title in the preferred language
        for elem in titlesJsonArray:
            type = self.getJsonValue("type", elem)
            title = self.getJsonValue("title", elem)

            if (type == "Default"):
                defaultTitle = title

            if (type == preferred):
                return title

        # fallback to default
        return defaultTitle

    '''
    Get the main Directory of the Media 
    '''
    def getMediaDirectory(self, media, type):
        if (type == "show"):
            return os.path.dirname(media.seasons[1].episodes[1].items[0].parts[0].file)
        elif (type == "movie"):
            return os.path.dirname(media.items[0].parts[0].file)
        else:
            return None
    '''
    read the .match file and return a dictionary with the key/value pairs
    '''
    def readMatchFile(self, path):
        try:
            matchValues = {}

            for elem in Data.Load(path).split("\n"):
                elem = elem.replace("\r", "")
                if elem.startswith('title'):
                    matchValues['title'] = elem.replace("title: ","")
                if elem.startswith('mal-id'):
                    matchValues['mal-id'] = elem.replace("mal-id: ","")

            Log.Debug("[" + self.AGENT_NAME + "] " + ".match values: " + str(matchValues))
            return matchValues

        except Exception as e:
            Log.Error("[" + self.AGENT_NAME + "] " + "Error reading .match file '" + str(e) + "'")
            return None