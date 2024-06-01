from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils
from rdflib import URIRef
from rdflib.namespace import RDFS

class BibPage:

    @staticmethod
    def pageWidgetConstraint():
        return DocConfig.bibtextypemappings

    @staticmethod
    def collectionConstraint():
        return ["http://purl.org/ontology/bibo/Collection"]

    @staticmethod
    def resolveBibtexReference(predobjs, item, graph):
        bibtexmappings = {"http://purl.org/dc/elements/1.1/title": "title",
                          "http://purl.org/dc/terms/title": "title",
                          "http://purl.org/dc/terms/created": "year",
                          "http://purl.org/dc/terms/issued": "year",
                          "http://purl.org/ontology/bibo/number": "number",
                          "http://purl.org/ontology/bibo/publisher": "publisher",
                          "http://purl.org/dc/terms/publisher": "publisher",
                          "http://purl.org/dc/terms/language": "language",
                          "http://purl.org/ontology/bibo/issuer": "journal",
                          "http://purl.org/ontology/bibo/volume": "volume",
                          "http://purl.org/ontology/bibo/doi": "doi",
                          "http://purl.org/ontology/bibo/eissn": "eissn",
                          "http://purl.org/ontology/bibo/eprint": "eprint",
                          "http://purl.org/ontology/bibo/url": "url",
                          "http://purl.org/ontology/bibo/issn": "issn",
                          "http://purl.org/ontology/bibo/isbn": "isbn",
                          "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "type"
                          }
        bibtexitem = {"type": "@misc"}
        for tup in predobjs:
            tupstr=str(tup[0])
            tupstrobj=str(tup[1])
            if tupstr == "http://purl.org/dc/elements/1.1/creator" or tupstr == "http://purl.org/dc/terms/creator":
                if "author" not in bibtexitem:
                    bibtexitem["author"] = []
                if isinstance(tup[1], URIRef):
                    bibtexitem["author"].append(DocUtils.getLabelForObject(tup[1], graph))
                else:
                    bibtexitem["author"].append(tupstrobj)
            elif tupstr == "http://purl.org/ontology/bibo/pageStart":
                if "pages" not in bibtexitem:
                    bibtexitem["pages"] = {}
                bibtexitem["pages"]["start"] = tupstrobj
            elif tupstr == "http://purl.org/ontology/bibo/pageEnd":
                if "pages" not in bibtexitem:
                    bibtexitem["pages"] = {}
                bibtexitem["pages"]["end"] = tupstrobj
            elif tupstr == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and tupstrobj in DocConfig.bibtextypemappings:
                bibtexitem["type"] = DocConfig.bibtextypemappings[tupstrobj]
            elif tupstr in bibtexmappings:
                if isinstance(tup[1], URIRef):
                    bibtexitem[bibtexmappings[tupstr]] = DocUtils.getLabelForObject(tup[1], graph)
                else:
                    bibtexitem[bibtexmappings[tupstr]] = tupstrobj
        res = bibtexitem["type"] + "{" + DocUtils.shortenURI(item) + ",\n"
        for bibpart in sorted(bibtexitem):
            if bibpart == "type":
                continue
            res += bibpart + "={"
            if bibpart == "author":
                first = True
                for author in bibtexitem["author"]:
                    if first:
                        res += author + " "
                        first = False
                    else:
                        res += "and " + author + " "
                res = res[0:-1]
                res += "},\n"
            elif bibpart == "pages":
                res += bibtexitem[bibpart]["start"] + "--" + bibtexitem[bibpart]["end"] + "},\n"
            else:
                res += str(bibtexitem[bibpart]) + "},\n"
        res = res[0:-2]
        res += "\n}"
        return res

    @staticmethod
    def generatePageWidget(graph,memberid,templates,f,pageWidget=False):
        return BibPage.resolveBibtexReference(graph.predicate_objects(memberid),memberid,graph)

    @staticmethod
    def generateCollectionWidget(graph,subject,templates, f):
        f.write("<details><summary>[BIBTEX]</summary><pre>")
        for bibentry in graph.objects(subject, RDFS.member, True):
            f.write(BibPage.generatePageWidget(graph,bibentry,templates,f,True))
            f.write("\n")
        f.write("</pre></details>")


