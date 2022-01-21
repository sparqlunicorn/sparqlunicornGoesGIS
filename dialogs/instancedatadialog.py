
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QTableWidgetItem
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QDesktopServices, QStandardItem
from qgis.PyQt import uic
from qgis.gui import QgsMapCanvas, QgsMapToolPan
from qgis.core import Qgis, QgsVectorLayer, QgsRasterLayer, QgsProject, QgsGeometry, QgsCoordinateReferenceSystem, \
    QgsCoordinateTransform, QgsPointXY, QgsApplication, QgsMessageLog
from qgis.PyQt.QtCore import QSortFilterProxyModel, Qt
from qgis.PyQt.QtGui import QStandardItemModel

from ..util.ui.uiutils import UIUtils
from ..tasks.instancequerytask import InstanceQueryTask
from ..tasks.querylayertask import QueryLayerTask
from ..util.sparqlutils import SPARQLUtils
import os.path

MESSAGE_CATEGORY = 'InstanceDataDialogggg'
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/instancedatadialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class InstanceDataDialog(QDialog, FORM_CLASS):

    ##
    #  @brief Initializes the search dialog
    #
    #  @param self The object pointer
    #  @param column The column of the GUI widget which called this dialog, if any
    #  @param row The row of the GUI widget which called this dialog, if any
    #  @param triplestoreconf The triple store configuration of the plugin
    #  @param prefixes A list of prefixes known to the plugin
    #  @param interlinkOrEnrich indicates whether this dialog was called from an enrichment or interlinking dialog
    #  @param table The GUI element ot return the result to
    #  @param propOrClass indicates whether a class or a property can be searched
    #  @param bothOptions indicates whether both a class or property may be searched
    #  @param currentprefixes Description for currentprefixes
    #  @param addVocab Description for addVocab
    #  @return Return description
    #
    #  @details More details
    #
    def __init__(self, concept,concepttype,label,triplestoreurl,triplestoreconf,prefixes,curindex,title="Data Instance View"):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.concept=concept
        self.concepttype=concepttype
        self.label=label
        self.prefixes=prefixes
        self.alreadyloadedSample=[]
        self.triplestoreconf=triplestoreconf
        self.triplestoreurl=triplestoreurl
        self.curindex=curindex
        if concepttype==SPARQLUtils.geoinstancenode:
            self.setWindowIcon(SPARQLUtils.geoinstanceicon)
            self.setWindowTitle(title+" for GeoInstance")
        else:
            self.setWindowIcon(SPARQLUtils.instanceicon)
            self.setWindowTitle(title+" for Instance")
        self.vl = QgsVectorLayer("Point", "temporary_points", "memory")
        self.map_canvas.setDestinationCrs(QgsCoordinateReferenceSystem(3857))
        actionPan = QAction("Pan", self)
        actionPan.setCheckable(True)
        actionPan.triggered.connect(lambda: self.map_canvas.setMapTool(self.toolPan))
        self.toolPan = QgsMapToolPan(self.map_canvas)
        self.toolPan.setAction(actionPan)
        self.map_canvas.hide()
        uri = "url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz&zmax=19&crs=EPSG3857"
        self.mts_layer = QgsRasterLayer(uri, 'OSM', 'wms')
        QgsMessageLog.logMessage(str(self.mts_layer), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(str(self.mts_layer.isValid()), MESSAGE_CATEGORY, Qgis.Info)
        if not self.mts_layer.isValid():
            print("Layer failed to load!")
        self.map_canvas.setExtent(self.mts_layer.extent())
        self.map_canvas.setLayers([self.mts_layer])
        self.map_canvas.setCurrentLayer(self.mts_layer)
        self.map_canvas.setMapTool(self.toolPan)
        self.instanceDataNameLabel.setText(str(label)+" (<a href=\""+str(concept)+"\">"+SPARQLUtils.labelFromURI(str(concept),self.triplestoreconf[self.curindex]["prefixesrev"])+"</a>)")
        header =self.instanceDataTableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Sample Instances")
        self.tablemodel.insertRow(0)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.instanceDataTableView.setModel(self.filter_proxy_model)
        item = QStandardItem()
        item.setText("Loading...")
        self.tablemodel.setItem(0,0,item)
        self.instanceDataTableView.entered.connect(lambda modelindex: UIUtils.showTableURI(modelindex,self.instanceDataTableView,self.statusBarLabel))
        self.instanceDataTableView.doubleClicked.connect(lambda modelindex: UIUtils.openTableURL(modelindex,self.instanceDataTableView))
        self.filterTableEdit.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.queryInstanceLayerButton.clicked.connect(self.queryInstance)
        self.okButton.clicked.connect(self.close)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf[self.curindex]), "InstanceDataDialog", Qgis.Info)
        self.getAttributes(self.concept,triplestoreurl)

    def queryInstance(self):
        querydepth = self.graphQueryDepthBox.value()
        if int(querydepth)>1:
            query=SPARQLUtils.expandRelValToAmount("SELECT ?" + " ?".join(self.triplestoreconf[self.curindex][
                                       "mandatoryvariables"]) + " ?rel ?val\n WHERE\n {\n BIND( <" + str(
                self.concept) + "> AS ?item)\n" +
            self.triplestoreconf[self.curindex]["geotriplepattern"][0] + "\n ?item ?rel ?val . }",querydepth)
            self.qlayerinstance = QueryLayerTask(
            "Instance to Layer: " + str(self.concept),
            self.triplestoreconf[self.curindex]["endpoint"],query,
            self.triplestoreconf[self.curindex], False, SPARQLUtils.labelFromURI(self.concept), None,self.graphQueryDepthBox.value(),self.shortenURICheckBox.isChecked())
        else:
            self.qlayerinstance = QueryLayerTask(
            "Instance to Layer: " + str(self.concept),
            self.triplestoreconf[self.curindex]["endpoint"],
            "SELECT ?" + " ?".join(self.triplestoreconf[self.curindex][
                                       "mandatoryvariables"]) + " ?rel ?val\n WHERE\n {\n BIND( <" + str(
                self.concept) + "> AS ?item)\n ?item ?rel ?val . " +
            self.triplestoreconf[self.curindex]["geotriplepattern"][0] + "\n }",
            self.triplestoreconf[self.curindex], False, SPARQLUtils.labelFromURI(self.concept), None,self.graphQueryDepthBox.value(),self.shortenURICheckBox.isChecked())
        QgsApplication.taskManager().addTask(self.qlayerinstance)

    ##
    #  @brief Gives statistics about most commonly occuring properties from a certain class in a given triple store.
    #  
    #  @param [in] self The object pointer
    #  @return A list of properties with their occurance given in percent
    def getAttributes(self, concept="wd:Q3914", endpoint_url="https://query.wikidata.org/sparql"):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf[self.curindex]), "InstanceDataDialog", Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.curindex)+ " "+str(self.triplestoreconf[self.curindex]["endpoint"])), "DataSchemaDialog",
                                 Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf[self.curindex]["whattoenrichquery"]), "DataSchemaDialog",
                                 Qgis.Info)
        if self.concept == "" or self.concept is None or "whattoenrichquery" not in self.triplestoreconf[self.curindex]:
            return
        self.qtask = InstanceQueryTask("Querying dataset schema.... (" + self.label + ")",
                                           self.triplestoreurl,
                                           self.concept,
                                           self.triplestoreconf[self.curindex],
                                           self.tablemodel,self.map_canvas,self.vl,self)
        QgsApplication.taskManager().addTask(self.qtask)