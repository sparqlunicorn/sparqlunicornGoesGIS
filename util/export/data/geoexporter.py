import json
import os

from ...doc.docutils import DocUtils


class GeoExporter:

    @staticmethod
    def filterGeoClasses(classlist):
        geoclasslist=set()
        for cls in classlist:
            if classlist[cls]["item"]["type"]=="geoclass":
                geoclasslist.add(classlist[cls]["item"]["id"])
        return geoclasslist


    @staticmethod
    def geometryToCoordinateList(geometry):
        reslist=[]
        if geometry['type'] == 'Polygon':
            reslist.extend(geometry['coordinates'][0])
            reslist.append([None, None])  # mark the end of a polygon
        elif geometry['type'] == 'LineString':
            reslist.extend(geometry['coordinates'])
        elif geometry['type'] == 'Point':
            reslist.extend(geometry['coordinates'])
        return reslist

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
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w", encoding="utf-8")
            resjson={"type":"FeatureCollection","features":[]}
            for res in typeToRes[type]:
                resjson["features"].append({"type":"Feature","properties":res,"geometry":typeToGeom[type]})
            f.write(json.dumps(resjson))
            f.close()
        return None

    @staticmethod
    def preprocessGeometryData(g,file,subjectstorender,classlist,formatt):
        if subjectstorender == None:
            subjectstorender = g.subjects(None, None, True)
        geoclasslist=GeoExporter.filterGeoClasses(classlist)
        res=GeoExporter.detectSubjectType(g,subjectstorender,geoclasslist)
        subjectsToType = res[0]
        typeToFields = res[1]
        typeToRes = {}
        typeToGeo={}
        for type in typeToFields:
            typeToRes[type] = []
        for sub in subjectstorender:
            if str(sub) not in subjectsToType:
                continue
            res = {}
            for tup in g.predicate_objects(sub):
                res[str(tup[0])] = str(tup[1])
                geojsonrep=DocUtils.resolveGeoLiterals(tup[0], tup[1], g, {}, None , sub)
                if geojsonrep!={}:
                    typeToGeo[subjectsToType[str(sub)]].append(geojsonrep)
            typeToRes[subjectsToType[str(sub)]].append(res)
        return [typeToFields,typeToRes,typeToGeo]

    @staticmethod
    def convertTTLToKML(g, file, subjectstorender=None,classlist=None, formatt="kml"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w", encoding="utf-8")
            f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?><kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">\n")
            f.write("<Placemark>\n")
            f.write("<"+str(typeToGeom[type]["type"]+">\n<coordinates>\n"))
            f.write(str(typeToGeom[type]["coordinates"].replace("[","").replace("]","")))
            f.write("</coordinates>\n</"+str(typeToGeom[type]["type"])+">\n")
            f.write("</Placemark>\n</kml>")
            f.close()
        return None

    @staticmethod
    def convertTTLToMapML(g, file, subjectstorender=None,classlist=None, formatt="mapml"):
        ress=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=ress[0]
        typeToRes=ress[1]
        typeToGeom=ress[2]
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w", encoding="utf-8")
            f.write("<mapml>\n<head>\n<title></title>\n</head>\n<body>\n")
            for res in typeToRes[type]:
                f.write("<feature id=\""+str("")+"\" \"itemscope\"=\"itemscope\">\n")
                f.write("<properties>\n<div class=\"table-container\"><table>\n<caption>Feature Properties</caption>\n<thead><tr><th>Property</th><th>Value</th></tr></thead>\n<tbody>\n")
                for prop in res:
                    f.write("<tr>\n<td itemprop=\""+str(prop)+"\"><a href=\""+str(prop)+"\">"+DocUtils.shortenURI(prop)+"</a></td>\n")
                    if str(res[prop]).startswith("http"):
                        f.write("<td><a href=\""+str(res[prop])+"\">"+DocUtils.shortenURI(res[prop])+"</a></td>\n")
                    elif "^^" in str(res[prop]):
                        f.write("<td><a href=\""+str(res[prop][res[prop].rfind("^^")+1:])+"\">"+res[prop][0:res[prop].rfind("^^")-2]+"</a></td>\n")
                    else:
                        f.write("<td>"+str(res[prop])+"</td>\n")
                    f.write("</tr>\n")
                f.write("</tbody>\n</table>\n</properties>\n")
                f.write("<geometry>\n")
                f.write("<"+str(typeToGeom[res]["type"])+">\n")
                f.write("<coordinates>\n")
                f.write(GeoExporter.geometryToCoordinateList(typeToGeom[res]))
                f.write("</coordinates>\n")
                f.write("</"+str(typeToGeom[res]["type"])+">\n")
                f.write("</geometry>\n")
                f.write("</feature>\n")
            f.write("</body>\n</mapml>")
            f.close()
        return None

    @staticmethod
    def convertTTLToGeoURI(g, file, subjectstorender=None,classlist=None, formatt="geouri"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w", encoding="utf-8")
            f.write("geo:"+str(typeToGeom[type]["coordinates"]).replace("[","").replace("]","")+"\n")
            f.close()
        return None

    @staticmethod
    def convertTTLToWKT(g, file, subjectstorender=None,classlist=None, formatt="wkt"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w", encoding="utf-8")
            f.write(str(typeToGeom[type]["type"])+"("+str(typeToGeom[type]["coordinates"])+")\n")
            f.close()
        return None