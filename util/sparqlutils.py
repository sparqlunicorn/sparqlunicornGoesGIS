from SPARQLWrapper import SPARQLWrapper, JSON, RDFXML, GET, POST, BASIC, DIGEST
import urllib
import requests
from urllib.request import urlopen
import json

from ..dialogs.info.errormessagebox import ErrorMessageBox
from osgeo import ogr
from qgis.core import Qgis, QgsGeometry,QgsVectorLayer, QgsMessageLog
from qgis.PyQt.QtCore import QSettings
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

MESSAGE_CATEGORY = "SPARQLUtils"

class SPARQLUtils:
    supportedLiteralTypes = {
                             "http://www.opengis.net/ont/geosparql#wktLiteral": "wkt",
                             "http://www.opengis.net/ont/geosparql#gmlLiteral": "gml",
                             "http://www.opengis.net/ont/geosparql#wkbLiteral": "wkb",
                             "http://www.opengis.net/ont/geosparql#geoJSONLiteral": "geojson",
                             "http://www.opengis.net/ont/geosparql#kmlLiteral": "kml",
                             "http://www.opengis.net/ont/geosparql#dggsLiteral": "dggs"
                             }

    namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs":"http://www.w3.org/2000/01/rdf-schema#","owl":"http://www.w3.org/2002/07/owl#","dc":"http://purl.org/dc/terms/","skos":"http://www.w3.org/2004/02/skos/core#"}

    annotationnamespaces=["http://www.w3.org/2004/02/skos/core#","http://www.w3.org/2000/01/rdf-schema#","http://purl.org/dc/terms/"]

    metadatanamespaces = ["http://ldf.fi/void-ext#", "http://rdfs.org/ns/void#", "http://purl.org/dc/terms/",
                          "http://purl.org/dc/elements/1.1/", "http://www.w3.org/ns/prov#",
                          "http://www.w3.org/ns/prov-o/", "http://creativecommons.org/ns#",
                          "http://www.w3.org/ns/dcat#", "http://purl.org/cerif/frapo/", "http://www.lido-schema.org/"]

    addressproperties={
        "https://schema.org/address": "ObjectProperty"
    }

    lexicontypes = {"http://www.w3.org/ns/lemon/lexicog#Entry": "","http://www.w3.org/ns/lemon/ontolex#Entry": "",
                    "http://www.w3.org/ns/lemon/lexicog#LexicalEntry": "","http://www.w3.org/ns/lemon/ontolex#LexicalEntry": "",
                    "http://www.w3.org/ns/lemon/ontolex#Word": "","http://www.w3.org/ns/lemon/lexicog#Word": ""}

    #, "http://www.w3.org/ns/lemon/ontolex#Form": ""



    graphResource = ["solid:forClass"]

    authmethods={"HTTP BASIC":BASIC,"HTTP DIGEST":DIGEST}

    classnode="Class"
    geoclassnode="GeoClass"
    linkedgeoclassnode="LinkedGeoClass"
    halfgeoclassnode="HalfGeoClass"
    linkedgeoinstancenode="LinkedGeoInstance"
    instancenode="Instance"
    objectpropertynode="ObjectProperty"
    geoobjectpropertynode="GeoObjectProperty"
    geodatatypepropertynode="GeoDatatypeProperty"
    datatypepropertynode="DatatypeProperty"
    annotationpropertynode="AnnotationProperty"
    geoinstancenode="GeoInstance"
    collectionclassnode="CollectionClass"
    instancesloadedindicator="InstancesLoaded"
    treeNodeToolTip="Double click to load, right click for menu"
    exception=""

    @staticmethod
    def queryPreProcessing(query,triplestoreconf,concept=None,convertToCollectionForm=False,pquery=False):
        QgsMessageLog.logMessage('Preprocessing"{}"'.format(query.replace("<", "").replace(">", "")), MESSAGE_CATEGORY,
                                 Qgis.Info)
        if convertToCollectionForm:
            query=query.replace("?con %%typeproperty%% %%concept%% .","%%concept%% %%collectionmemberproperty%% ?con .")
        if concept is not None:
            if "resource" in triplestoreconf and "url" in triplestoreconf["resource"] and ("wikidata" in triplestoreconf["resource"]["url"] or "factgrid" in triplestoreconf["resource"]["url"]) and concept[concept.find('(')+1:-1].startswith("Q"):
                query=query.replace("%%concept%%",str("wd:" + concept[concept.find('(')+1:]))
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
            .replace("%%labelproperty%%","<"+labelproperty[0]+">")\
            .replace("%%collectionmemberproperty%%","<"+collectionmemberproperty+">").replace("<<","<").replace(">>",">")
        QgsMessageLog.logMessage('Preprocessing finished"{}"'.format(query.replace("<", "").replace(">", "")), MESSAGE_CATEGORY,
                             Qgis.Info)
        if pquery:
            return prepareQuery(query)
        return query

    @staticmethod
    def constructBBOXQuerySegment(triplestoreconf,bboxpoints,widthm=None,curquery=None):
        if "bboxquery" in triplestoreconf and \
                triplestoreconf["bboxquery"]["type"] == "geosparql":
            filterstatement=triplestoreconf["bboxquery"][
                "query"].replace("%%x1%%", str(bboxpoints[0].asPoint().x())).replace("%%x2%%",str(bboxpoints[2].asPoint().x())).replace(
                "%%y1%%", str(bboxpoints[0].asPoint().y())).replace("%%y2%%", str(bboxpoints[2].asPoint().y())) + "\n"
            if curquery is not None:
                return curquery[0:curquery.rfind('}')] + filterstatement + curquery[curquery.rfind('}') + 1:]
            else:
                return filterstatement
        elif "bboxquery" in triplestoreconf and \
                triplestoreconf["bboxquery"]["type"] == "minmax":
            filterstatement=triplestoreconf["bboxquery"][
                "query"].replace("%%minPoint%%", bboxpoints[1].asWkt()).replace("%%maxPoint%%", bboxpoints[3].asWkt())
            if curquery is not None:
                curquery = curquery[0:curquery.rfind('}')] + filterstatement + curquery[curquery.rfind('}') + 1:]
                return curquery
            else:
                return filterstatement
        elif "bboxquery" in triplestoreconf and \
                triplestoreconf["bboxquery"]["type"] == "pointdistance":
            filterstatement=triplestoreconf["bboxquery"][
                "query"].replace("%%lat%%", str(bboxpoints[0].asPoint().y())).replace("%%lon%%",str(bboxpoints[0].asPoint().x())).replace("%%distance%%", str(widthm / 1000))
            if curquery is not None:
                return curquery[0:curquery.rfind('}')] + filterstatement + curquery[curquery.rfind('}') + 1:]
            else:
                return filterstatement
        else:
            geosparqltemplate="FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#wktLiteral>))"
            filterstatement=geosparqltemplate.replace("%%x1%%", str(bboxpoints[0].asPoint().x())).replace("%%x2%%",
                                                                               str(bboxpoints[2].asPoint().x())).replace(
                "%%y1%%", str(bboxpoints[0].asPoint().y())).replace("%%y2%%",str(bboxpoints[2].asPoint().y())) + "\n"
            if curquery is not None:
                return curquery[0:curquery.rfind('}')] + filterstatement + curquery[curquery.rfind('}') + 1:]
            else:
                return filterstatement

    @staticmethod
    ## Executes a SPARQL query using RDFlib, with or without credentials and tries GET and POST query methods and uses proxy settings
    def executeQuery(triplestoreurl, query,triplestoreconf=None):
        results=False
        SPARQLUtils.exception = None
        QgsMessageLog.logMessage(str(triplestoreurl), MESSAGE_CATEGORY, Qgis.Info)
        if triplestoreurl["type"]=="endpoint":
            s = QSettings()  # getting proxy from qgis options settings
            proxyEnabled = s.value("proxy/proxyEnabled")
            proxyType = s.value("proxy/proxyType")
            proxyHost = s.value("proxy/proxyHost")
            proxyPort = s.value("proxy/proxyPort")
            proxyUser = s.value("proxy/proxyUser")
            proxyPassword = s.value("proxy/proxyPassword")
            if proxyHost is not None and proxyHost != "" and proxyPort is not None and proxyPort != "":
                QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
                proxy = urllib.request.ProxyHandler({'http': proxyHost})
                opener = urllib.request.build_opener(proxy)
                urllib.request.install_opener(opener)
            QgsMessageLog.logMessage('Started task "{}"'.format(str(query).replace("<","").replace(">","")), MESSAGE_CATEGORY, Qgis.Info)
            sparql = SPARQLWrapper(triplestoreurl["url"])
            if triplestoreconf is not None and "auth" in triplestoreconf and "userCredential" in triplestoreconf["auth"] \
                    and triplestoreconf["auth"]["userCredential"]!="" \
                    and "userPassword" in triplestoreconf["auth"] \
                    and triplestoreconf["auth"]["userPassword"] is not None:
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
                QgsMessageLog.logMessage("Result: QUERY FINISHED WITH RESULTS", MESSAGE_CATEGORY, Qgis.Info)
                #QgsMessageLog.logMessage("Result: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(results,dict) and "status_code" in results:
                    QgsMessageLog.logMessage("Result: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
                    SPARQLUtils.exception = str(results)
                    raise Exception
            except Exception as e:
                try:
                    sparql = SPARQLWrapper(triplestoreurl["url"],agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                    sparql.setQuery(query)
                    if triplestoreconf is not None and "auth" in triplestoreconf and "userCredential" in triplestoreconf["auth"] \
                            and triplestoreconf["auth"]["userCredential"] != "" \
                            and "userPassword" in triplestoreconf["auth"] \
                            and triplestoreconf["auth"]["userPassword"] is not None:
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
                    QgsMessageLog.logMessage("Result: QUERY FINISHED WITH RESULTS", MESSAGE_CATEGORY, Qgis.Info)
                    #QgsMessageLog.logMessage("Result: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
                    if isinstance(results,dict) and "status_code" in results:
                        SPARQLUtils.exception = str(results)
                        raise Exception
                except Exception as e:
                    QgsMessageLog.logMessage("Exception: " + str(e), MESSAGE_CATEGORY, Qgis.Info)
                    SPARQLUtils.exception=str(e)
                    if "OntopUnsupportedInputQueryException: The expression Exists" in str(e):
                        return "Exists error"
                    return False
        else:
            if "instance" in triplestoreurl:
                graph=triplestoreurl["instance"]
            else:
                graph=SPARQLUtils.loadGraph(str(triplestoreurl["url"]))
                triplestoreurl["instance"]=graph
            #QgsMessageLog.logMessage("Graph: " + str(triplestoreurl), MESSAGE_CATEGORY, Qgis.Info)
            #QgsMessageLog.logMessage("Query: " + str(query).replace("<", "").replace(">", ""), MESSAGE_CATEGORY, Qgis.Info)
            if graph is not None:
                if "CONSTRUCT" in str(query):
                    results = graph.query(query)
                    resg = Graph()
                    for res in results:
                        resg.add(res)
                    results=resg
                else:
                    res=graph.query(query)
                    #QgsMessageLog.logMessage("Result: " + str(len(res)) + " triples", MESSAGE_CATEGORY, Qgis.Info)
                    results=json.loads(res.serialize(format="json"))
                #QgsMessageLog.logMessage("Result: " + str(len(results))+" triples", MESSAGE_CATEGORY, Qgis.Info)
        if results!=False:
            QgsMessageLog.logMessage("Result: " + str(len(results))+" triples", MESSAGE_CATEGORY, Qgis.Info)
        return results

    @staticmethod
    def invertPrefixes(prefixes):
        #QgsMessageLog.logMessage("Invert Prefixes: " + str(prefixes), MESSAGE_CATEGORY, Qgis.Info)
        inv_map = {v: k for k, v in prefixes.items()}
        return inv_map

    @staticmethod
    def handleException(callingtask="",title=None,text=None):
        if SPARQLUtils.exception is not None:
            ErrorMessageBox(callingtask+" An error occurred!","<html>"+str(SPARQLUtils.exception).replace("\n","<br/>")+"</html>").exec_()
            return True
        if title is not None and text is not None:
            ErrorMessageBox(callingtask+" "+title,"<html>"+text.replace("\n","<br/>")+"</html>").exec_()
            return True
        return False

    @staticmethod
    def instanceToNS(uri):
        if not uri.startswith("http"):
            return uri
        if "#" in uri:
            return uri[:uri.rfind("#") + 1]
        if "/" in uri:
            return uri[:uri.rfind("/") + 1]
        return uri

    @staticmethod
    def labelFromURI(uri,prefixlist=None):
        if not uri.startswith("http"):
            return uri
        if uri.endswith("#"):
            uri=uri[0:-1]
        if "#" in uri:
            prefix=uri[:uri.rfind("#")+1]
            if prefixlist is not None and prefix in prefixlist:
                return str(prefixlist[prefix])+":"+str(uri[uri.rfind("#") + 1:])
            return uri[uri.rfind("#") + 1:]
        if uri.endswith("/"):
            uri=uri[0:-1]
        if "/" in uri:
            prefix=uri[:uri.rfind("/")+1]
            if prefixlist is not None and prefix in prefixlist:
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
        if graphuri is None or graphuri=="":
            return None

    @staticmethod
    def loadGraph(graphuri,graph=None):
        if graphuri is None or graphuri=="":
            return None
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled")
        proxyType = s.value("proxy/proxyType")
        proxyHost = s.value("proxy/proxyHost")
        proxyPort = s.value("proxy/proxyPort")
        proxyUser = s.value("proxy/proxyUser")
        proxyPassword = s.value("proxy/proxyPassword")
        if proxyHost is not None and proxyHost != "" and proxyPort is not None and proxyPort != "":
            #QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        #QgsMessageLog.logMessage('Started task "{}"'.format("Load Graph"), MESSAGE_CATEGORY, Qgis.Info)
        if graph is None:
            graph = Graph()
        try:
            if graphuri.startswith("http"):
                QgsMessageLog.logMessage(" Data: " + str(graphuri) + "", MESSAGE_CATEGORY, Qgis.Info)
                graph.parse(graphuri)
            else:
                filepath = graphuri.split(".")
                graph.parse(graphuri, format=filepath[len(filepath) - 1])
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
        try:
            ogr.CreateGeometryFromGML(literal)
            return "gml"
        except:
            print("no geojson")
        return ""

    @staticmethod
    def mergeLayers(layer1,geojson):
        result=[]
        if "properties" not in geojson:
            geojson["properties"]={}
        feats1 = layer1.getFeatures()
        for feature in feats1:
            curfeature={"type":"Feature","id":feature.id,"properties":{},"geometry":feature.geometry().asJson()}
            if "properties" in geojson:
                for prop in geojson["properties"]:
                    curfeature["properties"][prop]=geojson["properties"][prop]
            for attr in feature:
                curfeature["properties"][attr] = feature[attr]
            result.append(curfeature)
        return result

    @staticmethod
    def handleGeoJSONFile(myjson,currentlayergeojson,onlygeo):
        result=[]
        if "data" in myjson and "type" in myjson["data"] and myjson["data"]["type"] == "FeatureCollection":
            features = myjson["data"]["features"]
            curcounter = 0
            for feat in features:
                if currentlayergeojson is None:
                    result.append(feat["geometry"])
                else:
                    if onlygeo and "properties" in feat:
                        del feat["properties"]
                    if "id" in feat and curcounter > 0:
                        feat["id"] = feat["id"] + "_" + str(curcounter)
                    if "properties" in currentlayergeojson:
                        if "properties" not in feat:
                            feat["properties"] = {}
                        for prop in currentlayergeojson["properties"]:
                            feat["properties"][prop] = currentlayergeojson["properties"][prop]
                    result.append(feat)
                curcounter = 1

    @staticmethod
    def handleURILiteral(uri,currentlayergeojson,onlygeo=True):
        if uri.startswith("http"):
            if uri.endswith(".map") or uri.endswith("geojson"):
                try:
                    f = urlopen(uri)
                    myjson = json.loads(f.read())
                    return SPARQLUtils.handleGeoJSONFile(myjson,currentlayergeojson,onlygeo)
                except Exception as e:
                    QgsMessageLog.logMessage("Error getting geoshape " + str(uri) + " - " + str(e))
            elif uri.startswith("http") and uri.endswith(".kml"):
                try:
                    f = urlopen(uri)
                    kmlfile=f.read()
                    f=open("temp.kml","w")
                    f.write(kmlfile)
                    f.close()
                    vlayer = QgsVectorLayer("temp.kml", "layer", "ogr")
                    return SPARQLUtils.mergeLayers(vlayer,currentlayergeojson)
                except Exception as e:
                    QgsMessageLog.logMessage("Error getting kml " + str(uri) + " - " + str(e))
            elif uri.startswith("http") and uri.endswith(".gml"):
                try:
                    f = urlopen(uri)
                    gmlfile=f.read()
                    f=open("temp.gml","w")
                    f.write(gmlfile)
                    f.close()
                    vlayer = QgsVectorLayer("temp.gml", "layer", "ogr")
                    return SPARQLUtils.mergeLayers(vlayer,currentlayergeojson)
                except Exception as e:
                    QgsMessageLog.logMessage("Error getting gml " + str(uri) + " - " + str(e))
        return None

    ## Executes a SPARQL endpoint specific query to find labels for given classes. The query may be configured in the configuration file.
    #  @param self The object pointer.
    #  @param classes array of classes to find labels for
    #  @param query the class label query
    @staticmethod
    def getLabelsForClasses(classes, query, triplestoreconf, triplestoreurl,preferredlang="en",typeindicator="class"):
        # url="https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids="
        result = classes
        if query is None:
            if typeindicator=="class":
                query="SELECT ?class ?label\n WHERE { %%concepts%%  \n "+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?class",triplestoreconf,"OPTIONAL","FILTER(LANG(?label) = \""+str(preferredlang)+"\") ")+" \n} "
        if "SELECT" in query and "resource" in triplestoreconf \
                and "type" in triplestoreconf["resource"] \
                and ((triplestoreconf["resource"]["type"]=="endpoint"
                and "sparql11" in triplestoreconf["resource"]
                and triplestoreconf["resource"]["sparql11"]==True)
                or triplestoreconf["resource"]["type"]!="endpoint"):
            vals = "VALUES ?class {\n "
            for qid in classes.keys():
                vals += "<"+qid + "> \n"
            vals += "}\n"
            query = query.replace("%%concepts%%", vals)
            #QgsMessageLog.logMessage("Querying for "+str(len(vals))+" concepts", MESSAGE_CATEGORY, Qgis.Info)
            results = SPARQLUtils.executeQuery(triplestoreurl, query)
            if not results:
                return result
            #QgsMessageLog.logMessage("Got " + str(len(results)) + " labels", MESSAGE_CATEGORY, Qgis.Info)
            for res in results["results"]["bindings"]:
                if res["class"]["value"] in classes and "label" in res:
                    classes[res["class"]["value"]]["label"]=res["label"]["value"]
                else:
                    classes[res["class"]["value"]]["label"] = ""
        elif query.startswith("http"):
            url = query
            i = 0
            qidquery = ""
            wdprefix = ""
            firstkey=next(iter(classes))
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
                            #QgsMessageLog.logMessage(str(result), MESSAGE_CATEGORY, Qgis.Info)
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

    @staticmethod
    def patternsToUnion(patternarray,propvar,itemvar):
        res=""
        if len(patternarray)==1:
            return patternarray[0]
        if patternarray>1:
            first=True
            for pat in patternarray:
                if first:
                    first=False
                    res+="{ "+str(itemvar)+" <"+str(pat)+"> "+str(propvar)+" . } "
                else:
                    res+="UNION { "+str(itemvar)+" <"+str(pat)+"> "+str(propvar)+" . } "
            return res
        return res

    @staticmethod
    def propertyVarPatternToUnion(propertyid,triplestoreconf,propvar,itemvar):
        propidcleaned = propertyid.replace("%", "")
        if propidcleaned in triplestoreconf:
            return SPARQLUtils.patternsToUnion(triplestoreconf[propidcleaned],propvar,itemvar)
        return ""

    @staticmethod
    def selectQueryToConstructQuery(query):
        mquery=query[query.find("WHERE"):query.rfind("}")+1]
        query=query[query.find("WHERE"):]
        constructpart=""
        for line in mquery.split("\n"):
            if "BIND" in line or "FILTER" in line or "EXISTS" in line:
                continue
            elif "OPTIONAL" in line:
                constructpart += line[0:line.rfind("}")].replace("OPTIONAL {","") + "\n"
            else:
                constructpart+=line+"\n"
        result="CONSTRUCT \n"+constructpart.replace("WHERE","")+"\n"+query
        QgsMessageLog.logMessage('SELECT TO CONSTRUCT '+str(result), MESSAGE_CATEGORY,Qgis.Info)
        return result

    @staticmethod
    def resolvePropertyToTriplePattern(propertyid,propvar,itemvar,triplestoreconf,patterntype,filterstatement,proplabel=False,asUnion=True):
        if filterstatement==None:
            filterstatement=""
        propidcleaned=propertyid.replace("%","")
        if propidcleaned in triplestoreconf:
            res=""
            first=True
            if asUnion and patterntype=="OPTIONAL":
                res+="OPTIONAL { "
            for propid in triplestoreconf[propidcleaned]:
                thepattern=str(itemvar)+" <"+str(propid)+"> "+str(propvar)+" .\n "+filterstatement
                if proplabel and "url" in triplestoreconf["resource"] and (
                        "wikidata" in triplestoreconf["resource"]["url"] or "factgrid" in triplestoreconf["resource"][
                    "url"]):
                    thepattern="?prop <http://wikiba.se/ontology#directClaim> "+str(itemvar)+" . ?prop <"+str(propid)+"> "+str(propvar)+" .\n"+filterstatement
                if patterntype=="OPTIONAL" and not asUnion:
                    res+="OPTIONAL { "+thepattern+"}\n"
                elif patterntype == "OPTIONAL" and  asUnion:
                    if first:
                        first=False
                        res+=" { "+thepattern+" } "
                    else:
                        res += " UNION { " + thepattern + "}\n"
                else:
                    res+=thepattern
            if asUnion and patterntype=="OPTIONAL":
                res+="} "
            return res
        if proplabel and "url" in triplestoreconf["resource"] and (
                "wikidata" in triplestoreconf["resource"]["url"] or "factgrid" in triplestoreconf["resource"]["url"]):
            return "?prop <http://wikiba.se/ontology#directClaim> "+str(itemvar)+" . ?prop "+str(propertyid)+" "+str(propvar)+" .\n"
        else:
            return str(itemvar)+" "+str(propertyid)+" "+str(propvar)+" .\n"