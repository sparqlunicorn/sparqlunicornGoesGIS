from rdflib import URIRef, Literal, Graph, XSD
from rdflib.namespace import RDF, RDFS, VOID, VANN, FOAF, DCAT, DC
from ...doc.docconfig import DocConfig

from ...doc.docutils import DocUtils


class VoidExporter:

    @staticmethod
    def createVoidDataset(pubconfig,licenseuri,stats,subjectstorender,classtree=None,propstats=None,nonnscount=None,nscount=None,objectmap=None):
        g=Graph()
        g.bind("voaf","http://purl.org/vocommons/voaf#")
        g.bind("vext", "http://ldf.fi/void-ext#")
        g.bind("vann", "http://purl.org/vocab/vann/")
        g.bind("adms", "http://www.w3.org/ns/adms#")
        g.bind("dcat", "http://www.w3.org/ns/dcat#")
        dsname=pubconfig["datasettitle"]
        if pubconfig["datasettitle"] is None or pubconfig["datasettitle"]== "":
            dsname="dataset"
        dsname=dsname.replace(" ","_")
        voidds=pubconfig["prefixns"]+dsname
        if pubconfig["repository"] is not None and pubconfig["repository"]!= "" and pubconfig["repository"].startswith("http"):
            g.add((URIRef(pubconfig["repository"]), RDF.type,
                   URIRef("http://www.w3.org/ns/adms#AssetRepository")))
            g.add((URIRef(pubconfig["repository"]), DCAT.accessURL,
                   Literal(str(pubconfig["repository"]),datatype=XSD.anyURI)))
            g.add((URIRef(pubconfig["repository"]), DCAT.dataset,
                   URIRef(voidds)))
            g.add((URIRef(pubconfig["repository"]), RDFS.label,
                   Literal("Repository for "+str(dsname), lang="en")))
        g.add((URIRef(voidds),RDF.type,VOID.Dataset))
        g.add((URIRef(voidds), RDF.type, URIRef("http://www.w3.org/ns/adms#Asset")))
        g.add((URIRef(voidds), RDFS.label,
              Literal(dsname,lang="en")))
        g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/title"),
              Literal(dsname,lang="en")))
        if pubconfig["labellang"] is not None and pubconfig["labellang"]!= "":
            g.add((URIRef(voidds), DC.language,
                  URIRef("http://www.lexvo.org/page/iso639-1/"+str(pubconfig["labellang"]))))
        g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/modified"),
              Literal(pubconfig["modtime"],datatype=XSD.dateTime)))
        if licenseuri is not None:
            g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/license"),
                  URIRef(licenseuri)))
        g.add((URIRef(voidds), VOID.dataDump,
              URIRef(pubconfig["deploypath"]+"/index.ttl")))
        g.add((URIRef(voidds), FOAF.homepage,
              URIRef(pubconfig["deploypath"])))
        g.add((URIRef(voidds), DCAT.landingPage,
              URIRef(pubconfig["deploypath"])))
        g.add((URIRef(voidds), FOAF.page,
              URIRef(pubconfig["deploypath"]+"/index.html")))
        g.add((URIRef(voidds), VOID.dataDump,
              URIRef(pubconfig["deploypath"]+"/index.ttl")))
        g.add((URIRef(voidds), DCAT.distribution,
               URIRef(voidds+"_dist_ttl")))
        g.add((URIRef(voidds + "_dist_ttl"), RDF.type, URIRef("http://www.w3.org/ns/adms#AssetDistribution")))
        g.add((URIRef(voidds+"_dist_ttl"), RDFS.label,
               Literal(dsname+" TTL Distribution",lang="en")))
        g.add((URIRef(voidds+"_dist_ttl"), DCAT.downloadURL,
               Literal(pubconfig["deploypath"]+"/index.ttl",datatype=XSD.anyURI)))
        g.add((URIRef(voidds+"_dist_ttl"), DCAT.mediaType,
               URIRef("http://www.w3.org/ns/formats/Turtle")))
        g.add((URIRef(voidds), VOID.feature,
              URIRef("http://www.w3.org/ns/formats/Turtle")))
        g.add((URIRef(voidds), VOID.feature,
              URIRef("http://www.w3.org/ns/formats/RDFa")))
        if pubconfig["startconcept"] is not None and pubconfig["startconcept"]!= "":
            g.add((URIRef(voidds), VOID.rootResource, URIRef(pubconfig["startconcept"].replace("index.html",""))))
            g.add((URIRef(voidds), VOID.exampleResource, URIRef(pubconfig["startconcept"].replace("index.html",""))))
        for stat in stats:
            g.add((URIRef(voidds), URIRef(stat),Literal(stats[stat], datatype=XSD.integer)))
        g.add((URIRef(voidds), VOID.uriSpace,
              Literal(pubconfig["prefixns"],datatype=XSD.string)))
        g.add((URIRef(voidds), VANN.preferredNamespaceUri,
               Literal(pubconfig["prefixns"], datatype=XSD.anyURI)))
        g.add((URIRef(voidds), VANN.preferredNamespacePrefix,
               Literal(pubconfig["namespaceshort"], datatype=XSD.string)))
        for ns_prefix, namespace in g.namespaces():
            g.add((URIRef(voidds), VOID.vocabulary,URIRef(namespace)))
            g.add((URIRef(namespace), RDF.type, URIRef("http://purl.org/vocommons/voaf#Vocabulary")))
            if "nstolabel" in pubconfig["prefixes"] and str(namespace) in pubconfig["prefixes"]["nstolabel"]:
                g.add((URIRef(namespace), RDFS.label,
                       Literal(pubconfig["prefixes"]["nstolabel"][str(namespace)],lang="en")))
            else:
                g.add((URIRef(namespace), RDFS.label,
                       Literal(str(ns_prefix)+" Vocabulary",lang="en")))
            g.add((URIRef(namespace), VANN.preferredNamespaceUri,
                   Literal(namespace,datatype=XSD.anyURI)))
            g.add((URIRef(namespace), VANN.preferredNamespacePrefix,
                   Literal(ns_prefix,datatype=XSD.string)))
            g.add((URIRef(pubconfig["prefixns"]+str(ns_prefix)+"_"+str(dsname)+"_occ"), RDF.type,
                   URIRef("http://purl.org/vocommons/voaf#DatasetOccurrence")))
            g.add((URIRef(pubconfig["prefixns"]+str(ns_prefix)+"_"+str(dsname)+"_occ"), RDFS.label,
                   Literal("Occurrences of vocabulary "+str(namespace)+" in "+dsname)))
            if nscount is not None and str(namespace) in nscount:
                g.add((URIRef(pubconfig["prefixns"]+str(ns_prefix)+"_"+str(dsname)+"_occ"), URIRef("http://purl.org/vocommons/voaf#occurrences"),
                       Literal(str(nscount[str(namespace)]),datatype=XSD.integer)))
            g.add((URIRef(namespace), URIRef("http://purl.org/vocommons/voaf#usageInDataset"), URIRef(namespace+"_"+str(dsname)+"_occ")))
            g.add((URIRef(pubconfig["prefixns"]+str(ns_prefix)+"_"+str(dsname)+"_occ"), URIRef("http://purl.org/vocommons/voaf#inDataset"), URIRef(voidds)))
            if str(namespace) in DocConfig.namespaceToTopic:
                for entry in DocConfig.namespaceToTopic[str(namespace)]:
                    g.add((URIRef(voidds), DCAT.keyword, Literal(DocUtils.shortenURI(entry["uri"]).replace("_"," "),lang="en")))
                    g.add((URIRef(voidds), URIRef("http://purl.org/dc/terms/subject"),URIRef(entry["uri"])))
                    g.add((URIRef(entry["uri"]),RDFS.label,Literal(entry["label"],lang="en")))
        for pred in propstats:
            cururi=voidds+"_"+DocUtils.shortenURI(pred)
            g.add((URIRef(voidds),VOID.propertyPartition,URIRef(cururi)))
            g.add((URIRef(cururi), RDF.type,VOID.Dataset))
            g.add((URIRef(cururi), RDFS.label,Literal("Property Partition: " + str(DocUtils.shortenURI(pred)), lang="en")))
            g.add((URIRef(cururi),VOID.property,URIRef(pred)))
            g.add((URIRef(cururi),VOID.triples,Literal(str(propstats[pred]["triples"]),datatype=XSD.integer)))
            subjectstorender.add(URIRef(cururi))
        for item in classtree["core"]["data"]:
            if item["type"]=="class":
                cururi = voidds +"_"+ DocUtils.shortenURI(item["id"])
                g.add((URIRef(voidds), VOID.classPartition, URIRef(cururi)))
                g.add((URIRef(cururi), RDF.type,VOID.Dataset))
                g.add((URIRef(cururi), RDFS.label,Literal("Class Partition: " + str(DocUtils.shortenURI(item["id"])),lang="en")))
                g.add((URIRef(cururi), URIRef("http://rdfs.org/ns/void#class"), URIRef(item["id"])))
                if item["id"] in objectmap:
                    g.add((URIRef(cururi), VOID.entities,Literal(str(objectmap[item["id"]]), datatype=XSD.integer)))
                #subjectstorender.add(URIRef(cururi))
        for prop in nonnscount:
            for ns in nonnscount[prop]:
                cururi=voidds+"_"+ns.replace("http://","").replace("https://","").replace("/","_").replace("#","_")
                g.add((URIRef(cururi), RDF.type,VOID.Linkset))
                g.add((URIRef(cururi), RDFS.label,Literal("Linkset: "+str(DocUtils.shortenURI(voidds))+" - "+str(DocUtils.getLabelForObject(URIRef(ns),g,pubconfig["prefixes"])),lang="en")))
                g.add((URIRef(cururi), VOID.subjectsTarget,URIRef(voidds)))
                g.add((URIRef(cururi), VOID.objectsTarget,URIRef(ns)))
                g.add((URIRef(cururi), VOID.linkPredicate,URIRef(prop)))
                g.add((URIRef(cururi), VOID.triples,Literal(str(nonnscount[prop][ns]),datatype=XSD.integer)))
                subjectstorender.add(URIRef(cururi))
        g.serialize(pubconfig["outpath"]+"/void.ttl", encoding="utf-8")
        return {"graph":g,"subjects":subjectstorender}

    @staticmethod
    def toHTML(stats,deploypath):
        result="<details><summary>Dataset Statistics <a href=\""+str(deploypath)+"/void.ttl"+"\" target=\"_blank\">[VOID]</a></summary><table border=\"1\"><thead><th>Property</th><th>Value</th></thead><tbody>"
        for stat in stats:
            result+="<tr><td><a href=\""+str(stat)+"\" target=\"_blank\">"+str(DocUtils.shortenURI(stat))+"</a></td><td><span property=\""+str(stat)+"\" content=\""+str(stats[stat])+"\" datatype=\"http://www.w3.org/2001/XMLSchema#integer\">"+str(stats[stat])+"</span>&nbsp;<a href=\"http://www.w3.org/2001/XMLSchema#integer\" style=\"color:#666;\"><small>(xsd:integer)</small></a></td></tr>"
        result+="</tbody></table></details>"
        return result