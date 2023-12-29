from .rdf.geoexporter import GeoExporter
from .rdf.graphexporter import GraphExporter
from .rdf.miscexporter import MiscExporter


class ExporterUtils:

    @staticmethod
    def getExporterString():
        return GraphExporter.getExporterString()+" "+MiscExporter.getExporterString()

    rdfformats = ["TTL", "TRIX", "TRIG", "N3", "NQ", "NT", "XML", "JSON-LD"]

    exportToFunction = {"CYPHER": GraphExporter.convertTTLToCypher, "GML": GraphExporter.convertTTLToGML,
                        "GEXF": GraphExporter.convertTTLToGEXF,
                        "GDF": GraphExporter.convertTTLToTGF, "DOT": GraphExporter.convertTTLToDOT,
                        "NET": GraphExporter.convertTTLToNET,
                        "GRAPHML": GraphExporter.convertTTLToGraphML, "GeoJSON": GeoExporter.convertTTLToGeoJSON,
                        "JGF": GraphExporter.convertTTLToJGF, "TGF": GraphExporter.convertTTLToTGF,
                        "TLP": GraphExporter.convertTTLToTLP,"SIGMA": GraphExporter.convertTTLToSigmaJSON,
                        "TTL": GraphExporter.serializeRDF, "TRIG": GraphExporter.serializeRDF,
                        "xml": GraphExporter.serializeRDF,
                        "TRIX": GraphExporter.serializeRDF, "NT": GraphExporter.serializeRDF,
                        "N3": GraphExporter.serializeRDF,
                        "NQ": GraphExporter.serializeRDF, "CSV": MiscExporter.convertTTLToCSV,
                        "TSV": MiscExporter.convertTTLToCSV}