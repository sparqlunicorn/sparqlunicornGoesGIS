from enum import Enum
from qgis.core import QgsStringUtils

class StringMatching(Enum):
     LEVENSTHEIN = 1
     HAMMING = 2
     SUBSTRING = 3

class MatchingTools:



    @staticmethod
    def matchString(originalString,comparisonString,matchingMethod,threshold):
        if matchingMethod==StringMatching.LEVENSTHEIN:
            return QgsStringUtils.levenshteinDistance(originalString, comparisonString, False)<threshold
        elif matchingMethod==StringMatching.HAMMING:
            return QgsStringUtils.hammingDistance(originalString,comparisonString,False)<threshold
        elif matchingMethod==StringMatching.SUBSTRING:
            return len(comparisonString)/QgsStringUtils.longestCommonSubstring(originalString, comparisonString, False)>threshold
        return False

    @staticmethod
    def matchStringMapToReference(map,reference,matchingMethod,threshold=0.8):
        resmap=[]
        for curstr in map:
            if MatchingTools.matchString(reference,curstr,matchingMethod,threshold):
                resmap.append(curstr)
        return resmap


