
class ConfigUtils:

    @staticmethod
    def isOldConfigurationFile(configjson):
        for item in configjson:
            if "endpoint" in item:
                return True
        return False

    @staticmethod
    def migrateOldConfigurationFile(configjson):
        for item in configjson:
            if "endpoint" in item:
                item["resource"]={"type": "endpoint","url":item["endpoint"]}
                del item["endpoint"]
        return configjson