import json
import os

from .....doc.docutils import DocUtils

class GeoExporter:

    @staticmethod
    def getExporterString():
        return "GeoData (*.geojson)"

    @staticmethod
    def filterGeoClasses(classlist):
        geoclasslist=set()
        for cls in classlist:
            if classlist[cls]["item"]["type"]=="geoclass":
                geoclasslist.add(classlist[cls]["item"]["id"])
        return geoclasslist

    @staticmethod
    def detectSubjectType(g,subjectstorender,geoclasslist):
        subjectsToType={}
        typeToFields={}
        for sub in subjectstorender:
            typeToFields[str(sub)]=set()
            for tup in g.predicate_objects(sub):
                if str(tup[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and str(tup[1]) in geoclasslist:
                    subjectsToType[str(sub)]=str(tup[1])
                typeToFields[str(sub)].add(str(tup[0]))
            if str(sub) in subjectsToType:
                if subjectsToType[str(sub)] not in typeToFields:
                    typeToFields[subjectsToType[str(sub)]]=set()
                typeToFields[subjectsToType[str(sub)]]=typeToFields[subjectsToType[str(sub)]].union(typeToFields[str(sub)])
                del typeToFields[str(sub)]
        return [subjectsToType,typeToFields]


    @staticmethod
    def convertTTLToGeoJSON(g, file, subjectstorender=None,classlist=None, formatt="json"):
        if subjectstorender == None:
            subjectstorender = g.subjects(None, None, True)
        geoclasslist=GeoExporter.filterGeoClasses(classlist)
        res=GeoExporter.detectSubjectType(g,subjectstorender,geoclasslist)
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
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w", encoding="utf-8")
            resjson={"type":"FeatureCollection","features":[]}
            for res in typeToRes[type]:
                resjson["features"].append({"type":"Feature","properties":res,"geometry":{"type":"Point","coordinates":[]}})
            f.write(json.dumps(resjson))
            f.close()
        return None