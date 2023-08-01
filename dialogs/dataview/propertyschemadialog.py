
from qgis.PyQt.QtWidgets import QWidget, QHeaderView, QProgressDialog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import uic
from qgis.gui import QgsMapToolPan
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel
from qgis.PyQt.QtCore import QSortFilterProxyModel
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsCoordinateReferenceSystem, \
    QgsApplication

from ...tasks.query.discovery.instancesamplequerytask import InstanceSampleQueryTask
from ...util.ui.uiutils import UIUtils
from ...tasks.query.discovery.propertyschemaquerytask import PropertySchemaQueryTask
from ...util.sparqlutils import SPARQLUtils
import os.path


MESSAGE_CATEGORY = 'PropertySchemaDialog'

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/dataschemadialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class PropertySchemaDialog(QWidget, FORM_CLASS):

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
    def __init__(self, property,propertytype,label,triplestoreurl,triplestoreconf,prefixes,title="Data Schema View"):
        super(QWidget, self).__init__()
        self.setupUi(self)
        self.concept=property
        self.concepttype=propertytype
        self.label=label
        self.prefixes=prefixes
        self.selected=True
        self.styleprop=[]
        self.alreadyloadedSample=[]
        self.triplestoreconf=triplestoreconf
        self.triplestoreurl=triplestoreurl
        if propertytype==SPARQLUtils.geoobjectpropertynode:
            self.setWindowIcon(UIUtils.geoobjectpropertyicon)
            self.setWindowTitle(title+" (GeoObjectProperty)")
        elif propertytype==SPARQLUtils.objectpropertynode:
            self.setWindowIcon(UIUtils.objectpropertyicon)
            self.setWindowTitle(title+" (ObjectProperty)")
        elif propertytype==SPARQLUtils.geodatatypepropertynode:
            self.setWindowIcon(UIUtils.geodatatypepropertyicon)
            self.setWindowTitle(title+" (GeoDatatypeProperty)")
            self.geospatialConstraintButton.hide()
        else:
            self.setWindowIcon(UIUtils.datatypepropertyicon)
            self.setWindowTitle(title+" (DatatypeProperty)")
            self.geospatialConstraintButton.hide()
        self.dataSchemaNameLabel.setText(str(label)+" (<a href=\""+str(property)+"\">"+str(property[property.rfind('/')+1:])+"</a>)")
        #self.queryAllInstancesButton.clicked.connect(self.queryAllInstances)
        self.vl = QgsVectorLayer("Point", "temporary_points", "memory")
        self.map_canvas.setDestinationCrs(QgsCoordinateReferenceSystem.fromOgcWmsCrs("EPSG:3857"))
        actionPan = QAction("Pan", self)
        actionPan.setCheckable(True)
        actionPan.triggered.connect(lambda: self.map_canvas.setMapTool(self.toolPan))
        self.toolPan = QgsMapToolPan(self.map_canvas)
        self.toolPan.setAction(actionPan)
        self.map_canvas.hide()
        uri = "url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz&zmax=19&crs=EPSG3857"
        self.mts_layer = QgsRasterLayer(uri, 'OSM', 'wms')
        if not self.mts_layer.isValid():
            print("Layer failed to load!")
        self.map_canvas.setExtent(self.mts_layer.extent())
        self.map_canvas.setLayers([self.mts_layer])
        self.map_canvas.setCurrentLayer(self.mts_layer)
        self.map_canvas.setMapTool(self.toolPan)
        header =self.dataSchemaTableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Type")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Class")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Sample Instances")
        self.tablemodel.insertRow(0)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.dataSchemaTableView.setModel(self.filter_proxy_model)
        item = QStandardItem()
        item.setText("Loading...")
        self.tablemodel.setItem(0,0,item)
        self.dataSchemaTableView.entered.connect(lambda modelindex: UIUtils.showTableURI(modelindex, self.dataSchemaTableView, self.statusBarLabel))
        self.dataSchemaTableView.doubleClicked.connect(lambda modelindex: UIUtils.openTableURL(modelindex, self.dataSchemaTableView))
        self.filterTableEdit.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.dataSchemaTableView.clicked.connect(self.loadSamples)
        #self.geospatialConstraintButton.clicked.connect(self.loadBBOXDialog)
        self.toggleSelectionButton.clicked.connect(self.toggleSelect)
        self.filterTableComboBox.currentIndexChanged.connect(lambda: self.filter_proxy_model.setFilterKeyColumn(self.filterTableComboBox.currentIndex()))
        self.getAttributeStatistics(self.concept,triplestoreurl)
        self.show()

    def toggleSelect(self):
        self.selected=not self.selected
        for row in range(self.tablemodel.rowCount()):
            if self.selected:
                self.tablemodel.item(row, 0).setCheckState(Qt.Checked)
            else:
                self.tablemodel.item(row, 0).setCheckState(Qt.Unchecked)

    ##
    #  @brief Gives statistics about most commonly occuring properties from a certain class in a given triple store.
    #
    #  @param [in] self The object pointer
    #  @return A list of properties with their occurance given in percent
    def getAttributeStatistics(self, concept="wd:Q3914", endpoint_url="https://query.wikidata.org/sparql"):
        if self.concept == "" or self.concept is None or "whattoenrichquery" not in self.triplestoreconf:
            return
        progress = QProgressDialog("Querying dataset schema....", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.setCancelButton(None)
        thequery="""SELECT (COUNT(distinct ?val) AS ?countval) (COUNT(?rel) AS ?countrel) ?reltype ?valtype
            WHERE { 
            ?rel %%concept%% ?val .
            OPTIONAL {?rel %%typeproperty%% ?reltype . }
            OPTIONAL {?val %%typeproperty%% ?valtype . }
            OPTIONAL {BIND( datatype(?val) AS ?valtype ) } }
            GROUP BY ?reltype ?valtype
            ORDER BY DESC(?countrel)"""
        self.qtask = PropertySchemaQueryTask("Querying property dataset schema.... (" + str(self.label) + ")",
                               self.triplestoreurl,
                               SPARQLUtils.queryPreProcessing(thequery,self.triplestoreconf,self.concept,self.concepttype==SPARQLUtils.collectionclassnode),
                               self.concept,
                               None,
                               self.tablemodel,self.triplestoreconf, progress,self,self.styleprop)
        QgsApplication.taskManager().addTask(self.qtask)

    def loadSamples(self,modelindex):
        row=modelindex.row()
        column=modelindex.column()
        if column==2 and row not in self.alreadyloadedSample:
            relation = str(self.dataSchemaTableView.model().index(row, column-1).data(UIUtils.dataslot_conceptURI))
            self.qtask2 = InstanceSampleQueryTask("Querying dataset schema.... (" + str(self.label)+ ")",
                                             self.triplestoreurl,
                                             self,
                                             self.concept,
                                             relation,
                                             column,row,self.triplestoreconf,self.tablemodel,
                                            self.map_canvas,self.concepttype)
            QgsApplication.taskManager().addTask(self.qtask2)
            self.alreadyloadedSample.append(row)