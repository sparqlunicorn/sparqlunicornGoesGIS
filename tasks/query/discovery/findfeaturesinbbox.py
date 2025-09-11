from qgis.core import Qgis

from ....util.layerutils import LayerUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.core import QgsProject,QgsTask, QgsMessageLog

MESSAGE_CATEGORY="FindFeatureInBBOXTask"
class FindFeaturesInBBOXTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,bbox,fromcrs,triplestoreconf):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreconf=triplestoreconf
        self.triplestoreurl=triplestoreurl
        self.dlg=dlg
        self.treeNode=bbox
        self.amount=-1
        self.thequery=""
        bbox=LayerUtils.reprojectGeometry(bbox,fromcrs)
        QgsMessageLog.logMessage("Finished query " + str(self.triplestoreconf), MESSAGE_CATEGORY, Qgis.Info)
        if "bboxquery" in triplestoreconf:
            self.thequery=f"SELECT ?item ?itemLabel ?geo WHERE {{ ?item <http://www.w3.org/2000/01/rdf-schema#label> ?itemLabel . FILTER(lang(?itemLabel)=\"en\")\n"+triplestoreconf["bboxquery"]["query"].replace("%%minPoint%%","Point("+str(bbox.boundingBox().xMinimum())+" "+str(bbox.boundingBox().yMinimum())+")").replace("%%maxPoint%%","Point("+str(bbox.boundingBox().xMaximum())+" "+str(bbox.boundingBox().yMaximum())+")")+"\n}"
        QgsMessageLog.logMessage("The Query " + str(self.thequery), MESSAGE_CATEGORY, Qgis.Info)
        self.thequery=SPARQLUtils.queryPreProcessing(self.thequery,self.triplestoreconf)

    def run(self):
        self.results = SPARQLUtils.executeQuery(self.triplestoreurl,self.thequery,self.triplestoreconf)
        #SPARQLUtils.handleException(MESSAGE_CATEGORY)
        return True

    def finished(self, result):
        QgsMessageLog.logMessage("Finished query "+str(self.results), MESSAGE_CATEGORY, Qgis.Info)