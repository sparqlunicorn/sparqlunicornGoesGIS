from ..util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (
    QgsTask
)

MESSAGE_CATEGORY = 'LoadGraphTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class LoadGraphTask(QgsTask):

    def __init__(self, description, filename, loadgraphdlg, dlg, maindlg, query, triplestoreconf, progress, closedlg):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.dlg = dlg
        self.maindlg = maindlg
        self.triplestoreconf = triplestoreconf
        self.loadgraphdlg = loadgraphdlg
        self.query = query
        self.graph = None
        self.geoconcepts = None
        self.closedlg = closedlg
        self.exception = None
        self.filename = filename
        self.geojson = None

    def run(self):
        self.graph=SPARQLUtils.loadGraph(self.filename)
        self.geoconcepts = []
        if self.graph != None:
            print("WE HAVE A GRAPH")
            results = self.graph.query(self.query)
            for row in results:
                self.geoconcepts.append(str(row[0]))
            return True
        return False

    def finished(self, result):
        if result == True:
            self.dlg.geoTreeViewModel.clear()
            self.dlg.comboBox.setCurrentIndex(0);
            self.maindlg.currentgraph = self.graph
            self.dlg.layercount.setText("[" + str(len(self.geoconcepts)) + "]")
            for geo in self.geoconcepts:
                item = QStandardItem()
                item.setData(geo, 256)
                item.setText(geo[geo.rfind('/') + 1:])
                self.dlg.geoTreeViewModel.appendRow(item)
            # comp=QCompleter(self.dlg.layerconcepts)
            # comp.setCompletionMode(QCompleter.PopupCompletion)
            # comp.setModel(self.dlg.layerconcepts.model())
            # self.dlg.layerconcepts.setCompleter(comp)
            self.dlg.inp_sparql2.setPlainText(
                self.triplestoreconf[0]["querytemplate"][0]["query"].replace("%%concept%%", self.geoconcepts[0]))
            self.dlg.inp_sparql2.columnvars = {}
            self.maindlg.loadedfromfile = True
            self.maindlg.justloadingfromfile = False
            if self.closedlg:
                self.loadgraphdlg.close()
        else:
            msgBox = QMessageBox()
            msgBox.setText(self.exception)
            msgBox.exec()
        self.progress.close()
