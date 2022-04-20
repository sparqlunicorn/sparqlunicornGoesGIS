from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtCore import QSortFilterProxyModel
import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsApplication, QgsMessageLog

from ..util.ui.uiutils import UIUtils
from ..tasks.findrelatedconceptquerytask import FindRelatedConceptQueryTask

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/clusterviewdialog.ui'))

class ClusterViewDialog(QDialog, FORM_CLASS):

    def __init__(self,triplestoreconf,concept):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Related Concepts to "+str(concept))
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation'))))
        self.closeButton.clicked.connect(self.close)
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Ingoing Concept")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Ingoing Relation")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Outgoing Relation")
        self.tablemodel.setHeaderData(3, Qt.Horizontal, "Target Concept")
        self.tablemodel.insertRow(0)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(3)
        self.tableView.setModel(self.filter_proxy_model)
        self.clusterView.hide()
        self.tableView.entered.connect(lambda modelindex: UIUtils.showTableURI(modelindex, self.tableView, self.statusBarLabel))
        self.tableView.doubleClicked.connect(lambda modelindex: UIUtils.openTableURL(modelindex, self.tableView))
        self.filterTableEdit.textChanged.connect(self.filter_proxy_model.setFilterRegExp)
        self.filterTableComboBox.currentIndexChanged.connect(lambda: self.filter_proxy_model.setFilterKeyColumn(self.filterTableComboBox.currentIndex()))
        self.show()
        self.getRelatedClassStatistics()


    def getRelatedClassStatistics(self):
        if self.concept == "" or self.concept is None:
            return
        self.qtask = FindRelatedConceptQueryTask("Querying related classes.... (" + str(self.concept) + ")",
                               self.triplestoreconf["resource"],
                               self.tablemodel,
                               self.concept,
                               self.triplestoreconf,self.tableView)
        QgsApplication.taskManager().addTask(self.qtask)