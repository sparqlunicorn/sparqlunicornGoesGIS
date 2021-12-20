
from qgis.PyQt.QtWidgets import QDialog, QHeaderView, QTableWidgetItem, QProgressDialog
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt import uic
from qgis.core import Qgis
from ..tasks.dataschemaquerytask import DataSchemaQueryTask
from ..tasks.datasamplequerytask import DataSampleQueryTask
from ..tasks.findstylestask import FindStyleQueryTask
from ..tasks.querylayertask import QueryLayerTask
from ..util.sparqlutils import SPARQLUtils
import os.path
from qgis.core import (
    QgsApplication, QgsMessageLog,
)


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/dataschemadialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.


class DataSchemaDialog(QDialog, FORM_CLASS):

    ##
    #  @brief Initializes the search dialog
    #
    #  @param self The object pointer
    #  @param column The column of the GUI widget which called this dialog, if any
    #  @param row The row of the GUI widget which called this dialog, if any
    #  @param triplestoreconf The triple store configuration of the plugin
    #  @param prefixes A list of prefixes known to the plugin
    #  @param interlinkOrEnrich indicates whether this dialog was called from an enrichment or interlinking dialog
    #  @param table The GUI element ot return the result to
    #  @param propOrClass indicates whether a class or a property can be searched
    #  @param bothOptions indicates whether both a class or property may be searched
    #  @param currentprefixes Description for currentprefixes
    #  @param addVocab Description for addVocab
    #  @return Return description
    #
    #  @details More details
    #
    def __init__(self, concept,label,triplestoreurl,triplestoreconf,prefixes,curindex):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.concept=concept
        self.label=label
        self.prefixes=prefixes
        self.alreadyloadedSample=[]
        self.triplestoreconf=triplestoreconf
        self.triplestoreurl=triplestoreurl
        self.curindex=curindex
        self.dataSchemaNameLabel.setText(str(label)+" (<a href=\""+str(concept)+"\">"+str(concept[concept.rfind('/')+1:])+"</a>)")
        self.queryAllInstancesButton.clicked.connect(self.queryAllInstances)
        header =self.dataSchemaTableView.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.dataSchemaTableView.setHorizontalHeaderLabels(["Selection","Attribute", "Sample Instances"])
        self.dataSchemaTableView.insertRow(0)
        item = QTableWidgetItem()
        item.setText("Loading...")
        self.dataSchemaTableView.setItem(0,0,item)
        self.dataSchemaTableView.setMouseTracking(True)
        self.dataSchemaTableView.cellClicked.connect(self.loadSamples)
        self.dataSchemaTableView.cellEntered.connect(self.showURI)
        self.dataSchemaTableView.cellDoubleClicked.connect(self.openURL)
        self.okButton.clicked.connect(self.close)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf[self.curindex]), "DataSchemaDialog", Qgis.Info)
        self.getAttributeStatistics(self.concept,triplestoreurl)


    def queryAllInstances(self):
        querydepth=self.graphQueryDepthBox.value()
        if int(querydepth)>1:
            query=SPARQLUtils.expandRelValToAmount("SELECT ?" + " ?".join(self.triplestoreconf[self.curindex][
                                       "mandatoryvariables"]) + " ?rel ?val\n WHERE\n {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                self.concept) + ">  .\n " +
            self.triplestoreconf[self.curindex]["geotriplepattern"][0] + "\n ?item ?rel ?val . }",querydepth)
            self.qlayerinstance = QueryLayerTask(
            "Instance to Layer: " + str(self.concept),
            self.triplestoreconf[self.curindex]["endpoint"],
            query,
            self.triplestoreconf[self.curindex], False, SPARQLUtils.labelFromURI(self.concept), None)
        else:
            self.qlayerinstance = QueryLayerTask(
            "Instance to Layer: " + str(self.concept),
            self.triplestoreconf[self.curindex]["endpoint"],
            "SELECT ?" + " ?".join(self.triplestoreconf[self.curindex][
                                       "mandatoryvariables"]) + " ?rel ?val\n WHERE\n {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                self.concept) + "> .\n ?item ?rel ?val . " +
            self.triplestoreconf[self.curindex]["geotriplepattern"][0] + "\n }",
            self.triplestoreconf[self.curindex], False, SPARQLUtils.labelFromURI(self.concept), None)
        QgsApplication.taskManager().addTask(self.qlayerinstance)

    def openURL(self,row,column):
        if self.dataSchemaTableView.item(row,column)!=None:
            concept=str(self.dataSchemaTableView.item(row,column).data(256))
            if concept.startswith("http"):
                url = QUrl(concept)
                QDesktopServices.openUrl(url)

    def showURI(self,row,column):
        if self.dataSchemaTableView.item(row,column)!=None:
            concept=str(self.dataSchemaTableView.item(row,column).data(256))
            if concept.startswith("http"):
                self.statusBarLabel.setText(concept)

    def loadSamples(self,row,column):
        if column==2 and row not in self.alreadyloadedSample and row!=self.dataSchemaTableView.rowCount()-1:
            relation = str(self.dataSchemaTableView.item(row, column-1).data(256))
            self.qtask2 = DataSampleQueryTask("Querying dataset schema.... (" + self.label + ")",
                                             self.triplestoreurl,
                                             self,
                                             self.concept,
                                             relation,
                                             column,row,self.triplestoreconf[self.curindex])
            QgsApplication.taskManager().addTask(self.qtask2)
            self.alreadyloadedSample.append(row)
        elif row==self.dataSchemaTableView.rowCount()-1 and row not in self.alreadyloadedSample:
            relation = str(self.dataSchemaTableView.item(row, column-1).data(256))
            self.qtask3 = FindStyleQueryTask("Querying styles for dataset.... (" + self.label + ")",
                                             self.triplestoreurl,
                                             self,
                                             self.concept,
                                             column,row,self.triplestoreconf[self.curindex])
            QgsApplication.taskManager().addTask(self.qtask3)

    ##
    #  @brief Gives statistics about most commonly occuring properties from a certain class in a given triple store.
    #  
    #  @param [in] self The object pointer
    #  @return A list of properties with their occurance given in percent
    def getAttributeStatistics(self, concept="wd:Q3914", endpoint_url="https://query.wikidata.org/sparql"):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf[self.curindex]), "DataSchemaDialog", Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.curindex)+ " "+str(self.triplestoreconf[self.curindex]["endpoint"])), "DataSchemaDialog",
                                 Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf[self.curindex]["whattoenrichquery"]), "DataSchemaDialog",
                                 Qgis.Info)
        if self.concept == "" or self.concept is None or "whattoenrichquery" not in self.triplestoreconf[self.curindex]:
            return
        concept = "<" + self.concept + ">"
        progress = QProgressDialog("Querying dataset schema....", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        self.qtask = DataSchemaQueryTask("Querying dataset schema.... (" + self.label + ")",
                                           self.triplestoreurl,
                                           self.triplestoreconf[self.curindex][
                                               "whattoenrichquery"].replace("%%concept%%", concept),
                                           self.concept,
                                           self.prefixes[self.curindex],
                                           self.dataSchemaTableView,self.triplestoreconf[self.curindex], progress)
        QgsApplication.taskManager().addTask(self.qtask)
