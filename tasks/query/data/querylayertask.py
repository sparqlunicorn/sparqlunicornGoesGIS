import json
from rdflib.plugins.sparql import prepareQuery

from ....dialogs.info.errormessagebox import ErrorMessageBox
from ....util.style.styleutils import StyleUtils
from ....util.layerutils import LayerUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import QgsProject, QgsVectorLayer

MESSAGE_CATEGORY = 'QueryLayerTask'


class QueryLayerTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description,concept, triplestoreurl, query, triplestoreconf, allownongeo, filename, progress=None,dlgtoclose=None,querydepth=0,shortenURIs=False,styleuri=None,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.concept=concept
        self.dlgtoclose=dlgtoclose
        self.querydepth=querydepth
        self.preferredlang=preferredlang
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.styleuri=styleuri
        self.vlayer=None
        self.vlayernongeo=None
        if self.progress is not None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Query execution (1/2)")
        self.query = query
        if triplestoreurl["type"]=="file":
            self.query=prepareQuery(self.query)
        self.shortenURIs=shortenURIs
        self.allownongeo = allownongeo
        self.filename = filename
        if self.filename is None or self.filename=="":
            self.filename="mylayer"
        self.geojson = None
        self.nongeojson = None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            str(self.query).replace("<","_").replace(">","_")),
            MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            self.exception=SPARQLUtils.exception
            return False
        #QgsMessageLog.logMessage('Started task "{}"'.format(
        #    results),
        #    MESSAGE_CATEGORY, Qgis.Info)
        if self.progress is not None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Processing results (2/2)")
        res = self.processResults(results,(self.triplestoreconf["crs"] if "crs" in self.triplestoreconf else ""),
                                           self.triplestoreconf["mandatoryvariables"][1:], self.allownongeo)
        self.geojson=res[0]
        self.nongeojson=res[1]
        if self.nongeojson is not None:
            self.vlayernongeo = QgsVectorLayer(json.dumps(self.nongeojson), "unicorn_" + self.filename, "ogr")
        if self.geojson is not None:
            #QgsMessageLog.logMessage('Started task "{}"'.format(
            #    self.geojson),
            #    MESSAGE_CATEGORY, Qgis.Info)
            self.vlayer = QgsVectorLayer(json.dumps(self.geojson), "unicorn_" + self.filename, "ogr")
            #QgsMessageLog.logMessage('Started task "{}"'.format(
            #    len(self.vlayer)),
            #    MESSAGE_CATEGORY, Qgis.Info)
            if len(res)>1 and res[2] is not None:
                crs=self.vlayer.crs()
                crsstring=res[2]
                if crsstring is not None and crsstring.isdigit():
                    crs.createFromId(int(crsstring))
                else:
                    crs.createFromString(crsstring)
                self.vlayer.setCrs(crs)
            QgsMessageLog.logMessage("Style URI Status: "+str(self.styleuri), MESSAGE_CATEGORY, Qgis.Info)
            if self.styleuri is not None and self.styleuri!=[] and self.concept is not None:
                QgsMessageLog.logMessage("Querying style definition",MESSAGE_CATEGORY, Qgis.Info)
                mystyle=StyleUtils.queryStyleByURI(self.concept,self.triplestoreurl,self.triplestoreconf,self.styleuri).toSLD("unicorn_" + self.filename)
                QgsMessageLog.logMessage("Querying style definition II "+str(mystyle).replace("<","").replace(">",""),MESSAGE_CATEGORY, Qgis.Info)
                myStyleDoc = QDomDocument()
                myStyleDoc.setContent(mystyle, False)
                errormsg=""
                self.vlayer.readSld(myStyleDoc,errormsg)
                QgsMessageLog.logMessage( "Querying style definition III " + str(errormsg), MESSAGE_CATEGORY,Qgis.Info)
            QgsMessageLog.logMessage("Layer valid: " + str(self.vlayer.name()), MESSAGE_CATEGORY, Qgis.Info)
            QgsMessageLog.logMessage("Layer valid: " + str(self.vlayer.isValid()), MESSAGE_CATEGORY, Qgis.Info)
            QgsMessageLog.logMessage("Layer valid: " + str(self.vlayer.featureCount()), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def dropUnwantedKeys(self,properties):
        properties.pop("item", None)
        properties.pop("geo", None)
        properties.pop("lat", None)
        properties.pop("lon", None)
        properties.pop("item2", None)
        properties.pop("rel", None)
        properties.pop("val", None)
        properties.pop("rel2", None)
        properties.pop("val2", None)
        return properties


    def addFeatureToCorrectCollection(self,feature,features,nongeofeatures,crsset):
        if feature["geometry"] is None:
            nongeofeatures.append(feature)
        else:
            features.append(feature)
        if feature is not None and "crs" in feature:
            crsset.add(feature["crs"])
            del feature["crs"]
        #QgsMessageLog.logMessage(str(features), MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage(str(nongeofeatures), MESSAGE_CATEGORY, Qgis.Info)



    ## Processes query results and reformats them to a QGIS layer.
    #  @param self The object pointer.
    #  @param results The query results
    #  @param reproject The crs from which to reproject to WGS84
    #  @param mandatoryvars mandatoryvariables to find in the query result
    #  @param geooptional indicates if a geometry is mandatory
    def processResults(self, results, reproject, mandatoryvars, geooptional):
        latval = "lat"
        lonval = "lon"
        features = []
        nongeofeatures=[]
        properties={}
        item = ""
        crsset=set()
        QgsMessageLog.logMessage('Processing results....',MESSAGE_CATEGORY, Qgis.Info)
        lastaddeditem=""
        for result in results["results"]["bindings"]:
            #QgsMessageLog.logMessage('CurResult Row' + str(result),MESSAGE_CATEGORY, Qgis.Info)
            if self.concept is not None and "item" not in result:
                result["item"]={"value":self.concept}
            if "item" in result and "rel" in result and "val" in result:
                #QgsMessageLog.logMessage('rel val' + str(len(features))+" "+str(result["val"]),MESSAGE_CATEGORY, Qgis.Info)
                if "geo" in result and (item == "" or result["item"]["value"] != item):
                    #QgsMessageLog.logMessage('rel val + geo' + str(len(features)),
                    #                         MESSAGE_CATEGORY, Qgis.Info)
                    if item != "":
                        #QgsMessageLog.logMessage('Add New Feature Geo ' + str(item),MESSAGE_CATEGORY, Qgis.Info)
                        self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                            result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                            {'id':item,'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),'geometry': {}},
                            self.triplestoreconf),features,nongeofeatures,crsset)
                        lastaddeditem=item
                    properties = {}
                    item = result["item"]["value"]
                elif "lat" in result and "lon" in result and (
                    item == "" or result["item"]["value"] != item) and "lat" in mandatoryvars and "lon" in mandatoryvars:
                    #QgsMessageLog.logMessage('rel val + lat lon' + str(len(features)),
                    #                         MESSAGE_CATEGORY, Qgis.Info)
                    #QgsMessageLog.logMessage('Add New Feature Lat/Lon ' + str(item), MESSAGE_CATEGORY, Qgis.Info)
                    if item != "":
                        self.addFeatureToCorrectCollection(LayerUtils.processLiteral(
                            f'POINT({float(result[lonval]["value"])} {float(result[latval]["value"])})', "wkt", reproject,{'id':item,'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                                   'geometry': {}},self.triplestoreconf),features,nongeofeatures,crsset)
                        lastaddeditem = item
                    properties = {}
                    item = result["item"]["value"]
                elif geooptional and (item == "" or result["item"]["value"] != item):
                    #QgsMessageLog.logMessage('rel val + no geo' + str(len(features)),
                    #                         MESSAGE_CATEGORY, Qgis.Info)
                    #QgsMessageLog.logMessage('Add New Feature Else ' + str(item), MESSAGE_CATEGORY, Qgis.Info)
                    if item != "":
                        self.addFeatureToCorrectCollection({'id':item,'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                                   'geometry': {}},features,nongeofeatures,crsset)
                        lastaddeditem = item
                    properties = {}
                    item = result["item"]["value"]
            elif "rel" not in result and "val" not in result:
                properties = {}
            for var in results["head"]["vars"]:
                if var in result:
                    if var=="item":
                        item = result["item"]["value"]
                    if var == "rel" and "val" in result:
                        if "datatype" in result["val"]:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])]=LayerUtils.detectDataType(result["val"])
                        elif self.shortenURIs:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = result["val"]["value"]
                        elif self.shortenURIs==1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(result["val"]["value"])
                        else:
                            properties[result[var]["value"]] = result["val"]["value"]
                    if var=="rel2" in result and "val2"!=self.triplestoreconf["typeproperty"] and "val2" in result:
                        if "datatype" in result["val2"]:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])]=LayerUtils.detectDataType(result["val2"])
                        elif self.shortenURIs:
                            properties["_"+SPARQLUtils.labelFromURI(result[var]["value"])] = result["val2"]["value"]
                        elif self.shortenURIs==1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(result["val2"]["value"])
                        else:
                            properties["_"+result[var]["value"]] = result["val2"]["value"]
                    elif var != "val" and var!="val2":
                        if "datatype" in result[var]:
                            properties[SPARQLUtils.labelFromURI(var)]=LayerUtils.detectDataType(result[var])
                        elif self.shortenURIs:
                            properties[SPARQLUtils.labelFromURI(var)] = result[var]["value"]
                        elif self.shortenURIs==1:
                            properties[SPARQLUtils.labelFromURI(var)] = SPARQLUtils.labelFromURI(result[var]["value"])
                        else:
                            properties[var] = result[var]["value"]
            if "rel" not in result and "val" not in result:
                #QgsMessageLog.logMessage('Not rel val ' + str(len(features)),MESSAGE_CATEGORY, Qgis.Info)
                if "geo" in result:
                    #QgsMessageLog.logMessage('Not rel val + geo' + str(len(features)),
                    #                         MESSAGE_CATEGORY, Qgis.Info)
                    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                        result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                        {'id': result["item"]["value"], 'type': 'Feature',
                        'properties': self.dropUnwantedKeys(properties),'geometry': {}},
                         self.triplestoreconf),features,nongeofeatures,crsset)
                    lastaddeditem = result["item"]["value"]
                elif latval in result and lonval in result:
                    #QgsMessageLog.logMessage('Not rel val + lat lon' + str(len(features)),
                    #                         MESSAGE_CATEGORY, Qgis.Info)
                    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(
                        f'POINT({float(result[lonval]["value"])} {float(result[latval]["value"])})',
                        "wkt", reproject,
                        {'id': result["item"]["value"], 'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                         'geometry': {}},
                        self.triplestoreconf),features,nongeofeatures,crsset)
                    lastaddeditem = result["item"]["value"]
                elif "geo" not in result and geooptional:
                    #QgsMessageLog.logMessage('Not rel val + no geo' + str(len(features)),
                    #                         MESSAGE_CATEGORY, Qgis.Info)
                    self.addFeatureToCorrectCollection({'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}},features,nongeofeatures,crsset)
                    lastaddeditem = result["item"]["value"]
        #QgsMessageLog.logMessage('Last Item '+str(item),MESSAGE_CATEGORY, Qgis.Info)
        if len(results)>=0 and lastaddeditem!=item:
            if "geo" in properties:
                self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                {'id':result["item"]["value"], 'type': 'Feature','properties': self.dropUnwantedKeys(properties),'geometry': {}},
                self.triplestoreconf),features,nongeofeatures,crsset)
            elif "lat" in properties and "lon" in properties:
                self.addFeatureToCorrectCollection(LayerUtils.processLiteral("POINT(" + str(float(result[lonval]["value"]))
                                                                   + " " + str(float(result[latval]["value"])) + ")",
                "wkt", reproject,{'id':result["item"]["value"], 'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}},self.triplestoreconf),features,nongeofeatures,crsset)
            else:
                self.addFeatureToCorrectCollection({'id':result["item"]["value"], 'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}},features,nongeofeatures,crsset)
            #QgsMessageLog.logMessage('Number of features '+str(len(features)),MESSAGE_CATEGORY, Qgis.Info)
        if features == [] and len(results["results"]["bindings"]) == 0:
            return [None,None,None]
        #if features == [] and len(results["results"]["bindings"]) > 0:
        #    return len(results["results"]["bindings"])
        geojson = {'type': 'FeatureCollection', 'features': features}
        #QgsMessageLog.logMessage(str(geojson),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        if len(nongeofeatures)>0:
            geojsonnongeo = {'type': 'FeatureCollection', 'features': nongeofeatures}
        else:
            geojsonnongeo=None
        if len(crsset)>0:
            return [geojson,geojsonnongeo,crsset.pop()]
        return [geojson,geojsonnongeo,None]

    def finished(self, result):
        QgsMessageLog.logMessage('Finishing up..... ',MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Adding vlayer ' + str(self.vlayer),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Adding vlayernongeo ' + str(self.vlayernongeo),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        if self.geojson is None and self.exception is not None:
            msgBox = ErrorMessageBox("Query Error","")
            msgBox.setText("An error occurred while querying: " + str(self.exception))
            msgBox.exec()
            if self.progress is not None:
                self.progress.close()
            return
        if self.geojson is None and self.nongeojson is None:
            msgBox = ErrorMessageBox("Query Error","")
            msgBox.setText("The query yielded no results. Therefore no layer will be created!")
            msgBox.exec()
            if self.progress is not None:
                self.progress.close()
            return
        #if self.geojson != None and isinstance(self.geojson, int) and not self.allownongeo:
        #    msgBox = QMessageBox()
        #    msgBox.setText("The query did not retrieve a geometry result. However, there were " + str(
        #        self.geojson) + " non-geometry query results. You can retrieve them by allowing non-geometry queries!")
        #    msgBox.exec()
        #    return
        #QgsMessageLog.logMessage('Adding vlayer ' + str(self.geojson),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        if self.progress is not None:
            self.progress.close()
        if self.vlayer is not None:
            QgsMessageLog.logMessage('Adding vlayer ' + str(self.vlayer),MESSAGE_CATEGORY, Qgis.Info)
            QgsProject.instance().addMapLayer(self.vlayer)
            canvas = iface.mapCanvas()
            canvas.setExtent(self.vlayer.extent())
            iface.messageBar().pushMessage("Add layer", "OK", level=Qgis.Success)
        if self.vlayernongeo is not None:
            QgsProject.instance().addMapLayer(self.vlayernongeo)
        if self.dlgtoclose is not None:
            self.dlgtoclose.close()
