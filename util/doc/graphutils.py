from rdflib import URIRef, BNode, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, VOID, GEO
from .docutils import DocUtils
from .docconfig import DocConfig
import json
from collections import defaultdict
from ..export.data.vowlexporter import VOWLExporter

class GraphUtils:

    subclassofproperties=["http://www.w3.org/2000/01/rdf-schema#subClassOf","http://www.w3.org/2000/01/rdf-schema#subClassOf"]

    typeproperties=["http://www.w3.org/1999/02/22-rdf-syntax-ns#type","http://www.w3.org/2000/01/rdf-schema#subClassOf"]

    @staticmethod
    def determineKeyProperties(graph):
        res={"typeproperty":{},"subclassofproperty":{}}
        subclassofprops=[]
        typeprops=[]
        for pred in graph.predicates(None,None,True):
            predstr=str(pred)
            if predstr in GraphUtils.subclassofproperties and predstr not in subclassofprops:
                subclassofprops.append(predstr)
            if predstr in GraphUtils.typeproperties and predstr not in typeprops:
                typeprops.append(predstr)
        res["typeproperty"]=typeprops
        res["subclassproperty"]=subclassofprops
        return res


    @staticmethod
    def createCollections(graph, namespace,typeproperty,collectionClass=None):
        classToInstances = defaultdict(set)
        classToGeoColl = defaultdict(int)
        classToFColl = defaultdict(int)
        tprop=URIRef(typeproperty)
        for tup in graph.subject_objects(tprop):
            tuppredstr=str(tup[0])
            tupobjstr=str(tup[1])
            if namespace in tuppredstr:
                classToInstances[tupobjstr].add(tuppredstr)
                isgeo = False
                isfeature = False
                for geotup in graph.predicate_objects(tup[0]):
                    if str(geotup[0]) in DocConfig.geopointerproperties:
                        isfeature = True
                    if str(geotup[0]) in DocConfig.geoproperties:
                        isgeo = True
                if isgeo:
                    classToGeoColl[tupobjstr] += 1
                if isfeature:
                    classToFColl[tupobjstr] += 1
        collrelprop = "http://www.w3.org/2000/01/rdf-schema#member"
        collcls=URIRef(collectionClass)
        sobjcoll=URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")
        fcoll = URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection")
        gcoll = URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection")
        for cls in classToInstances:
            colluri = URIRef(f"{namespace}{DocUtils.shortenURI(cls)}_collection")
            if classToFColl[cls] == len(classToInstances[cls]):
                graph.add((sobjcoll,
                           RDFS.subClassOf,
                           collcls))
                graph.add((fcoll,
                           RDFS.subClassOf,
                           sobjcoll))
                graph.add((colluri, tprop,
                           fcoll))
            elif classToGeoColl[cls] == len(classToInstances[cls]):
                graph.add((sobjcoll,
                           RDFS.subClassOf,
                           collcls))
                graph.add((gcoll,
                           RDFS.subClassOf,
                           sobjcoll))
                graph.add((colluri, tprop,
                           gcoll))
            elif cls in DocConfig.classToCollectionClass:
                if "super" in DocConfig.classToCollectionClass[cls]:
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["class"]),
                               RDFS.subClassOf,
                               URIRef(DocConfig.classToCollectionClass[cls]["super"])))
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["super"]),
                               RDFS.subClassOf,
                               collcls))
                else:
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["class"]),
                               RDFS.subClassOf,
                               collcls))
                graph.add((colluri, tprop,
                           URIRef(DocConfig.classToCollectionClass[cls]["class"])))
                collrelprop = DocConfig.classToCollectionClass[cls]["prop"]
            else:
                graph.add((colluri, tprop,collcls))
            graph.add((colluri, RDFS.label,Literal(f"{DocUtils.shortenURI(cls)} Instances Collection", lang="en")))
            crelprop=URIRef(collrelprop)
            for instance in classToInstances[cls]:
                graph.add((colluri, crelprop, URIRef(instance)))
        return graph

    @staticmethod
    def addAdditionalTriplesForInd(graph, ind, tobeaddedPerInd):
        for prop in tobeaddedPerInd:
            propp = URIRef(prop)
            if "value" in tobeaddedPerInd[prop] and "uri" in tobeaddedPerInd[prop]:
                valuri=URIRef(str(tobeaddedPerInd[prop]["value"]))
                graph.add((ind, propp, valuri))
                graph.add((valuri,
                           RDF.type,
                           URIRef(str(tobeaddedPerInd[prop]["uri"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"]).replace(" ", "_")),
                           RDFS.label,
                           valuri))
            elif "value" in tobeaddedPerInd[prop] and not tobeaddedPerInd[prop]["value"].startswith("http"):
                if "type" in tobeaddedPerInd[prop]:
                    graph.add((ind, propp,Literal(tobeaddedPerInd[prop]["value"], datatype=tobeaddedPerInd[prop]["type"])))
                elif "value" in tobeaddedPerInd[prop]:
                    graph.add((ind, propp, Literal(tobeaddedPerInd[prop]["value"])))
            elif "value" in tobeaddedPerInd[prop] and "uri" not in tobeaddedPerInd[prop]:
                graph.add((ind, propp, URIRef(str(tobeaddedPerInd[prop]["value"]))))

    @staticmethod
    def getPropertyRelations(graph, outpath,typeproperty,createVOWL):
        predicates = {}
        predicatecounter = 0
        predicatelength = 0
        predicateClasses = 0
        objects = set()
        tpprop=URIRef(typeproperty)
        for pred in graph.predicates(None, None, True):
            predicates[pred] = {"from": set(), "to": set(), "triples": 0}
            for tup in graph.subject_objects(pred):
                if tup[0] == tpprop:
                    predicateClasses += 1
                predicates[pred]["from"].update(graph.objects(tup[0], tpprop, True))
                predicates[pred]["to"].update(graph.objects(tup[1], tpprop, True))
                #for item in graph.objects(tup[0], tpprop, True):
                #    predicates[pred]["from"].add(item)
                #for item in graph.objects(tup[1], tpprop, True):
                #    predicates[pred]["to"].add(item)
                objects.add(str(tup[1]))
                predicates[pred]["triples"] += 1
            predicates[pred]["from"] = list(predicates[pred]["from"])
            predicates[pred]["to"] = list(predicates[pred]["to"])
            predicatecounter += 1
            predicatelength += len(str(pred))
        VOWLExporter.convertOWL2MiniVOWL(graph, outpath, "minivowl_result.js", predicates)
        with open(outpath + "proprelations.js", 'w', encoding='utf-8') as f:
            f.write("var proprelations=")
            json.dump(predicates,f)
        return {"preds": predicatecounter, "avgpredlen": str(int(DocUtils.zero_div(predicatelength,predicatecounter))),
                "predclasses": predicateClasses, "objs": len(objects), "predmap": predicates}

    @staticmethod
    def analyzeGraph(graph,prefixnamespace,typeproperty,voidds,labeltouri,uritolabel,outpath,createVOWL):
        graphstatresult={}
        voidstats = {"http://rdfs.org/ns/void#classes": 0, "http://rdfs.org/ns/void#entities": 0,
                     "http://rdfs.org/ns/void#distinctObjects": 0, "http://rdfs.org/ns/void#distinctSubjects": 0,
                     "http://rdfs.org/ns/void#properties": 0, "http://rdfs.org/ns/void#triples": 0}
        subjectstorender = {URIRef(voidds)}
        res = GraphUtils.getPropertyRelations(graph, outpath,typeproperty,createVOWL)
        predmap=res["predmap"]
        voidstats["http://rdfs.org/ns/void#properties"] = res["preds"]
        voidstats["http://ldf.fi/void-ext#propertyClasses"] = res["predclasses"]
        voidstats["http://ldf.fi/void-ext#averagePropertyIRILength"] = res["avgpredlen"]
        voidstats["http://rdfs.org/ns/void#distinctObjects"] = res["objs"]
        nonnscount = defaultdict(dict)
        nscount = defaultdict(int)
        instancecount = defaultdict(int)
        literaltypes = defaultdict(set)
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
        voidds=URIRef(voidds)
        for sub in graph.subjects(None, None, True):
            substr=str(sub)
            if prefixnamespace in sub and (isinstance(sub, URIRef)) or isinstance(sub, BNode):
                subjectstorender.add(sub)
                label = DocUtils.shortenURI(substr)
                restriction = False
                ns = DocUtils.shortenURI(substr, True)
                #nscount.setdefault(ns,0)
                nscount[ns] += 1
                graph.add((sub, VOID.inDataset,voidds))
                if isinstance(sub, BNode):
                    blanknodes.add(substr)
                irirefs += 1
                subjectcounter += 1
                subjectlength += len(substr)
                for tup in graph.predicate_objects(sub):
                    tuppredstr=str(tup[0])
                    tupobjstr = str(tup[1])
                    if isinstance(tupobjstr, Literal):
                        if tup[1].datatype is not None:
                            literaltypes[str(tup[1].datatype)].add(tuppredstr)
                            #literaltypes.setdefault(str(tup[1].datatype),set()).add(tuppredstr)
                            if str(tup[1].datatype) in DocConfig.geoliteraltypes or tuppredstr in DocConfig.geoproperties:
                                geocounter+=1
                        if tup[1].language is not None:
                            literallangs.add(str(tup[1].language))
                        val=tupobjstr
                        literallength += len(val)
                        literals.add(val)
                        if "." in val and val[val.rfind("."):] in DocConfig.imageextensions:
                            imgcounter+=1
                        literalcount += 1
                    elif isinstance(tup[1], BNode):
                        blanknodes.add(tupobjstr)
                    else:
                        objectlength += len(tupobjstr)
                        objectcounter += 1
                        irirefs += 1
                        ns = DocUtils.shortenURI(tupobjstr, True)
                        #nscount.setdefault(ns, 0)
                        nscount[ns] += 1
                    if tuppredstr in DocConfig.labelproperties:
                        labeltouri[tupobjstr] = substr
                        uritolabel[substr] = {"label": tupobjstr}
                        label = tupobjstr
                    elif tuppredstr == typeproperty:
                        #instancecount.setdefault(tupobjstr, 0)
                        instancecount[tupobjstr] += 1
                    elif tupobjstr == "http://www.w3.org/2002/07/owl#Restriction":
                        restriction = True
                    elif tuppredstr == "http://www.w3.org/2000/01/rdf-schema#subClassOf":
                        ressubcls =tupobjstr
                    if isinstance(tup[1], URIRef) and prefixnamespace not in tupobjstr:
                        ns = DocUtils.shortenURI(tupobjstr, True)
                        #nscount.setdefault(ns, 0)
                        nscount[ns] += 1
                        #nonnscount.setdefault(tuppredstr,{})
                        nonnscount[tuppredstr].setdefault(ns,0)
                        nonnscount[tuppredstr][ns] += 1
                if isinstance(sub, BNode) and restriction:
                    graph.add((sub, RDFS.label,Literal(label + " [Restriction]", lang="en")))
            voidstats["http://rdfs.org/ns/void#distinctSubjects"] += 1
        voidstats["http://rdfs.org/ns/void#entities"] = len(subjectstorender)
        voidstats["http://ldf.fi/void-ext#languages"] = len(literallangs)
        voidstats["http://ldf.fi/void-ext#distinctBlankNodes"] = len(blanknodes)
        voidstats["http://ldf.fi/void-ext#datatypes"] = len(literaltypes.keys())
        voidstats["http://ldf.fi/void-ext#distinctLiterals"] = len(literals)
        voidstats["http://ldf.fi/void-ext#averageSubjectIRILength"] = int(DocUtils.zero_div(subjectlength,subjectcounter))
        voidstats["http://ldf.fi/void-ext#averageObjectIRILength"] = int(DocUtils.zero_div(objectlength,objectcounter))
        voidstats["http://ldf.fi/void-ext#averageLiteralLength"] = int(DocUtils.zero_div(literallength,literalcount))
        voidstats["http://ldf.fi/void-ext#distinctIRIReferences"] = voidstats["http://rdfs.org/ns/void#distinctSubjects"] + res["preds"] + res["objs"]
        voidstats["http://ldf.fi/void-ext#distinctRDFNodes"] = len(blanknodes) + len(literals) + voidstats["http://ldf.fi/void-ext#distinctIRIReferences"]
        return {"voidstats":voidstats,"iiif":(imgcounter>0),"geo":(geocounter>0),
                "subjectstorender":subjectstorender,"predmap":predmap,"nonnscount":nonnscount,"nscount":nscount,"instancecount":instancecount}