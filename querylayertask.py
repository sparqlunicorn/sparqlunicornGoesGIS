from time import sleep
from rdflib import *
import json
import requests
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem,QMessageBox
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from qgis.core import QgsProject,QgsGeometry,QgsVectorLayer,QgsExpression,QgsFeatureRequest,QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsApplication,QgsWkbTypes,QgsField
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'RandomIntegerSumTask'

class QueryLayerTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl,query,triplestoreconf,allownongeo,filename):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl=triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.query=query
        self.allownongeo=allownongeo
        self.filename=filename
        self.geojson=None

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery(self.query)
        sparql.setMethod(POST)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
        except Exception as e: 
            try:
                sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                sparql.setQuery(self.query)
                sparql.setMethod(GET)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            except Exception as e:
                self.exception=e
                return            
        #print(results)
        # geojson stuff
        self.geojson=self.processResults(results,(self.triplestoreconf["crs"] if "crs" in self.triplestoreconf else ""),self.triplestoreconf["mandatoryvariables"][1:],self.allownongeo)
        return True

    ## Processes query results and reformats them to a QGIS layer.
    #  @param self The object pointer.
    #  @param results The query results
    #  @param reproject The crs from which to reproject to WGS84
    #  @param mandatoryvars mandatoryvariables to find in the query result
    #  @param geooptional indicates if a geometry is mandatory
    def processResults(self,results,reproject,mandatoryvars,geooptional):
        latval=mandatoryvars[0]
        lonval=""
        if len(mandatoryvars)>1:
            lonval=mandatoryvars[1]
        features = []
        first=True
        newobject=True
        item=""
        for result in results["results"]["bindings"]:
            if "item" in result and "rel" in result and "val" in result and (item=="" or result["item"]["value"]!=item) and "geo" in mandatoryvars:
                if item!="":
                    myGeometryInstance=QgsGeometry.fromWkt(result["geo"]["value"])
                    if reproject!="":
                        sourceCrs = QgsCoordinateReferenceSystem(reproject)
                        destCrs = QgsCoordinateReferenceSystem(4326)
                        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                        myGeometryInstance.transform(tr)
                    #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
                    feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstance.asJson()) }
                    features.append(feature)
                properties = {}
                item=result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and "lat" in result and "lon" in result and (item=="" or result["item"]["value"]!=item) and "lat" in mandatoryvars and "lon" in mandatoryvars:
                if item!="":
                    myGeometryInstance = QgsGeometry.fromWkt("POINT("+str(float(result[lonval]["value"]))+" "+str(float(result[latval]["value"]))+")")
                    if reproject!="":
                        sourceCrs = QgsCoordinateReferenceSystem(reproject)
                        destCrs = QgsCoordinateReferenceSystem(4326)
                        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                        myGeometryInstance.transform(tr)
                    #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
                    feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstance.asJson()) }
                    features.append(feature)
                properties = {}
                item=result["item"]["value"]
            #if not "rel" in result and not "val" in result:
            properties = {}
            for var in results["head"]["vars"]:
                if var in result:
                    if var=="rel" and "val" in result:
                        properties[result[var]["value"]] = result["val"]["value"]
                    elif var!="val":
                        properties[var] = result[var]["value"]
            if not "rel" in result and not "val" in result and "geo" in result:
                myGeometryInstance=QgsGeometry.fromWkt(result["geo"]["value"].replace("<http://www.opengis.net/def/crs/EPSG/0/"+str(reproject)+"> ",""))
                if reproject!="":
                    sourceCrs = QgsCoordinateReferenceSystem(reproject)
                    destCrs = QgsCoordinateReferenceSystem(4326)
                    tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                    myGeometryInstance.transform(tr)
                #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstance.asJson()) }
                features.append(feature)
            if not "rel" in result and not "val" in result and latval in result and lonval in result and reproject==27700:
                myGeometryInstance = QgsGeometry.fromWkt("POINT("+str(float(result[latval]["value"]))+" "+str(float(result[lonval]["value"]))+")")
                if reproject!="":
                    sourceCrs = QgsCoordinateReferenceSystem(reproject)
                    destCrs = QgsCoordinateReferenceSystem(4326)
                    tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                    myGeometryInstance.transform(tr)
                #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstance.asJson()) }
                features.append(feature)
            if not "rel" in result and not "val" in result and latval in result and lonval in result and reproject!=27700:
                myGeometryInstance = QgsGeometry.fromWkt("POINT("+str(float(result[lonval]["value"]))+" "+str(float(result[latval]["value"]))+")")
                if reproject!="":
                    sourceCrs = QgsCoordinateReferenceSystem(reproject)
                    destCrs = QgsCoordinateReferenceSystem(4326)
                    tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                    myGeometryInstance.transform(tr)
                #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstance.asJson()) }
                features.append(feature)
            if not "rel" in result and not "val" in result and not "geo" in result and geooptional:
                #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  {} }
                features.append(feature)
            #print(properties)
        if "rel" in results["results"]["bindings"] and "val" in results["results"]["bindings"]:
            myGeometryInstance = QgsGeometry.fromWkt(result["geo"]["value"])
            if reproject!="":
                sourceCrs = QgsCoordinateReferenceSystem(reproject)
                destCrs = QgsCoordinateReferenceSystem(4326)
                tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
                myGeometryInstance.transform(tr)
            #feature = { 'type': 'Feature', 'properties': { 'label': result["label"]["value"], 'item': result["item"]["value"] }, 'geometry': wkt.loads(result["geo"]["value"].replace("Point", "POINT")) }
            feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstance.asJson()) }
            features.append(feature)		
        if features==[] and len(results["results"]["bindings"])==0:
            return None
        if features==[] and len(results["results"]["bindings"])>0:
            return len(results["results"]["bindings"])
        geojson = {'type': 'FeatureCollection', 'features': features }
        return geojson


    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        #msgBox=QMessageBox()
        #msgBox.setText(str("Task is finished!"))
        #msgBox.exec()
        if self.geojson==None:
            msgBox=QMessageBox()
            msgBox.setText("The query yielded no results. Therefore no layer will be created!")
            msgBox.exec()
            return
        if isinstance(self.geojson, int) and not self.dlg.allownongeo.isChecked():
            msgBox=QMessageBox()
            msgBox.setText("The query did not retrieve a geometry result. However, there were "+str(geojson)+" non-geometry query results. You can retrieve them by allowing non-geometry queries!")
            msgBox.exec()
            return
        vlayer = QgsVectorLayer(json.dumps(self.geojson, sort_keys=True, indent=4),"unicorn_"+self.filename,"ogr")
        print(vlayer.isValid())
        QgsProject.instance().addMapLayer(vlayer)
        canvas = iface.mapCanvas()
        canvas.setExtent(vlayer.extent())
        iface.messageBar().pushMessage("Add layer", "OK", level=Qgis.Success)
