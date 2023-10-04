from ...util.doc.ontdocgeneration import OntDocGeneration
from ...util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsTask
from rdflib import Graph

MESSAGE_CATEGORY = 'OntDocTask'

class OntDocTask(QgsTask):

    def __init__(self, description, graphname, namespace,prefixes,license,labellang,outpath,createcollections,baselayers,tobeaddedperInd,maincolor,titlecolor, progress,createIndexPages,nonNSPagesCBox,createMetadataTable,createVOWL,ogcapifeatures,iiif,ckan,startconcept,deploymenturl,logopath="",offlinecompat=False,exports=["ttl","json"]):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.prefixes=prefixes
        self.tobeaddedperInd=tobeaddedperInd
        self.baselayers=baselayers
        self.license=license
        self.deploymenturl=deploymenturl
        self.startconcept=startconcept
        self.offlinecompat=offlinecompat
        self.exports=exports
        self.ogcapifeatures=ogcapifeatures
        self.iiif=iiif
        self.ckan=ckan
        self.createVOWL=createVOWL
        self.createMetadataTable=createMetadataTable
        self.nonNSPagesCBox=nonNSPagesCBox
        self.labellang=labellang
        self.createIndexPages=createIndexPages
        self.createcollections=createcollections
        self.maincolor=maincolor
        self.logopath=logopath
        self.titlecolor=titlecolor
        self.graphname=graphname
        self.namespace=namespace
        self.outpath=outpath

    def run(self):
        QgsMessageLog.logMessage("Graph "+str(self.graphname), MESSAGE_CATEGORY, Qgis.Info)
        if isinstance(self.graphname,str):
            self.graph=SPARQLUtils.loadGraph(self.graphname)
        else:
            self.graph=Graph()
            for file in self.graphname:
                SPARQLUtils.loadGraph(file,self.graph)
        QgsMessageLog.logMessage("Graph "+str(self.graph), MESSAGE_CATEGORY, Qgis.Info)
        nsshort=""
        if self.namespace in self.prefixes["reversed"]:
            nsshort=self.prefixes["reversed"][self.namespace]
        elif self.namespace.endswith("/"):
            nsshort=self.namespace[self.namespace[0:-1].rfind('/') + 1:]
        else:
            nsshort=self.namespace[self.namespace.rfind('/') + 1:]
        #try:
        ontdoc=OntDocGeneration(self.prefixes, self.namespace, nsshort,self.license,self.labellang, self.outpath, self.graph,self.createcollections,self.baselayers,self.tobeaddedperInd,self.maincolor,self.titlecolor,self.progress,self.createIndexPages,self.nonNSPagesCBox,self.createMetadataTable,self.createVOWL,self.ogcapifeatures,self.iiif,self.ckan,self.startconcept,self.deploymenturl,self.logopath,self.offlinecompat,self.exports)
        ontdoc.generateOntDocForNameSpace(self.namespace)
        #except Exception as e:
        #    self.exception=e
        #    return False
        return True

    def finished(self, result):
        self.progress.close()
        if result == True:
            msgBox = QMessageBox()
            msgBox.setText("Ontology documentation finished in folder "+str(self.outpath))
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            if self.exception!=None:
                msgBox.setText("Ontology documentation failed!\n"+str(self.exception))
            else:
                msgBox.setText("Ontology documentation failed!")
            msgBox.exec()
