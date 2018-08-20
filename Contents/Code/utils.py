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