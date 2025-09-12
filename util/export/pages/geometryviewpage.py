from rdflib import URIRef, Literal
from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils
from ...doc.literalutils import LiteralUtils

from .owltimepage import OWLTimePage

from qgis.core import QgsGeometry, QgsGeometryCollection, QgsJsonUtils
#import shapely.wkt
#import shapely.geometry
import json


class GeometryViewPage:

    def createSVGFromWKT(self, templates, features, f):
        thepath = "<svg>"
        #geomcoll = shapely.geometry.GeometryCollection(
        #    [shapely.geometry.shape(feature["geometry"]) for feature in features["features"]])
        #svgpath = geomcoll.svg()
        # print(svgpath)
        #thepath += svgpath
        thepath += "</svg>"
        # print(thepath)
        f.write(templates["imagestemplatesvg"].replace("{{carousel}}", "image").replace("{{image}}",
                                                                                        str(thepath.replace("<svg>",
                                                                                                            "<svg class=\"svgview\">"))))

    def generatePageWidget(self, graph, subject, templates, f, uritotreeitem, geojsonrep, predobjmap, geocache,
                           parameters={}, onlybody=False):
        if uritotreeitem is not None and str(subject) in uritotreeitem:
            uritotreeitem[str(subject)][-1]["type"] = "geoinstance"
        props = predobjmap
        dateprops = parameters.get("dateprops", [])
        epsgcode = parameters.get("epsgcode", "")
        if parameters.get("timeobj") is not None:
            #print(parameters.get("timeobj"))
            dateprops+=[item for item in parameters.get("timeobj")]
            #for item in parameters.get("timeobj"):
            #    dateprops.append(item)
                #props[item] = str(parameters.get("timeobj")[item])
                #props[item] = str(item)
        jsonfeat = {"type": "Feature", 'id': str(subject), 'name': parameters.get("foundlabel", ""),
                    'dateprops': dateprops, 'properties': props, "geometry": geojsonrep}
        if epsgcode == "" and "crs" in geojsonrep:
            epsgcode = "EPSG:" + geojsonrep["crs"]
            jsonfeat["crs"] = epsgcode
        if parameters.get("hasnonnslen", 0) > 0:
            geocache[str(subject)] = jsonfeat
        geom = {"has_z":False}
        #QgsJsonUtils.geometryFromJson(jsonfeat["geometry"])
        if geom["has_z"]:
            self.createSVGFromWKT(templates, {"type": "FeatureCollection", "features": [jsonfeat]}, f)
        else:
            f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",
                                                                                                f'[{json.dumps(jsonfeat)}]').replace(
                "{{relativepath}}",
                DocUtils.generateRelativePathFromGivenDepth(parameters.get("checkdepth", 0))).replace("{{epsg}}",
                                                                                                      epsgcode).replace(
                "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsgdefspath}}",
                                                                            parameters.get("epsgdefslink", "")).replace(
                "{{dateatt}}", str(dateprops)))
        return geocache


    def generateCollectionWidget(self, graph, subject, templates, f, uritotreeitem, featurecollectionspaths,
                                 parameters={"foundlabel": ""}):
        if parameters.get("foundlabel") is not None and parameters.get("foundlabel") != "":
            featcoll = {"type": "FeatureCollection", "id": subject, "name": str(parameters["foundlabel"]),
                        "features": []}
        else:
            featcoll = {"type": "FeatureCollection", "id": subject, "name": DocUtils.shortenURI(subject),
                        "features": []}
        geocache = parameters.get("geocache", {})
        nonns = parameters.get("nonns", False)
        hasnonns = parameters.get("hasnonns", {})
        thecrs = set()
        dateatt = ""
        memberpred = URIRef("http://www.w3.org/2000/01/rdf-schema#member")
        if not nonns:
            for memberid in graph.objects(subject, memberpred, True):
                memberidstr = str(memberid)
                geojsonrep = None
                timeobj = {}
                dateatt = []
                properties = {}
                for geoinstance in graph.predicate_objects(memberid, True):
                    geoinstance0str = str(geoinstance[0])
                    geoinstance1str = str(geoinstance[1])
                    if isinstance(geoinstance[1], Literal) and (
                            geoinstance0str in DocConfig.geoproperties or str(
                        geoinstance[1].datatype) in DocConfig.geoliteraltypes):
                        geojsonrep = LiteralUtils.processLiteral(geoinstance1str, str(geoinstance[1].datatype), "")
                        uritotreeitem[str(subject)][-1]["type"] = "geocollection"
                    elif geoinstance0str in DocConfig.geopointerproperties:
                        uritotreeitem[str(subject)][-1]["type"] = "featurecollection"
                        for geotup in graph.predicate_objects(geoinstance[1], True):
                            if isinstance(geotup[1], Literal) and (str(geotup[0]) in DocConfig.geoproperties or str(
                                    geotup[1].datatype) in DocConfig.geoliteraltypes):
                                geojsonrep = LiteralUtils.processLiteral(str(geotup[1]), str(geotup[1].datatype), "")
                                break
                    else:
                        if geoinstance0str in DocConfig.timepointerproperties:
                            timeobj = OWLTimePage.resolveTimeLiterals(geoinstance[0], geoinstance[1], graph)
                            for key in timeobj:
                                dateatt.append(key)
                                properties[key] = str(timeobj[key])
                        elif isinstance(geoinstance[1], URIRef):
                            foundunit = None
                            foundval = None
                            # print("RESOLVE UNIT FROM: "+str(geoinstance[1]))
                            res = DocUtils.resolveUnitValue(graph, geoinstance[1], None, geoinstance1str, foundunit,
                                                            foundval)
                            foundval = res[0]
                            foundunit = res[1]
                            # print("FOUNDVAL: "+str(foundval)+" FOUNDUNIT: "+str(foundunit))
                            if foundval is not None:
                                properties[geoinstance0str + ".value"] = foundval
                            if foundunit is not None:
                                properties[geoinstance0str + ".unit"] = foundunit
                        else:
                            properties[geoinstance0str] = geoinstance1str
                    # print(geojsonrep)
                if geojsonrep is not None and geojsonrep != "" and isinstance(geojsonrep,
                                                                              dict) and "coordinates" in geojsonrep and len(
                        geojsonrep["coordinates"]) > 0:
                    if uritotreeitem is not None and memberidstr in uritotreeitem:
                        featcoll["features"].append({"type": "Feature", 'id': memberidstr,
                                                     'name': uritotreeitem[memberidstr][-1]["text"],
                                                     'dateprops': list(timeobj.keys()), 'properties': properties,
                                                     "geometry": geojsonrep})
                    else:
                        featcoll["features"].append(
                            {"type": "Feature", 'id': memberidstr, 'name': memberidstr,
                             'dateprops': list(timeobj.keys()),
                             'properties': properties, "geometry": geojsonrep})
                    if len(featcoll["features"][-1]["dateprops"]) > 0:
                        dateatt = featcoll["features"][-1]["dateprops"][0]
                    if "crs" in geojsonrep:
                        thecrs.add(geojsonrep["crs"])
                        # break
            if parameters.get("hasnonnslen", 0) > 0:
                geocache[str(subject)] = featcoll
        else:
            for item in hasnonns:
                if item in geocache:
                    featcoll["features"].append(geocache[item])
                    if len(geocache[item]["dateprops"]) > 0:
                        dateatt = geocache[item]["dateprops"][0]
                    if "crs" in geocache[item]:
                        thecrs.add(geocache[item]["crs"])
        if len(featcoll["features"]) > 0:
            featcoll["numberMatched"] = len(featcoll["features"])
            featcoll["numberReturned"] = len(featcoll["features"])
            geomcoll={"has_z":False}
            #geomcoll =QgsGeometryCollection shapely.geometry.GeometryCollection(
            #    [QgsJsonUtils.geometryFromJson(feature["geometry"]) for feature in featcoll["features"]])
            #featcoll["bbox"] = geomcoll.bounds
            if geomcoll["has_z"]:
                self.createSVGFromWKT(templates, featcoll, f)
            else:
                firstcrs = "4326"
                featcoll["crs"] = "http://www.opengis.net/def/crs/EPSG/0/4326"
                if len(thecrs) > 0:
                    firstcrs = str(next(iter(thecrs)))
                    featcoll["crs"] = "http://www.opengis.net/def/crs/EPSG/0/" + firstcrs
                epsgcode = "EPSG:" + firstcrs
                if len(dateatt) > 0:
                    for feat in featcoll["features"]:
                        if dateatt not in feat["properties"]:
                            feat["properties"][dateatt] = ""
                if parameters.get("localOptimized", False):
                    f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",
                                                                                                        f'[{json.dumps(featcoll)}]').replace(
                        "{{relativepath}}",
                        DocUtils.generateRelativePathFromGivenDepth(parameters.get("checkdepth", 0))).replace(
                        "{{epsg}}",
                        epsgcode).replace(
                        "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsgdefspath}}",
                                                                                    parameters.get("epsgdefslink",
                                                                                                   "")).replace(
                        "{{dateatt}}",
                        str(dateatt)))
                else:
                    f.write(templates["maptemplate"].replace("{{myfeature}}",
                                                             f'["{DocUtils.shortenURI(str(parameters.get("completesavepath", "").replace(".html", ".geojson")))}"]').replace(
                        "{{relativepath}}",
                        DocUtils.generateRelativePathFromGivenDepth(
                            parameters.get("checkdepth", 0))).replace(
                        "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsg}}",
                                                                                    epsgcode).replace(
                        "{{epsgdefspath}}",
                        parameters.get(
                            "epsgdefslink",
                            "")).replace(
                        "{{dateatt}}",
                        str(dateatt)))
                spath = parameters.get("completesavepath", "").replace(".html", ".geojson")
                with open(spath, 'w', encoding='utf-8') as fgeo:
                    featurecollectionspaths[spath] = {
                        "name": featcoll["name"],
                        "id": featcoll["id"]}
                    json.dump(featcoll, fgeo)
        return geocache

    def generatePageView(self, headertemplate, footertemplate, g, f):
        f.write(str(headertemplate))
