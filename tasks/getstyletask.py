from ..util.sparqlutils import SPARQLUtils
from ..util.styleobject import StyleObject
from qgis.core import Qgis
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'GetStyleQueryTask'

class GetStyleQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,styleuri=None,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.dlg=dlg
        self.styleuri=styleuri
        self.graph=graph
        self.treeNode=treeNode
        self.amount=-1

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        thequery=""
        if "wikidata" in self.triplestoreurl:
            wikicon=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            thequery="SELECT ?style ?pointstyle ?polygonstyle ?linestyle ?img ?linestringImageStyle ?lineStringImage ?hatch WHERE { <http://www.wikidata.org/entity/"+str(wikicon)+"> geo:style <"+str(self.styleuri)+"> . "+ \
                     "OPTIONAL {?style geost:pointStyle ?pointstyle. }\n"+\
                     "OPTIONAL { ?style geost:linestringStyle ?linestyle. }\n"+\
                     "OPTIONAL { ?style geost: polygonStyle ?polygonstyle. }\n"+\
                     "OPTIONAL { ?style geost:image ?img. }\n"+\
                     "OPTIONAL { ?style geost:linestringImageStyle ?linestringImageStyle. }\n"+\
                     "OPTIONAL { ?style geost:linestringImage ?linestringImage. }\n"+\
                     "OPTIONAL { ?style geost:hatch  ?hatch. }\n"+\
                     "}"
        else:
            con=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            thequery="SELECT ?style ?pointstyle ?polygonstyle ?linestyle ?img ?linestringImageStyle ?lineStringImage ?hatch WHERE { <http://www.wikidata.org/entity/"+str(con)+"> geo:style <"+str(self.styleuri)+"> . "+ \
                     "OPTIONAL {?style geost:pointStyle ?pointstyle. }\n"+\
                     "OPTIONAL { ?style geost:linestringStyle ?linestyle. }\n"+\
                     "OPTIONAL { ?style geost:polygonStyle ?polygonstyle. }\n"+\
                     "OPTIONAL { ?style geost:image ?img. }\n"+\
                     "OPTIONAL { ?style geost:linestringImageStyle ?linestringImageStyle. }\n"+\
                     "OPTIONAL { ?style geost:linestringImage ?linestringImage. }\n"+\
                     "OPTIONAL { ?style geost:hatch  ?hatch. }\n"+\
                     "}"
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        else:
            results=self.graph.query(thequery)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        self.resultstyles=[]
        self.resultstyles.append(StyleObject())
        resstylecounter=0
        for result in results["results"]["bindings"]:
            if "style" in result:
                self.resultstyles[resstylecounter].styleId=result["style"]["value"]
            if "pointstyle" in result:
                self.resultstyles[resstylecounter].pointStyle=result["pointstyle"]["value"]
            if "img" in result:
                self.resultstyles[resstylecounter].pointImage=result["img"]["value"]
            if "linestyle" in result:
                self.resultstyles[resstylecounter].lineStringStyle=result["linestyle"]["value"]
            if "linestringImage" in result:
                self.resultstyles[resstylecounter].lineStringImage=result["linestringImage"]["value"]
            if "polygonstyle" in result:
                self.resultstyles[resstylecounter].polygonStyle=result["polygonstyle"]["value"]
            if "hatch" in result:
                self.resultstyles[resstylecounter].hatch=result["hatch"]["value"]
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.resultstyles)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.resultstyles[0].toSLD(""))+"]"), MESSAGE_CATEGORY, Qgis.Info)

