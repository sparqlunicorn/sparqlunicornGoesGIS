import json
import os

from ...doc.docutils import DocUtils


class GeoExporter:

    @staticmethod
    def filterGeoClasses(classlist):
        #geoclasslist=set()
        #for cls in classlist:
        #    if classlist[cls]["item"]["type"]=="geoclass":
        #        geoclasslist.add(classlist[cls]["item"]["id"])
        return {classlist[cls]["item"]["id"] for cls in classlist if classlist[cls]["item"]["type"]=="geoclass"}
        #geoclasslist


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
            substr=str(sub)
            typeToFields[substr]=set()
            for tup in g.predicate_objects(sub):
                if str(tup[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and str(tup[1]) in geoclasslist:
                    subjectsToType[substr]=str(tup[1])
                typeToFields[substr].add(str(tup[0]))
            if substr in subjectsToType:
                if subjectsToType[substr] not in typeToFields:
                    typeToFields[subjectsToType[substr]]=set()
                typeToFields[subjectsToType[substr]]=typeToFields[subjectsToType[substr]].union(typeToFields[substr])
                del typeToFields[substr]
        return [subjectsToType,typeToFields]


    @staticmethod
    def convertTTLToGeoJSON(g, file, subjectstorender=None,classlist=None, formatt="json"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("." + formatt, "")}_{DocUtils.shortenURI(type)}.{formatt}', "w", encoding="utf-8") as f:
                #resjson={"type":"FeatureCollection","features":[{"type":"Feature","properties":res,"geometry":typeToGeom[type]} for res in typeToRes[type]]}
                #for res in typeToRes[type]:
                #    resjson["features"].append({"type":"Feature","properties":res,"geometry":typeToGeom[type]})
                json.dump({"type":"FeatureCollection","features":[{"type":"Feature","properties":res,"geometry":typeToGeom[type]} for res in typeToRes[type]]},f)
        return None

    @staticmethod
    def preprocessGeometryData(g,file,subjectstorender,classlist,formatt):
        if subjectstorender is None:
            subjectstorender = g.subjects(None, None, True)
        geoclasslist=GeoExporter.filterGeoClasses(classlist)
        res=GeoExporter.detectSubjectType(g,subjectstorender,geoclasslist)
        subjectsToType = res[0]
        typeToFields = res[1]
        typeToRes = dict((el,[]) for el in typeToFields)
        typeToGeo={}
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in subjectsToType:
                continue
            res = {}
            for tup in g.predicate_objects(sub):
                res[str(tup[0])] = str(tup[1])
                geojsonrep=DocUtils.resolveGeoLiterals(tup[0], tup[1], g, {}, None , sub)
                if geojsonrep!={}:
                    typeToGeo[subjectsToType[substr]].append(geojsonrep)
            typeToRes[subjectsToType[substr]].append(res)
        return [typeToFields,typeToRes,typeToGeo]

    @staticmethod
    def convertTTLToKML(g, file, subjectstorender=None,classlist=None, formatt="kml"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("." + formatt, "")}_{DocUtils.shortenURI(type)}.{formatt}', "w", encoding="utf-8") as f:
                f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?><kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">\n")
                f.write("<Placemark>\n")
                f.write(f'<{typeToGeom[type]["type"]}>\n<coordinates>\n')
                f.write(str(typeToGeom[type]["coordinates"]).replace("[","").replace("]",""))
                f.write(f'</coordinates>\n</{typeToGeom[type]["type"]}>\n')
                f.write("</Placemark>\n</kml>")
        return None

    @staticmethod
    def convertTTLToMapML(g, file, subjectstorender=None,classlist=None, formatt="mapml"):
        ress=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=ress[0]
        typeToRes=ress[1]
        typeToGeom=ress[2]
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("." + formatt, "")}_{DocUtils.shortenURI(type)}.{formatt}', "w", encoding="utf-8") as f:
                f.write("<mapml>\n<head>\n<title></title>\n</head>\n<body>\n")
                for res in typeToRes[type]:
                    f.write("<feature id=\""+str("")+"\" \"itemscope\"=\"itemscope\">\n")
                    f.write("<properties>\n<div class=\"table-container\"><table>\n<caption>Feature Properties</caption>\n<thead><tr><th>Property</th><th>Value</th></tr></thead>\n<tbody>\n")
                    for prop in res:
                        f.write(f'<tr>\n<td itemprop="{prop}"><a href="{str(prop)}">{DocUtils.shortenURI(prop)}</a></td>\n')
                        if str(res[prop]).startswith("http"):
                            f.write(f'<td><a href={res[prop]}">{DocUtils.shortenURI(res[prop])}</a></td>\n')
                        elif "^^" in str(res[prop]):
                            f.write(f'<td><a href="{str(res[prop])[res[prop].rfind("^^")+1:]}">"{res[prop][0:res[prop].rfind("^^")-2]}</a></td>\n')
                        else:
                            f.write(f'<td>{res[prop]}</td>\n')
                        f.write("</tr>\n")
                    f.write("</tbody>\n</table>\n</properties>\n")
                    f.write("<geometry>\n")
                    f.write(f'<{typeToGeom[res]["type"]}>\n')
                    f.write("<coordinates>\n")
                    f.write(GeoExporter.geometryToCoordinateList(typeToGeom[res]))
                    f.write("</coordinates>\n")
                    f.write("</"+str(typeToGeom[res]["type"])+">\n")
                    f.write("</geometry>\n")
                    f.write("</feature>\n")
                f.write("</body>\n</mapml>")
        return None

    @staticmethod
    def convertTTLToGeoURI(g, file, subjectstorender=None,classlist=None, formatt="geouri"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("." + formatt, "")}_{DocUtils.shortenURI(type)}.{formatt}', "w", encoding="utf-8") as f:
                f.write(f'geo:{str(typeToGeom[type]["coordinates"]).replace("[","").replace("]","")}\n')
        return None


    @staticmethod
    def convertTTLToWKT(g, file, subjectstorender=None,classlist=None, formatt="wkt"):
        res=GeoExporter.preprocessGeometryData(g,file,subjectstorender,classlist,formatt)
        typeToFields=res[0]
        typeToRes=res[1]
        typeToGeom=res[2]
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("." + formatt, "")}_{DocUtils.shortenURI(type)}.{formatt}', "w", encoding="utf-8") as f:
                f.write(f'{typeToGeom[type]["type"]}({typeToGeom[type]["coordinates"]})\n')
        return None