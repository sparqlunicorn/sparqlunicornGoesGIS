from rdflib import *
from ..util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox, QProgressDialog, QFileDialog
from qgis.core import QgsProject, QgsGeometry, QgsVectorLayer, QgsExpression, QgsFeatureRequest, \
    QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsApplication, QgsWkbTypes, QgsField
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'ConvertCRSTask'

class ConvertCRSTask(QgsTask):

    def __init__(self, description, filename, crsdef, convertFrom, convertTo, dialog, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.filename = filename
        self.crsdef = crsdef
        self.dialog = dialog
        self.convertFrom=convertFrom
        self.convertTo=convertTo

    def processLiteral(self, literal, literaltype, reproject, projectto):
        QgsMessageLog.logMessage("Process literal: " + str(literal) + " " + str(literaltype) + " " + str(reproject))
        QgsMessageLog.logMessage("REPROJECT: " + str(reproject))
        geom = None
        if literaltype == "" or literaltype == None:
            literaltype = SPARQLUtils.detectLiteralType(literal)
        if "wkt" in literaltype.lower():
            literal = literal.strip()
            if literal.startswith("<http"):
                index = literal.index(">") + 1
                slashindex = literal.rfind("/") + 1
                reproject = literal[slashindex:(index - 1)]
                geom = QgsGeometry.fromWkt(literal[index:])
            else:
                reproject = "CRS84"
                geom = QgsGeometry.fromWkt(literal)
        # elif "gml" in literaltype.lower():
        #    geom=QgsGeometry.fromWkb(ogr.CreateGeometryFromGML(literal).ExportToWkb())
        elif "wkb" in literaltype.lower():
            geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
        if geom != None and projectto != None:
            if reproject != "CRS84":
                sourceCrs = QgsCoordinateReferenceSystem("EPSG:" + str(reproject))
            else:
                sourceCrs = QgsCoordinateReferenceSystem("CRS:84")
            destCrs = QgsCoordinateReferenceSystem(projectto)
            QgsMessageLog.logMessage('PROJECTIT ' + str(sourceCrs.description()) + " " + str(projectto.description()),
                                     MESSAGE_CATEGORY, Qgis.Info)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            geom.transform(tr)
        if geom != None and "wkt" in literaltype.lower():
            return "<http://www.opengis.net/def/crs/EPSG/0/" + str(
                str(projectto.authid())[str(projectto.authid()).rfind(':') + 1:]) + "> " + geom.asWkt()
        if geom != None and "wkb" in literaltype.lower():
            return geom.asWkb()
        if geom != None:
            return geom.asJson()
        return None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        self.graph=SPARQLUtils.loadGraph(self.filename)
        if self.graph != None:
            print("WE HAVE A GRAPH")
            for s, p, o in self.graph:
                QgsMessageLog.logMessage('BEFORE "{}"'.format(o), MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(o, Literal):
                    QgsMessageLog.logMessage('ISLITERAL "{}"'.format(o) + " - " + str(o.datatype), MESSAGE_CATEGORY,
                                             Qgis.Info)
                    QgsMessageLog.logMessage(str(o.datatype), MESSAGE_CATEGORY, Qgis.Info)
                    if str(o.datatype) in self.supportedLiteralTypes:
                        QgsMessageLog.logMessage('ISGEOLITERAL "{}"'.format(self.graph), MESSAGE_CATEGORY, Qgis.Info)
                        newliteral = Literal(self.processLiteral(o, o.datatype, "", self.crsdef), datatype=o.datatype)
                        self.graph.set((s, p, newliteral))
                        QgsMessageLog.logMessage('AFTER "{}"'.format(newliteral) + " - " + str(newliteral.datatype),
                                                 MESSAGE_CATEGORY, Qgis.Info)
        return True

    def finished(self, result):
        self.progress.close()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.dialog, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.ttl)", options=options)
        if fileName:
            fo = open(fileName, "w")
            fo.write(self.graph.serialize(format="turtle").decode())
            fo.close()
        iface.messageBar().pushMessage("Save converted file", "OK", level=Qgis.Success)
        self.dialog.close()
