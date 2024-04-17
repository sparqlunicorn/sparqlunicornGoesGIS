from rdflib import URIRef, BNode, Literal
from .docutils import DocUtils
from .docconfig import DocConfig
from ..sparqlutils import SPARQLUtils
import json
from ..export.data.vowlexporter import OWL2VOWL

class GraphUtils:

    subclassofproperties=["http://www.w3.org/2000/01/rdf-schema#subClassOf","http://www.w3.org/2000/01/rdf-schema#subClassOf"]

    typeproperties=["http://www.w3.org/1999/02/22-rdf-syntax-ns#type","http://www.w3.org/2000/01/rdf-schema#subClassOf"]

    @staticmethod
    def determineKeyProperties(graph):
        res={"typeproperty":{},"subclassofproperty":{}}
        subclassofprops=[]
        typeprops=[]
        for pred in graph.predicates(None,None,True):
            if str(pred) in GraphUtils.subclassofproperties and str(pred) not in subclassofprops:
                subclassofprops.append(str(pred))
            if str(pred) in GraphUtils.typeproperties and str(pred) not in typeprops:
                typeprops.append(str(pred))
        res["typeproperty"]=typeprops
        res["subclassproperty"]=subclassofprops
        return res


    @staticmethod
    def createCollections(graph, namespace,typeproperty):
        classToInstances = {}
        classToGeoColl = {}
        classToFColl = {}
        for tup in graph.subject_objects(URIRef(typeproperty)):
            if namespace in str(tup[0]):
                if str(tup[1]) not in classToInstances:
                    classToInstances[str(tup[1])] = set()
                    classToFColl[str(tup[1])] = 0
                    classToGeoColl[str(tup[1])] = 0
                classToInstances[str(tup[1])].add(str(tup[0]))
                isgeo = False
                isfeature = False
                for geotup in graph.predicate_objects(tup[0]):
                    if str(geotup[0]) in SPARQLUtils.geopointerproperties:
                        isfeature = True
                    elif str(geotup[0]) in SPARQLUtils.geoproperties:
                        isgeo = True
                if isgeo:
                    classToGeoColl[str(tup[1])] += 1
                if isfeature:
                    classToFColl[str(tup[1])] += 1
        for cls in classToInstances:
            colluri = namespace + DocUtils.shortenURI(cls) + "_collection"
            collrelprop = "http://www.w3.org/2000/01/rdf-schema#member"
            if classToFColl[cls] == len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                           URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection"),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                           URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(typeproperty),
                           URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection")))
            elif classToGeoColl[cls] == len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                           URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection"),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                           URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(typeproperty),
                           URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection")))
            elif cls in DocConfig.classToCollectionClass:
                if "super" in DocConfig.classToCollectionClass[cls]:
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["class"]),
                               URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                               URIRef(DocConfig.classToCollectionClass[cls]["super"])))
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["super"]),
                               URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                               URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                else:
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["class"]),
                               URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                               URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef(colluri), URIRef(typeproperty),
                           URIRef(DocConfig.classToCollectionClass[cls]["class"])))
                collrelprop = DocConfig.classToCollectionClass[cls]["prop"]
            else:
                graph.add((URIRef(colluri), URIRef(typeproperty),
                           URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
            graph.add((URIRef(colluri), URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                       Literal(str(DocUtils.shortenURI(cls)) + " Instances Collection", lang="en")))
            for instance in classToInstances[cls]:
                graph.add((URIRef(colluri), URIRef(collrelprop), URIRef(instance)))
        return graph

    @staticmethod
    def addAdditionalTriplesForInd(graph, ind, tobeaddedPerInd):
        for prop in tobeaddedPerInd:
            if "value" in tobeaddedPerInd[prop] and "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"])),
                           URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                           URIRef(str(tobeaddedPerInd[prop]["uri"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"]).replace(" ", "_")),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                           URIRef(str(tobeaddedPerInd[prop]["value"]))))
            elif "value" in tobeaddedPerInd[prop] and not tobeaddedPerInd[prop]["value"].startswith("http"):
                if "type" in tobeaddedPerInd[prop]:
                    graph.add((ind, URIRef(prop),
                               Literal(tobeaddedPerInd[prop]["value"], datatype=tobeaddedPerInd[prop]["type"])))
                elif "value" in tobeaddedPerInd[prop]:
                    graph.add((ind, URIRef(prop), Literal(tobeaddedPerInd[prop]["value"])))
            elif "value" in tobeaddedPerInd[prop] and not "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))

    @staticmethod
    def getPropertyRelations(graph, outpath,typeproperty,createVOWL):
        predicates = {}
        predicatecounter = 0
        predicatelength = 0
        predicateClasses = 0
        objects = set()
        for pred in graph.predicates(None, None, True):
            predicates[pred] = {"from": set(), "to": set(), "triples": 0}
            for tup in graph.subject_objects(pred):
                if str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    predicateClasses += 1
                for item in graph.objects(tup[0], URIRef(typeproperty), True):
                    predicates[pred]["from"].add(item)
                for item in graph.objects(tup[1], URIRef(typeproperty), True):
                    predicates[pred]["to"].add(item)
                objects.add(str(tup[1]))
                predicates[pred]["triples"] += 1
            predicates[pred]["from"] = list(predicates[pred]["from"])
            predicates[pred]["to"] = list(predicates[pred]["to"])
            predicatecounter += 1
            predicatelength += len(str(pred))
        if createVOWL:
            OWL2VOWL.convertOWL2MiniVOWL(graph, outpath, "minivowl_result.js", predicates)
        with open(outpath + "proprelations.js", 'w', encoding='utf-8') as f:
            f.write("var proprelations=" + json.dumps(predicates))
            f.close()
        return {"preds": predicatecounter, "avgpredlen": str(int(DocUtils.zero_div(predicatelength,predicatecounter))),
                "predclasses": predicateClasses, "objs": len(objects), "predmap": predicates}

    @staticmethod
    def analyzeGraph(graph,prefixnamespace,typeproperty,voidds,labeltouri,uritolabel,outpath,createVOWL):
        graphstatresult={}
        voidstats = {"http://rdfs.org/ns/void#classes": 0, "http://rdfs.org/ns/void#entities": 0,
                     "http://rdfs.org/ns/void#distinctObjects": 0, "http://rdfs.org/ns/void#distinctSubjects": 0,
                     "http://rdfs.org/ns/void#properties": 0, "http://rdfs.org/ns/void#triples": 0}
        subjectstorender = set()
        subjectstorender.add(URIRef(voidds))
        res = GraphUtils.getPropertyRelations(graph, outpath,typeproperty,createVOWL)
        predmap=res["predmap"]
        voidstats["http://rdfs.org/ns/void#properties"] = res["preds"]
        voidstats["http://ldf.fi/void-ext#propertyClasses"] = res["predclasses"]
        voidstats["http://ldf.fi/void-ext#averagePropertyIRILength"] = res["avgpredlen"]
        voidstats["http://rdfs.org/ns/void#distinctObjects"] = res["objs"]
        nonnscount = {}
        nscount = {}
        instancecount = {}
        literaltypes = {}
        blanknodes = set()
        literallangs = set()
        literals = set()
        irirefs = 0
        literallength = 0
        literalcount = 0
        subjectlength = 0
        objectlength = 0
        subjectcounter = 0
        objectcounter = 0
        imgcounter= 0
        geocounter= 0
        for sub in graph.subjects(None, None, True):
            if (prefixnamespace in sub and (isinstance(sub, URIRef)) or isinstance(sub, BNode)):
                subjectstorender.add(sub)
                label = DocUtils.shortenURI(str(sub))
                restriction = False
                ns = DocUtils.shortenURI(str(sub), True)
                if ns not in nscount:
                    nscount[ns] = 0
                nscount[ns] += 1
                graph.add((sub, URIRef("http://rdfs.org/ns/void#inDataset"),
                                URIRef(voidds)))
                if isinstance(sub, BNode):
                    blanknodes.add(str(sub))
                irirefs += 1
                subjectcounter += 1
                subjectlength += len(str(sub))
                for tup in graph.predicate_objects(sub):
                    if isinstance(tup[1], Literal):
                        if tup[1].datatype != None:
                            if str(tup[1].datatype) not in literaltypes:
                                literaltypes[str(tup[1].datatype)] = set()
                            literaltypes[str(tup[1].datatype)].add(str(tup[0]))
                            if str(tup[1].datatype) in SPARQLUtils.geoliteraltypes or str(tup[0]) in SPARQLUtils.geoproperties:
                                geocounter+=1
                        if tup[1].language != None:
                            literallangs.add(str(tup[1].language))
                        val=str(tup[1])
                        literallength += len(val)
                        literals.add(val)
                        if "." in val and val[val.rfind("."):] in SPARQLUtils.imageextensions:
                            imgcounter+=1
                        literalcount += 1
                    elif isinstance(tup[1], BNode):
                        blanknodes.add(str(tup[1]))
                    else:
                        objectlength += len(str(tup[1]))
                        objectcounter += 1
                        irirefs += 1
                        ns = DocUtils.shortenURI(str(tup[1]), True)
                        if ns not in nscount:
                            nscount[ns] = 0
                        nscount[ns] += 1
                    if str(tup[0]) in SPARQLUtils.labelproperties:
                        labeltouri[str(tup[1])] = str(sub)
                        uritolabel[str(sub)] = {"label": str(tup[1])}
                        label = str(tup[1])
                    elif str(tup[0]) == typeproperty:
                        if str(tup[1]) not in instancecount:
                            instancecount[str(tup[1])] = 0
                        instancecount[str(tup[1])] += 1
                    elif str(tup[1]) == "http://www.w3.org/2002/07/owl#Restriction":
                        restriction = True
                    elif str(tup[0]) == "http://www.w3.org/2000/01/rdf-schema#subClassOf":
                        ressubcls = str(tup[1])
                    if isinstance(tup[1], URIRef) and prefixnamespace not in str(tup[1]):
                        ns = DocUtils.shortenURI(str(tup[1]), True)
                        if ns not in nscount:
                            nscount[ns] = 0
                        nscount[ns] += 1
                        if str(tup[0]) not in nonnscount:
                            nonnscount[str(tup[0])] = {}
                        if ns not in nonnscount[str(tup[0])]:
                            nonnscount[str(tup[0])][ns] = 0
                        nonnscount[str(tup[0])][ns] += 1
                if isinstance(sub, BNode) and restriction:
                    graph.add((sub, URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                    Literal(label + " [Restriction]", lang="en")))
            voidstats["http://rdfs.org/ns/void#distinctSubjects"] += 1
        voidstats["http://rdfs.org/ns/void#entities"] = len(subjectstorender)
        voidstats["http://ldf.fi/void-ext#languages"] = len(literallangs)
        voidstats["http://ldf.fi/void-ext#distinctBlankNodes"] = len(blanknodes)
        voidstats["http://ldf.fi/void-ext#datatypes"] = len(literaltypes.keys())
        voidstats["http://ldf.fi/void-ext#distinctLiterals"] = len(literals)
        voidstats["http://ldf.fi/void-ext#averageSubjectIRILength"] = int(DocUtils.zero_div(subjectlength,subjectcounter))
        voidstats["http://ldf.fi/void-ext#averageObjectIRILength"] = int(DocUtils.zero_div(objectlength,objectcounter))
        voidstats["http://ldf.fi/void-ext#averageLiteralLength"] = int(DocUtils.zero_div(literallength,literalcount))
        voidstats["http://ldf.fi/void-ext#distinctIRIReferences"] = voidstats[
                                                                        "http://rdfs.org/ns/void#distinctSubjects"] + \
                                                                    res["preds"] + res["objs"]
        voidstats["http://ldf.fi/void-ext#distinctRDFNodes"] = len(blanknodes) + len(literals) + voidstats[
            "http://ldf.fi/void-ext#distinctIRIReferences"]
        return {"voidstats":voidstats,"iiif":(imgcounter>0),"geo":(geocounter>0),
                "subjectstorender":subjectstorender,"predmap":predmap,"nonnscount":nonnscount,"nscount":nscount,"instancecount":instancecount}