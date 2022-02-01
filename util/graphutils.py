from ..util.sparqlutils import SPARQLUtils

from qgis.core import Qgis
from qgis.core import (
    QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'GraphUtils'

class GraphUtils:

    def __init__(self,testURL):
        self.feasibleConfiguration=False
        self.configuration={}
        self.testURL=testURL

    def testTripleStoreConnection(self, triplestoreurl, query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1",credentialUserName=None,credentialPassword=None,authmethod=None):
        QgsMessageLog.logMessage("Execute query: "+str(query), MESSAGE_CATEGORY, Qgis.Info)
        results=SPARQLUtils.executeQuery(triplestoreurl,query,{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        QgsMessageLog.logMessage("Query results: "+str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results!=False:
            if self.testURL and not self.testConfiguration:
                self.message = "URL depicts a valid SPARQL Endpoint!"
            if "ASK" in query:
                QgsMessageLog.logMessage("Result: "+str(results["boolean"]), MESSAGE_CATEGORY, Qgis.Info)
                return results["boolean"]
            self.feasibleConfiguration = True
            return True
        return results

    def detectNamespaces(self, subpredobj,progress,triplestoreurl,credentialUserName=None,credentialPassword=None,authmethod=None):
        if subpredobj < 0 or subpredobj == None:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        elif subpredobj == 0:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?p), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
            newtext = "\n".join(progress.labelText().split("\n")[0:-1])
            progress.setLabelText(newtext + "\nCurrent Task: Namespace detection (2/3)")
        else:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?o), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
            newtext = "\n".join(progress.labelText().split("\n")[0:-1])
            progress.setLabelText(newtext + "\nCurrent Task: Namespace detection (3/3)")
        results=SPARQLUtils.executeQuery(triplestoreurl,query,{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        if results==False:
            return []
        reslist = []
        for nss in results["results"]["bindings"]:
            if "ns" in nss:
                reslist.append(nss["ns"]["value"])
        return reslist

    ## Detects default configurations of common geospatial triple stores.
    #  @param self The object pointer.
    def detectTripleStoreConfiguration(self,triplestorename,triplestoreurl,detectnamespaces,prefixstore,progress,credentialUserName=None,credentialPassword=None,authmethod=None):
        self.configuration = {}
        self.configuration["name"] = triplestorename
        self.configuration["resource"]={}
        if isinstance(triplestoreurl,str):
            self.configuration["type"] = "sparqlendpoint"
            self.configuration["resource"]["type"]="endpoint"
            self.configuration["resource"]["url"] = triplestoreurl
        else:
            self.configuration["type"] = "file"
            self.configuration["resource"]["type"]="file"
            self.configuration["resource"]["instance"] = triplestoreurl
        self.configuration["geoconceptlimit"] = 500
        self.configuration["crs"] = 4326
        if credentialUserName!=None and credentialUserName!="" and credentialPassword!=None and credentialPassword!=None:
            self.configuration["auth"]={}
            self.configuration["auth"]["userCredential"] = credentialUserName
            self.configuration["auth"]["userPassword"] = credentialPassword
            self.configuration["auth"]["method"]=authmethod
        self.configuration["typeproperty"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.configuration["labelproperty"] = "http://www.w3.org/2000/01/rdf-schema#label"
        self.configuration["subclassproperty"] = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        self.configuration["whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype\n WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% .\n ?con ?rel ?val .\n BIND( datatype(?val) AS ?valtype )\n } GROUP BY ?rel ?valtype\n ORDER BY DESC(?countrel)"
        self.configuration["staticconcepts"] = []
        self.configuration["active"] = True
        self.configuration["prefixes"] = {"owl": "http://www.w3.org/2002/07/owl#",
                                          "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                          "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                                          "geosparql": "http://www.opengis.net/ont/geosparql#",
                                          "geof": "http://www.opengis.net/def/function/geosparql/",
                                          "geor": "http://www.opengis.net/def/rule/geosparql/",
                                          "sf": "http://www.opengis.net/ont/sf#",
                                          "wgs84_pos": "http://www.w3.org/2003/01/geo/wgs84_pos#"}
        testQueries = {
            "geosparql": "PREFIX geof:<http://www.opengis.net/def/function/geosparql/> SELECT ?a ?b ?c WHERE { BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?a) BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?b) FILTER(geof:sfIntersects(?a,?b))}",
            "available": "SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1",
            "hasRDFSLabel": "PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ASK { ?a rdfs:label ?c . }",
            "hasRDFType": "PREFIX rdf:<http:/www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { ?a <http:/www.w3.org/1999/02/22-rdf-syntax-ns#type> ?c . }",
            "hasWKT": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asWKT ?c .}",
            "hasGeometry": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:hasGeometry ?c .}",
            "hasGML": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGML ?c .}",
            "hasKML": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asKML ?c .}",
            "hasGeoJSON": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGeoJSON ?c .}",
            "hasWgs84LatLon": "PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:lat ?c . ?a geo:long ?d . }",
            "hasWgs84Geometry": "PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:geometry ?c . }",
            "hasSchemaOrgGeo": "PREFIX schema:<http://schema.org/> ASK { ?a schema:geo ?c . }",
            "namespaceQuery": "select distinct ?ns where {  ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"}
        capabilitylist=[]
        if self.testTripleStoreConnection(self.configuration["resource"],testQueries["available"],credentialUserName,credentialPassword,authmethod):
            QgsMessageLog.logMessage("Triple Store "+str(triplestoreurl)+" is available!", MESSAGE_CATEGORY, Qgis.Info)
            if self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasWKT"],credentialUserName,credentialPassword,authmethod):
                QgsMessageLog.logMessage("Triple Store " + str(triplestoreurl) + " contains WKT literals!", MESSAGE_CATEGORY,
                                         Qgis.Info)
                geomobjprop="http://www.opengis.net/ont/geosparql#hasGeometry"
                if self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasGeometry"],credentialUserName,credentialPassword,authmethod):
                    self.configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#hasGeometry"]
                elif self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasWgs84Geometry"],credentialUserName,credentialPassword,authmethod):
                    self.configuration["geometryproperty"] = ["http://www.w3.org/2003/01/geo/wgs84_pos#geometry"]
                    geomobjprop="http://www.w3.org/2003/01/geo/wgs84_pos#geometry"
                if self.testTripleStoreConnection(self.configuration["resource"],testQueries["geosparql"],credentialUserName,credentialPassword,authmethod):
                    self.configuration["type"]="geosparqlendpoint"
                    self.configuration["bboxquery"] = {}
                    self.configuration["bboxquery"]["type"] = "geosparql"
                    self.configuration["bboxquery"][
                        "query"] = "FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#wktLiteral>))"
                    self.message = "URL depicts a valid SPARQL Endpoint with the following capabilities: <ul><li>GeoSPARQL Query Capabilities</li><li>WKT Literals</li></ul>Would you like to add this SPARQL endpoint?"
                else:
                    self.message = "URL depicts a valid SPARQL Endpoint with the following capabilities: <ul><li>No GeoSPARQL Query Capabilities</li><li>WKT Literals</li></ul><br/>Would you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "geo"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?geo WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%>.\n ?item <"+str(geomobjprop)+"> ?geom_obj .\n ?geom_obj <http://www.opengis.net/ont/geosparql#asWKT> ?geo .\n } LIMIT 10"})
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?item <"+str(geomobjprop)+"> ?item_geom . ?item_geom <http://www.opengis.net/ont/geosparql#asWKT> ?wkt .} ORDER BY ?class"
                self.configuration["geotriplepattern"]=["?item <"+str(geomobjprop)+"> ?item_geom . ?item_geom <http://www.opengis.net/ont/geosparql#asWKT> ?geo ."]
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration["subclassquery"]="SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a ?rel ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asWKT> ?wkt . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype\n WHERE {\n ?con %%typeproperty%% %%concept%% .\n ?con ?rel ?val .\n BIND( datatype(?val) AS ?valtype )\n } GROUP BY ?rel ?valtype\n ORDER BY DESC(?countrel)"
            elif self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasWgs84LatLon"],credentialUserName,credentialPassword,authmethod):
                QgsMessageLog.logMessage("Triple Store " + str(triplestoreurl) + " contains WGS84 Lat/Lon properties!",
                                         MESSAGE_CATEGORY,
                                         Qgis.Info)
                self.configuration["geometryproperty"] = ["http://www.w3.org/2003/01/geo/wgs84_pos#long","http://www.w3.org/2003/01/geo/wgs84_pos#lat"]
                self.message = "URL depicts a valid SPARQL Endpoint with the following capabilities: <ul><li>No GeoSPARQL Query Capabilities</li><li>W3C Geo Lat/long!</li></ul><br/>Would you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "lat", "lon"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?lat ?lon WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%> .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .\n } LIMIT 10"})
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .} ORDER BY ?class"
                self.configuration["geotriplepattern"]=[" ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon . "]
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration[
                    "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype\nWHERE {\n ?con %%typeproperty%% %%concept%% .\n ?con ?rel ?val .\n BIND( datatype(?val) AS ?valtype )\n } GROUP BY ?rel ?valtype\n ORDER BY DESC(?countrel)"
            elif self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasSchemaOrgGeo"],credentialUserName,credentialPassword,authmethod):
                QgsMessageLog.logMessage("Triple Store " + str(triplestoreurl) + " contains Schema.org Lat/Lon properties!",MESSAGE_CATEGORY,Qgis.Info)
                self.configuration["geometryproperty"] = ["https://schema.org/geo"]
                self.message = "URL depicts a valid SPARQL Endpoint with the following capabilities: <ul><li>No GeoSPARQL Query Capabilities</li><li>Schema.org Lat/long!</li></ul><br/>Would you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "lat", "lon"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?lat ?lon WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%> .\n ?item <http://schema.org/geo> ?itemgeo . ?itemgeo <http://schema.org/latitude> ?lat .\n ?itemgeo <http://schema.org/longitude> ?lon .\n } LIMIT 10"})
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?item <http://schema.org/geo> ?item_geo . ?item_geo <http://schema.org/latitude> ?lat . ?item <http://schema.org/longitude> ?lon .} ORDER BY ?class"
                self.configuration["geotriplepattern"]=[" ?item <http://schema.org/geo> ?item_geo . ?item_geo <http://schema.org/latitude> ?lat . ?item <http://schema.org/longitude> ?lon . "]
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration[
                    "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a <http://schema.org/latitude> ?lat . ?a <http://schema.org/longitude> ?lon . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
            elif self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasGeoJSON"],credentialUserName,credentialPassword,authmethod):
                QgsMessageLog.logMessage("Triple Store " + str(triplestoreurl) + " contains GeoJSON literals!",MESSAGE_CATEGORY,Qgis.Info)
                if self.testTripleStoreConnection(self.configuration["resource"],testQueries["geosparql"],credentialUserName,credentialPassword,authmethod):
                    self.configuration["type"]="geosparqlendpoint"
                    self.configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#hasGeometry"]
                    self.configuration["bboxquery"] = {}
                    self.configuration["bboxquery"]["type"] = "geosparql"
                    self.configuration["bboxquery"][
                        "query"] = "FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#geoJSONLiteral>))"
                    self.message = "URL depicts a valid SPARQL Endpoint with the following capabilities: <ul><li>GeoSPARQL Query Capabilities</li><li>GeoJSON Literals</li></ul><br/>Would you like to add this SPARQL endpoint?"
                else:
                    self.message = "URL depicts a valid SPARQL Endpoint with the following capabilities: <ul><li>No GeoSPARQL Query Capabilities</li><li>GeoJSON Literals</li></ul><br/>Would you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "geo"]
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?geo WHERE {\n ?item a <%%concept%%>.\n ?item <http://www.opengis.net/ont/geosparql#hasGeometry> ?geom_obj .\n ?geom_obj <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo .\n } LIMIT 10"})
                self.configuration["querytemplate"].append({"label": "10 Random Geometries (All Attributes",
                                                            "query": "SELECT DISTINCT ?item ?rel ?val ?geo WHERE {\n ?item rdf:type <%%concept%%> .\n ?item ?rel ?val . \n ?val <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo .\n}\n LIMIT 100"})
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?item ?rel ?item_geom . ?item_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?wkt .} ORDER BY ?class"
                self.configuration["geotriplepattern"]=[" ?item ?rel ?item_geom . ?item_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo . "]
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration[
                    "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a ?rel ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?wkt . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype\n WHERE {\n ?con %%typeproperty%% %%concept%% .\n ?con ?rel ?val .\n BIND( datatype(?val) AS ?valtype )\n } GROUP BY ?rel ?valtype \n ORDER BY DESC(?countrel)"
            else:
                self.message = "SPARQL endpoint does not seem to include the following geometry relations:<ul><li>geo:asWKT</li><li>geo:asGeoJSON</li><li> geo:lat, geo:long</li></ul><br>A manual configuration is probably necessary to include this SPARQL endpoint if it contains geometries<br>Do you still want to add this SPARQL endpoint?"
                self.feasibleConfiguration = True
                #return True
            res = set()
            if detectnamespaces:
                newtext = "\n".join(progress.labelText().split("\n")[0:-1])
                progress.setLabelText(newtext + "\nCurrent Task: Namespace detection (1/3)")
                res = set(self.detectNamespaces(-1,progress,self.configuration["resource"],credentialUserName,credentialPassword,authmethod) + self.detectNamespaces(0,progress,self.configuration["resource"],credentialUserName,credentialPassword,authmethod) + self.detectNamespaces(1,progress,self.configuration["resource"],credentialUserName,credentialPassword,authmethod))
            i = 0
            for ns in res:
                if ns != "http://" and ns.startswith("http://"):
                    if ns in prefixstore["reversed"]:
                        self.configuration["prefixes"][prefixstore["reversed"][ns]] = ns
                    else:
                        self.configuration["prefixes"]["ns" + str(i)] = ns
                        i = i + 1
            self.feasibleConfiguration = True
            QgsMessageLog.logMessage(str(self.configuration))
            if self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasRDFSLabel"]) and self.testTripleStoreConnection(self.configuration["resource"],testQueries["hasRDFType"]):
                self.configuration[
                    "classfromlabelquery"] = "SELECT DISTINCT ?class ?label { ?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
                self.configuration[
                    "propertyfromlabelquery"] = "SELECT DISTINCT ?class ?label { ?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> . ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
            QgsMessageLog.logMessage(str("SELECT DISTINCT ?acon ?rel WHERE { ?a a ?acon . ?a ?rel ?item. "+str(self.configuration["geotriplepattern"][0])+" }"))
            results=SPARQLUtils.executeQuery(self.configuration["resource"],"SELECT DISTINCT ?acon ?rel WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?acon . ?a ?rel ?item. "+str(self.configuration["geotriplepattern"][0])+" }")
            if results!=False:
                self.configuration["geoobjproperty"] = set()
                self.configuration["geoclasses"] = {}
                for result in results["results"]["bindings"]:
                    if "rel" in result \
                            and SPARQLUtils.namespaces["owl"] not in result["rel"]["value"]\
                            and SPARQLUtils.namespaces["rdfs"] not in result["rel"]["value"]\
                            and SPARQLUtils.namespaces["skos"] not in result["rel"]["value"]:
                        self.configuration["geoobjproperty"].add(result["rel"]["value"])
                        if "acon" in result:
                            if result["acon"]["value"] not in self.configuration["geoclasses"]:
                                self.configuration["geoclasses"][result["acon"]["value"]]=set()
                            self.configuration["geoclasses"][result["acon"]["value"]].add(result["rel"]["value"])
                for cls in self.configuration["geoclasses"]:
                    self.configuration["geoclasses"][cls]=list(self.configuration["geoclasses"][cls])
                QgsMessageLog.logMessage(str(self.configuration["geoobjproperty"]))
        else:
            self.message = "URL does not depict a valid SPARQL Endpoint!"
            self.feasibleConfiguration = False
            return False
        return True