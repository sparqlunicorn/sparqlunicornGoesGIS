import json
import requests

from ....util.ui.uiutils import UIUtils
from ....dialogs.info.errormessagebox import ErrorMessageBox
from qgis.PyQt.QtGui import QIcon, QStandardItem, QStandardItemModel
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'ExtractNamespaceTask'

class TripleStoreRepositoryTask(QgsTask):


    def __init__(self, description,resCombobox,triplestorerepourl=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestorerepourl = triplestorerepourl
        self.resComboBox=resCombobox
        if triplestorerepourl==None:
            self.triplestorerepourl="https://raw.githubusercontent.com/sparqlunicorn/sparqlunicornGoesGIS/ldregistry/ldregistry.json"
        self.results = None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.triplestorerepourl)), MESSAGE_CATEGORY, Qgis.Info)
        try:
            self.results = json.loads(requests.get(self.triplestorerepourl).text)
            QgsMessageLog.logMessage('Started task "{}"'.format(str(self.results)), MESSAGE_CATEGORY,
                                     Qgis.Info)
            return True
        except Exception as e:
            self.exception=e
            return False

    def finished(self, result):
        if self.exception!=None:
            msgBox = ErrorMessageBox("Error while accessing the triple store repository", "")
            msgBox.setText("An error occured while accessing the triple store repository:\n" + str(self.exception))
            msgBox.exec()
        if self.results!=None:
            model=QStandardItemModel()
            self.resComboBox.setModel(model)
            for item in self.results:
                citem=QStandardItem()
                citem.setData(item["name"], UIUtils.dataslot_conceptURI)
                citem.setText(item["name"])
                citem.setIcon(UIUtils.linkeddataicon)
                model.appendRow(citem)