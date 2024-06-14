from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QStyle,QWidget,QMenu,QAction
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtCore import QSortFilterProxyModel

from ...util.sparqlutils import SPARQLUtils
from ...util.ui.uiutils import UIUtils
from ...tasks.query.discovery.findrelatedconceptquerytask import FindRelatedConceptQueryTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/advancedquerydialog.ui'))

##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
class AdvancedQueryDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={}, concept="",title="Convert CRS"):
        """Constructor."""
        super(QWidget, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.rdffileicon)
        self.triplestoreconf = triplestoreconf
        self.tablemodel = QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Ingoing Concept")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Ingoing Relation")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Outgoing Relation")
        self.tablemodel.setHeaderData(3, Qt.Horizontal, "Target Concept")
        self.tablemodel.insertRow(0)
        self.nodetype = SPARQLUtils.classnode
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(3)
        self.tableView.setModel(self.filter_proxy_model)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.entered.connect(lambda modelindex: UIUtils.showTableURI(modelindex, self.tableView, self.statusBarLabel))
        #self.tableView.doubleClicked.connect(self.showRelatedFromIndex)
        #self.tableView.customContextMenuRequested.connect(self.onContext)
        #self.filterTableEdit.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        #self.filterTableComboBox.currentIndexChanged.connect(lambda: self.filter_proxy_model.setFilterKeyColumn(self.filterTableComboBox.currentIndex()))
        self.show()


    def getRelatedClassStatistics(self):
        if self.concept == "" or self.concept is None:
            return
        self.qtask = FindRelatedConceptQueryTask("Querying related classes.... (" + str(self.concept) + ")",
                               self.triplestoreconf["resource"],
                               self.tablemodel,
                               self.concept,
                               self.label,
                               self.nodetype,
                               self.triplestoreconf,self.tableView)
        QgsApplication.taskManager().addTask(self.qtask)



