
import xml.etree.ElementTree as ET
import json

from .layerutils import LayerUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog


class InterlinkUtils:

    geoterms=["POINT","POLYGON","LINESTRING","LINE","BBOX","GEOMETRY"]
    geofieldnames=["GEOMETRY","X","Y","Z","LAT","LATITUDE","LON","LONG","LONGITUDE"]
    idfieldnames=["ID"]
    labelfieldnames=["NAME","TITLE","LABEL"]
    descriptorfieldnames = ["DESCRIPTION", "COMMENT", "REMARK", "DEFINITION", "CONTENT","ABSTRACT"]
    subclassterms=["TYPE","SUB"]

    @staticmethod
    def readXMLMappingToDict(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        filedata = root.find('file')[0]
        result={"namespace":filedata.get("namespace"),"class":filedata.get("class"),"column":[]}
        for neighbor in root.iter('column'):
            col={"valuemappings":{},"name":neighbor.get("name"),"proptype":neighbor.get("prop"),"propiri":neighbor.get("propiri"),"concept":neighbor.get("concept"),"query":neighbor.get("query"),"triplestoreurl":neighbor.get("triplestoreurl")}
            for vmap in neighbor.findall("valuemapping"):
                col["valuemappings"][vmap.get("from")] = vmap.get("to")
        return result

    @staticmethod
    def readJSONMappingToDict(filename):
        result=json.loads(filename,encoding="utf-8")
        return result


    @staticmethod
    def suggestMappingSchema(layer):
        print("Suggest mapping schema based on data")
        columntypes=[]
        counter=0
        idcols=set()
        for column in layer.fields().names():
            thetype=LayerUtils.detectLayerColumnType(layer,counter)
            if thetype["unique"]:
                idcols.add(layer.fields().names()[counter])
                thetype["id"]=True
            columntypes.append(InterlinkUtils.checkTypeFromColumnName(layer.fields().names()[counter],thetype))
            counter+=1
        #QgsMessageLog.logMessage("IDCols: "+str(columntypes),"InterlinkUtils", Qgis.Info)
        #QgsMessageLog.logMessage("Columntypes: "+str(columntypes),"InterlinkUtils", Qgis.Info)
        return columntypes

    @staticmethod
    def checkTypeFromColumnName(fieldname,columntype):
        if columntype["xsdtype"]=="xsd:double":
            for term in InterlinkUtils.geoterms:
                if term in str(fieldname).upper():
                    columntype["geotype"]=True
                    columntype["id"]=False
        if columntype["xsdtype"]=="xsd:string":
            for term in InterlinkUtils.subclassterms:
                if term in str(fieldname).upper():
                    columntype["xsdtype"]="owl:Class"
                    columntype["id"]=False
            for term in InterlinkUtils.labelfieldnames:
                if term in str(fieldname).upper():
                    columntype["xsdtype"]="ct:LabelProperty"
                    columntype["id"]=False
            for term in InterlinkUtils.descriptorfieldnames:
                if term in str(fieldname).upper():
                    columntype["xsdtype"]="ct:DescriptionProperty"
                    columntype["id"]=False
        if "geotype" not in columntype:
            columntype["geotype"]=False
        return columntype

    def suggestMostProbableID(self, layer):
        fieldmapping = {}
        for field in layer.fields().names():
            if field.startswith("http"):
                fieldmapping[field] = field

    def suggestFieldNameMappings(self, layer):
        fieldmapping = {}
        for field in layer.fields().names():
            if field.startswith("http"):
                fieldmapping[field] = field


    @staticmethod
    def constructStrIfListElemsExist(exists,map):
        result=""
        for obj in exists:
            if obj["key"] in map:
                result+=str(obj.get("prefix"))+str(obj["key"])+str(obj.get("suffix"))
        return result

    @staticmethod
    def constructStrIfExists(exists,map,prefixstr="",suffixstr=""):
        if exists in map:
            return str(prefixstr)+str(exists)+str(suffixstr)
        return ""

    @staticmethod
    def exportMappingXML(mappingdict):
        xmlmappingheader = "<?xml version=\"1.0\" ?>\n<data>\n<file "
        xmlmapping = ""
        xmlmappingheader += "class=\"" + str(mappingdict.get("class")) + "\" "
        xmlmappingheader += "namespace=\"" + str(mappingdict.get("namespace")) + "\" "
        xmlmappingheader += "indid=\"" + str(mappingdict.get("indid")) + "\" >"
        for row in mappingdict["column"]:
            item = row
            if item.checkState():
                xmlmapping += "<column "+InterlinkUtils.constructStrIfListElemsExist([{"key":"name","prefix":"name=\"","suffix":"\" "},
                {"key": "propiri", "prefix":"propiri=\"", "suffix":"\" "}, {"key": "concept", "prefix":"concept=\"", "suffix":"\" "},
                {"key": "query", "prefix":"query=\"", "suffix":"\" "}, {"key": "triplestoreurl", "prefix":"triplestoreurl=\"", "suffix":"\" "}],row)+">"
                if "valuemapping" in mappingdict:
                    for key in mappingdict:
                        xmlmapping += "<valuemapping from=\"" + key + "\" to=\"" + mappingdict["valuemapping"][key] + "\"/>\n"
                xmlmapping += "</column>\n"
        xmlmapping += "</file>\n</data>"
        return xmlmappingheader + ">\n" + xmlmapping

