from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from .styleobject import StyleObject
from .sparqlutils import SPARQLUtils
from qgis.core import Qgis

MESSAGE_CATEGORY="Style Utils"

class StyleUtils:

    @staticmethod
    def convertRDFStyleToSLD(results):
        curStyleObject=StyleObject()
        for result in results["results"]["bindings"]:
            if "style" in result:
                curStyleObject.styleId=result["style"]
        return True

    @staticmethod
    def queryStyleByURI(con,triplestoreurl,triplestoreconf,styleuri):
        if isinstance(styleuri,list):
            styleuri=styleuri[0]
        thequery="SELECT ?style ?pointstyle ?polygonstyle ?linestyle ?img ?linestringImageStyle ?lineStringImage ?hatch WHERE { <"+str(con)+"> <http://www.opengis.net/ont/geosparql#style> ?style .\n "+ \
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#pointStyle> ?pointstyle. }\n"+\
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#linestringStyle> ?linestyle. }\n"+\
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#polygonStyle> ?polygonstyle. }\n"+\
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#image> ?img. }\n"+\
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#linestringImageStyle> ?linestringImageStyle. }\n"+\
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#linestringImage> ?linestringImage. }\n"+\
                     "OPTIONAL { ?style <http://www.opengis.net/ont/geosparql/style#hatch>  ?hatch. }\n"+\
                     "}"
        QgsMessageLog.logMessage("Query results: " + str(thequery).replace("<","").replace(">",""), MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(triplestoreurl,thequery,triplestoreconf)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        resultstyle=StyleObject()
        for result in results["results"]["bindings"]:
            if "style" in result:
                resultstyle.styleId=result["style"]["value"]
            if "pointstyle" in result:
                resultstyle.pointStyle=result["pointstyle"]["value"]
            if "img" in result:
                resultstyle.pointImage=result["img"]["value"]
            if "linestyle" in result:
                resultstyle.lineStringStyle=result["linestyle"]["value"]
            if "linestringImage" in result:
                resultstyle.lineStringImage=result["linestringImage"]["value"]
            if "polygonstyle" in result:
                resultstyle.polygonStyle=result["polygonstyle"]["value"]
            if "hatch" in result:
                resultstyle.hatch=result["hatch"]["value"]
        return resultstyle
