from ..layerutils import LayerUtils
from ..doc.docconfig import DocConfig
from rdflib import Graph, Literal, URIRef

class LiteralUtils:

    @staticmethod
    def resolveGeoLiterals(pred, object, graph, geojsonrep, nonns, subject=None):
        predstr=str(pred)
        if isinstance(object, Literal):
            if subject is not None and (predstr in DocConfig.geopairproperties):
                pairprop = DocConfig.geopairproperties[predstr]["pair"]
                latorlong = DocConfig.geopairproperties[predstr]["islong"]
                othervalue = ""
                for obj in graph.objects(subject, URIRef(pairprop)):
                    othervalue = str(obj)
                if latorlong:
                    geojsonrep = {"type": "Point", "coordinates": [float(str(othervalue)), float(str(object))]}
                else:
                    geojsonrep = {"type": "Point", "coordinates": [float(str(object)), float(str(othervalue))]}
            elif predstr in DocConfig.geoproperties or str(object.datatype) in DocConfig.geoliteraltypes:
                geojsonrep = LiteralUtils.processLiteral(str(object), str(object.datatype), "")
        elif isinstance(object, URIRef) and nonns:
            for pobj in graph.predicate_objects(object):
                if isinstance(pobj[1], Literal) and (str(pobj[0]) in DocConfig.geoproperties or str(pobj[1].datatype) in DocConfig.geoliteraltypes):
                    geojsonrep = LiteralUtils.processLiteral(str(pobj[1]), str(pobj[1].datatype), "")
        return geojsonrep

    @staticmethod
    def processLiteral(literal, literaltype, reproject, currentlayergeojson=None, triplestoreconf=None):
        return LayerUtils.processLiteral(literal,literaltype,reproject,currentlayergeojson,triplestoreconf)