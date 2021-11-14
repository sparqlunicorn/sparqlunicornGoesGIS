from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from styleobject import StyleObject

class StyleUtils:

    @staticmethod
    def convertRDFStyleToSLD(results):
        curStyleObject=StyleObject()
        for result in results["results"]["bindings"]:
            if "style" in result:
                curStyleObject.styleId=result["style"]
        return True