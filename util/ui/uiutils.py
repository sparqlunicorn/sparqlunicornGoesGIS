
from ..sparqlutils import SPARQLUtils
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator, QValidator
from qgis.PyQt.QtCore import Qt, QUrl, QEvent
from qgis.PyQt.QtGui import QDesktopServices

class UIUtils:

    urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    @staticmethod
    def check_state(sender):
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    @staticmethod
    def openListURL(item):
        concept = str(item.data(256))
        if concept.startswith("http"):
            url = QUrl(concept)
            QDesktopServices.openUrl(url)

    @staticmethod
    def openTableURL(modelindex,table):
        if table.model().data(modelindex)!=None:
            concept=str(table.model().data(modelindex,256))
            if concept.startswith("http"):
                url = QUrl(concept)
                QDesktopServices.openUrl(url)

    @staticmethod
    def showTableURI(modelindex,table,statusbar):
        if table.model().data(modelindex)!=None:
            concept=str(table.model().data(modelindex,256))
            if concept.startswith("http"):
                statusbar.setText(concept)


    @staticmethod
    def iterateTree(node,result,visible,classesonly,triplestoreconf,currentContext):
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        labelproperty="http://www.w3.org/2000/01/rdf-schema#label"
        subclassproperty="http://www.w3.org/2000/01/rdf-schema#subClassOf"
        if "labelproperty" in triplestoreconf:
            labelproperty=triplestoreconf["labelproperty"]
        if "typeproperty" in triplestoreconf:
            typeproperty=triplestoreconf["typeproperty"]
        if "subclassproperty" in triplestoreconf:
            subclassproperty=triplestoreconf["subclassproperty"]
        for i in range(node.rowCount()):
            if node.child(i).hasChildren():
                UIUtils.iterateTree(node.child(i),result,visible,classesonly,triplestoreconf,currentContext)
            if node.data(256)==None or (visible and not currentContext.visualRect(node.child(i).index()).isValid()):
                continue
            if node.child(i).data(257)==SPARQLUtils.geoclassnode or node.child(i).data(257)==SPARQLUtils.classnode:
                result.add("<" + str(node.child(i).data(256)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.child(i).data(256)) + "> <"+labelproperty+"> \""+str(SPARQLUtils.labelFromURI(str(node.child(i).data(256)),None))+"\" .\n")
                result.add("<" + str(node.data(256)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.data(256)) + "> <"+labelproperty+"> \""+str(SPARQLUtils.labelFromURI(str(node.data(256)),None))+"\" .\n")
                result.add("<"+str(node.child(i).data(256))+"> <"+subclassproperty+"> <"+str(node.data(256))+"> .\n")
            elif not classesonly and node.child(i).data(257)==SPARQLUtils.geoinstancenode or node.child(i).data(257)==SPARQLUtils.instancenode:
                result.add("<" + str(node.data(256)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.data(256)) + "> <"+labelproperty+"> \"" + str(SPARQLUtils.labelFromURI(str(node.data(256)), None)) + "\" .\n")
                result.add("<" + str(node.child(i).data(256)) + "> <"+labelproperty+"> \"" + str(SPARQLUtils.labelFromURI(str(node.child(i).data(256)), None)) + "\" .\n")
                result.add("<"+str(node.child(i).data(256))+"> <"+typeproperty+"> <"+str(node.data(256))+"> .\n")
