git from qgis.core import Qgis,QgsTask, QgsMessageLog
import os
import time

MESSAGE_CATEGORY = 'CacheUtils'

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class CacheUtils:

    CLASSTREECACHE_EXPIRY=14

    GEOCONCEPTS_EXPIRY=14

    GRAPHCACHE_EXPIRY=30

    @staticmethod
    def is_file_older_than_x_days(path, days=1):
        modtime=os.path.getmtime(path)
        return ((time.time() - modtime) / 3600 > 24 * days)

    @staticmethod
    def graphCacheSize():
        graphcachesize=0
        thepath=os.path.join(__location__,"../../tmp/graphcache/")
        if os.path.exists(thepath):
            graphcachesize= len([name for name in os.listdir(thepath) if os.path.isfile(os.path.join(thepath,name))])
        return graphcachesize

    @staticmethod
    def classTreeCacheSize():
        classtreesize = 0
        thepath = os.path.join(__location__, "../../tmp/classtree/")
        if os.path.exists(thepath):
            classtreesize = len([name for name in os.listdir(thepath) if os.path.isfile(os.path.join(thepath,name))])
        return classtreesize

    @staticmethod
    def geoconceptsCacheSize():
        geoconceptssize = 0
        thepath = os.path.join(__location__, "../../tmp/geoconcepts/")
        if os.path.exists(thepath):
            geoconceptssize = len([name for name in os.listdir(thepath) if os.path.isfile(os.path.join(thepath,name))])
        return geoconceptssize

    @staticmethod
    def deleteGeoConceptsCache():
        dir=os.path.join(__location__ , "../../tmp/geoconcepts/")
        if os.path.exists(dir):
            for f in os.listdir(dir):
                if not f.endswith(".json"):
                    continue
                os.remove(os.path.join(dir, f))

    @staticmethod
    def deleteGraphCache():
        dir=os.path.join(__location__ , "../../tmp/graphcache/")
        if os.path.exists(dir):
            for f in os.listdir(dir):
                if not f.endswith(".ttl"):
                    continue
                os.remove(os.path.join(dir, f))

    @staticmethod
    def deleteClassTreeCache():
        dir=os.path.join(__location__ ,"../../tmp/classtree/")
        if os.path.exists(dir):
            for f in os.listdir(dir):
                if not f.endswith(".json"):
                    continue
                os.remove(os.path.join(dir, f))