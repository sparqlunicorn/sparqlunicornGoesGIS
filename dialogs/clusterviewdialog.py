from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel
from qgis.PyQt.QtCore import QSortFilterProxyModel
import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QWidget, QHeaderView, QProgressDialog
from qgis.core import Qgis, QgsVectorLayer, QgsRasterLayer, QgsCoordinateReferenceSystem, \
    QgsApplication, QgsMessageLog

from ..util.sparqlutils import SPARQLUtils
from ..util.ui.uiutils import UIUtils
from ..tasks.findrelatedconceptquerytask import FindRelatedConceptQueryTask

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/clusterviewdialog.ui'))

class ClusterViewDialog(QDialog, FORM_CLASS):

    def __init__(self,concept,triplestoreconf):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation'))))
        self.closeButton.clicked.connect(self.close)
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Sample Instances")
        self.tablemodel.insertRow(0)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.tableView.setModel(self.filter_proxy_model)
        self.show()
        self.getRelatedClassStatistics()


    def getRelatedClassStatistics(self):
        if self.concept == "" or self.concept is None:
            return
        progress = QProgressDialog("Querying related classes....", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.setCancelButton(None)
        self.qtask = FindRelatedConceptQueryTask("Querying related classes.... (" + str(self.concept) + ")",
                               self.triplestoreurl,
                               self.tablemodel,
                               self.concept,
                               self.triplestoreconf)
        QgsApplication.taskManager().addTask(self.qtask)