from rdflib import Literal

from ...util.layerutils import LayerUtils
from ...util.sparqlutils import SPARQLUtils
from ...util.export.srs.crsexporttools import ConvertCRS
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QFileDialog

MESSAGE_CATEGORY = 'ConvertCRSTask'

class ConvertCRSTask(QgsTask):

    def __init__(self, description, filename, crsdef, convertFrom, convertTo, dialog, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.filename = filename
        self.crsdef = crsdef
        self.crsdefs={}
        self.dialog = dialog
        self.convertFrom=convertFrom
        self.convertTo=convertTo

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        self.graph=SPARQLUtils.loadGraph(self.filename)
        if self.graph is not None:
            for s, p, o in self.graph:
                if isinstance(o, Literal):
                    if str(o.datatype) in SPARQLUtils.supportedLiteralTypes:
                        newliteral = Literal(LayerUtils.processLiteral(o, o.datatype, self.crsdef,None,None,False,o.datatype), datatype=o.datatype)
                        self.graph.set((s, p, newliteral))
        return True

    def finished(self, result):
        self.progress.close()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.dialog, "QFileDialog.getSaveFileName()", "", "All Files (*);;Text Files (*.ttl)", options=options)
        if fileName and self.graph is not None:
            fo = open(fileName, "w")
            fo.write(ConvertCRS().ttlhead)
            fo.write(self.graph.serialize(format="turtle"))
            for crs in self.crsdefs:
                fo.write(self.crsdefs[crs])
            fo.close()
        iface.messageBar().pushMessage("Save converted file", "OK", level=Qgis.Success)
        self.dialog.close()
