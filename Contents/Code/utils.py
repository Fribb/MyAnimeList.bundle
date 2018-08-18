'''
Last update on 26.05.2018

Plex Media Server Metadata Agent for MyAnimeList.net

TODO: Description

@author: Fribb http://coding.fribbtastic.net/
'''

import re
import difflib

'''Constants'''
AGENT_NAME = "MyAnimeList.net"

UTILS_DEFAULT_HEADERS = {'User-agent': 'Plex/MyAnimeList-Agent'}
UTILS_DEFAULT_CACHE_TIME = CACHE_1HOUR * 24


class Utils():
    
    '''
    Deprecated!!
    Fetch the content of an URL
    '''
    def fetchContent(self, url, additionalHeaders=None, cacheTime=None):
        Log.Info("[" + AGENT_NAME + "] [Utils] " + "Fetching URL " + str(url))
        result = None
        headers = None
        
        if additionalHeaders is None:
            additionalHeaders = dict()
        
        if additionalHeaders is not False:
            headers = UTILS_DEFAULT_HEADERS.copy()
            headers.update(additionalHeaders)
        
        if cacheTime is None:
            cacheTime = UTILS_DEFAULT_CACHE_TIME
        
        try:
            result = HTTP.Request(url, headers, sleep=2.0, cacheTime=cacheTime).content
            
        except Exception as e:
            Log.Error("[" + AGENT_NAME + "] [Utils] " + "Error occurred while fetching the content for URL: " + str(e))
            
        return result
    
    '''
    Method to remove all ASCII from the text
    '''
    def removeASCII(self, text):
        return re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    '''
    Method to remove all HTML tags
    '''
    def removeTags(self, text):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', text)
        return cleantext

    '''
    Method to get the JSON value of a key
    '''
    def getJSONValue(self, key, json):
        value = None
        
        if key in json:
            value = json[key]
        
        return value
    
    '''
    Method to calculate the Match Score of the titles
    '''
    def getMatchScore(self, title1, title2):
        #result = int(100 - abs(String.LevenshteinDistance(title1, title2)))
        result = int(difflib.SequenceMatcher(None, title1, title2).ratio() * 100)
        
        return result