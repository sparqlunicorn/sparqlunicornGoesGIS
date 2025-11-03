
import xml.etree.ElementTree as ET
import json

from .layerutils import LayerUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog


class InterlinkUtils:

    geoterms=["POINT","POLYGON","LINESTRING","LINE","BBOX","GEOMETRY"]
    geofieldnames=["GEOMETRY","X","Y","Z","THE_GEOM","GEO","LAT","LATITUDE","LON","LONG","LONGITUDE"]
    idfieldnames=["ID","IDENTIFIER"]
    labelfieldnames=["NAME","TITLE","LABEL"]
    descriptorfieldnames = ["DESCRIPTION", "COMMENT", "REMARK", "DEFINITION", "CONTENT","ABSTRACT"]
    subclassterms=["TYP","TYPE","SUB","CATEGORY"]

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
            name = layer.fields().names()[counter]
            if thetype["unique"]:
                idcols.add(name)
                thetype["id"]=True
                thetype["name"]=name
            columntypes.append(InterlinkUtils.checkTypeFromColumnName(name,thetype))
            counter+=1
        #QgsMessageLog.logMessage("IDCols: "+str(columntypes),"InterlinkUtils", Qgis.Info)
        #QgsMessageLog.logMessage("Columntypes: "+str(columntypes),"InterlinkUtils", Qgis.Info)
        return columntypes


    @staticmethod
    def suggestColumnURIs(layer,prefixes):
        columnprops=[]
        for name in layer.fields().names():
            if name=="id":
                columnprops.append("rdf:type")
            elif name.startswith("http:"):
                columnprops.append(name)
            elif ":" in name:
                splitted=name.split(":")
                if splitted[0] in prefixes:
                    columnprops.append(prefixes[splitted[0]]+splitted[1])
            else:
                columnprops.append("suni:"+name)
        return columnprops


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


    @staticmethod
    def constructStrIfListElemsExist(exists,map):
        #result=""
        #for obj in exists:
        #    if obj["key"] in map:
        #        result+=
        #return result
        return "".join(f'{obj.get("prefix")}{obj["key"]}{obj.get("suffix")}' for obj in exists if obj["key"] in map)

    @staticmethod
    def constructStrIfExists(exists,map,prefixstr="",suffixstr=""):
        if exists in map:
            return f"{prefixstr}{exists}{suffixstr}"
        return ""

    @staticmethod
    def exportMappingXML(mappingdict):
        xmlmappingheader = f'<?xml version=\"1.0\" ?>\n<data>\n<file class="{mappingdict.get("class")}" namespace="{mappingdict.get("namespace")}" indid="{mappingdict.get("indid")}">'
        xmlmapping = ""
        for row in mappingdict["columns"]:
            item = row
            xmlmapping += "<column "+InterlinkUtils.constructStrIfListElemsExist([{"key":"name","prefix":"name=\"","suffix":"\" "},
            {"key": "propiri", "prefix":"propiri=\"", "suffix":"\" "}, {"key": "concept", "prefix":"concept=\"", "suffix":"\" "},
            {"key": "query", "prefix":"query=\"", "suffix":"\" "}, {"key": "triplestoreurl", "prefix":"triplestoreurl=\"", "suffix":"\" "}],row)+">"
            if "valuemapping" in mappingdict:
                for key in mappingdict:
                    xmlmapping += f'<valuemapping from="{key}" to="{mappingdict["valuemapping"][key]}"/>\n'
            xmlmapping += "</column>\n"
        xmlmapping += "</file>\n</data>"
        return xmlmappingheader + ">\n" + xmlmapping

