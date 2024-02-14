import json

from ....util.style.styleutils import StyleUtils
from ....util.layerutils import LayerUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import QgsProject, QgsVectorLayer

MESSAGE_CATEGORY = 'QueryLayerTask'


class QueryLayerTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description,concept, triplestoreurl, query, triplestoreconf, allownongeo, filename, progress=None,querydepth=0,shortenURIs=False,styleuri=None,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.concept=concept
        self.querydepth=querydepth
        self.preferredlang=preferredlang
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.styleuri=styleuri
        self.vlayer=None
        self.vlayernongeo=None
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Query execution (1/2)")
        self.query = query
        self.shortenURIs=shortenURIs
        self.allownongeo = allownongeo
        self.filename = filename
        if self.filename==None or self.filename=="":
            self.filename="mylayer"
        self.geojson = None
        self.nongeojson = None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.query.replace("<","_").replace(">","_")),
            MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            self.exception=SPARQLUtils.exception
            return False
        #QgsMessageLog.logMessage('Started task "{}"'.format(
        #    results),
        #    MESSAGE_CATEGORY, Qgis.Info)
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Processing results (2/2)")
        res = self.processResults(results,
                                           (self.triplestoreconf["crs"] if "crs" in self.triplestoreconf else ""),
                                           self.triplestoreconf["mandatoryvariables"][1:], self.allownongeo)
        self.geojson=res[0]
        self.nongeojson=res[1]
        if self.nongeojson!=None:
            self.vlayernongeo = QgsVectorLayer(json.dumps(self.nongeojson, sort_keys=True), "unicorn_" + self.filename, "ogr")
        if self.geojson!=None:
            #QgsMessageLog.logMessage('Started task "{}"'.format(
            #    self.geojson),
            #    MESSAGE_CATEGORY, Qgis.Info)
            self.vlayer = QgsVectorLayer(json.dumps(self.geojson, sort_keys=True), "unicorn_" + self.filename, "ogr")
            #QgsMessageLog.logMessage('Started task "{}"'.format(
            #    len(self.vlayer)),
            #    MESSAGE_CATEGORY, Qgis.Info)
            if len(res)>1 and res[2]!=None:
                crs=self.vlayer.crs()
                crsstring=res[2]
                if crsstring.isdigit():
                    crs.createFromId(int(crsstring))
                else:
                    crs.createFromString(crsstring)
                self.vlayer.setCrs(crs)
            QgsMessageLog.logMessage("Style URI Status: "+str(self.styleuri), MESSAGE_CATEGORY, Qgis.Info)
            if self.styleuri!=None and self.styleuri!=[] and self.concept!=None:
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
        if feature["geometry"] == None:
            nongeofeatures.append(feature)
        else:
            features.append(feature)
        if feature != None and "crs" in feature:
            crsset.add(feature["crs"])
            del feature["crs"]

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
        first = True
        newobject = True
        item = ""
        relval=False
        crsset=set()
        QgsMessageLog.logMessage('Processing results....',
            MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            if self.concept!=None and "item" not in result:
                result["item"]={}
                result["item"]["value"]=self.concept
            if "item" in result and "rel" in result and "val" in result and "geo" in result and (
                    item == "" or result["item"]["value"] != item) and "geo" in mandatoryvars:
                relval=True
                if item != "":
                    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                        result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                        {'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                               'geometry': {}},
                        self.triplestoreconf),features,nongeofeatures,crsset)
                properties = {}
                item = result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and "lat" in result and "lon" in result and (
                    item == "" or result["item"]["value"] != item) and "lat" in mandatoryvars and "lon" in mandatoryvars:
                relval=True
                if item != "":
                    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(
                        "POINT(" + str(float(result[lonval]["value"])) + " " + str(
                            float(result[latval]["value"])) + ")", "wkt", reproject,{'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                               'geometry': {}},self.triplestoreconf),features,nongeofeatures,crsset)
                properties = {}
                item = result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and geooptional and (
                    item == "" or result["item"]["value"] != item):
                relval=True
                if item != "":
                    self.addFeatureToCorrectCollection({'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                               'geometry': {}},features,nongeofeatures,crsset)
                properties = {}
                item = result["item"]["value"]
            if "rel" not in result and "val" not in result:
                properties = {}
            for var in results["head"]["vars"]:
                if var in result:
                    if var == "rel" and "val" in result:
                        if self.shortenURIs:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = result["val"]["value"]
                        elif self.shortenURIs==1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(result["val"]["value"])
                        else:
                            properties[result[var]["value"]] = result["val"]["value"]
                    if var=="rel2" in result and "val2"!=self.triplestoreconf["typeproperty"] and "val2" in result:
                        if self.shortenURIs:
                            properties["_"+SPARQLUtils.labelFromURI(result["rel2"]["value"])] = result["val2"]["value"]
                        elif self.shortenURIs==1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(result["val"]["value"])
                        else:
                            properties["_"+result[var]["value"]] = result["val2"]["value"]
                    elif var != "val" and var!="val2":
                        if self.shortenURIs:
                            properties[SPARQLUtils.labelFromURI(var)] = result[var]["value"]
                        elif self.shortenURIs==1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(result["val"]["value"])
                        else:
                            properties[var] = result[var]["value"]
            if not "rel" in result and not "val" in result and "geo" in result:
                self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                    result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                    {'id': result["item"]["value"], 'type': 'Feature',
                    'properties': self.dropUnwantedKeys(properties),'geometry': {}},
                     self.triplestoreconf),features,nongeofeatures,crsset)
            elif not "rel" in result and not "val" in result and latval in result and lonval in result:
                self.addFeatureToCorrectCollection(LayerUtils.processLiteral(
                    "POINT(" + str(float(result[lonval]["value"])) + " " + str(float(result[latval]["value"])) + ")",
                    "wkt", reproject,
                    {'id': result["item"]["value"], 'type': 'Feature', 'properties': self.dropUnwantedKeys(properties),
                     'geometry': {}},
                    self.triplestoreconf),features,nongeofeatures,crsset)
            elif not "rel" in result and not "val" in result and not "geo" in result and geooptional:
                self.addFeatureToCorrectCollection({'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}},features,nongeofeatures,crsset)
            #if relval and not geooptional and "lat" not in result and "lon" not in result:
            #    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
            #        result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
            #        { 'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}},self.triplestoreconf),features,nongeofeatures,crsset)
        #if relval and geooptional:
        #    #myGeometryInstanceJSON = LayerUtils.processLiteral(result["geo"]["value"], (
        #    #    result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,self.triplestoreconf)
        #    feature = {'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}}#json.loads(myGeometryInstanceJSON)}
        #    features.append(feature)
        #if len(features)==0:
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
        QgsMessageLog.logMessage('Number of features '+str(len(features)),
            MESSAGE_CATEGORY, Qgis.Info)
        if features == [] and len(results["results"]["bindings"]) == 0:
            return [None,None,None]
        #if features == [] and len(results["results"]["bindings"]) > 0:
        #    return len(results["results"]["bindings"])
        geojson = {'type': 'FeatureCollection', 'features': features}
        if len(nongeofeatures)>0:
            geojsonnongeo = {'type': 'FeatureCollection', 'features': nongeofeatures}
        else:
            geojsonnongeo=None
        if len(crsset)>0:
            return [geojson,geojsonnongeo,crsset.pop()]
        return [geojson,geojsonnongeo,None]

    def finished(self, result):
        QgsMessageLog.logMessage('Finishing up..... ',
                                 MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Adding vlayer ' + str(self.vlayer),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Adding vlayernongeo ' + str(self.vlayernongeo),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        if self.geojson == None and self.exception != None:
            msgBox = QMessageBox()
            msgBox.setText("An error occurred while querying: " + str(self.exception))
            msgBox.exec()
            if self.progress != None:
                self.progress.close()
            return
        if self.geojson == None and self.nongeojson==None:
            msgBox = QMessageBox()
            msgBox.setText("The query yielded no results. Therefore no layer will be created!")
            msgBox.exec()
            if self.progress != None:
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
        if self.progress!=None:
            self.progress.close()
        if self.vlayer!=None:
            QgsMessageLog.logMessage('Adding vlayer ' + str(self.vlayer),MESSAGE_CATEGORY, Qgis.Info)
            QgsProject.instance().addMapLayer(self.vlayer)
            canvas = iface.mapCanvas()
            canvas.setExtent(self.vlayer.extent())
            iface.messageBar().pushMessage("Add layer", "OK", level=Qgis.Success)
        if self.vlayernongeo!=None:
            QgsProject.instance().addMapLayer(self.vlayernongeo)
