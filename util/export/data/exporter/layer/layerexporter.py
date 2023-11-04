
import json

from ..exporterutils import ExporterUtils
from .....layerutils import LayerUtils

from rdflib import Graph

class LayerExporter:



    @staticmethod
    def exportToFormat(layer,format):
        layerToTTL=LayerUtils.layerToTTLString(layer)
        g=Graph()
        g.parse(layerToTTL)
        if format in ExporterUtils.exportToFunction:
            ExporterUtils.exportToFunction[format](g,None,None,None,format.lower())


        @staticmethod
        def layerToGraphML(layer):
            fieldnames = [field.name() for field in layer.fields()]
            result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            result += "<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:y=\"http://www.yworks.com/xml/graphml\" xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd\">\n"
            result += "<key for=\"node\" id=\"nodekey\" yfiles.type=\"nodegraphics\"></key>\n<key for=\"edge\" id=\"edgekey\" yfiles.type=\"edgegraphics\"></key><graph id=\"G\" edgedefault=\"undirected\">\n"
            nodeset = set()
            edgeset = set()
            fidcounter = 0
            edgecounter = 0
            literalcounter = 1
            nodeset.add(
                "<node id=\"geo:SpatialObject\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:SpatialObject</y:NodeLabel></y:ShapeNode></data></node>\n")

            nodeset.add(
                "<node id=\"geo:Feature\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:Feature</y:NodeLabel></y:ShapeNode></data></node>\n")
            nodeset.add(
                "<node id=\"geo:Geometry\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:Geometry</y:NodeLabel></y:ShapeNode></data></node>\n")
            edgeset.add(
                "<edge id=\"eFeature\" source=\"geo:Feature\" target=\"geo:SpatialObject\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    "rdfs:subClassOf") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            edgeset.add(
                "<edge id=\"eGeometry\" source=\"geo:Geometry\" target=\"geo:SpatialObject\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    "rdfs:subClassOf") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            for f in layer.getFeatures():
                geom = f.geometry()
                nodeset.add("<node id=\"fid_" + str(
                    fidcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">fid_" + str(
                    fidcounter) + "</y:NodeLabel></y:ShapeNode></data></node>\n")
                fieldcounter = 0
                for propp in fieldnames:
                    fieldcounter += 1
                    prop = propp
                    if prop.startswith("http"):
                        toadd = "<node id=\"" + str(prop) + "\" uri=\"" + str(
                            prop) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">"
                        if f[propp].startswith("http"):
                            toadd += SPARQLUtils.labelFromURI(str(f[propp]).replace("<", "").replace(">",
                                                                                                     "")) + "</y:NodeLabel></y:ShapeNode></data></node>\n"
                        else:
                            toadd += "<!CDATA[" + str(f[propp]).replace("<", "").replace(">",
                                                                                         "") + "]]></y:NodeLabel></y:ShapeNode></data></node>\n"
                        nodeset.add(toadd)
                        edgeset.add(
                            "<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(propp) + "\" source=\"fid_" + str(
                                fidcounter) + "\" target=\"" + str(
                                prop) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                                propp) + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                        edgecounter += 1
                    else:
                        nodeset.add("<node id=\"literal" + str(
                            literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                            f[propp]).replace("<", "").replace(">", "")[
                                                                                                                                                                                                                                                                                                                                        0:10] + "</y:NodeLabel></y:ShapeNode></data></node>\n")
                        edgeset.add(
                            "<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(propp) + "\" source=\"fid_" + str(
                                fidcounter) + "\" target=\"literal" + str(
                                literalcounter) + "\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                                propp) + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                        literalcounter += 1
                        edgecounter += 1
                nodeset.add("<node id=\"fid_" + str(fidcounter
                                                    ) + "_geom\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">fid_" + str(
                    fidcounter) + "_geom</y:NodeLabel></y:ShapeNode></data></node>\n")
                nodeset.add("<node id=\"literal" + str(
                    literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    geom.asWkt())[0:10] + "</y:NodeLabel></y:ShapeNode></data></node>\n")
                edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                    fidcounter) + "\" target=\"fid_" + str(
                    fidcounter) + "_geom\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    "geom:asWkt") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                edgeset.add("<edge id=\"e" + str(edgecounter) + "type\" source=\"fid_" + str(
                    fidcounter) + "_geom\" target=\"geo:Geometry\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    "rdf:type") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                    fidcounter) + "_geom\" target=\"literal" + str(
                    literalcounter) + "\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    "geom:asWkt") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                edgecounter += 1
                edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                    fidcounter) + "\" target=\"geo:Feature\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                    "rdf:type") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                literalcounter += 1
                edgecounter += 1
                fidcounter += 1
            result += "".join(nodeset)
            result += "".join(edgeset)
            result += "</graph>\n"
            result += "</graphml>"
            return result

    @staticmethod
    def layerAsGeoJSONLD(layer):
        context = {
            "geojson": "https://purl.org/geojson/vocab#",
            "Feature": "geojson:Feature",
            "FeatureCollection": "geojson:FeatureCollection",
            "GeometryCollection": "geojson:GeometryCollection",
            "LineString": "geojson:LineString",
            "MultiLineString": "geojson:MultiLineString",
            "MultiPoint": "geojson:MultiPoint",
            "MultiPolygon": "geojson:MultiPolygon",
            "Point": "geojson:Point",
            "Polygon": "geojson:Polygon",
            "bbox": {
                "@container": "@list",
                "@id": "geojson:bbox"
            },
            "coordinates": {
                "@container": "@list",
                "@id": "geojson:coordinates"
            },
            "features": {
                "@container": "@set",
                "@id": "geojson:features"
            },
            "geometry": "geojson:geometry",
            "id": "@id",
            "properties": "geojson:properties",
            "type": "@type",
            "description": "http://purl.org/dc/terms/description",
            "title": "http://purl.org/dc/terms/title"
        }
        fieldnames = [field.name() for field in layer.fields()]
        currentgeo = {}
        geos = []
        for f in layer.getFeatures():
            geom = f.geometry()
            currentgeo = {'id': "", 'geometry': json.loads(geom.asJson()), 'properties': {}}
            for prop in fieldnames:
                if prop == "id":
                    currentgeo["id"] = f[prop]
                else:
                    currentgeo["properties"][prop] = f[prop]
            geos.append(currentgeo)
        featurecollection = {"@context": context, "type": "FeatureCollection",
                             "@id": "http://example.com/collections/1", "features": geos}
        return featurecollection