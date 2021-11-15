from ..util.sparqlutils import SPARQLUtils
from ..util.layerutils import LayerUtils
from qgis.PyQt.QtCore import QVariant
from qgis.core import Qgis, QgsField
from qgis.PyQt.QtWidgets import QMessageBox, QTableWidgetItem
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'EnrichmentQueryTask'


## Executes an enrichment task on a given layer with a given configuration.
class EnrichmentQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, layer, strategy, language, row, originalRowCount, item, table,
                 resulttable, idfield, idprop, propertyy, content, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.labels = None
        self.row = row
        self.propertyy = propertyy
        self.content = content
        self.item = item
        self.table = table
        self.resulttable = resulttable
        self.idfield = idfield
        self.idprop = idprop
        self.originalRowCount = originalRowCount
        self.progress = progress
        self.language = language
        self.strategy = strategy
        self.layer = layer
        self.columntype = QVariant.String
        self.urilist = None
        self.sortedatt = None
        self.resultmap = {}
        self.results = None

    ## Executes the enrichment task.
    # @param self The object pointer
    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        attlist = {}
        attlist[self.item] = []
        attlist[self.idfield] = {}
        query = ""
        for f in self.layer.getFeatures():
            if self.item in f:
                attlist[self.item].append(f[self.item])
            attlist[self.idfield][f[self.idfield]] = True
            query = ""
            if self.content == "Enrich URI":
                query += "SELECT ?item WHERE {\n"
            elif self.content == "Enrich Value" or self.strategy == "Enrich Both":
                query += "SELECT ?item ?val ?valLabel ?vals WHERE {\n"
            query += "VALUES ?vals { "
            print(attlist)
        for it in attlist[self.idfield]:
            if str(it).startswith("http"):
                query += "<" + str(it) + "> "
            elif self.idprop == "http://www.w3.org/2000/01/rdf-schema#label" and self.language != None and self.language != "":
                query += "\"" + str(it) + "\"@" + self.language + " "
            else:
                query += "\"" + str(it) + "\" "
        query += " } . \n"
        proppp = self.propertyy.data(1)
        if self.propertyy.data(1).startswith("//"):
            proppp = "http:" + proppp
        if self.table.item(self.row, 7).text() != "" and "wikidata" in self.triplestoreurl:
            query += "?item wdt:P31 <" + self.table.item(self.row, 7).text() + "> .\n"
        else:
            query += "?item rdf:type <" + self.table.item(self.row, 7).text() + "> .\n"
        query += "?item <" + self.idprop + "> ?vals .\n"
        query += "?item <" + proppp + "> ?val . \n"
        if (self.content == "Enrich Value" or self.content == "Enrich Both") and not "wikidata" in self.triplestoreurl:
            query += "OPTIONAL{ ?val rdfs:label ?valLabel }"
        elif (self.content == "Enrich Value" or self.content == "Enrich Both") and "wikidata" in self.triplestoreurl:
            query += "SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE]," + self.language + "\". }\n"
        query += "} "
        QgsMessageLog.logMessage("proppp: " + str(proppp),
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage("idprop: " + self.idprop,
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(query,
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(self.triplestoreurl,
                                 MESSAGE_CATEGORY, Qgis.Info)
        print(self.triplestoreurl)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,query)
        if results==False:
            return False
        print(str(results))
        # resultcounter=0
        for resultcounter in results["results"]["bindings"]:
            if self.content == "Enrich Value":
                self.resultmap[resultcounter["vals"]["value"]] = resultcounter["valLabel"]["value"]
            elif self.content == "Enrich URI":
                self.resultmap[resultcounter["vals"]["value"]] = resultcounter["val"]["value"]
            else:
                self.resultmap[resultcounter["vals"]["value"]] = resultcounter["valLabel"]["value"] + ";" + \
                                                                 resultcounter["val"]["value"]
        self.columntype = LayerUtils.detectColumnType(self.resultmap)
        QgsMessageLog.logMessage(str(self.columntype),
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(str(self.resultmap),
                                 MESSAGE_CATEGORY, Qgis.Info)
        return True

    ## Writes the result of the enrichment task to the result table in the main view.
    # @param self The object pointer
    # @param result the result indicator of the calculation
    def finished(self, result):
        QgsMessageLog.logMessage("Finished",
                                 MESSAGE_CATEGORY, Qgis.Info)
        rowww = 0
        if self.row >= self.originalRowCount:
            self.layer.dataProvider().addAttributes([QgsField(self.item, self.columntype)])
            self.layer.updateFields()
        fieldnames = [field.name() for field in self.layer.fields()]
        for f in self.layer.getFeatures():
            if rowww >= self.resulttable.rowCount():
                self.resulttable.insertRow(rowww)
            if f[self.idfield] in self.resultmap:
                QgsMessageLog.logMessage(str(f[self.idfield]) + " - " + str(self.resultmap[f[self.idfield]]),
                                         MESSAGE_CATEGORY, Qgis.Info)
                if self.strategy == "Merge":
                    newitem = QTableWidgetItem(str(f[self.item]) + str(self.resultmap[f[self.idfield]]))
                elif self.strategy == "Keep Local":
                    if f[self.item] == None:
                        newitem = QTableWidgetItem(str(self.resultmap[f[self.idfield]]))
                    else:
                        newitem = QTableWidgetItem(str(f[self.item]))
                elif self.strategy == "Ask User":
                    newitem = QTableWidgetItem(str(f[self.item]) + ";" + str(self.resultmap[f[self.idfield]]))
                elif self.strategy == "Keep Remote":
                    if not f[self.idfield] in self.resultmap or self.resultmap[f[self.idfield]] == None:
                        newitem = QTableWidgetItem(str(f[self.item]))
                    else:
                        newitem = QTableWidgetItem(str(self.resultmap[f[self.idfield]]))
                else:
                    newitem = QTableWidgetItem(str(self.resultmap[f[self.idfield]]))
                QgsMessageLog.logMessage(str(rowww) + " - " + str(self.row) + " - " + str(newitem), MESSAGE_CATEGORY,
                                         Qgis.Info)
                self.resulttable.setItem(rowww, self.row, newitem)
            rowww += 1
        self.layer.commitChanges()
        self.progress.close()
