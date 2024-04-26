from ....util.ui.uiutils import UIUtils
from ....util.sparqlutils import SPARQLUtils
from ....util.layerutils import LayerUtils
from qgis.core import Qgis, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import QgsTask, QgsMessageLog
import json

MESSAGE_CATEGORY = 'InstanceQueryTask'

class InstanceQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, searchTerm, triplestoreconf, searchResultModel,mymap=None,features=None,parentwindow=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchTerm=searchTerm
        self.features=features
        self.searchResultModel=searchResultModel
        self.mymap=mymap
        self.prefixes= SPARQLUtils.invertPrefixes(triplestoreconf["prefixes"])
        self.triplestoreconf=triplestoreconf
        self.parentwindow=parentwindow
        self.queryresult={}

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Started task "{}"'.format("SELECT ?con ?rel ?val WHERE { "+ str(self.searchTerm) + " ?rel ?val . }"), MESSAGE_CATEGORY, Qgis.Info)
        thequery="SELECT ?rel ?val WHERE { <" + str(self.searchTerm) + ">  ?rel ?val . }"
        if "geotriplepattern" in self.triplestoreconf:
            thequery = "SELECT ?rel ?val "
            if "mandatoryvariables" in self.triplestoreconf and len(self.triplestoreconf["mandatoryvariables"])>0:
                thequery+="?"
                thequery+="?".join(self.triplestoreconf["mandatoryvariables"][1:])
            thequery+=" WHERE { <" + str(self.searchTerm) + "> ?rel ?val . "
            if "geotriplepattern" in self.triplestoreconf and len(self.triplestoreconf["geotriplepattern"])>0:
                for geopat in self.triplestoreconf["geotriplepattern"]:
                    thequery += "OPTIONAL { " + str(geopat).replace("?item ","<" + str(self.searchTerm) + "> ") + " } "
            thequery+="}"
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        if results!=False:
            #QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
            for result in results["results"]["bindings"]:
                if "rel" in result and "val" in result:
                    #QgsMessageLog.logMessage("Query results: " + str(result["rel"]["value"]), MESSAGE_CATEGORY, Qgis.Info)
                    self.queryresult[result["rel"]["value"]]={"rel":result["rel"]["value"],"val":result["val"]["value"]}
                    if "datatype" in result["val"]:
                        self.queryresult[result["rel"]["value"]]["valtype"]=result["val"]["datatype"]
                    elif not result["val"]["value"].startswith("http"):
                        self.queryresult[result["rel"]["value"]]["valtype"] ="http://www.w3.org/2001/XMLSchema#string"
                    else:
                        self.queryresult[result["rel"]["value"]]["valtype"] = result["val"]["value"]
                if "geo" in result:
                    self.queryresult["geo"]={"value":result["geo"]["value"],"valtype":result["geo"]["datatype"]}
        return True

    def finished(self, result):
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        counter=0
        for rel in self.queryresult:
            if rel!="geo":
                self.searchResultModel.insertRow(counter)
            itemchecked = QStandardItem()
            itemchecked.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            itemchecked.setCheckState(Qt.Checked)
            if rel in SPARQLUtils.geoproperties:
                if SPARQLUtils.geoproperties[rel] == "DatatypeProperty":
                    itemchecked.setIcon(UIUtils.geodatatypepropertyicon)
                    itemchecked.setToolTip("Geo Datatype Property")
                    itemchecked.setText("GeoDP")
                elif SPARQLUtils.geoproperties[rel] == "ObjectProperty":
                    itemchecked.setIcon(UIUtils.geoobjectpropertyicon)
                    itemchecked.setToolTip("Geo Object Property")
                    itemchecked.setText("GeoOP")
            elif rel in SPARQLUtils.georelationproperties:
                itemchecked.setIcon(UIUtils.georelationpropertyicon)
                itemchecked.setToolTip("Geo Relation Property")
                itemchecked.setText("GeoRelP")
            elif rel in SPARQLUtils.commentproperties:
                itemchecked.setIcon(UIUtils.commentannotationpropertyicon)
                itemchecked.setToolTip("Description Property")
                itemchecked.setText("Description Property")
            elif rel in SPARQLUtils.labelproperties:
                itemchecked.setIcon(UIUtils.labelannotationpropertyicon)
                itemchecked.setToolTip("Label Property")
                itemchecked.setText("Label Property")
            elif rel in SPARQLUtils.relationproperties:
                itemchecked.setIcon(UIUtils.relationobjectpropertyicon)
                itemchecked.setToolTip("Relation Property")
                itemchecked.setText("Relation Property")
            elif "geoobjproperty" in self.triplestoreconf and rel in self.triplestoreconf["geoobjproperty"]:
                itemchecked.setIcon(UIUtils.linkedgeoobjectpropertyicon)
                itemchecked.setToolTip("Linked Geo Object Property")
                itemchecked.setText("LGeoOP")
            elif rel != "geo" and self.queryresult[rel]["val"].startswith("http"):
                itemchecked.setIcon(UIUtils.objectpropertyicon)
                itemchecked.setToolTip("Object Property")
                itemchecked.setText("OP")
            elif SPARQLUtils.namespaces["rdfs"] in rel \
                    or SPARQLUtils.namespaces["owl"] in rel \
                    or SPARQLUtils.namespaces["dc"] in rel \
                    or SPARQLUtils.namespaces["skos"] in rel:
                itemchecked.setIcon(UIUtils.annotationpropertyicon)
                itemchecked.setToolTip("Annotation Property")
                itemchecked.setText("AP")
            elif rel != "geo":
                itemchecked.setIcon(UIUtils.datatypepropertyicon)
                itemchecked.setToolTip("DataType Property")
                itemchecked.setText("DP")
            if "geometryproperty" in self.triplestoreconf and (rel in self.triplestoreconf["geometryproperty"] or rel=="geo"):
                myGeometryInstanceJSON=None
                encounteredcrs=None
                if isinstance(self.triplestoreconf["geometryproperty"],str) \
                        or (type(self.triplestoreconf["geometryproperty"]) is list and len(self.triplestoreconf["geometryproperty"])==1):
                    if "geo" in self.queryresult:
                        myGeometryInstanceJSON=LayerUtils.processLiteral(self.queryresult["geo"]["value"],
                        (self.queryresult["geo"]["valtype"] if "valtype" in self.queryresult["geo"] else ""),
                        True,None,self.triplestoreconf)
                    else:
                        myGeometryInstanceJSON=LayerUtils.processLiteral(self.queryresult[rel]["val"],
                        (self.queryresult[rel]["valtype"] if "valtype" in self.queryresult[rel] else ""),
                        True,None,self.triplestoreconf)
                    if myGeometryInstanceJSON is not None and "crs" in myGeometryInstanceJSON and myGeometryInstanceJSON["crs"] is not None:
                        if myGeometryInstanceJSON["crs"]=="CRS84":
                            encounteredcrs="urn:ogc:def:crs:OGC:1.3:CRS84"
                        else:
                            encounteredcrs=myGeometryInstanceJSON["crs"]
                        del myGeometryInstanceJSON["crs"]
                elif len(self.triplestoreconf["geometryproperty"])==2 and self.triplestoreconf["geometryproperty"][0] in self.queryresult and self.triplestoreconf["geometryproperty"][1] in self.queryresult:
                    myGeometryInstanceJSON=LayerUtils.processLiteral("POINT(" + str(float(self.queryresult[self.triplestoreconf["geometryproperty"][0]]["val"])) + " " + str(
                        float(self.queryresult[self.triplestoreconf["geometryproperty"][1]]["val"])) + ")", "wkt", True,None, self.triplestoreconf)
                if myGeometryInstanceJSON is not None:
                    geojson = {'type': 'FeatureCollection', 'features': [
                    {'id': str(self.searchTerm), 'type': 'Feature', 'properties': {},
                        'geometry': myGeometryInstanceJSON}
                    ]}
                    self.features = QgsVectorLayer(json.dumps(geojson), str(self.searchTerm),"ogr")
                    featuress = self.features.getFeatures()
                    geomcentroidpoint=None
                    for feat in featuress:
                        try:
                            if feat.geometry() is not None and feat.geometry().centroid() is not None:
                                geomcentroidpoint = feat.geometry().centroid().asPoint()
                        except:
                            print("error")
                    if encounteredcrs is not None:
                        crs = self.features.crs()
                        crsstring = encounteredcrs
                        if crsstring.isdigit():
                            crs.createFromId(int(crsstring))
                        else:
                            crs.createFromString(crsstring)
                        self.features.setCrs(crs)
                    else:
                        self.features.setCrs(QgsCoordinateReferenceSystem.fromOgcWmsCrs("EPSG:4326"))
                    layerlist=self.mymap.layers()
                    layerlist.insert(0,self.features)
                    self.mymap.setLayers(layerlist)
                    self.mymap.setCurrentLayer(self.features)
                    #if geomcentroidpoint != None:
                    #    self.mymap.zoomWithCenter(geomcentroidpoint.x(), geomcentroidpoint.y(), True)
                    self.mymap.show()
            if rel!="geo":
                self.searchResultModel.setItem(counter, 0, itemchecked)
                item = QStandardItem()
                item.setText(SPARQLUtils.labelFromURI(rel,self.prefixes))
                item.setData(str(rel),UIUtils.dataslot_conceptURI)
                item.setToolTip("<html><b>Property URI</b> " + str(rel) + "<br>Double click to view definition in web browser")
                self.searchResultModel.setItem(counter, 1, item)
                itembutton = QStandardItem()
                itembutton.setText(self.queryresult[rel]["val"])
                itembutton.setData(self.queryresult[rel]["valtype"],UIUtils.dataslot_conceptURI)
                self.searchResultModel.setItem(counter, 2, itembutton)
                counter+=1
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Value")
        SPARQLUtils.handleException(MESSAGE_CATEGORY)