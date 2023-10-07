import json
import os
from .miscexporter import MiscExporter
from qgis.core import Qgis, QgsMessageLog

class GeoExporter:

    def filterGeoClasses(self):

    @staticmethod
    def convertTTLToGeoJSON(g, file, subjectstorender=None,classlist=None, formatt="json"):
        QgsMessageLog.logMessage("Classlist " + str(classlist), "OntdocGeneration", Qgis.Info)
        if subjectstorender == None:
            subjectstorender = g.subjects(None, None, True)
        res = MiscExporter.detectSubjectType(g, subjectstorender)
        subjectsToType = res[0]
        typeToFields = res[1]
        typeToRes = {}
        for type in typeToFields:
            typeToRes[type] = []
        for sub in subjectstorender:
            if str(sub) not in subjectsToType:
                continue
            res = {}
            for tup in g.predicate_objects(sub):
                res[str(tup[0])] = str(tup[1])
            typeToRes[subjectsToType[str(sub)]].append(res)
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + MiscExporter.shortenURI(
                type) + "." + formatt, "w")
            f.write("\n")
            for res in typeToRes[type]:
                f.write(json.dumps(res))
            f.close()
        return None