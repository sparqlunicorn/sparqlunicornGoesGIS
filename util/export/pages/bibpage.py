from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils
from rdflib import URIRef

class BibPage:

    def pageWidgetConstraint(self):
        return DocConfig.bibtextypemappings

    def collectionConstraint(self):
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
            if str(tup[0]) == "http://purl.org/dc/elements/1.1/creator" or str(
                    tup[0]) == "http://purl.org/dc/terms/creator":
                if "author" not in bibtexitem:
                    bibtexitem["author"] = []
                if isinstance(tup[1], URIRef):
                    bibtexitem["author"].append(DocUtils.getLabelForObject(tup[1], graph))
                else:
                    bibtexitem["author"].append(str(tup[1]))
            elif str(tup[0]) == "http://purl.org/ontology/bibo/pageStart":
                if "pages" not in bibtexitem:
                    bibtexitem["pages"] = {}
                bibtexitem["pages"]["start"] = str(tup[1])
            elif str(tup[0]) == "http://purl.org/ontology/bibo/pageEnd":
                if "pages" not in bibtexitem:
                    bibtexitem["pages"] = {}
                bibtexitem["pages"]["end"] = str(tup[1])
            elif str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and str(
                    tup[1]) in DocConfig.bibtextypemappings:
                bibtexitem["type"] = DocConfig.bibtextypemappings[str(tup[1])]
            elif str(tup[0]) in bibtexmappings:
                if isinstance(tup[1], URIRef):
                    bibtexitem[bibtexmappings[str(tup[0])]] = DocUtils.getLabelForObject(tup[1], graph)
                else:
                    bibtexitem[bibtexmappings[str(tup[0])]] = str(tup[1])
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

    def generatePageWidget(self,graph,memberid,templates,f,pageWidget=False):
        print("PageWidget")
        self.resolveBibtexReference(memberid,graph)

    def generateCollectionWidget(self, graph,templates, subject, f):
        print("CollectionWidget")
        for bibentry in graph.objects(subject, URIRef("http://www.w3.org/ns/lemon/lime#entry"), True):
            self.generatePageWidget(graph,bibentry,f,True)


