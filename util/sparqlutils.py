from SPARQLWrapper import SPARQLWrapper, JSON, GET, POST, BASIC, DIGEST
import urllib
import requests
import sys
from urllib.request import urlopen
import json
from qgis.core import Qgis, QgsGeometry
from qgis.core import QgsMessageLog
from qgis.PyQt.QtCore import QSettings
from rdflib import Graph

MESSAGE_CATEGORY = "SPARQLUtils"

class SPARQLUtils:
    supportedLiteralTypes = {"http://www.opengis.net/ont/geosparql#wktLiteral": "wkt",
                             "http://www.opengis.net/ont/geosparql#gmlLiteral": "gml",
                             "http://www.opengis.net/ont/geosparql#wkbLiteral": "wkb",
                             "http://www.opengis.net/ont/geosparql#geoJSONLiteral": "geojson",
                             "http://www.opengis.net/ont/geosparql#kmlLiteral": "kml",
                             "http://www.opengis.net/ont/geosparql#dggsLiteral": "dggs"}

    namespaces={"rdfs":"http://www.w3.org/2000/01/rdf-schema#","owl":"http://www.w3.org/2002/07/owl#","dc":"http://purl.org/dc/terms/","skos":"http://www.w3.org/2004/02/skos/core#"}

    annotationnamespaces=["http://www.w3.org/2004/02/skos/core#","http://www.w3.org/2000/01/rdf-schema#","http://purl.org/dc/terms/"]

    geoproperties={"http://www.opengis.net/ont/geosparql#asWKT":"DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asGML": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asKML": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asGeoJSON": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
                   "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
                   "http://www.georss.org/georss/point": "DatatypeProperty",
                   "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#lat":"DatatypeProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#long": "DatatypeProperty",
                   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": "DatatypeProperty",
                   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": "DatatypeProperty",
                   "http://schema.org/geo": "ObjectProperty",
                   "http://geovocab.org/geometry#geometry": "ObjectProperty",
                   "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
                   "http://rdfs.co/juso/geometry": "ObjectProperty",
                   "http://www.wikidata.org/prop/direct/P625":"DatatypeProperty",
                   "http://www.wikidata.org/prop/direct/P3896": "DatatypeProperty",
    }

    styleproperties={
        "http://www.opengis.net/ont/geosparql#style"
    }

    latlongeomproperties=[
        ("http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude","http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude"),
        ("http://www.w3.org/2003/01/geo/wgs84_pos#long","http://www.w3.org/2003/01/geo/wgs84_pos#lat")
                          ]

    graphResource = ["solid:forClass"]

    authmethods={"HTTP BASIC":BASIC,"HTTP DIGEST":DIGEST}

    classnode="Class"
    geoclassnode="GeoClass"
    linkedgeoclassnode="LinkedGeoClass"
    linkedgeoinstancenode="LinkedGeoInstance"
    instancenode="Instance"
    objectpropertynode="ObjectProperty"
    datatypepropertynode="DatatypeProperty"
    geoinstancenode="GeoInstance"
    collectionclassnode="CollectionClass"
    instancesloadedindicator="InstancesLoaded"
    treeNodeToolTip="Double click to load, right click for menu"

    @staticmethod
    def queryPreProcessing(query,triplestoreconf,concept=None,convertToCollectionForm=False):
        QgsMessageLog.logMessage('Preprocessing"{}"'.format(query.replace("<", "").replace(">", "")), MESSAGE_CATEGORY,
                                 Qgis.Info)
        if convertToCollectionForm:
            query=query.replace("?con %%typeproperty%% %%concept%% .","%%concept%% %%collectionmemberproperty%% ?con .")
        if concept!=None:
            if "resource" in triplestoreconf and "url" in triplestoreconf["resource"] and "wikidata" in triplestoreconf["resource"]["url"] and concept[concept.find('(')+1:-1].startswith("Q"):
                query=query.replace("%%concept%%",str("wd:" + concept[concept.find('(')+1:-1]))
            else:
                query = query.replace("%%concept%%", "<" + str(concept) + ">")
        typeproperty = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in triplestoreconf:
            typeproperty=triplestoreconf["typeproperty"]
        subclassproperty = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        if "subclassproperty" in triplestoreconf:
            subclassproperty=triplestoreconf["subclassproperty"]
        labelproperty = "http://www.w3.org/2000/01/rdf-schema#label"
        if "labelproperty" in triplestoreconf:
            labelproperty =triplestoreconf["labelproperty"]
        collectionmemberproperty="http://www.w3.org/2000/01/rdf-schema#member"
        if "collectionmemberproperty" in triplestoreconf:
            collectionmemberproperty=triplestoreconf["collectionmemberproperty"]
        query=query.replace("%%subclassproperty%%","<"+subclassproperty+">")\
            .replace("%%typeproperty%%","<"+typeproperty+">")\
            .replace("%%labelproperty%%","<"+labelproperty+">")\
            .replace("%%collectionmemberproperty%%","<"+collectionmemberproperty+">").replace("<<","<").replace(">>",">")
        QgsMessageLog.logMessage('Preprocessing finished"{}"'.format(query.replace("<", "").replace(">", "")), MESSAGE_CATEGORY,
                             Qgis.Info)
        return query

    @staticmethod
    def executeQuery(triplestoreurl, query,triplestoreconf=None):
        results=False
        QgsMessageLog.logMessage(str(triplestoreurl), MESSAGE_CATEGORY,
                                 Qgis.Info)
        if triplestoreurl["type"]=="endpoint":
            s = QSettings()  # getting proxy from qgis options settings
            proxyEnabled = s.value("proxy/proxyEnabled")
            proxyType = s.value("proxy/proxyType")
            proxyHost = s.value("proxy/proxyHost")
            proxyPort = s.value("proxy/proxyPort")
            proxyUser = s.value("proxy/proxyUser")
            proxyPassword = s.value("proxy/proxyPassword")
            if proxyHost != None and proxyHost != "" and proxyPort != None and proxyPort != "":
                QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
                proxy = urllib.request.ProxyHandler({'http': proxyHost})
                opener = urllib.request.build_opener(proxy)
                urllib.request.install_opener(opener)
            QgsMessageLog.logMessage('Started task "{}"'.format(query.replace("<","").replace(">","")), MESSAGE_CATEGORY, Qgis.Info)
            sparql = SPARQLWrapper(triplestoreurl["url"])
            if triplestoreconf!=None and "auth" in triplestoreconf and "userCredential" in triplestoreconf["auth"] \
                    and triplestoreconf["auth"]["userCredential"]!="" \
                    and "userPassword" in triplestoreconf["auth"] \
                    and triplestoreconf["auth"]["userPassword"] != None:
                #QgsMessageLog.logMessage('Credentials? ' + str(triplestoreconf["auth"]["userCredential"])+" "+str(triplestoreconf["auth"]["userPassword"]), MESSAGE_CATEGORY, Qgis.Info)
                if "method" in triplestoreconf["auth"] and triplestoreconf["auth"]["method"] in SPARQLUtils.authmethods:
                    sparql.setHTTPAuth(SPARQLUtils.authmethods[triplestoreconf["auth"]["method"]])
                else:
                    sparql.setHTTPAuth(BASIC)
                sparql.setCredentials(triplestoreconf["auth"]["userCredential"], triplestoreconf["auth"]["userPassword"])
            sparql.setQuery(query)
            sparql.setMethod(GET)
            sparql.setReturnFormat(JSON)
            try:
                if len(query)>2000:
                    raise Exception
                results = sparql.queryAndConvert()
                if "status_code" in results:
                    QgsMessageLog.logMessage("Result: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
                    raise Exception
            except Exception as e:
                try:
                    sparql = SPARQLWrapper(triplestoreurl["url"],
                                           agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                    sparql.setQuery(query)
                    if triplestoreconf != None and "auth" in triplestoreconf and "userCredential" in triplestoreconf["auth"] \
                            and triplestoreconf["auth"]["userCredential"] != "" \
                            and "userPassword" in triplestoreconf["auth"] \
                            and triplestoreconf["auth"]["userPassword"] != None:
                        #QgsMessageLog.logMessage(
                        #    'Credentials? ' + str(triplestoreconf["auth"]["userCredential"]) + " " + str(
                        #       triplestoreconf["auth"]["userPassword"]), MESSAGE_CATEGORY, Qgis.Info)
                        if "method" in triplestoreconf["auth"] and triplestoreconf["auth"][
                            "method"] in SPARQLUtils.authmethods:
                            sparql.setHTTPAuth(SPARQLUtils.authmethods[triplestoreconf["auth"]["method"]])
                        else:
                            sparql.setHTTPAuth(BASIC)
                        sparql.setCredentials(triplestoreconf["auth"]["userCredential"],
                                              triplestoreconf["auth"]["userPassword"])
                    sparql.setMethod(POST)
                    sparql.setReturnFormat(JSON)
                    results = sparql.queryAndConvert()
                    if "status_code" in results:
                        QgsMessageLog.logMessage("Result: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
                        raise Exception
                except:
                    QgsMessageLog.logMessage("Exception: " + str(e), MESSAGE_CATEGORY, Qgis.Info)
                    if "OntopUnsupportedInputQueryException: The expression Exists" in str(e):
                        return "Exists error"
                    return False
        else:
            graph=triplestoreurl["instance"]
            QgsMessageLog.logMessage("Graph: " + str(triplestoreurl), MESSAGE_CATEGORY, Qgis.Info)
            QgsMessageLog.logMessage("Query: " + str(query), MESSAGE_CATEGORY, Qgis.Info)
            if graph!=None:
                results=json.loads(graph.query(query).serialize(format="json"))
        QgsMessageLog.logMessage("Result: " + str(len(results))+" triples", MESSAGE_CATEGORY, Qgis.Info)
        return results

    @staticmethod
    def invertPrefixes(prefixes):
        #QgsMessageLog.logMessage("Invert Prefixes: " + str(prefixes), MESSAGE_CATEGORY, Qgis.Info)
        inv_map = {v: k for k, v in prefixes.items()}
        return inv_map

    @staticmethod
    def labelFromURI(uri,prefixlist=None):
        if not uri.startswith("http"):
            return uri
        if "#" in uri:
            prefix=uri[:uri.rfind("#")+1]
            if prefixlist!=None and prefix in prefixlist:
                return str(prefixlist[prefix])+":"+str(uri[uri.rfind("#") + 1:])
            return uri[uri.rfind("#") + 1:]
        if "/" in uri:
            prefix=uri[:uri.rfind("/")+1]
            if prefixlist!=None and prefix in prefixlist:
                return str(prefixlist[prefix])+":"+str(uri[uri.rfind("/") + 1:])
            return uri[uri.rfind("/") + 1:]
        return uri

    @staticmethod
    def shortenLiteral(literal,numchars):
        return literal[numchars:]

    @staticmethod
    def expandRelValToAmount(query,amount):
        QgsMessageLog.logMessage('ExpandQuery '+str(amount)+"_" + str(query), MESSAGE_CATEGORY, Qgis.Info)
        if "?rel" not in query and "?val" not in query:
            return query
        selectpart=query[0:query.find("WHERE")]
        optionals="?item ?rel ?val . "
        if amount>1:
            for i in range(1,amount+1):
                selectpart+=" ?rel"+str(i)+" ?val"+str(i)+" "
                if i==1:
                    optionals += "OPTIONAL { ?val ?rel" + str(i) + " ?val" + str(i) + " . "
                else:
                    optionals+="OPTIONAL { ?val"+str(i-1)+" ?rel"+str(i)+" ?val"+str(i)+" . "
            for i in range(1,amount+1):
                optionals+="}"
        query=query.replace(query[0:query.find("WHERE")],selectpart).replace("?item ?rel ?val . ",optionals)
        QgsMessageLog.logMessage('ExpandQuery '+str(query), MESSAGE_CATEGORY, Qgis.Info)
        return query

    @staticmethod
    def loadAdditionalGraphResources(existinggraph,graphuri):
        if graphuri==None or graphuri=="":
            return None

    @staticmethod
    def loadGraph(graphuri,graph=None):
        if graphuri==None or graphuri=="":
            return None
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled")
        proxyType = s.value("proxy/proxyType")
        proxyHost = s.value("proxy/proxyHost")
        proxyPort = s.value("proxy/proxyPort")
        proxyUser = s.value("proxy/proxyUser")
        proxyPassword = s.value("proxy/proxyPassword")
        if proxyHost != None and proxyHost != "" and proxyPort != None and proxyPort != "":
            #QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        #QgsMessageLog.logMessage('Started task "{}"'.format("Load Graph"), MESSAGE_CATEGORY, Qgis.Info)
        if graph==None:
            graph = Graph()
        try:
            if graphuri.startswith("http"):
                QgsMessageLog.logMessage(" Data: " + str(graphuri) + "", MESSAGE_CATEGORY, Qgis.Info)
                with urllib.request.urlopen(graphuri) as data:
                    readit=data.read().decode()
                    QgsMessageLog.logMessage(" Data: "+str(readit)+"", MESSAGE_CATEGORY, Qgis.Info)
                    filepath = graphuri.split(".")
                    graph.parse(data=readit,format=filepath[len(filepath) - 1])
            else:
                filepath = graphuri.split(".")
                result = graph.parse(graphuri, format=filepath[len(filepath) - 1])
        except Exception as e:
            QgsMessageLog.logMessage('Failed "{}"'.format(str(e)), MESSAGE_CATEGORY, Qgis.Info)
            #self.exception = str(e)
            return None
        return graph

    @staticmethod
    def detectLiteralTypeByURI(literal):
        return ""

    @staticmethod
    def detectGeoLiteralType(literal):
        try:
            geom = QgsGeometry.fromWkt(literal)
            return "wkt"
        except:
            print("no wkt")
        try:
            geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
            return "wkb"
        except:
            print("no wkb")
        try:
            json.loads(literal)
            return "geojson"
        except:
            print("no geojson")
        return ""

    @staticmethod
    def handleURILiteral(uri):
        result = []
        if uri.startswith("http") and uri.endswith(".map"):
            try:
                f = urlopen(uri)
                myjson = json.loads(f.read())
                if "data" in myjson and "type" in myjson["data"] and myjson["data"]["type"] == "FeatureCollection":
                    features = myjson["data"]["features"]
                    for feat in features:
                        result.append(feat["geometry"])
                return result
            except:
                QgsMessageLog.logMessage("Error getting geoshape " + str(uri) + " - " + str(sys.exc_info()[0]))
        return None

    ## Executes a SPARQL endpoint specific query to find labels for given classes. The query may be configured in the configuration file.
    #  @param self The object pointer.
    #  @param classes array of classes to find labels for
    #  @param query the class label query
    @staticmethod
    def getLabelsForClasses(classes, query, triplestoreconf, triplestoreurl,preferredlang="en",typeindicator="class"):
        # url="https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids="
        if query==None:
            if typeindicator=="class":
                query="SELECT ?class ?label\n WHERE { %%concepts%%  \n OPTIONAL {\n ?class <"+str(triplestoreconf["labelproperty"])+"> ?label .\n FILTER(langMatches(lang(?label), \""+str(preferredlang)+"\"))\n }\n OPTIONAL {\n ?class <"+str(triplestoreconf["labelproperty"])+"> ?label .\n } \n} "
        if "SELECT" in query:
            vals = "VALUES ?class {\n "
            for qid in classes.keys():
                vals += "<"+qid + "> \n"
            vals += "}\n"
            query = query.replace("%%concepts%%", vals)
            #QgsMessageLog.logMessage("Querying for "+str(len(vals))+" concepts", MESSAGE_CATEGORY, Qgis.Info)
            results = SPARQLUtils.executeQuery(triplestoreurl, query)
            result=classes
            if results == False:
                return result
            #QgsMessageLog.logMessage("Got " + str(len(results)) + " labels", MESSAGE_CATEGORY, Qgis.Info)
            for res in results["results"]["bindings"]:
                if res["class"]["value"] in classes and "label" in res:
                    classes[res["class"]["value"]]["label"]=res["label"]["value"]
                else:
                    classes[res["class"]["value"]]["label"] = ""
        else:
            url = query
            i = 0
            qidquery = ""
            wdprefix = ""
            firstkey=next(iter(classes))
            result=classes
            #QgsMessageLog.logMessage(str(firstkey), MESSAGE_CATEGORY, Qgis.Info)
            if "Q" in firstkey:
                wdprefix = "http://www.wikidata.org/entity/"
            elif "P" in firstkey:
                wdprefix = "http://www.wikidata.org/prop/direct/"
            for qid in classes.keys():
                #QgsMessageLog.logMessage(str(qid), MESSAGE_CATEGORY, Qgis.Info)
                if "wikidata" in triplestoreurl["url"] and "Q" in qid:
                    qidquery += "Q" + qid.split("Q")[1]
                elif "wikidata" in triplestoreurl["url"] and "P" in qid:
                    qidquery += "P" + qid.split("P")[1]
                elif "wikidata" in triplestoreurl["url"]:
                    result[qid]["label"] = qid
                    continue
                if (i % 50) == 0:
                    while qidquery.endswith("|"):
                        qidquery=qidquery[:-1]
                    #QgsMessageLog.logMessage(str(url.replace("%%concepts%%", qidquery)), MESSAGE_CATEGORY, Qgis.Info)
                    myResponse = json.loads(requests.get(url.replace("%%concepts%%", qidquery).replace("%%language%%",preferredlang)).text)
                    #QgsMessageLog.logMessage(str(myResponse), MESSAGE_CATEGORY, Qgis.Info)
                    #QgsMessageLog.logMessage("Entities: "+str(len(myResponse["entities"])), MESSAGE_CATEGORY, Qgis.Info)
                    if "entities" in myResponse:
                        for ent in myResponse["entities"]:
                            #QgsMessageLog.logMessage(str(ent), MESSAGE_CATEGORY, Qgis.Info)
                            if ent.startswith("P"):
                                wdprefix="http://www.wikidata.org/prop/direct/"
                            elif ent.startswith("Q"):
                                wdprefix="http://www.wikidata.org/entity/"
                            else:
                                wdprefix=""
                            if preferredlang in myResponse["entities"][ent]["labels"]:
                                result[wdprefix+ent]["label"] = myResponse["entities"][ent]["labels"][preferredlang]["value"]
                            elif "en" in myResponse["entities"][ent]["labels"]:
                                result[wdprefix+ent]["label"] = myResponse["entities"][ent]["labels"]["en"]["value"]
                            else:
                                result[wdprefix+ent]["label"]=qid
                    qidquery = ""
                else:
                    qidquery += "|"
                i = i + 1
            if qidquery!="":
                while qidquery.endswith("|"):
                    qidquery = qidquery[:-1]
                #QgsMessageLog.logMessage(str(url.replace("%%concepts%%", qidquery)), MESSAGE_CATEGORY, Qgis.Info)
                myResponse = json.loads(requests.get(url.replace("%%concepts%%", qidquery)).text)
                #QgsMessageLog.logMessage(str(myResponse), MESSAGE_CATEGORY, Qgis.Info)
                #QgsMessageLog.logMessage("Entities: "+str(len(myResponse["entities"])), MESSAGE_CATEGORY, Qgis.Info)
                if "entities" in myResponse:
                    for ent in myResponse["entities"]:
                        print(ent)
                        if preferredlang in myResponse["entities"][ent]["labels"]:
                            result[wdprefix+ent]["label"] = myResponse["entities"][ent]["labels"][preferredlang]["value"]
                        elif "en" in myResponse["entities"][ent]["labels"]:
                            result[wdprefix+ent]["label"] = myResponse["entities"][ent]["labels"]["en"]["value"]
                        else:
                            result[wdprefix+ent]["label"] = ""
        return result
