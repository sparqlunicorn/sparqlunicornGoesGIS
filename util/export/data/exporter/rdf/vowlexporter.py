from rdflib import Graph, URIRef
from qgis.core import Qgis, QgsMessageLog
import json
from qgis.core import Qgis, QgsMessageLog

class OWL2VOWL():

    def __init__(self):
        print("init")

    @staticmethod
    def getTypeForProperty(prop,graph,typeproperty):
        for tup in graph.objects(URIRef(prop),URIRef(typeproperty)):
            #print(tup)
            if str(tup)!="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property":
                return OWL2VOWL.normalizeNS(str(tup))
        return "rdf:Property"

    @staticmethod
    def getBaseIRI(iri):
        if "#" in iri:
            return iri[0:iri.rfind("#")]
        return iri[0:iri.rfind("/")]

    @staticmethod
    def getIRILabel(iri):
        if "#" in iri:
            return iri[iri.rfind("#")+1:]
        return iri[iri.rfind("/")+1:]

    @staticmethod
    def normalizeNS(prop):
        return prop.replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdf:").replace("http://www.w3.org/2000/01/rdf-schema#","rdfs:").replace("http://www.w3.org/2002/07/owl#","owl:")

    #def inferDomainRanges(self,g,typeproperty):
    #    for subj in g.subjects():
    #        subjclasses=set()
    #        for tuppred in g.objects(subj,URIRef(typeproperty)):
    #            subjclasses.add(tuppred)

    @staticmethod
    def convertOWL2MiniVOWL(g,outpath,outfile=None,predicates=[],typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        minivowlresult={"info": [{
            "description": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin"}],
            "nodes": [],"links": []}
        nodes=[]
        nodeuriToId={}
        links=[]
        nodecounter=0
        for pred in g.subject_objects(URIRef(typeproperty)):
            if str(pred[1]) not in nodeuriToId:
                nodeuriToId[str(pred[1])]=nodecounter
                nodecounter+=1
                if str(pred[1])=="http://www.w3.org/2002/07/owl#Class" or str(pred[1])=="http://www.w3.org/2000/01/rdf-schema#Class" or str(pred[1])=="http://www.w3.org/2000/01/rdf-schema#Datatype":
                    nodes.append({"name":OWL2VOWL.getIRILabel(str(pred[1])),"type":"class","uri":str(pred[1])})
                else:
                    nodes.append({"name": OWL2VOWL.getIRILabel(str(pred[1])), "type": "class", "uri": str(pred[1])})
        if predicates!=[]:
            for pred in predicates:

                QgsMessageLog.logMessage(str(pred), "VOWL2OWL", Qgis.Info)
                if "from" in predicates[pred] and "to" in predicates[pred]:
                    QgsMessageLog.logMessage(str(predicates[pred]["from"]), "VOWL2OWL", Qgis.Info)
                    for fromsub in predicates[pred]["from"]:
                        if str(fromsub) in nodeuriToId:
                            if predicates[pred]["to"]!=[]:
                                for topred in predicates[pred]["to"]:
                                    if "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in str(topred) and "http://www.w3.org/2002/07/owl#" not in str(topred):
                                        links.append({"source": nodeuriToId[str(fromsub)],
                                                      "target": nodeuriToId[str(topred)],
                                                      "valueTo": OWL2VOWL.getIRILabel(str(pred)),
                                                      "propertyTo": "class",
                                                      "uriTo": str(pred)})
        else:
            for node in nodeuriToId:
                for predobj in g.predicate_objects(URIRef(node)):
                    if node in nodeuriToId and str(predobj[1]) in nodeuriToId and str(predobj[0])!=typeproperty:
                        links.append({"source":nodeuriToId[node],"target":nodeuriToId[str(predobj[1])],"valueTo": self.getIRILabel(str(predobj[0])),"propertyTo":("class" if isinstance(predobj[1],URIRef) else "datatype"), "uriTo":(str(predobj[1]) if isinstance(predobj[1],URIRef) else predobj[1].datatype)})
        minivowlresult["nodes"]=nodes
        minivowlresult["links"] = links
        f = open(outpath + "/"+str(outfile), "w")
        f.write("var minivowlresult=" + json.dumps(minivowlresult, indent=1))
        f.close()

    @staticmethod
    def convertOWL2VOWL(g,outpath,typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        vowlresult = {"_comment": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin",
                      "header": {"prefixList": {}, "baseIris": [], "languages": []}, "namespace": [], "class": [],
                      "classAttribute": [], "property": [], "propertyAttribute": []}
        props=[]
        propAttributes=[]
        classes=[]
        classAttributes=[]
        iriToProdId={}
        classiriToProdId={}
        propiriToProdId={}
        propidcounter=0
        classidcounter=0
        idcounter=0
        for nstup in g.namespaces():
            vowlresult["header"]["prefixList"][str(nstup[0])]=str(nstup[1])
            vowlresult["header"]["baseIris"].append(str(nstup[1]))
        for pred in g.subject_objects(URIRef(typeproperty)):
            #print(pred)
            iriToProdId[str(pred[0])]=idcounter
            if str(pred[1])=="http://www.w3.org/2002/07/owl#Class" or str(pred[1])=="http://www.w3.org/2000/01/rdf-schema#Class"  or str(pred[1])=="http://www.w3.org/2000/01/rdf-schema#Datatype":
                classes.append({"id":idcounter,"type":str(pred[1])})
                classiriToProdId[str(pred[0])]={"id":idcounter,"attid":len(classAttributes)-1}
                classAttributes.append({"id":idcounter,"iri":str(pred[0]),"baseIRI":OWL2VOWL.getBaseIRI(str(pred[0])),"instances":0,"label":{"IRI-based":OWL2VOWL.getIRILabel(str(pred[0]))},"annotations":{},"subClasses":[],"superClasses":[]})
                idcounter+=1
            else:
                props.append({"id":idcounter,"type":OWL2VOWL.getTypeForProperty(str(pred[0]),g,typeproperty)})
                propiriToProdId[str(pred[0])]={"id":idcounter,"attid":len(propAttributes)-1}
                propAttributes.append({"id":idcounter,"iri":str(pred[0]),"baseIRI":OWL2VOWL.getBaseIRI(str(pred[0])),"instances":0,"label":{"IRI-based":OWL2VOWL.getIRILabel(str(pred[0]))},"annotations":{},"range":[],"domain":[],"subProperties":[],"superProperties":[]})
                idcounter+=1

        for pred in g.subject_objects(URIRef("http://www.w3.org/2000/01/rdf-schema#range")):
            print(pred)
            if str(pred[1]) not in classiriToProdId:
                classes.append({"id":idcounter,"type":"http://www.w3.org/2000/01/rdf-schema#Datatype"})
                classiriToProdId[str(pred[1])]={"id":idcounter,"attid":len(classAttributes)-1}
                classAttributes.append({"id":idcounter,"iri":str(pred[1]),"baseIRI":OWL2VOWL.getBaseIRI(str(pred)),"instances":0,"label":{"IRI-based":OWL2VOWL.getIRILabel(str(pred[1]))},"annotations":{},"subClasses":[],"superClasses":[]})
                idcounter+=1

        for iri in classiriToProdId:
            #print(iri)
            for clsatt in g.predicate_objects(URIRef(iri)):
                #print(clsatt)
                if clsatt[0]!=URIRef(typeproperty):
                    if clsatt[0]==URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"):
                        if str(clsatt[1]) in classiriToProdId:
                            classAttributes[classiriToProdId[iri]["attid"]]["superClasses"].append(str(classiriToProdId[str(clsatt[1])]["id"]))
                            classAttributes[classiriToProdId[str(clsatt[1])]["attid"]]["subClasses"].append(str(classiriToProdId[iri]["id"]))
                    elif clsatt[0]==URIRef(labelproperty):
                        classAttributes[classiriToProdId[iri]["attid"]]["label"]=str(clsatt[1])
                    else:
                        classAttributes[classiriToProdId[iri]["attid"]]["annotations"][str(clsatt[0])]=[]
                        if str(clsatt[1]).startswith("http"):
                            classAttributes[classiriToProdId[iri]["attid"]]["annotations"][str(clsatt[0])].append({"identifier":str(clsatt[0]),"language":"undefined","value":str(clsatt[1]),"type":"iri"})
                        else:
                            classAttributes[classiriToProdId[iri]["attid"]]["annotations"][str(clsatt[0])].append({"identifier":str(clsatt[0]),"language":"undefined","value":str(clsatt[1]),"type":"label"})

        for iri in propiriToProdId:
            #print(iri)
            for propatt in g.predicate_objects(URIRef(iri)):
                #print(propatt)
                if propatt[0]!=URIRef(typeproperty):
                    if propatt[0]==URIRef("http://www.w3.org/2000/01/rdf-schema#subPropertyOf"):
                        if str(propatt[1]) in propiriToProdId:
                            propAttributes[propiriToProdId[iri]["attid"]]["superProperties"].append(str(propiriToProdId[str(propatt[1])]["id"]))
                            propAttributes[propiriToProdId[str(propatt[1])]["attid"]]["subProperties"].append(str(propiriToProdId[iri]["id"]))
                    elif propatt[0]==URIRef("http://www.w3.org/2000/01/rdf-schema#range") and str(propatt[1]) in propiriToProdId:
                        propAttributes[propiriToProdId[iri]["attid"]]["range"].append(str(classiriToProdId[str(propatt[1])]["id"]))
                    elif propatt[0]==URIRef("http://www.w3.org/2000/01/rdf-schema#domain") and str(propatt[1]) in propiriToProdId:
                        propAttributes[propiriToProdId[iri]["attid"]]["domain"].append(str(classiriToProdId[str(propatt[1])]["id"]))
                    elif propatt[0]==URIRef(labelproperty):
                        propAttributes[propiriToProdId[iri]["attid"]]["label"]=str(propatt[1])
                    else:
                        propAttributes[propiriToProdId[iri]["attid"]]["annotations"][str(propatt[0])]=[]
                        if str(propatt[1]).startswith("http"):
                            propAttributes[propiriToProdId[iri]["attid"]]["annotations"][str(propatt[0])].append({"identifier":str(propatt[0]),"language":"undefined","value":str(propatt[1]),"type":"iri"})
                        else:
                            propAttributes[propiriToProdId[iri]["attid"]]["annotations"][str(propatt[0])].append({"identifier":str(propatt[0]),"language":"undefined","value":str(propatt[1]),"type":"label"})

        vowlresult["property"]=props
        vowlresult["propertyAttribute"]=propAttributes
        vowlresult["class"]=classes
        vowlresult["classAttribute"]=classAttributes
        f=open(outpath+"/vowl_result.js","w")
        f.write("var vowlresult="+json.dumps(vowlresult,indent=1))
        f.close()
