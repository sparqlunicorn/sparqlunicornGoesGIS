
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
    def dumper(obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__