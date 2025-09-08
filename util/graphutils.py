from ..util.sparqlutils import SPARQLUtils
from ..util.doc.docconfig import DocConfig
from rdflib import Graph

from qgis.core import Qgis
from qgis.core import QgsMessageLog

MESSAGE_CATEGORY = 'GraphUtils'

class GraphUtils:

    labelToPropertyTypes={
        "instance of":"typeproperty",
        "subclass of": "subclassproperty",
        "coordinate": "geoproperty",
    }

    testQueries = {
        "geosparql": "PREFIX geof:<http://www.opengis.net/def/function/geosparql/> SELECT ?a ?b ?c WHERE { BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?a) BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?b) FILTER(geof:sfIntersects(?a,?b))}",
        "sparql11": "SELECT ?a ?b ?c WHERE { BIND( <http://www.opengis.net/ont/geosparql#test> AS ?b)  ?a ?b ?c . } LIMIT 1",
        "available": "SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1",
        "discoverLiteralRels": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> SELECT DISTINCT ?rel WHERE { ?a ?rel ?c . filter (datatype(?c) = <http://www.opengis.net/ont/geosparql#wktLiteral> || datatype(?c) = <http://www.opengis.net/ont/geosparql#geoJSONLiteral> || datatype(?c) = <http://www.opengis.net/ont/geosparql#kmlLiteral>) } LIMIT 5",
        "hasRDFSLabel": "PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ASK { ?a rdfs:label ?c . }",
        "hasSKOSPrefLabel": "PREFIX skos:<http://www.w3.org/2004/02/skos/core#> ASK { ?a skos:prefLabel ?c . }",
        "hasDCTermsTitleLabel": "PREFIX dc:<http://purl.org/dc/terms/> ASK { ?a dc:title ?c . }",
        "hasRDFType": "ASK { ?a <http:/www.w3.org/1999/02/22-rdf-syntax-ns#type> ?c . }",
        "hasPropEquivalent":"SELECT DISTINCT ?prop ?propLabel WHERE { VALUES ?propLabel { %%proplabels%% } . ?a ?prop ?b .{ ?ab <http://wikiba.se/ontology#directClaim> ?prop . ?ab <http://www.w3.org/2000/01/rdf-schema#label> ?propLabel .} UNION { ?prop <http://www.w3.org/2000/01/rdf-schema#label> ?propLabel .}}",
        "hassubClassOf": "ASK { ?a <http://www.w3.org/2000/01/rdf-schema#subClassOf> ?c . }",
        "hasSKOSTopConcept": "ASK { ?a <http://www.w3.org/2004/02/skos/core#hasTopConcept> ?c . }",
        "hasWKT": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asWKT ?c .}",
        "hasGeometry": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:hasGeometry ?c .}",
        "hasJusoGeometry": "PREFIX juso:<http://rdfs.co/juso/> ASK { ?a juso:geometry ?c .}",
        "hasGML": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGML ?c .}",
        "hasKML": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asKML ?c .}",
        "hasGeoJSON": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGeoJSON ?c .}",
        "hasWgs84LatLon": "PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:lat ?c . ?a geo:long ?d . }",
        "hasWgs84Geometry": "PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:geometry ?c . }",
        "hasSchemaOrgGeoLatLonHTTPS": "PREFIX schema:<https://schema.org/> ASK { ?a schema:geo ?c . ?c schema:latitude ?d . ?c schema:longitude ?e . }",
        "hasSchemaOrgGeoLatLonHTTP": "PREFIX schema:<http://schema.org/> ASK { ?a schema:geo ?c . ?c schema:latitude ?d . ?c schema:longitude ?e . }",
        "hasSchemaOrgGeoPolygonHTTP": "PREFIX schema:<http://schema.org/> ASK { ?a schema:geo ?c .  ?c schema:polygon ?d . }",
        "hasSchemaOrgGeoPolygonHTTPS": "PREFIX schema:<https://schema.org/> ASK { ?a schema:geo ?c .  ?c schema:polygon ?d . }",
        "namespaceQuery": "select distinct ?ns where {  ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
    }

    def __init__(self,testURL):
        self.feasibleConfiguration=False
        self.configuration={}
        self.testURL=testURL
        self.message=""
        self.missingproperties=[]

    def addDefaultConfigurationParameters(self,triplestorename,triplestoreurl,credentialUserName=None,credentialPassword=None,authmethod=None):
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
        if credentialUserName is not None and credentialUserName!="" and credentialPassword is not None and credentialPassword is not None:
            self.configuration["auth"]={}
            self.configuration["auth"]["userCredential"] = credentialUserName
            self.configuration["auth"]["userPassword"] = credentialPassword
            self.configuration["auth"]["method"]=authmethod
        self.configuration["typeproperty"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.configuration["labelproperty"] = ["http://www.w3.org/2000/01/rdf-schema#label"]
        self.configuration["collectionnmemberproperty"] = ["http://www.w3.org/2000/01/rdf-schema#member"]
        self.configuration["subclassproperty"] = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        self.configuration["whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype\n WHERE { ?con %%typeproperty%% %%concept%% .\n ?con ?rel ?val .\n BIND( datatype(?val) AS ?valtype )\n } GROUP BY ?rel ?valtype\n ORDER BY DESC(?countrel)"
        self.configuration["staticconcepts"] = []
        self.configuration["mandatoryvariables"] = []
        self.configuration["active"] = True
        self.configuration["prefixes"] = {"owl": "http://www.w3.org/2002/07/owl#",
                                          "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                          "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                                          "geosparql": "http://www.opengis.net/ont/geosparql#",
                                          "geof": "http://www.opengis.net/def/function/geosparql/",
                                          "geor": "http://www.opengis.net/def/rule/geosparql/",
                                          "sf": "http://www.opengis.net/ont/sf#",
                                          "wgs84_pos": "http://www.w3.org/2003/01/geo/wgs84_pos#"}
        self.configuration["whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype\n WHERE {\n ?con %%typeproperty%% %%concept%% .\n ?con ?rel ?val .\n BIND( datatype(?val) AS ?valtype )\n } GROUP BY ?rel ?valtype \n ORDER BY DESC(?countrel)"
        return self.configuration

    ## Creates a String representation of the capabilities of the triple store
    def createCapabilityMessage(self,capabilitylist):
        capabilitymessage="A valid SPARQL Endpoint with the following capabilities: <ul>"
        for cap in capabilitylist:
            capabilitymessage+=f"<li>{cap}</li>"
        capabilitymessage+="</ul>"
        return capabilitymessage


    def detectLiteralType(self,configuration,credentialUserName,credentialPassword, authmethod,capabilitylist):
        configuration["geotriplepattern"]=[]
        configuration["querytemplate"] = []
        gottype=False
        mandvardef=" ?item ?geo "
        geomobjprop="?item ?rel ?item_geom . "
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasGeometry"],
                                          credentialUserName, credentialPassword, authmethod):
            configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#hasGeometry"]
            geomobjprop = "?item <http://www.opengis.net/ont/geosparql#hasGeometry> ?item_geom . "
            #configuration["geotriplepattern"].append(str(geomobjprop) + " ?item_geom ?georel ?geo . ")
        elif self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasWgs84Geometry"],
                                            credentialUserName, credentialPassword, authmethod):
            configuration["geometryproperty"] = ["http://www.w3.org/2003/01/geo/wgs84_pos#geometry"]
            geomobjprop="?item <http://www.w3.org/2003/01/geo/wgs84_pos#geometry> ?item_geom . "
            #configuration["geotriplepattern"].append(str(geomobjprop) + " ?item_geom ?georel ?geo . ")
        if self.testTripleStoreConnection(configuration["resource"],self.testQueries["hasWKT"],credentialUserName,credentialPassword,authmethod):
            capabilitylist.append("WKT Literals")
            configuration["mandatoryvariables"] = ["item", "geo"]
            if "geometryproperty" not in configuration:
                configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#asWKT"]
            configuration["geotriplepattern"].append(str(geomobjprop) + " ?item_geom <http://www.opengis.net/ont/geosparql#asWKT> ?geo . ")
            configuration["geotriplepattern"].append(" ?item <http://www.opengis.net/ont/geosparql#asWKT> ?geo . ")
            gottype=True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasGML"],
                                          credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("GML Literals")
            configuration["mandatoryvariables"] = ["item", "geo"]
            configuration["geotriplepattern"].append(str(geomobjprop)+" ?item_geom <http://www.opengis.net/ont/geosparql#asGML> ?geo . ")
            configuration["geotriplepattern"].append(" ?item <http://www.opengis.net/ont/geosparql#asGML> ?geo . ")
            if "geometryproperty" not in configuration:
                configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#asGML"]
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasKML"],
                                          credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("KML Literals")
            configuration["mandatoryvariables"] = ["item", "geo"]
            configuration["geotriplepattern"].append(str(geomobjprop)+" ?item_geom <http://www.opengis.net/ont/geosparql#asKML> ?geo . ")
            configuration["geotriplepattern"].append(" ?item <http://www.opengis.net/ont/geosparql#asKML> ?geo . ")
            if "geometryproperty" not in configuration:
                configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#asKML"]
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasGeoJSON"],
                                          credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("GeoJSON Literals")
            configuration["mandatoryvariables"] = ["item", "geo"]
            configuration["geotriplepattern"].append(str(geomobjprop)+" ?item_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo . ")
            configuration["geotriplepattern"].append(" ?item <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo . ")
            if "geometryproperty" not in configuration:
                configuration["geometryproperty"] = ["http://www.opengis.net/ont/geosparql#asGeoJSON"]
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasWgs84LatLon"],
                                       credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("WGS84 Lat/Lon")
            mandvardef = " ?item ?lat ?lon "
            configuration["geometryproperty"] = ["http://www.w3.org/2003/01/geo/wgs84_pos#long",
                                                      "http://www.w3.org/2003/01/geo/wgs84_pos#lat"]
            configuration["mandatoryvariables"] = ["item", "lat","lon"]
            configuration["geotriplepattern"].append(" ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon . ")
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasSchemaOrgGeoLatLonHTTPS"],
                                       credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("Schema.org Lat/Lon")
            mandvardef = " ?item ?lat ?lon "
            configuration["mandatoryvariables"] = ["item", "lat", "lon"]
            configuration["geometryproperty"] = ["https://schema.org/geo"]
            configuration["geotriplepattern"].append(" ?item <https://schema.org/latitude> ?lat . ?item <https://schema.org/longitude> ?lon . ")
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasSchemaOrgGeoLatLonHTTP"],
                                       credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("Schema.org Lat/Lon")
            mandvardef = " ?item ?lat ?lon "
            configuration["mandatoryvariables"] = ["item", "lat", "lon"]
            configuration["geometryproperty"] = ["http://schema.org/geo"]
            configuration["geotriplepattern"].append(" ?item <http://schema.org/latitude> ?lat . ?item <http://schema.org/longitude> ?lon . ")
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasSchemaOrgGeoPolygonHTTPS"],
                                       credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("Schema.org Geo Polygon")
            configuration["mandatoryvariables"] = ["item", "geo"]
            configuration["geometryproperty"] = ["https://schema.org/polygon"]
            configuration["geotriplepattern"].append(" ?item <https://schema.org/polygon> ?geo . ")
            gottype = True
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["hasSchemaOrgGeoPolygonHTTP"],
                                       credentialUserName, credentialPassword, authmethod):
            capabilitylist.append("Schema.org Geo Polygon")
            configuration["mandatoryvariables"] = ["item", "geo"]
            configuration["geometryproperty"] = ["http://schema.org/polygon"]
            configuration["geotriplepattern"].append(" ?item <http://schema.org/polygon> ?geo . ")
            gottype = True
        if not gottype:
            results = SPARQLUtils.executeQuery(configuration["resource"],
                                               self.testQueries["hasPropEquivalent"].replace("%%proplabels%%",
                                                                                             "\"coordinate\"@en \"coordinate location\"@en \"has coordinate\"@en"),
                                               {"auth": {"method": authmethod, "userCredential": credentialUserName,
                                                         "userPassword": credentialPassword}})
            # QgsMessageLog.logMessage("ASK FOR LABEL OF RDFTYPE PROPERTY " + str(results), MESSAGE_CATEGORY, Qgis.Info)
            if results != False:
                for res in results["results"]["bindings"]:
                    if "prop" in res:
                        if configuration is not None:
                            mandvardef = " ?item ?geo "
                            capabilitylist.append("Custom Geometry Property")
                            configuration["mandatoryvariables"] = ["item", "geo"]
                            configuration["geometryproperty"] = [res["prop"]["value"]]
                            configuration["geotriplepattern"].append(" ?item <"+str(res["prop"]["value"])+"> ?geo . ")
                            gottype=True
                        break
        #self.detectGeometryLiteralRelations(configuration, credentialUserName, credentialPassword, authmethod) #Does not terminate on most triple stores
        geoconceptquery="SELECT DISTINCT ?class WHERE {\n"
        if len(configuration["geotriplepattern"])==1:
            geoconceptquery+="?item %%typeproperty%% ?class . "+str(configuration["geotriplepattern"][0])
        else:
            index=0
            for pat in configuration["geotriplepattern"]:
                if index==0:
                    geoconceptquery += "{ ?item %%typeproperty%% ?class . " + str(pat)+"} "
                else:
                    geoconceptquery += " UNION { ?item %%typeproperty%% ?class . " + str(pat) + "} "
                index+=1
        geoconceptquery+="} ORDER BY ?class"
        configuration["geoconceptquery"] = geoconceptquery
        if "geotriplepattern" in self.configuration and len(self.configuration["geotriplepattern"])>0:
            self.configuration["querytemplate"].append(
                {"label": "10 Random Geometries",
                 "query": "SELECT "+str(mandvardef)+" WHERE {\n ?item %%typeproperty%% <%%concept%%> .\n "+str(self.configuration["geotriplepattern"][0])+"\n } LIMIT 10"})
            self.configuration[
                "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?item %%typeproperty%% ?subclass . ?item ?rel ?item_geom . " + str(
                configuration["geotriplepattern"][
                    0]) + " ?item_geom <http://www.opengis.net/ont/geosparql#asWKT> ?wkt ."" OPTIONAL { ?subclass %%labelproperty%% ?label . } ?subclass %%subclassproperty%% %%concept%% . }"
        self.configuration["geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label WHERE { ?colinstance %%typeproperty%% %%concept%% . OPTIONAL { ?colinstance %%labelproperty%% ?label . } }"
        return gottype

    ## Detects namespaces available in the given triple store in subject, predicate and object position
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

    def detectTypeProperty(self,triplestoreurl,credentialUserName,credentialPassword, authmethod,configuration=None):
        #QgsMessageLog.logMessage("Execute query: "+str(self.testQueries["hasRDFType"]), MESSAGE_CATEGORY, Qgis.Info)
        results=SPARQLUtils.executeQuery(triplestoreurl,self.testQueries["hasRDFType"],{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        QgsMessageLog.logMessage("Execute query RDFTYPE RESULT: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results==True or isinstance(results,dict) and "boolean" in results and results["boolean"]==True:
            QgsMessageLog.logMessage("Detected RDFTYPE PROPERTY", MESSAGE_CATEGORY, Qgis.Info)
            if configuration is not None:
                configuration["typeproperty"]="http:/www.w3.org/1999/02/22-rdf-syntax-ns#type"
            return "http:/www.w3.org/1999/02/22-rdf-syntax-ns#type"
        else:
            results = SPARQLUtils.executeQuery(triplestoreurl,
                    self.testQueries["hasPropEquivalent"].replace("%%proplabels%%","\"instance of\"@en \"Instance of\"@en \"Instance Of\"@en"),
                    {"auth": {"method": authmethod, "userCredential": credentialUserName,"userPassword": credentialPassword}})
            QgsMessageLog.logMessage("ASK FOR LABEL OF RDFTYPE PROPERTY " + str(results), MESSAGE_CATEGORY, Qgis.Info)
            if results!=False:
                for res in results["results"]["bindings"]:
                    if "prop" in res:
                        if configuration is not None:
                            configuration["typeproperty"] = res["prop"]["value"]
                        return res["prop"]
        return ""

    def detectSubClassOfProperty(self,triplestoreurl,credentialUserName,credentialPassword, authmethod,configuration=None):
        #QgsMessageLog.logMessage("Execute query: "+str(self.testQueries["hassubClassOf"].replace("<"," ").replace(">"," ")), MESSAGE_CATEGORY, Qgis.Info)
        results=SPARQLUtils.executeQuery(triplestoreurl,self.testQueries["hassubClassOf"],{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        #QgsMessageLog.logMessage("Execute query: " + str(results), MESSAGE_CATEGORY,
        #                         Qgis.Info)
        if "boolean" in results and results["boolean"]:
            if configuration is not None:
                configuration["subclassproperty"]="http://www.w3.org/2000/01/rdf-schema#subClassOf"
            return "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        #QgsMessageLog.logMessage(
        #    "Execute query: " + str(self.testQueries["hasSKOSTopConcept"].replace("<", " ").replace(">", " ")),
        #    MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(triplestoreurl, self.testQueries["hasSKOSTopConcept"], {
            "auth": {"method": authmethod, "userCredential": credentialUserName, "userPassword": credentialPassword}})
        if "boolean" in results and results["boolean"]:
            if configuration is not None:
                configuration["subclassproperty"]="http://www.w3.org/2004/02/skos/core#hasTopConcept"
            return "http://www.w3.org/2004/02/skos/core#hasTopConcept"
        results = SPARQLUtils.executeQuery(triplestoreurl,
                self.testQueries["hasPropEquivalent"].replace("%%proplabels%%","\"subclass of\"@en \"Subclass of\"@en \"SubClass Of\"@en"),
                {"auth": {"method": authmethod, "userCredential": credentialUserName,"userPassword": credentialPassword}})
        if results!=False:
            for res in results["results"]["bindings"]:
                if "prop" in res:
                    if configuration is not None:
                        configuration["subclassproperty"] = res["prop"]["value"]
                    return res["prop"]["value"]
        return ""

    def detectEquivalentProperties(self,triplestoreurl,credentialUserName,credentialPassword, authmethod,configuration=None,equivalentPropProperty="http://www.w3.org/2002/07/owl#equivalentProperty",query="SELECT DISTINCT ?prop ?equivprop ?label WHERE { ?prop %%equivprop%% ?equivprop . OPTIONAL { ?equivprop %%labelproperty%% ?label .} }"):
        #QgsMessageLog.logMessage("Execute query: "+str(query), MESSAGE_CATEGORY, Qgis.Info)
        query=query.replace("%%equivprop%%","<"+equivalentPropProperty+">").replace("%%labelproperty%%","<http://www.w3.org/2000/01/rdf-schema#label>")
        results=SPARQLUtils.executeQuery(triplestoreurl,query,{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        #QgsMessageLog.logMessage("Query results: "+str(results), MESSAGE_CATEGORY, Qgis.Info)
        res={}
        if results!=False:
            for restup in results["results"]["bindings"]:
                if "prop" in restup and str(restup["prop"]) not in res:
                    res[str(restup["prop"])]=[]
                res[str(restup["prop"])].append({"uri":restup["equivprop"]})
        if configuration != None:
            configuration["equivalentProperties"] = res
        return res

    def detectEquivalentClasses(self,triplestoreurl,credentialUserName,credentialPassword, authmethod,configuration=None,equivalentClassProperty="http://www.w3.org/2002/07/owl#equivalentClass",query="SELECT DISTINCT ?cls ?equivcls ?label WHERE { { ?cls <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> } UNION { ?ind <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?cls } ?cls %%equivprop%% ?equivcls . OPTIONAL { ?equivcls %%labelproperty%% ?label .} }"):
        #QgsMessageLog.logMessage("Execute query: "+str(query), MESSAGE_CATEGORY, Qgis.Info)
        query=query.replace("%%equivprop%%","<"+equivalentClassProperty+">").replace("%%labelproperty%%","<http://www.w3.org/2000/01/rdf-schema#label>")
        results=SPARQLUtils.executeQuery(triplestoreurl,query,{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        #QgsMessageLog.logMessage("Query results: "+str(results), MESSAGE_CATEGORY, Qgis.Info)
        res={}
        if results!=False:
            for restup in results["results"]["bindings"]:
                if str(restup["cls"]) not in res:
                    res[str(restup["cls"])]=[]
                res[str(restup["cls"])].append({"uri":restup["equivcls"]})
        if configuration!=None:
            configuration["equivalentClasses"]=res
        return res

    def detectGeometryLiteralRelations(self,configuration,credentialUserName,credentialPassword, authmethod):
        newrels=[]
        results=self.testTripleStoreConnection(configuration["resource"], self.testQueries["discoverLiteralRels"],
                                       credentialUserName, credentialPassword, authmethod)
        for result in results["results"]["bindings"]:
            if "rel" in result and result["rel"]["value"] not in DocConfig.geoproperties:
                configuration["geotriplepattern"].append(f' ?item <{result["rel"]["value"]}> ?geo . ')
                newrels.append(result["rel"]["value"])
        return newrels


    def detectGeometryObjectRelations(self):
        if "geotriplepattern" in self.configuration and len(self.configuration["geotriplepattern"]) > 0:
            thequery = "SELECT DISTINCT ?acon ?rel WHERE { ?a <" + str(
                self.configuration["typeproperty"]) + "> ?acon . ?a ?rel ?item. "
            if len(self.configuration["geotriplepattern"]) > 0:
                thequery += str(self.configuration["geotriplepattern"][0]) + " }"
            else:
                first = True
                for pat in self.configuration["geotriplepattern"]:
                    if first:
                        first = False
                        thequery += "{ " + pat + " }"
                    else:
                        thequery += " UNION { " + pat + " }"
                thequery += "}}"
            results = SPARQLUtils.executeQuery(self.configuration["resource"], thequery)
            if results != False:
                self.configuration["geoobjproperty"] = []
                self.configuration["geoclasses"] = {}
                for result in results["results"]["bindings"]:
                    if "rel" in result \
                            and result["rel"]["value"] not in DocConfig.geoproperties \
                            and SPARQLUtils.namespaces["owl"] not in result["rel"]["value"] \
                            and SPARQLUtils.namespaces["rdfs"] not in result["rel"]["value"] \
                            and SPARQLUtils.namespaces["skos"] not in result["rel"]["value"]:
                        if not result["rel"]["value"] in self.configuration["geoobjproperty"]:
                            self.configuration["geoobjproperty"].append(result["rel"]["value"])
                        if "acon" in result:
                            if result["acon"]["value"] not in self.configuration["geoclasses"]:
                                self.configuration["geoclasses"][result["acon"]["value"]] = []
                            if not result["rel"]["value"] in self.configuration["geoclasses"][result["acon"]["value"]]:
                                self.configuration["geoclasses"][result["acon"]["value"]].append(result["rel"]["value"])
                for cls in self.configuration["geoclasses"]:
                    self.configuration["geoclasses"][cls] = list(self.configuration["geoclasses"][cls])
                # QgsMessageLog.logMessage(str(self.configuration["geoobjproperty"])

    def detectTripleStoreType(self,configuration,credentialUserName,credentialPassword, authmethod,capabilitylist):
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["sparql11"], credentialUserName,
                                          credentialPassword, authmethod):
            configuration["resource"]["sparql11"] = True
            capabilitylist.append("SPARQL 1.1 Support")
        else:
            configuration["resource"]["sparql11"] = False
            capabilitylist.append("SPARQL 1.0 Support")
        if self.testTripleStoreConnection(configuration["resource"], self.testQueries["geosparql"], credentialUserName,
                                          credentialPassword, authmethod):
            configuration["resource"]["geosparql10"] = True
            configuration["featurecollectionclasses"] = ["http://www.opengis.net/ont/geosparql#FeatureCollection"]
            configuration["geometrycollectionclasses"] = ["http://www.opengis.net/ont/geosparql#GeometryCollection"]
            configuration["type"] = "geosparqlendpoint"
            configuration["bboxquery"] = {}
            configuration["bboxquery"]["type"] = "geosparql"
            configuration["bboxquery"][
                "query"] = "FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#wktLiteral>))"
            capabilitylist.append("GeoSPARQL 1.0 Support")
        else:
            configuration["resource"]["geosparql10"] = False
            capabilitylist.append("No GeoSPARQL Support")
        return capabilitylist

    def testTripleStoreConnection(self, triplestoreurl, query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1",credentialUserName=None,credentialPassword=None,authmethod=None):
        #QgsMessageLog.logMessage("Execute query: "+str(query), MESSAGE_CATEGORY, Qgis.Info)
        results=SPARQLUtils.executeQuery(triplestoreurl,query,{"auth":{"method":authmethod,"userCredential":credentialUserName,"userPassword":credentialPassword}})
        #QgsMessageLog.logMessage("Query results: "+str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results!=False:
            if self.testURL and not self.testConfiguration:
                self.message = "URL depicts a valid SPARQL Endpoint!"
            if "ASK" in query:
                #QgsMessageLog.logMessage("Result: "+str(results["boolean"]), MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(results,bool):
                    return results
                return results["boolean"]
            self.feasibleConfiguration = True
            return True
        return results

    def detectPropertiesByName(self,triplestoreurl, query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1",credentialUserName=None,credentialPassword=None,authmethod=None):
        query="SELECT DISTINCT ?prop ?propLabel WHERE {?a ?prop ?b .{ ?ab <http://wikiba.se/ontology#directClaim> ?prop . ?ab <http://www.w3.org/2000/01/rdf-schema#label> ?propLabel .}UNION {?prop <<http://www.w3.org/2000/01/rdf-schema#label> ?propLabel .} FILTER(lang(?propLabel)=\"en\"))}"
        results = SPARQLUtils.executeQuery(triplestoreurl, query, {"auth": {"method": authmethod, "userCredential": credentialUserName, "userPassword": credentialPassword}})


    ## Detects default configurations of common geospatial triple stores.
    #  @param self The object pointer.
    def detectTripleStoreConfiguration(self,triplestorename,triplestoreurl,detectnamespaces,prefixstore,progress,credentialUserName=None,credentialPassword=None,authmethod=None):
        self.configuration=self.addDefaultConfigurationParameters(triplestorename,triplestoreurl,credentialUserName,credentialPassword,authmethod)
        capabilitylist=[]
        if self.testTripleStoreConnection(self.configuration["resource"],self.testQueries["available"],credentialUserName,credentialPassword,authmethod):
            capabilitylist=self.detectTripleStoreType(self.configuration,credentialUserName,credentialPassword,authmethod,capabilitylist)
            gottype=self.detectLiteralType(self.configuration,credentialUserName,credentialPassword,authmethod,capabilitylist)
            rdftype = self.detectTypeProperty(self.configuration["resource"], credentialUserName,credentialPassword, authmethod, self.configuration)
            subclassof=self.detectSubClassOfProperty(self.configuration["resource"],credentialUserName, credentialPassword, authmethod,self.configuration)
            equivprops=self.detectEquivalentProperties(self.configuration["resource"],credentialUserName, credentialPassword, authmethod,self.configuration)
            equivcls=self.detectEquivalentClasses(self.configuration["resource"],credentialUserName, credentialPassword, authmethod,self.configuration)
            if not gottype:
                self.message = "SPARQL endpoint does not seem to include the following geometry relations:<ul><li>geo:asWKT</li><li>geo:asGeoJSON</li><li> geo:lat, geo:long</li></ul><br>A manual configuration is probably necessary to include this SPARQL endpoint if it contains geometries<br>Do you still want to add this SPARQL endpoint?"
            self.feasibleConfiguration = True
            res = set()
            if isinstance(triplestoreurl,Graph):
                for nstup in triplestoreurl.namespaces():
                    if str(nstup[1]) in prefixstore["reversed"]:
                        self.configuration["prefixes"][prefixstore["reversed"][str(nstup[1])]] = str(nstup[0])
                    else:
                        self.configuration["prefixes"][nstup[0]] = nstup[1]
            elif detectnamespaces:
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
            if rdftype=="":
                self.missingproperties.append("typeproperty")
            if subclassof=="":
                self.missingproperties.append("subclassproperty")
            if self.testTripleStoreConnection(self.configuration["resource"],self.testQueries["hasDCTermsTitleLabel"]):
                self.configuration["labelproperty"].append("http://purl.org/dc/terms/title")
            if self.testTripleStoreConnection(self.configuration["resource"],self.testQueries["hasSKOSPrefLabel"]):
                self.configuration["labelproperty"].append("http://www.w3.org/2004/02/skos/core#prefLabel")
            self.configuration["classfromlabelquery"] = "SELECT DISTINCT ?class ?label { ?class %%typeproperty%% <http://www.w3.org/2002/07/owl#Class> . \n"+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?class",self.configuration,"OPTIONAL","")+" FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
            self.configuration["propertyfromlabelquery"] = "SELECT DISTINCT ?class ?label { ?class %%typeproperty%% <http://www.w3.org/2002/07/owl#ObjectProperty> . \n"+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?class",self.configuration,"OPTIONAL","")+" FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
            #QgsMessageLog.logMessage(str("SELECT DISTINCT ?acon ?rel WHERE { ?a a ?acon . ?a ?rel ?item. "+str(self.configuration["geotriplepattern"][0])+" }"))
            if not isinstance(triplestoreurl,Graph):
                self.detectGeometryObjectRelations()
        else:
            self.message = "URL does not depict a valid SPARQL Endpoint!"
            self.feasibleConfiguration = False
            return False
        self.message=self.createCapabilityMessage(capabilitylist)
        return True