from rdflib import URIRef, Literal, Graph
from .....doc.docconfig import DocConfig

from .....doc.docutils import DocUtils


class VoidExporter:

    @staticmethod
    def createVoidDataset(dsname,prefixnamespace,deploypath,outpath,licenseuri,modtime,language,stats,classtree=None,propstats=None,nonnscount=None,objectmap=None,startconcept=None):
        g=Graph()
        subjects = set()
        if dsname==None or dsname=="":
            dsname="dataset"
        voidds=prefixnamespace+dsname
        g.add((URIRef(voidds),URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://rdfs.org/ns/void#Dataset")))
        g.add((URIRef(voidds), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
              Literal(dsname,lang="en")))
        g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/title"),
              Literal(dsname,lang="en")))
        if language!=None and language!="":
            g.add((URIRef(voidds), URIRef("http://purl.org/dc/elements/1.1/language"),
                  URIRef("http://www.lexvo.org/page/iso639-1/"+str(language))))
        g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/modified"),
              Literal(modtime,datatype="http://www.w3.org/2001/XMLSchema#dateTime")))
        if licenseuri!=None:
            g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/license"),
                  URIRef(licenseuri)))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#dataDump"),
              URIRef(deploypath+"/index.ttl")))
        g.add((URIRef(voidds), URIRef("http://xmlns.com/foaf/0.1/homepage"),
              URIRef(deploypath)))
        g.add((URIRef(voidds), URIRef("http://xmlns.com/foaf/0.1/page"),
              URIRef(deploypath+"/index.html")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#dataDump"),
              URIRef(deploypath+"/index.ttl")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#feature"),
              URIRef("http://www.w3.org/ns/formats/Turtle")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#feature"),
              URIRef("http://www.w3.org/ns/formats/RDFa")))
        if startconcept!=None:
            g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#rootResource"), URIRef(startconcept)))
            g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#exampleResource"), URIRef(startconcept)))
        for stat in stats:
            g.add((URIRef(voidds),URIRef(stat),Literal(stats[stat],datatype="http://www.w3.org/2001/XMLSchema#integer")))
        g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#uriSpace"),
              Literal(prefixnamespace,datatype="http://www.w3.org/2001/XMLSchema#string")))
        for ns_prefix, namespace in g.namespaces():
            g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#vocabulary"),URIRef(namespace)))
            if str(namespace) in DocConfig.namespaceToTopic:
                for entry in DocConfig.namespaceToTopic[str(namespace)]:
                    g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/subject"),URIRef(entry)))
        for pred in propstats:
            cururi=voidds+"_"+DocUtils.shortenURI(pred)
            g.add((URIRef(voidds),URIRef("http://rdfs.org/ns/void#propertyPartition"),URIRef(cururi)))
            g.add((URIRef(cururi), URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://rdfs.org/ns/void#Dataset")))
            g.add((URIRef(cururi), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal("Property Partition: " + str(DocUtils.shortenURI(pred)), lang="en")))
            g.add((URIRef(cururi),URIRef("http://rdfs.org/ns/void#property"),URIRef(pred)))
            g.add((URIRef(cururi),URIRef("http://rdfs.org/ns/void#triples"),Literal(str(propstats[pred]["triples"]),datatype="http://www.w3.org/2001/XMLSchema#integer")))
            subjects.add(URIRef(cururi))
        for item in classtree["core"]["data"]:
            if item["type"] == "class":
                cururi = voidds + "_" + DocUtils.shortenURI(item["id"])
                g.add((URIRef(voidds), URIRef("http://rdfs.org/ns/void#classPartition"), URIRef(cururi)))
                g.add((URIRef(cururi), URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                       URIRef("http://rdfs.org/ns/void#Dataset")))
                g.add((URIRef(cururi), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                       Literal("Class Partition: " + str(DocUtils.shortenURI(item["id"])), lang="en")))
                g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#class"), URIRef(item["id"])))
                if item["id"] in objectmap:
                    g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#entities"),
                           Literal(str(objectmap[item["id"]]), datatype="http://www.w3.org/2001/XMLSchema#integer")))
                subjects.add(URIRef(cururi))
        for prop in nonnscount:
            for ns in nonnscount[prop]:
                cururi = voidds + "_" + DocUtils.shortenURI(ns)
                g.add((URIRef(cururi), URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                       URIRef("http://rdfs.org/ns/void#Linkset")))
                g.add((URIRef(cururi), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                       Literal("Linkset: " + str(DocUtils.shortenURI(voidds)) + " - " + str(DocUtils.shortenURI(ns)),
                               lang="en")))
                g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#subjectsTarget"), URIRef(voidds)))
                g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#objectsTarget"), URIRef(ns)))
                g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#linkPredicate"), URIRef(prop)))
                g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#triples"),Literal(str(nonnscount[prop][ns]), datatype="http://www.w3.org/2001/XMLSchema#integer")))
                subjects.add(URIRef(cururi))
        g.serialize(outpath+"/void.ttl", encoding="utf-8")
        return {"graph":g,"subjects":subjects}

    @staticmethod
    def toHTML(stats,deploypath):
        result="<details><summary>Dataset Statistics <a href=\""+str(deploypath)+"/void.ttl"+"\" target=\"_blank\">[VOID]</a></summary>"
        result+="<table border=\"1\"><thead><th>Property</th><th>Value</th></thead><tbody>"
        for stat in stats:
            result+="<tr><td><a href=\""+str(stat)+"\" target=\"_blank\">"+str(DocUtils.shortenURI(stat))+"</a></td><td><span property=\""+str(stat)+"\" content=\""+str(stats[stat])+"\" datatype=\"http://www.w3.org/2001/XMLSchema#integer\">"+str(stats[stat])+"</span>&nbsp;<a href=\"http://www.w3.org/2001/XMLSchema#integer\" style=\"color:#666;\"><small>(xsd:integer)</small></a></td></tr>"
        result+="</tbody></table></details>"
        return result