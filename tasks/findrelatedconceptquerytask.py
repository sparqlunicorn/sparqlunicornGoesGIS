from ..util.layerutils import LayerUtils
from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis, QgsFeature, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtGui import QStandardItem
import json

from qgis.PyQt.QtCore import Qt, QSize

MESSAGE_CATEGORY = 'FindRelatedConceptQueryTask'

class FindRelatedConceptQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,triplestoreconf):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchResultModel=dlg
        self.triplestoreconf=triplestoreconf
        self.concept=concept

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        if "sparql11" in self.triplestoreurl and self.triplestoreurl["sparql11"]:
            thequery = "SELECT (COUNT(?rel) AS ?relcount) ?rel COUNT(?item) ?val (COUNT(?val) AS ?valcount) WHERE { ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
                self.concept) + "> . ?con ?rel ?item . OPTIONAL { ?item  <" + str(self.triplestoreconf["typeproperty"]) + "> ?val . } }"
        else:
            thequery="SELECT ?rel ?val WHERE { ?con <"+str(self.triplestoreconf["typeproperty"])+"> <"+str(self.concept)+"> . ?con ?rel ?item . OPTIONAL { ?item  <"+str(self.triplestoreconf["typeproperty"])+"> ?val . } }"
        QgsMessageLog.logMessage("SELECT ?rel WHERE { ?con "+str(self.triplestoreconf["typeproperty"])+" "+str(self.concept)+" . ?con ?rel ?item . OPTIONAL { ?item "+str(self.triplestoreconf["typeproperty"])+" ?val . } }", MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        self.queryresult={}
        for result in results["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult[result["rel"]["value"]]=set()
                    #self.queryresult[result["rel"]["value"]]["values"]=set()
                self.queryresult[result["rel"]["value"]].add(result["val"]["value"])
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            str(self.concept)), MESSAGE_CATEGORY, Qgis.Info)
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        counter=0
        for rel in self.queryresult:
            #QgsMessageLog.logMessage("Query results: " + str(rel), MESSAGE_CATEGORY, Qgis.Info)
            if SPARQLUtils.namespaces["rdf"] in rel or SPARQLUtils.namespaces["rdfs"] in rel \
                or SPARQLUtils.namespaces["owl"] in rel \
                or SPARQLUtils.namespaces["dc"] in rel \
                or SPARQLUtils.namespaces["skos"] in rel:
                continue
            if rel!="geo":
                self.searchResultModel.insertRow(counter)
            itemchecked = QStandardItem()
            itemchecked.setFlags(Qt.ItemIsUserCheckable |
                                 Qt.ItemIsEnabled)
            itemchecked.setCheckState(Qt.Checked)
            if rel in SPARQLUtils.geoproperties:
                if SPARQLUtils.geoproperties[rel]=="DatatypeProperty":
                    itemchecked.setIcon(UIUtils.geodatatypepropertyicon)
                    itemchecked.setToolTip("Geo Datatype Property")
                    itemchecked.setText("GeoDP")
                elif SPARQLUtils.geoproperties[rel]=="ObjectProperty":
                    itemchecked.setIcon(UIUtils.geoobjectpropertyicon)
                    itemchecked.setToolTip("Geo Object Property")
                    itemchecked.setText("GeoOP")
            elif "geoobjproperty" in self.triplestoreconf and rel in self.triplestoreconf["geoobjproperty"]:
                itemchecked.setIcon(UIUtils.linkedgeoobjectpropertyicon)
                itemchecked.setToolTip("Linked Geo Object Property")
                itemchecked.setText("LGeoOP")
            elif rel!="geo":
                    itemchecked.setIcon(UIUtils.objectpropertyicon)
                    itemchecked.setToolTip("Object Property")
                    itemchecked.setText("OP")
            elif rel!="geo":
                itemchecked.setIcon(UIUtils.datatypepropertyicon)
                itemchecked.setToolTip("DataType Property")
                itemchecked.setText("DP")
            if rel!="geo":
                self.searchResultModel.setItem(counter, 0, itemchecked)
                item = QStandardItem()
                item.setText(str(SPARQLUtils.labelFromURI(rel)))
                item.setData(str(rel),UIUtils.dataslot_conceptURI)
                item.setToolTip("<html><b>Property URI</b> " + str(rel) + "<br>Double click to view definition in web browser")
                self.searchResultModel.setItem(counter, 1, item)
                itembutton = QStandardItem()
                for val in self.queryresult[rel]:
                    mystring=""
                    mystring+=str(val)+" "
                    itembutton.setText(mystring)
                self.searchResultModel.setItem(counter, 2, itembutton)
                counter+=1
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Value")
