from rdflib import URIRef, Literal, Graph, XSD
from rdflib.namespace import RDF, RDFS, VOID, VANN, FOAF, DCAT, DC
from ...doc.docconfig import DocConfig

from ...doc.docutils import DocUtils


class VoidExporter:

    @staticmethod
    def createVoidDataset(pubconfig, licenseuri, stats, subjectstorender, classtree=None, propstats=None,
                          nonnscount=None, nscount=None, objectmap=None):
        g = Graph()
        g.bind("voaf", "http://purl.org/vocommons/voaf#")
        g.bind("vext", "http://ldf.fi/void-ext#")
        g.bind("vann", "http://purl.org/vocab/vann/")
        g.bind("adms", "http://www.w3.org/ns/adms#")
        g.bind("dcat", "http://www.w3.org/ns/dcat#")
        dsname = pubconfig["datasettitle"]
        if pubconfig["datasettitle"] is None or pubconfig["datasettitle"] == "":
            dsname = "dataset"
        dsname = dsname.replace(" ", "_")
        voidds = URIRef(pubconfig["prefixns"] + dsname)
        pcrep = URIRef(pubconfig["repository"])
        if pubconfig["repository"] is not None and pubconfig["repository"] != "" and pubconfig["repository"].startswith(
                "http"):
            g.add((pcrep, RDF.type, URIRef("http://www.w3.org/ns/adms#AssetRepository")))
            g.add((pcrep, DCAT.accessURL, Literal(str(pubconfig["repository"]), datatype=XSD.anyURI)))
            g.add((pcrep, DCAT.dataset, voidds))
            g.add((pcrep, RDFS.label, Literal(f"Repository for {dsname}", lang="en")))
        g.add((voidds, RDF.type, VOID.Dataset))
        g.add((voidds, RDF.type, URIRef("http://www.w3.org/ns/adms#Asset")))
        g.add((voidds, RDFS.label, Literal(dsname, lang="en")))
        g.add((voidds, URIRef("http://purl.org/dc/terms/title"), Literal(dsname, lang="en")))
        if pubconfig["labellang"] is not None and pubconfig["labellang"] != "":
            g.add((voidds, DC.language, URIRef("http://www.lexvo.org/page/iso639-1/" + str(pubconfig["labellang"]))))
        g.add((voidds, URIRef("http://purl.org/dc/terms/modified"),
               Literal(pubconfig["modtime"], datatype=XSD.dateTime)))
        if licenseuri is not None:
            g.add((voidds, URIRef("http://purl.org/dc/terms/license"), URIRef(licenseuri)))
        g.add((voidds, VOID.dataDump,
               URIRef(pubconfig["deploypath"] + "/index.ttl")))
        g.add((voidds, FOAF.homepage,
               URIRef(pubconfig["deploypath"])))
        g.add((voidds, DCAT.landingPage,
               URIRef(pubconfig["deploypath"])))
        g.add((voidds, FOAF.page,
               URIRef(pubconfig["deploypath"] + "/index.html")))
        g.add((voidds, VOID.dataDump,
               URIRef(pubconfig["deploypath"] + "/index.ttl")))
        voiddistttl = URIRef(f"{voidds}_dist_ttl")
        g.add((voidds, DCAT.distribution,
               voiddistttl))
        g.add((voiddistttl, RDF.type, URIRef("http://www.w3.org/ns/adms#AssetDistribution")))
        g.add((voiddistttl, RDFS.label,
               Literal(dsname + " TTL Distribution", lang="en")))
        g.add((voiddistttl, DCAT.downloadURL,
               Literal(pubconfig["deploypath"] + "/index.ttl", datatype=XSD.anyURI)))
        g.add((voiddistttl, DCAT.mediaType,
               URIRef("http://www.w3.org/ns/formats/Turtle")))
        g.add((voidds, VOID.feature,
               URIRef("http://www.w3.org/ns/formats/Turtle")))
        g.add((voidds, VOID.feature,
               URIRef("http://www.w3.org/ns/formats/RDFa")))
        if pubconfig["startconcept"] is not None and pubconfig["startconcept"] != "":
            g.add((voidds, VOID.rootResource, URIRef(pubconfig["startconcept"].replace("index.html", ""))))
            g.add((voidds, VOID.exampleResource, URIRef(pubconfig["startconcept"].replace("index.html", ""))))
        for stat in stats:
            g.add((voidds, URIRef(stat), Literal(stats[stat], datatype=XSD.integer)))
        g.add((voidds, VOID.uriSpace, Literal(pubconfig["prefixns"], datatype=XSD.string)))
        g.add((voidds, VANN.preferredNamespaceUri, Literal(pubconfig["prefixns"], datatype=XSD.anyURI)))
        g.add((voidds, VANN.preferredNamespacePrefix, Literal(pubconfig["namespaceshort"], datatype=XSD.string)))
        dcsub = URIRef("http://purl.org/dc/terms/subject")
        voafd = URIRef("http://purl.org/vocommons/voaf#inDataset")
        voafocc = URIRef("http://purl.org/vocommons/voaf#occurrences")
        voafusage = URIRef("http://purl.org/vocommons/voaf#usageInDataset")
        voafVocab = URIRef("http://purl.org/vocommons/voaf#Vocabulary")
        voidc = URIRef("http://rdfs.org/ns/void#class")
        dsocc = URIRef("http://purl.org/vocommons/voaf#DatasetOccurrence")
        for ns_prefix, namespace in g.namespaces():
            thens = URIRef(namespace)
            g.add((voidds, VOID.vocabulary, thens))
            g.add((thens, RDF.type, voafVocab))
            if "nstolabel" in pubconfig["prefixes"] and str(namespace) in pubconfig["prefixes"]["nstolabel"]:
                g.add((thens, RDFS.label,
                       Literal(pubconfig["prefixes"]["nstolabel"][str(namespace)], lang="en")))
            else:
                g.add((thens, RDFS.label, Literal(f"{ns_prefix} Vocabulary", lang="en")))
            g.add((thens, VANN.preferredNamespaceUri,
                   Literal(namespace, datatype=XSD.anyURI)))
            g.add((thens, VANN.preferredNamespacePrefix,
                   Literal(ns_prefix, datatype=XSD.string)))
            g.add((URIRef(f'{pubconfig["prefixns"]}{ns_prefix}_{dsname}_occ'), RDF.type,
                   dsocc))
            g.add((URIRef(f'{pubconfig["prefixns"]}{ns_prefix}_{dsname}_occ'), RDFS.label,
                   Literal(f"Occurrences of vocabulary {namespace} in {dsname}")))
            if nscount is not None and str(namespace) in nscount:
                g.add((URIRef(f'{pubconfig["prefixns"]}{ns_prefix}_{dsname}_occ'), voafocc,
                       Literal(str(nscount[str(namespace)]), datatype=XSD.integer)))
            g.add((thens, voafusage, URIRef(f"{namespace}_{dsname}_occ")))
            g.add((URIRef(f'{pubconfig["prefixns"]}{ns_prefix}_{dsname}_occ'), voafd, voidds))
            if str(namespace) in DocConfig.namespaceToTopic:
                for entry in DocConfig.namespaceToTopic[str(namespace)]:
                    g.add(
                        (voidds, DCAT.keyword, Literal(DocUtils.shortenURI(entry["uri"]).replace("_", " "), lang="en")))
                    g.add((voidds, dcsub, URIRef(entry["uri"])))
                    g.add((URIRef(entry["uri"]), RDFS.label, Literal(entry["label"], lang="en")))
        for pred in propstats:
            cururi = URIRef(f'{voidds}_{DocUtils.shortenURI(pred)}')
            g.add((voidds, VOID.propertyPartition, cururi))
            g.add((cururi, RDF.type, VOID.Dataset))
            g.add((cururi, RDFS.label, Literal(f"Property Partition: {DocUtils.shortenURI(pred)}", lang="en")))
            g.add((cururi, VOID.property, URIRef(pred)))
            g.add((cururi, VOID.triples, Literal(str(propstats[pred]["triples"]), datatype=XSD.integer)))
            subjectstorender.add(cururi)
        for item in classtree["core"]["data"]:
            if item["type"] == "class":
                cururi = URIRef(f'{voidds}_{DocUtils.shortenURI(item["id"])}')
                g.add((voidds, VOID.classPartition, cururi))
                g.add((cururi, RDF.type, VOID.Dataset))
                g.add((cururi, RDFS.label, Literal(f'Class Partition: {DocUtils.shortenURI(item["id"])}', lang="en")))
                g.add((cururi, voidc, URIRef(item["id"])))
                if item["id"] in objectmap:
                    g.add((cururi, VOID.entities, Literal(str(objectmap[item["id"]]), datatype=XSD.integer)))
                # subjectstorender.add(URIRef(cururi))
        for prop in nonnscount:
            for ns in nonnscount[prop]:
                cururi = URIRef(
                    f'{voidds}_{ns.replace("http://", "").replace("https://", "").replace("/", "_").replace("#", "_")}')
                g.add((cururi, RDF.type, VOID.Linkset))
                g.add((cururi, RDFS.label, Literal(
                    f'Linkset: {DocUtils.shortenURI(str(voidds))} - {DocUtils.getLabelForObject(URIRef(ns), g, pubconfig["prefixes"])}',
                    lang="en")))
                g.add((cururi, VOID.subjectsTarget, voidds))
                g.add((cururi, VOID.objectsTarget, URIRef(ns)))
                g.add((cururi, VOID.linkPredicate, URIRef(prop)))
                g.add((cururi, VOID.triples, Literal(str(nonnscount[prop][ns]), datatype=XSD.integer)))
                subjectstorender.add(cururi)
        g.serialize(pubconfig["outpath"] + "/void.ttl", encoding="utf-8")
        return {"graph": g, "subjects": subjectstorender}

    @staticmethod
    def toHTML(stats, deploypath):
        result = f'<details><summary>Dataset Statistics <a href="{deploypath}/void.ttl" target="_blank">[VOID]</a></summary><table border="1"><thead><th>Property</th><th>Value</th></thead><tbody>'
        for stat in stats:
            result += f'<tr><td><a href="{stat}" target="_blank">"{DocUtils.shortenURI(stat)}</a></td><td><span property="{stat}" content="{stats[stat]}" datatype="http://www.w3.org/2001/XMLSchema#integer">"{stats[stat]}</span>&nbsp;<a href="http://www.w3.org/2001/XMLSchema#integer" style="color:#666;"><small>(xsd:integer)</small></a></td></tr>'
        result += "</tbody></table></details>"
        return result