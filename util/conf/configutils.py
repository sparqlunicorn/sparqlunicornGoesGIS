from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'ConfigUtils'

class ConfigUtils:

    @staticmethod
    ##
    #  @brief Checks if an old triplestore.conf file is present
    #
    #  @param configjson the configuration file to check
    #
    def isOldConfigurationFile(configjson):
        for item in configjson:
            if "endpoint" in item:
                return True
        return False

    @staticmethod
    ##
    #  @brief Migrates an old triplestore.conf file to its newer version
    #
    #  @param configjson the configuration file to migrate
    #
    def migrateOldConfigurationFile(configjson):
        for item in configjson:
            if "endpoint" in item:
                item["resource"]={"type": "endpoint","url":item["endpoint"]}
                del item["endpoint"]
        return configjson

    @staticmethod
    def removeInstanceKeys(triplestoreconf,key):
        if isinstance(triplestoreconf, dict):
            return {k: ConfigUtils.removeInstanceKeys(v, key) for k, v in triplestoreconf.items() if k != key}

        elif isinstance(triplestoreconf, list):
            return [ConfigUtils.removeInstanceKeys(element, key) for element in triplestoreconf]

        else:
            return triplestoreconf


    @staticmethod
    def dumper(obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__

    @staticmethod
    def updateTripleStoreConf(triplestoreconf,newtriplestoreconf,removeold=False):
        triplestoreconfindex={}
        urltoindex={}
        seentriplestores={}
        counter=0
        for conf in triplestoreconf:
            if "resource" in conf and conf["resource"]["type"]=="endpoint":
                triplestoreconfindex[conf["resource"]["url"]]=conf
                seentriplestores[conf["resource"]["url"]]=True
                urltoindex[conf["resource"]["url"]]=str(counter)
                counter+=1
        QgsMessageLog.logMessage('TripleStoreConfIndex' + str(triplestoreconfindex), MESSAGE_CATEGORY, Qgis.Info)
        for nconf in newtriplestoreconf:
            QgsMessageLog.logMessage('NCONF ' + str(nconf), MESSAGE_CATEGORY, Qgis.Info)
            if "resource" in nconf and nconf["resource"]["type"] == "endpoint":
                if nconf["resource"]["url"] in triplestoreconfindex:
                    QgsMessageLog.logMessage('Updating conf for ' + str(nconf["resource"]["url"]), MESSAGE_CATEGORY, Qgis.Info)
                    triplestoreconfindex[nconf["resource"]["url"]]=nconf
                    del seentriplestores[nconf["resource"]["url"]]
                else:
                    QgsMessageLog.logMessage('Found new conf for ' + str(nconf["resource"]["url"]), MESSAGE_CATEGORY,Qgis.Info)
                    triplestoreconf.append(nconf)
        if removeold:
            for ts in seentriplestores:
                if ts in urltoindex:
                    del triplestoreconf[urltoindex[ts]]
        return triplestoreconf



