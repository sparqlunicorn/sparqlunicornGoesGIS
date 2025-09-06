import os

from rdflib import URIRef, Literal, Graph
from rdflib.namespace import RDF, RDFS, OWL, FOAF

from ...doc.docutils import DocUtils


class SolidExporter:

    @staticmethod
    def createSolidSettings(graph,outpath,deploypath,publisher,datasetname,classtree):
        if not os.path.exists(outpath+"/settings/"):
            os.makedirs(outpath + "/settings/")
        if not os.path.exists(outpath+"/profile/"):
            os.makedirs(outpath + "/profile/")
        webidprofilegraph=Graph()
        webidprofilegraph.add((URIRef(outpath+"/profile/card"), RDF.type, URIRef("http://xmlns.com/foaf/0.1/PersonalProfileDocument")))
        preferencesgraph=Graph()
        preferencesgraph.serialize(destination=outpath+"/settings/prefs.ttl", format="ttl")
        publisheruri=publisher.replace(" ","_")
        if not publisher.startswith("http"):
            publisheruri=deploypath+"/profile/card#"+str(publisher).replace(" ","_")
        puburi=URIRef(str(publisheruri))
        ptypeindex = URIRef(deploypath + "/settings/publicTypeIndex.ttl")
        webidprofilegraph.add((URIRef(outpath + "/profile/card"), FOAF.primaryTopic, puburi))
        webidprofilegraph.add((puburi, RDF.type, FOAF.Person))
        webidprofilegraph.add((puburi, URIRef("http://www.w3.org/ns/pim/space#storage"), URIRef(str(deploypath) + str(datasetname).replace(" ","_"))))
        webidprofilegraph.add((puburi, URIRef("http://www.w3.org/ns/solid/terms#publicTypeIndex"), ptypeindex))
        webidprofilegraph.add((puburi, URIRef("http://www.w3.org/ns/solid/terms#privateTypeIndex"), URIRef(deploypath + "/settings/privateTypeIndex.ttl")))
        webidprofilegraph.serialize(destination=outpath+"/profile/card.ttl", format="ttl")
        typeindexgraph=Graph()
        typeindexgraph.add((ptypeindex, RDF.type, URIRef("http://www.w3.org/ns/solid/terms#TypeIndex")))
        typeindexgraph.add((ptypeindex, RDF.type, URIRef("http://www.w3.org/ns/ldp#RDFResource")))
        typeindexgraph.add((ptypeindex, RDF.type, URIRef("http://www.w3.org/ns/solid/terms#ListedDocument")))
        typeindexgraph.add((ptypeindex, RDFS.comment, Literal("This Document contains a list of links to other Documents, along with the type of data that is to be included in those Documents",lang="en")))
        typeindexgraph.add((ptypeindex, RDF.type, Literal("Public Type Index", lang="en")))
        forclass=URIRef("http://www.w3.org/ns/solid/terms#forClass")
        sinstance = URIRef("http://www.w3.org/ns/solid/terms#instance")
        for cls in classtree:
            ptyeindexhash=URIRef(f'{deploypath}/settings/publicTypeIndex.ttl#{DocUtils.shortenURI(cls["id"])}')
            typeindexgraph.add((ptypeindex, RDFS.member, ptyeindexhash))
            typeindexgraph.add((ptyeindexhash,forclass, URIRef(cls["parent"])))
            typeindexgraph.add((ptyeindexhash,sinstance, URIRef(f'{deploypath}/{DocUtils.shortenURI(cls["id"])}')))
        for subj,obj in graph.subject_objects(RDFS.subClassOf):
            typeindexgraph.add((subj, RDFS.subClassOf, obj))
            typeindexgraph.add((subj, RDF.type, OWL.Class))
            typeindexgraph.add((obj, RDF.type, OWL.Class))
        for obj in graph.objects(None,RDF.type):
            typeindexgraph.add((obj, RDF.type, OWL.Class))
        typeindexgraph.serialize(destination=outpath+"/settings/publicTypeIndex.ttl", format="ttl")
        typeindexgraph2=Graph()
        ptypeindex = URIRef(deploypath + "/settings/privateTypeIndex.ttl")
        typeindexgraph2.add((ptypeindex, RDF.type, URIRef("http://www.w3.org/ns/solid/terms#TypeIndex")))
        typeindexgraph2.add((ptypeindex, RDF.type, URIRef("http://www.w3.org/ns/ldp#RDFResource")))
        typeindexgraph2.add((ptypeindex, RDF.type, URIRef("http://www.w3.org/ns/solid/terms#ListedDocument")))
        typeindexgraph2.add((ptypeindex, RDFS.comment, Literal("This Document contains a list of links to other Documents, along with the type of data that is to be included in those Documents",lang="en")))
        typeindexgraph2.add((ptypeindex, RDFS.label, Literal("Private Type Index", lang="en")))
        typeindexgraph2.serialize(destination=outpath+"/settings/privateTypeIndex.ttl", format="ttl")

    @staticmethod
    def prepareSolidPartitions(graph,classtree,properties):
        print("Graph partitioning here")

    @staticmethod
    def addSolidStorage(graph,deploypath,datasetname):
        graph.add((URIRef(str(deploypath) + str(datasetname)),RDF.type,URIRef("http://www.w3.org/ns/pim/space#Storage")))
        graph.add((URIRef(str(deploypath) + str(datasetname)), RDFS.label, Literal("Solid Storage for "+str(datasetname))))

    @staticmethod
    def createSolidDocumentIndex():
        print("Create document index")

    @staticmethod
    def addSolidContainer(graph,deploypath,datasetname,collections):
        ldpcon=URIRef("http://www.w3.org/ns/ldp#Container")
        ianattl=URIRef("http://www.w3.org/ns/iana/media-types/text/ttl#Resource")
        pimstorage=URIRef("http://www.w3.org/ns/pim/space#storage")
        for coll in collections:
            colluri=URIRef(coll)
            graph.add((colluri,RDF.type, ianattl))
            graph.add((colluri, RDF.type, ldpcon))
            graph.add((colluri, pimstorage,URIRef(f'{deploypath}{datasetname}')))