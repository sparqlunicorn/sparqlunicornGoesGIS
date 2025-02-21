import json
import requests

from ....util.ui.uiutils import UIUtils
from ....util.conf.configutils import ConfigUtils
from ....dialogs.info.errormessagebox import ErrorMessageBox
from qgis.PyQt.QtGui import QIcon, QStandardItem, QStandardItemModel
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'TripleStoreRepositorySyncTask'

class TripleStoreRepositorySyncTask(QgsTask):


    def __init__(self, description,dlg,combobox,triplestoreconf,removeOldConfig=False,triplestorerepourl=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreconf=triplestoreconf
        self.dlg=dlg
        self.combobox=combobox
        self.triplestorerepourl = triplestorerepourl
        self.removeOldConfig=removeOldConfig
        if triplestorerepourl is None:
            self.triplestorerepourl="https://raw.githubusercontent.com/sparqlunicorn/sparqlunicornGoesGIS/ldregistry/ldregistry.json"
        self.results = None

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(str(self.triplestorerepourl)), MESSAGE_CATEGORY, Qgis.Info)
        try:
            self.results = json.loads(requests.get(self.triplestorerepourl).text)
            #QgsMessageLog.logMessage('Started task "{}"'.format(str(len(self.results))), MESSAGE_CATEGORY,Qgis.Info)
            return True
        except Exception as e:
            self.exception=e
            return False

    def finished(self, result):
        if self.exception is not None:
            QgsMessageLog.logMessage("An error occured while accessing the triple store repository:\n" + str(self.exception), MESSAGE_CATEGORY,Qgis.Info)
            ErrorMessageBox("Error syncing triple stores","An error occured while accessing the triple store repository:\n" + str(self.exception)).exec()
        if self.results is not None:
           #QgsMessageLog.logMessage("Updating triplestoreconf:",MESSAGE_CATEGORY, Qgis.Info)
           self.dlg.triplestoreconf=ConfigUtils.updateTripleStoreConf(self.triplestoreconf,self.results,self.removeOldConfig)
           if self.dlg.comboBox is not None:
                self.dlg.comboBox.clear()
                UIUtils.createTripleStoreCBox(self.dlg.comboBox, self.triplestoreconf)
