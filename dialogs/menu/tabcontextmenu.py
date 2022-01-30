from ...util.sparqlutils import SPARQLUtils
from ...util.ui.uiutils import UIUtils
from qgis._core import Qgis
from qgis.PyQt.QtWidgets import QMenu, QAction, QFileDialog
from qgis.core import QgsMessageLog

MESSAGE_CATEGORY = 'ContextMenu'

class TabContextMenu(QMenu):

    def __init__(self,name,parent,position,triplestoreconf):
        super().__init__(name,parent)
        self.triplestoreconf=triplestoreconf
        actionsaveRDF = QAction("Save Contents as RDF")
        actionsaveRDF.setIcon(UIUtils.linkeddataicon)
        self.addAction(actionsaveRDF)
        actionsaveRDF.triggered.connect(self.saveTreeToRDF)
        actionsaveClassesRDF = QAction("Save Classes as RDF")
        actionsaveClassesRDF.setIcon(UIUtils.linkeddataicon)
        self.addAction(actionsaveClassesRDF)
        actionsaveClassesRDF.triggered.connect(self.saveClassesTreeToRDF)
        actionsaveVisibleRDF = QAction("Save Visible Contents as RDF")
        actionsaveVisibleRDF.setIcon(UIUtils.linkeddataicon)
        self.addAction(actionsaveVisibleRDF)
        actionsaveVisibleRDF.triggered.connect(self.saveVisibleTreeToRDF)
        self.exec_(position)

    def saveClassesTreeToRDF(self, context):
        filename, _filter = QFileDialog.getSaveFileName(
                self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
                return
        result=set()
        UIUtils.iterateTree(context.invisibleRootItem(),result,False,True,self.triplestoreconf,context)
        QgsMessageLog.logMessage('Started task "{}"'.format(""+str(result)), MESSAGE_CATEGORY, Qgis.Info)
        with open(filename, 'w') as output_file:
            output_file.write("".join(result))
        return result

    def saveVisibleTreeToRDF(self, context):
        filename, _filter = QFileDialog.getSaveFileName(
                self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
                return
        result=set()
        UIUtils.iterateTree(context.invisibleRootItem(),result,True,False,self.triplestoreconf,context)
        QgsMessageLog.logMessage('Started task "{}"'.format(""+str(result)), MESSAGE_CATEGORY, Qgis.Info)
        with open(filename, 'w') as output_file:
            output_file.write("".join(result))
        return result

    def saveTreeToRDF(self, context):
        filename, _filter = QFileDialog.getSaveFileName(
                self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
                return
        result=set()
        UIUtils.iterateTree(context.invisibleRootItem(),result,False,False,self.triplestoreconf,context)
        QgsMessageLog.logMessage('Started task "{}"'.format(""+str(result)), MESSAGE_CATEGORY, Qgis.Info)
        with open(filename, 'w') as output_file:
            output_file.write("".join(result))
        return result