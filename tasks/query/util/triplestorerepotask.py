import json
import requests

from ...dialogs.info.errormessagebox import ErrorMessageBox
from ...util.ui.uiutils import UIUtils
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox

MESSAGE_CATEGORY = 'Search Class/Property Task'

class TripleStoreRepositoryTask(QgsTask):


    def __init__(self, description,triplestorerepourl):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestorerepourl = triplestorerepourl
        if triplestorerepourl==None:
            self.triplestorerepourl="https://raw.githubusercontent.com/sparqlunicorn/sparqlunicornGoesGIS/ldregistry/ldregistry.json"
        self.results = None

    def run(self):
        try:
            self.results = json.loads(requests.get(self.triplestorerepourl).text)
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
            for item in self.results:
                print(item)