
from ...util.export.layer.layerexporter import LayerExporter
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox

MESSAGE_CATEGORY = 'ConvertLayerTask'

class ConvertLayerTask(QgsTask):

    def __init__(self, description, layer, filename, vocabulary, literaltype, prefixes, columntypes=None,dialog=None, progress=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.filename = filename
        self.prefixes=prefixes
        self.vocabulary = vocabulary
        self.layer= layer
        self.columntypes=columntypes
        self.literaltype = literaltype
        self.dialog = dialog


    def run(self):
        fileext=self.filename[0][self.filename[0].rfind('.')+1:].upper()
        if self.columntypes!=None:
            ttlstring = LayerExporter.layerToTTLString(self.layer,
                                                       self.prefixes,
                                                       self.vocabulary, self.literaltype,
                                                       self.columntypes)
        else:
            ttlstring = LayerExporter.layerToTTLString(self.layer,
                                                       self.prefixes,
                                                       self.vocabulary, self.literaltype,
                                                       None, None, None, None, None, None)
        QgsMessageLog.logMessage('Started task "{}"'.format(
            fileext),
            "Convert Layer Dialog", Qgis.Info)
        with open(self.filename[0], 'w') as output_file:
            LayerExporter.exportToFormat(ttlstring, output_file, self.filename[0], fileext,self.prefixes)
        return True

    def finished(self, result):
        self.progress.close()
        if result == True:
            iface.messageBar().pushMessage("Exported layer successfully to " + str(self.filename[0]) + "!", "OK",
                                           level=Qgis.Success)
            msgBox = QMessageBox()
            msgBox.setText("Layer converted to and saved as "+str(self.filename[0]))
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("An error occurred while converting the layer converted to "+str(self.filename[0]))
            msgBox.exec()


