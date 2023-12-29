from rdflib import URIRef, Literal
from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils
from ...layerutils import LayerUtils
from ...sparqlutils import SPARQLUtils

import shapely.wkt
import shapely.geometry
import json


class GeometryViewPage:

    def generatePageWidget(self,graph,templates,subject,f,uritotreeitem,geojsonrep,predobjmap,geocache,parameters={},onlybody=False):
        print("PageWidget")
        if uritotreeitem != None and str(subject) in uritotreeitem:
            uritotreeitem[str(subject)][-1]["type"] = "geoinstance"
        props = predobjmap
        dateprops=parameters.get("dateprops",[])
        epsgcode=parameters.get("epsgcode","")
        if parameters.get("timeobj") != None:
            for item in parameters.get("timeobj"):
                dateprops.append(item)
                props[item] = str(parameters.get("timeobj")[item])
        jsonfeat = {"type": "Feature", 'id': str(subject), 'name': parameters.get("foundlabel",""), 'dateprops': dateprops,
                    'properties': props, "geometry": geojsonrep}
        if epsgcode == "" and "crs" in geojsonrep:
            epsgcode = "EPSG:" + geojsonrep["crs"]
        if parameters.get("hasnonnslen",0) > 0:
            geocache[str(subject)] = jsonfeat
        f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",
                                                                                            "[" + json.dumps(
                                                                                                jsonfeat) + "]").replace(
            "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(parameters.get("checkdepth",0))).replace("{{epsg}}",
                                                                                                 epsgcode).replace(
            "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsgdefspath}}", parameters.get("epsgdefslink","")).replace(
            "{{dateatt}}", ""))
        return geocache

    def generateCollectionWidget(self,graph,templates,subject,f,uritotreeitem,featurecollectionspaths,parameters={"foundlabel":""}):
        print("CollectionWidget")
        if parameters.get("foundlabel") != None and parameters.get("foundlabel") != "":
            featcoll = {"type": "FeatureCollection", "id": subject, "name": str(parameters["foundlabel"]), "features": []}
        else:
            featcoll = {"type": "FeatureCollection", "id": subject, "name": DocUtils.shortenURI(subject),
                        "features": []}
        geocache=parameters.get("geocache",{})
        nonns=parameters.get("nonns",False)
        hasnonns=parameters.get("hasnonns",{})
        thecrs = set()
        dateatt = ""
        memberpred = URIRef("http://www.w3.org/2000/01/rdf-schema#member")
        if not nonns:
            for memberid in graph.objects(subject, memberpred, True):
                for geoinstance in graph.predicate_objects(memberid, True):
                    geojsonrep = None
                    if geoinstance != None and isinstance(geoinstance[1], Literal) and (
                            str(geoinstance[0]) in SPARQLUtils.geoproperties or str(
                            geoinstance[1].datatype) in SPARQLUtils.geoliteraltypes):
                        geojsonrep = LayerUtils.processLiteral(str(geoinstance[1]), str(geoinstance[1].datatype), "")
                        uritotreeitem[str(subject)][-1]["type"] = "geocollection"
                    elif geoinstance != None and str(geoinstance[0]) in SPARQLUtils.geopointerproperties:
                        uritotreeitem[str(subject)][-1]["type"] = "featurecollection"
                        for geotup in graph.predicate_objects(geoinstance[1], True):
                            if isinstance(geotup[1], Literal) and (str(geotup[0]) in SPARQLUtils.geoproperties or str(
                                    geotup[1].datatype) in SPARQLUtils.geoliteraltypes):
                                geojsonrep = LayerUtils.processLiteral(str(geotup[1]), str(geotup[1].datatype), "")
                    if geojsonrep != None and "coordinates" in geojsonrep and len(geojsonrep["coordinates"])>0:
                        if uritotreeitem != None and str(memberid) in uritotreeitem:
                            featcoll["features"].append({"type": "Feature", 'id': str(memberid),
                                                         'name': uritotreeitem[str(memberid)][-1]["text"],
                                                         'dateprops': parameters.get("dateprops",{}), 'properties': {},
                                                         "geometry": geojsonrep})
                        else:
                            featcoll["features"].append(
                                {"type": "Feature", 'id': str(memberid), 'name': str(memberid), 'dateprops': parameters.get("dateprops",{}),
                                 'properties': {}, "geometry": geojsonrep})
                        if len(featcoll["features"][-1]["dateprops"]) > 0:
                            dateatt = featcoll["features"][-1]["dateprops"][0]
            if parameters.get("hasnonnslen",0) > 0:
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
            featcoll["bbox"] = shapely.geometry.GeometryCollection(
                [shapely.geometry.shape(feature["geometry"]) for feature in featcoll["features"]]).bounds
            firstcrs="4326"
            if len(thecrs) > 0:
                firstcrs=str(next(iter(thecrs)))
                featcoll["crs"] = "http://www.opengis.net/def/crs/EPSG/0/" + firstcrs
            else:
                featcoll["crs"] = "http://www.opengis.net/def/crs/EPSG/0/4326"
            epsgcode = "EPSG:" + firstcrs
            if dateatt != "":
                for feat in featcoll["features"]:
                    if dateatt not in feat["properties"]:
                        feat["properties"][dateatt] = ""
            if parameters.get("localOptimized",False):
                f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",
                                                                                                    "[" + json.dumps(
                                                                                                        featcoll) + "]").replace(
                    "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(parameters.get("checkdepth",0))).replace("{{epsg}}",
                                                                                                 epsgcode).replace(
                    "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsgdefspath}}",
                                                                                parameters.get("epsgdefslink","")).replace("{{dateatt}}",
                                                                                                      dateatt))
            else:
                f.write(templates["maptemplate"].replace("{{myfeature}}", "[\"" + DocUtils.shortenURI(
                    str(parameters.get("completesavepath","").replace(".html", ".geojson"))) + "\"]").replace("{{relativepath}}",
                                                                                         DocUtils.generateRelativePathFromGivenDepth(
                                                                                             parameters.get("checkdepth",0))).replace(
                    "{{baselayers}}", json.dumps(DocConfig.baselayers)).replace("{{epsg}}",
                                                                                                 epsgcode).replace("{{epsgdefspath}}",
                                                                                parameters.get("epsgdefslink","")).replace("{{dateatt}}",
                                                                                                      dateatt))
            with open(parameters.get("completesavepath","").replace(".html", ".geojson"), 'w', encoding='utf-8') as fgeo:
                featurecollectionspaths[parameters.get("completesavepath","").replace(".html", ".geojson")] = {"name": featcoll["name"],
                                                                                          "id": featcoll["id"]}
                fgeo.write(json.dumps(featcoll))
                fgeo.close()
        return geocache

    def generatePageView(self,headertemplate,footertemplate,g,f):
        f.write(str(headertemplate))
        print("PageView")