import json
import ogr
from ..util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox, QProgressDialog
from qgis.core import QgsProject, QgsGeometry, QgsVectorLayer, QgsExpression, QgsFeatureRequest, \
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsApplication, QgsWkbTypes, QgsField
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'QueryLayerTask'


class QueryLayerTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl, query, triplestoreconf, allownongeo, filename, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.query = query
        self.allownongeo = allownongeo
        self.filename = filename
        self.geojson = None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            return False
        # geojson stuff
        self.geojson = self.processResults(results,
                                           (self.triplestoreconf["crs"] if "crs" in self.triplestoreconf else ""),
                                           self.triplestoreconf["mandatoryvariables"][1:], self.allownongeo)
        return True

    def processLiteral(self, literal, literaltype, reproject):
        QgsMessageLog.logMessage("Process literal: " + str(literal) + " " + str(literaltype))
        geom = None
        if "literaltype" in self.triplestoreconf:
            literaltype = self.triplestoreconf["literaltype"]
        if literal.startswith("http"):
            res = SPARQLUtils.handleURILiteral(literal)
            if res == None:
                return "{\"geometry\":null}"
            return json.dumps(res[0])
        if literaltype == "":
            literaltype = SPARQLUtils.detectLiteralType(literal)
        if "wkt" in literaltype.lower():
            literal = literal.strip()
            if literal.startswith("<http"):
                index = literal.index(">") + 1
                slashindex = literal.rfind("/") + 1
                reproject = literal[slashindex:(index - 1)]
                geom = QgsGeometry.fromWkt(literal[index:])
            else:
                geom = QgsGeometry.fromWkt(literal)
        elif "gml" in literaltype.lower():
            geom=QgsGeometry.fromWkb(ogr.CreateGeometryFromGML(literal).ExportToWkb())
        elif "geojson" in literaltype.lower():
            return literal
        elif "wkb" in literaltype.lower():
            geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
        if geom != None and reproject != "":
            sourceCrs = QgsCoordinateReferenceSystem(reproject)
            destCrs = QgsCoordinateReferenceSystem(4326)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            geom.transform(tr)
        if geom != None:
            return geom.asJson()
        return None

    ## Processes query results and reformats them to a QGIS layer.
    #  @param self The object pointer.
    #  @param results The query results
    #  @param reproject The crs from which to reproject to WGS84
    #  @param mandatoryvars mandatoryvariables to find in the query result
    #  @param geooptional indicates if a geometry is mandatory
    def processResults(self, results, reproject, mandatoryvars, geooptional):
        latval = "lat"
        lonval = "lon"
        # if len(mandatoryvars)>1:
        #    lonval=mandatoryvars[1]
        features = []
        first = True
        newobject = True
        item = ""
        for result in results["results"]["bindings"]:
            if "item" in result and "rel" in result and "val" in result and "geo" in result and (
                    item == "" or result["item"]["value"] != item) and "geo" in mandatoryvars:
                if item != "":
                    myGeometryInstanceJSON = self.processLiteral(result["geo"]["value"], (
                        result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject)
                    feature = {'type': 'Feature', 'properties': properties,
                               'geometry': json.loads(myGeometryInstanceJSON)}
                    features.append(feature)
                properties = {}
                item = result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and "lat" in result and "lon" in result and (
                    item == "" or result["item"][
                "value"] != item) and "lat" in mandatoryvars and "lon" in mandatoryvars:
                if item != "":
                    myGeometryInstanceJSON = self.processLiteral(
                        "POINT(" + str(float(result[lonval]["value"])) + " " + str(
                            float(result[latval]["value"])) + ")", "wkt", reproject)
                    feature = {'type': 'Feature', 'properties': properties,
                               'geometry': json.loads(myGeometryInstanceJSON)}
                    features.append(feature)
                properties = {}
                item = result["item"]["value"]
            # if not "rel" in result and not "val" in result:
            properties = {}
            for var in results["head"]["vars"]:
                if var in result:
                    if var == "rel" and "val" in result:
                        properties[result[var]["value"]] = result["val"]["value"]
                    elif var != "val":
                        properties[var] = result[var]["value"]
            if not "rel" in result and not "val" in result and "geo" in result:
                myGeometryInstanceJSON = self.processLiteral(result["geo"]["value"], (
                    result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject)
                feature = {'type': 'Feature', 'properties': properties, 'geometry': json.loads(myGeometryInstanceJSON)}
                features.append(feature)
            elif not "rel" in result and not "val" in result and latval in result and lonval in result:
                myGeometryInstanceJSON = self.processLiteral(
                    "POINT(" + str(float(result[lonval]["value"])) + " " + str(float(result[latval]["value"])) + ")",
                    "wkt", reproject)
                feature = {'type': 'Feature', 'properties': properties, 'geometry': json.loads(myGeometryInstanceJSON)}
                features.append(feature)
            elif not "rel" in result and not "val" in result and not "geo" in result and geooptional:
                feature = {'type': 'Feature', 'properties': properties, 'geometry': {}}
                features.append(feature)
        if "rel" in results["results"]["bindings"] and "val" in results["results"]["bindings"]:
            myGeometryInstanceJSON = self.processLiteral(result["geo"]["value"], (
                result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject)
            feature = {'type': 'Feature', 'properties': properties, 'geometry': json.loads(myGeometryInstanceJSON)}
            features.append(feature)
        if features == [] and len(results["results"]["bindings"]) == 0:
            return None
        if features == [] and len(results["results"]["bindings"]) > 0:
            return len(results["results"]["bindings"])
        geojson = {'type': 'FeatureCollection', 'features': features}
        return geojson

    def finished(self, result):
        if self.geojson == None and self.exception != None:
            msgBox = QMessageBox()
            msgBox.setText("An error occured while querying: " + str(self.exception))
            msgBox.exec()
            return
        if self.geojson == None:
            msgBox = QMessageBox()
            msgBox.setText("The query yielded no results. Therefore no layer will be created!")
            msgBox.exec()
            return
        if self.geojson != None and isinstance(self.geojson, int) and not self.allownongeo:
            msgBox = QMessageBox()
            msgBox.setText("The query did not retrieve a geometry result. However, there were " + str(
                self.geojson) + " non-geometry query results. You can retrieve them by allowing non-geometry queries!")
            msgBox.exec()
            return
        self.progress.close()
        vlayer = QgsVectorLayer(json.dumps(self.geojson, sort_keys=True, indent=4), "unicorn_" + self.filename, "ogr")
        print(vlayer.isValid())
        QgsProject.instance().addMapLayer(vlayer)
        canvas = iface.mapCanvas()
        canvas.setExtent(vlayer.extent())
        iface.messageBar().pushMessage("Add layer", "OK", level=Qgis.Success)
