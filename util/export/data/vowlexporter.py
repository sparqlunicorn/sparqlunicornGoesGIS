from rdflib import Graph, URIRef
from rdflib.namespace import RDFS,OWL,RDF
from qgis.core import Qgis, QgsMessageLog
import json

class VOWLExporter:

    def __init__(self):
        print("init")

    @staticmethod
    def getTypeForProperty(prop, graph, typeproperty):
        for tup in graph.objects(URIRef(prop), URIRef(typeproperty)):
            # print(tup)
            if str(tup) != "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property":
                return VOWLExporter.normalizeNS(str(tup))
        return "rdf:Property"

    @staticmethod
    def getBaseIRI(iri):
        if "#" in iri:
            return iri[0:iri.rfind("#")]
        return iri[0:iri.rfind("/")]

    @staticmethod
    def getIRILabel(iri):
        if "#" in iri:
            return iri[iri.rfind("#") + 1:]
        return iri[iri.rfind("/") + 1:]

    @staticmethod
    def normalizeNS(prop):
        return prop.replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:").replace(
            "http://www.w3.org/2000/01/rdf-schema#", "rdfs:").replace("http://www.w3.org/2002/07/owl#", "owl:")

    # def inferDomainRanges(self,g,typeproperty):
    #    for subj in g.subjects():
    #        subjclasses=set()
    #        for tuppred in g.objects(subj,URIRef(typeproperty)):
    #            subjclasses.add(tuppred)

    @staticmethod
    def convertOWL2MiniVOWL(g, outpath, outfile=None, predicates=[],
                            typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                            labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        minivowlresult = {"info": [{
            "description": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin"}],
            "nodes": [], "links": []}
        nodes = []
        nodeuriToId = {}
        links = []
        nodecounter = 0
        for pred in g.subject_objects(URIRef(typeproperty)):
            predstr = str(pred[1])
            if predstr not in nodeuriToId:
                nodeuriToId[predstr] = nodecounter
                nodecounter += 1
                if pred[1] == OWL.Class or pred[1] == RDFS.Class or pred[1] == RDFS.Datatype:
                    nodes.append({"name": VOWLExporter.getIRILabel(predstr), "type": "class", "uri": predstr})
                else:
                    nodes.append({"name": VOWLExporter.getIRILabel(predstr), "type": "class", "uri": predstr})
        if predicates:
            for pred in predicates:
                if "from" in predicates[pred] and "to" in predicates[pred]:
                    for fromsub in predicates[pred]["from"]:
                        if str(fromsub) in nodeuriToId:
                            if predicates[pred]["to"] != []:
                                for topred in predicates[pred]["to"]:
                                    if "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in str(
                                            topred) and "http://www.w3.org/2002/07/owl#" not in str(topred):
                                        links.append({"source": nodeuriToId[str(fromsub)],
                                                      "target": nodeuriToId[str(topred)],
                                                      "valueTo": VOWLExporter.getIRILabel(str(pred)),
                                                      "propertyTo": "class",
                                                      "uriTo": str(pred)})
        else:
            for node in nodeuriToId:
                for predobj in g.predicate_objects(URIRef(node)):
                    if node in nodeuriToId and str(predobj[1]) in nodeuriToId and str(predobj[0]) != typeproperty:
                        links.append({"source": nodeuriToId[node], "target": nodeuriToId[str(predobj[1])],
                                      "valueTo": VOWLExporter.getIRILabel(str(predobj[0])),
                                      "propertyTo": ("class" if isinstance(predobj[1], URIRef) else "datatype"),
                                      "uriTo": (
                                          str(predobj[1]) if isinstance(predobj[1], URIRef) else predobj[1].datatype)})
        minivowlresult["nodes"] = nodes
        minivowlresult["links"] = links
        with open(f'{outpath}/{outfile}', "w", encoding="utf-8") as f:
            f.write("var minivowlresult=")
            json.dump(minivowlresult, f, indent=1)
        return minivowlresult

    @staticmethod
    def convertOWL2VOWL(g, outpath, typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                        labelproperty="http://www.w3.org/2000/01/rdf-schema#label"):
        vowlresult = {"_comment": "Created with pyowl2vowl (version 0.1) as part of the SPARQLing Unicorn QGIS Plugin",
                      "header": {"prefixList": {}, "baseIris": [], "languages": []}, "namespace": [], "class": [],
                      "classAttribute": [], "property": [], "propertyAttribute": []}
        props = []
        propAttributes = []
        classes = []
        classAttributes = []
        iriToProdId = {}
        classiriToProdId = {}
        propiriToProdId = {}
        propidcounter = 0
        classidcounter = 0
        idcounter = 0
        for nstup in g.namespaces():
            vowlresult["header"]["prefixList"][str(nstup[0])] = str(nstup[1])
            vowlresult["header"]["baseIris"].append(str(nstup[1]))
        for pred in g.subject_objects(URIRef(typeproperty)):
            # print(pred)
            predsubstr = str(pred[0])
            predobjstr = str(pred[1])
            iriToProdId[predsubstr] = idcounter
            if predobjstr == "http://www.w3.org/2002/07/owl#Class" or predobjstr == "http://www.w3.org/2000/01/rdf-schema#Class" or predobjstr == "http://www.w3.org/2000/01/rdf-schema#Datatype":
                classes.append({"id": idcounter, "type": predobjstr})
                classiriToProdId[predsubstr] = {"id": idcounter, "attid": len(classAttributes) - 1}
                classAttributes.append(
                    {"id": idcounter, "iri": predsubstr, "baseIRI": VOWLExporter.getBaseIRI(predsubstr), "instances": 0,
                     "label": {"IRI-based": VOWLExporter.getIRILabel(predsubstr)}, "annotations": {}, "subClasses": [],
                     "superClasses": []})
                idcounter += 1
            else:
                props.append(
                    {"id": idcounter, "type": VOWLExporter.getTypeForProperty(str(predsubstr), g, typeproperty)})
                propiriToProdId[predsubstr] = {"id": idcounter, "attid": len(propAttributes) - 1}
                propAttributes.append(
                    {"id": idcounter, "iri": str(predsubstr), "baseIRI": VOWLExporter.getBaseIRI(predsubstr),
                     "instances": 0, "label": {"IRI-based": VOWLExporter.getIRILabel(predsubstr)}, "annotations": {},
                     "range": [], "domain": [], "subProperties": [], "superProperties": []})
                idcounter += 1

        for pred in g.subject_objects(RDFS.range):
            print(pred)
            predstr = str(pred[1])
            if predstr not in classiriToProdId:
                classes.append({"id": idcounter, "type": "http://www.w3.org/2000/01/rdf-schema#Datatype"})
                classiriToProdId[predstr] = {"id": idcounter, "attid": len(classAttributes) - 1}
                classAttributes.append(
                    {"id": idcounter, "iri": predstr, "baseIRI": VOWLExporter.getBaseIRI(str(pred)), "instances": 0,
                     "label": {"IRI-based": VOWLExporter.getIRILabel(predstr)}, "annotations": {}, "subClasses": [],
                     "superClasses": []})
                idcounter += 1

        for iri in classiriToProdId:
            # print(iri)
            for clsatt in g.predicate_objects(URIRef(iri)):
                # print(clsatt)
                if clsatt[0] != URIRef(typeproperty):
                    if clsatt[0] == RDFS.subClassOf:
                        if str(clsatt[1]) in classiriToProdId:
                            classAttributes[classiriToProdId[iri]["attid"]]["superClasses"].append(
                                str(classiriToProdId[str(clsatt[1])]["id"]))
                            classAttributes[classiriToProdId[str(clsatt[1])]["attid"]]["subClasses"].append(
                                str(classiriToProdId[iri]["id"]))
                    elif clsatt[0] == URIRef(labelproperty):
                        classAttributes[classiriToProdId[iri]["attid"]]["label"] = str(clsatt[1])
                    else:
                        classAttributes[classiriToProdId[iri]["attid"]]["annotations"][str(clsatt[0])] = []
                        if str(clsatt[1]).startswith("http"):
                            classAttributes[classiriToProdId[iri]["attid"]]["annotations"][str(clsatt[0])].append(
                                {"identifier": str(clsatt[0]), "language": "undefined", "value": str(clsatt[1]),
                                 "type": "iri"})
                        else:
                            classAttributes[classiriToProdId[iri]["attid"]]["annotations"][str(clsatt[0])].append(
                                {"identifier": str(clsatt[0]), "language": "undefined", "value": str(clsatt[1]),
                                 "type": "label"})

        for iri in propiriToProdId:
            # print(iri)
            for propatt in g.predicate_objects(URIRef(iri)):
                # print(propatt)
                propattpred = str(propatt[0])
                propattobj = str(propatt[1])
                if propattpred != typeproperty:
                    if propattpred == "http://www.w3.org/2000/01/rdf-schema#subPropertyOf":
                        if propattobj in propiriToProdId:
                            propAttributes[propiriToProdId[iri]["attid"]]["superProperties"].append(
                                str(propiriToProdId[propattobj]["id"]))
                            propAttributes[propiriToProdId[propattobj]["attid"]]["subProperties"].append(
                                str(propiriToProdId[iri]["id"]))
                    elif propattpred == "http://www.w3.org/2000/01/rdf-schema#range" and propattobj in propiriToProdId:
                        propAttributes[propiriToProdId[iri]["attid"]]["range"].append(
                            str(classiriToProdId[propattobj]["id"]))
                    elif propattpred == "http://www.w3.org/2000/01/rdf-schema#domain" and str(
                            propattobj) in propiriToProdId:
                        propAttributes[propiriToProdId[iri]["attid"]]["domain"].append(
                            str(classiriToProdId[propattobj]["id"]))
                    elif propattpred == labelproperty:
                        propAttributes[propiriToProdId[iri]["attid"]]["label"] = propattobj
                    else:
                        propAttributes[propiriToProdId[iri]["attid"]]["annotations"][propattpred] = []
                        if propattobj.startswith("http"):
                            propAttributes[propiriToProdId[iri]["attid"]]["annotations"][propattpred].append(
                                {"identifier": propattpred, "language": "undefined", "value": propattobj,
                                 "type": "iri"})
                        else:
                            propAttributes[propiriToProdId[iri]["attid"]]["annotations"][propattpred].append(
                                {"identifier": propattpred, "language": "undefined", "value": propattobj,
                                 "type": "label"})

        vowlresult["property"] = props
        vowlresult["propertyAttribute"] = propAttributes
        vowlresult["class"] = classes
        vowlresult["classAttribute"] = classAttributes
        with open(outpath + "/vowl_result.js", "w", encoding="utf-8") as f:
            f.write("var vowlresult=")
            json.dump(vowlresult, f, indent=1)
        return vowlresult
