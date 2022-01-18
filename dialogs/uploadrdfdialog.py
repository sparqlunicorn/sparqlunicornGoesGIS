from qgis.PyQt.QtWidgets import QDialog, QCompleter,QMessageBox, QProgressDialog
from qgis.core import QgsProject, QgsApplication
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QRegExp, Qt
from qgis.PyQt.QtGui import QRegExpValidator, QValidator

from ..util.ui.uiutils import UIUtils
from ..tasks.detecttriplestoretask import DetectTripleStoreTask
from SPARQLWrapper import SPARQLWrapper, BASIC
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/uploadrdfdialog.ui'))


## Dialog to upload a generated RDF result to a triple store.
class UploadRDFDialog(QDialog, FORM_CLASS):
    currentrow = ""

    triplestoreconf = ""

    interlinkOrEnrich = False

    searchResultMap = {}

    table = False

    valmaptable = False

    fieldname = ""

    def __init__(self, ttlstring, triplestoreconf, currentindex):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.ttlstring = ttlstring
        if "endpoint" in triplestoreconf[currentindex]:
            self.tripleStoreURLEdit.setText(triplestoreconf[currentindex]["endpoint"])
        self.tripleStoreURLEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.tripleStoreURLEdit.textChanged.connect(lambda: UIUtils.check_state(self.tripleStoreURLEdit))
        self.tripleStoreURLEdit.textChanged.emit(self.tripleStoreURLEdit.text())
        layers = QgsProject.instance().layerTreeRoot().children()
        # Populate the comboBox with names of all the loaded unicorn layers
        self.loadedLayers.clear()
        for layer in layers:
            ucl = layer.name()
            self.loadedLayers.add(ucl)
        endpointurls = []
        for item in triplestoreconf:
            endpointurls.append(item["endpoint"])
        self.tripleStoreURLEdit.setCompleter(QCompleter(endpointurls))
        self.checkConnectionButton.clicked.connect(self.checkConnection)
        self.applyButton.clicked.connect(self.addNewLayerToTripleStore)

    ## 
    #  @brief Checks the connection to a triple store which has been defined by a given internet address.
    #  
    #  @param self The object pointer
    #  @return True if the connection was successful, false otherwise 
    def checkConnection(self, calledfromotherfunction=False, showMessageBox=True,
                        query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1"):
        progress = QProgressDialog("Checking connection to triple store " + self.tripleStoreURLEdit.text() + "...",
                                   "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        self.qtask = DetectTripleStoreTask(
            "Checking connection to triple store " + self.tripleStoreURLEdit.text() + "...", self.triplestoreconf,
            self.tripleStoreURLEdit.text(), self.tripleStoreURLEdit.text(), True, False, [], {}, None, None, False,
            None, progress)
        QgsApplication.taskManager().addTask(self.qtask)

    def compareLayers(layer1, layer2, idcolumn):
        changedTriples = ""
        fieldnames = [field.name() for field in layer.fields()]
        for f in layer1.getFeatures():
            geom = f.geometry()
            id = f[idcolumn]
            expr = QgsExpression("\"" + idcolumn + "\"=" + id)
            it = cLayer.getFeatures(QgsFeatureRequest(expr))
            # if len(it)==0:
            # Add new line
            # elif len(it)>0:
            # Compare

    ## Adds a new QGIS layer to a triplestore with a given address.
    #  @param self The object pointer.
    #  @param triplestoreaddress The address of the triple store
    #  @param layer The layer to add
    def addNewLayerToTripleStore(self):
        # ttlstring=self.layerToTTLString(layer)
        queryString = "INSERT DATA { GRAPH <http://example.com/> { " + self.ttlstring + " } }"
        sparql = SPARQLWrapper(self.tripleStoreURLEdit.text())
        sparql.setHTTPAuth(BASIC)
        if self.usernameEdit.text() != "" and self.passwordEdit.text() != "":
            sparql.setCredentials(self.usernameEdit.text(), self.passwordEdit.text())
        sparql.setQuery(queryString)
        sparql.method = 'POST'
        results = sparql.query()
        msgBox = QMessageBox()
        msgBox.setWindowTitle("SPARQL UPDATE Status")
        msgBox.setText(str(results.response.read()))
        msgBox.exec()
