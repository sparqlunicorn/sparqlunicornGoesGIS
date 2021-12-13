from qgis.PyQt.QtWidgets import QDialog, QMessageBox,QListWidgetItem, QTableWidgetItem
from qgis.PyQt import uic
from ..dialogs.searchdialog import SearchDialog
from ..util.sparqlhighlighter import SPARQLHighlighter
from ..util.sparqlutils import SPARQLUtils
import json
import requests
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/valuemappingdialog.ui'))


class ValueMappingDialog(QDialog, FORM_CLASS):
    currentrow = ""

    triplestoreconf = ""

    interlinkOrEnrich = False

    searchResultMap = {}

    table = False

    valmaptable = False

    fieldname = ""

    def __init__(self, column, row, triplestoreconf, interlinkOrEnrich, table, fieldname, layer, valuemap):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.currentcol = column
        self.currentrow = row
        self.table = table
        self.fieldname = fieldname
        self.triplestoreconf = triplestoreconf
        self.interlinkOrEnrich = interlinkOrEnrich
        self.valuemap = None
        if self.table.item(row, column) != None and self.table.item(row, column).data(1) != None:
            self.valuemap = json.loads(self.table.item(row, column).data(1))
            msgBox = QMessageBox()
            msgBox.setText(str(self.valuemap))
            msgBox.exec()
        self.queryedit.zoomIn(4)
        self.queryhighlight = SPARQLHighlighter(self.queryedit)
        if self.table.item(row, column) != None and self.table.item(row, column).data(2) != None and self.table.item(
                row, column).data(2) != "ValueMap{}":
            self.queryedit.setPlainText(self.table.item(row, column).data(2))
        else:
            self.queryedit.setPlainText("SELECT ?item\n WHERE {\n ?item ?rel %%" + fieldname + "%% . \n}")
        for triplestore in self.triplestoreconf:
            if not "File" == triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        while self.valmaptable.rowCount() > 0:
            self.valmaptable.removeRow(0);
        row = 0
        self.valmaptable.setColumnCount(2)
        self.valmaptable.setHorizontalHeaderLabels(["From", "To"])
        if self.valuemap != None:
            for key in self.valuemap:
                row = self.valmaptable.rowCount()
                self.valmaptable.insertRow(row)
                item = QTableWidgetItem(key)
                item2 = QTableWidgetItem(self.valuemap[key])
                self.valmaptable.setItem(row, 0, item)
                self.valmaptable.setItem(row, 1, item2)
        toaddset = {"All"}
        for f in layer.getFeatures():
            toaddset.add(f.attribute(fieldname))
        for item in toaddset:
            self.cbox.addItem(str(item))
        self.findMappingButton.clicked.connect(self.createValueMappingSearchDialog)
        self.addMappingButton.clicked.connect(self.addMappingToTable)
        self.deleteRowButton.clicked.connect(self.deleteSelectedRow)
        self.applyButton.clicked.connect(self.applyMapping)

    def addMappingToTable(self):
        if self.foundClass.text() != "":
            row = self.valmaptable.rowCount()
            self.valmaptable.insertRow(row)
            item = QTableWidgetItem(self.cbox.currentText())
            item2 = QTableWidgetItem(self.foundClass.text())
            self.valmaptable.setItem(row, 0, item)
            self.valmaptable.setItem(row, 1, item2)
            self.foundClass.setText("")

    def deleteSelectedRow(self):
        for index in self.valmaptable.selectedIndexes():
            self.valmaptable.removeRow(index.row())

    """Returns classes for a given label from a triple store."""

    def getClassesFromLabel(self, comboBox):
        viewlist = []
        resultlist = []
        label = self.conceptSearchEdit.text()
        language = "en"
        results = {}
        self.searchResult.clear()
        query = ""
        if self.currentcol == 4:
            if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["propertyfromlabelquery"].replace(
                    "%%label%%", label)
        else:
            if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["classfromlabelquery"].replace(
                    "%%label%%", label)
        if "SELECT" in query:
            query = query.replace("%%label%%", label).replace("%%language%%", language)
            results=SPARQLUtils.executeQuery(self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["endpoint"],query)
            self.searchResultMap = {}
            for res in results["results"]["bindings"]:
                item = QListWidgetItem()
                item.setData(0, str(res["class"]["value"]))
                item.setText(str(res["label"]["value"]))
                self.searchResultMap[res["label"]["value"]] = res["class"]["value"]
                self.searchResult.addItem(item)
        else:
            myResponse = json.loads(requests.get(query).text)
            for ent in myResponse["search"]:
                qid = ent["url"]
                label = ent["label"] + " (" + ent["id"] + ") "
                if "description" in ent:
                    label += "[" + ent["description"] + "]"
                results[qid] = label
                self.searchResultMap[label] = ent["url"]
            for result in results:
                item = QListWidgetItem()
                item.setData(0, result)
                item.setText(str(results[result]))
                self.searchResult.addItem(item)
        return viewlist

    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row, column, -1, self.foundClass)

    def buildSearchDialog(self, row, column, interlinkOrEnrich, table):
        self.currentcol = column
        self.currentrow = row
        self.interlinkdialog = SearchDialog(column, row, self.triplestoreconf, interlinkOrEnrich, table, True)
        self.interlinkdialog.setMinimumSize(650, 500)
        self.interlinkdialog.setWindowTitle("Search Property or Class")
        self.interlinkdialog.exec_()

    def applyMapping(self):
        resmap = {}
        for row in range(self.valmaptable.rowCount()):
            fromm = self.valmaptable.item(row, 0).text()
            to = self.valmaptable.item(row, 1).text()
            resmap[fromm] = to
        msgBox = QMessageBox()
        msgBox.setText(str(resmap))
        msgBox.exec()
        item = QTableWidgetItem("ValueMap{}")
        item.setData(1, str(json.dumps(resmap)))
        if "SELECT ?item\n WHERE {\n ?item ?rel %%" + self.fieldname + "%% . \n}" != self.queryedit.toPlainText():
            item.setData(2, self.queryedit.toPlainText())
            item.setData(3, self.tripleStoreEdit.currentText())
        self.table.setItem(self.currentrow, self.currentcol, item)
        self.close()
        return resmap
