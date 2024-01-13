from rdflib import URIRef, Literal

from ...doc.docutils import DocUtils
from ....util.sparqlutils import SPARQLUtils

class LexiconPage:

    tableheader="<thead><th>Lemma</th><th>Lexical Category</th><th>Language</th><th>Forms</th><th>Senses</th></thead>"

    def extractLexEntry(self,graph,subject):
        forms = []
        senses = []
        lemma = DocUtils.shortenURI(subject)
        lexcat = "N/A"
        language = ""
        for lexprop in graph.predicate_objects(subject, True):
            if lexprop[0] == URIRef("http://www.w3.org/ns/lemon/ontolex#sense"):
                label=None
                senseref=""
                for senseprop in graph.predicate_objects(lexprop[1], True):
                    if str(senseprop[0]) in SPARQLUtils.labelproperties and isinstance(senseprop[1],Literal):
                        label=senseprop[1]
                    if str(senseprop[0])=="http://www.w3.org/ns/lemon/ontolex#reference":
                        senseref=senseprop[1]
                senses.append({"uri":str(lexprop[1]),"label":label,"reference":str(senseref)})
            if lexprop[0] == URIRef("http://www.w3.org/ns/lemon/ontolex#lexicalForm") or lexprop[0] == URIRef("http://www.w3.org/ns/lemon/ontolex#form"):
                label=None
                for formprop in graph.predicate_objects(lexprop[1], True):
                    if str(formprop[0]) in SPARQLUtils.labelproperties and isinstance(formprop[1], Literal):
                        label = formprop[1]
                forms.append({"uri": str(lexprop[1]), "label": label})
            if lexprop[0] == URIRef("http://www.w3.org/ns/lemon/ontolex#lemma") or lexprop[0] == URIRef("http://www.w3.org/ns/lemon/ontolex#canonicalForm"):
                lemma = str(lexprop[1])
            if lexprop[0] == URIRef("http://purl.org/dc/terms/") or lexprop[0] == URIRef("http://www.w3.org/ns/lemon/lime#language"):
                language = str(lexprop[1])
            if lexprop[0] == URIRef("http://www.w3.org/ns/lemon/ontolex#lexicalCategory"):
                lexcat = str(lexprop[1])
        return {"lemma":lemma,"lexcat":lexcat,"language":language,"forms":forms,"senses":senses}

    def generatePageWidget(self,graph,subject,f,parameters={},onlybody=False):
        print("PageWidget")
        lexentry=self.extractLexEntry(graph,subject)
        if not onlybody:
            f.write("<table id=\"lexicon\">"+self.tableheader+"<tbody>")
        f.write("<tr><td><a href=\""+str(subject)+"\" target=\"_blank\">"+str(lexentry["lemma"])+"</a></td><td>"+str(lexentry["lexcat"])+"</td><td>"+str(lexentry["language"])+"</td><td>")
        for form in lexentry["forms"]:
            f.write("<a href=\""+str(form["uri"])+"\" target=\"_blank\">"+str(form["label"])+"</a> ")
        f.write("</td><td>")
        for sense in lexentry["senses"]:
            if sense["reference"]!="":
                f.write("<a href=\"" + str(sense["uri"]) + "\" target=\"_blank\">" + str(sense["label"]) + "</a> <a href=\""+str(sense["reference"])+"\" target=\"_blank\">["+DocUtils.shortenURI(str(sense["reference"]))+"]</a>")
            else:
                f.write("<a href=\""+str(sense["uri"])+"\" target=\"_blank\">"+str(sense["label"])+"</a> ")
        f.write("</td></tr>")
        if not onlybody:
            f.write("</tbody></table><script>$('#lexicon').DataTable();</script>")

    def generateCollectionWidget(self,graph,templates,subject,f,parameters={}):
        f.write("<table id=\"lexicon\">"+self.tableheader+"<tbody>")
        for lexentry in graph.objects(subject, URIRef("http://www.w3.org/ns/lemon/lexicog#entry"), True):
            self.generatePageWidget(graph,lexentry,f,parameters,True)
        f.write("</tbody></table><script>$('#lexicon').DataTable();</script>")

    def generatePageView(self,headertemplate,footertemplate,g,f):
        f.write(str(headertemplate))
        print("PageView")


    def pageWidgetConstraint(self):
        return ["http://www.w3.org/ns/lemon/lexicog#Entry", "http://www.w3.org/ns/lemon/ontolex#Entry",
     "http://www.w3.org/ns/lemon/lexicog#LexicalEntry", "http://www.w3.org/ns/lemon/ontolex#LexicalEntry",
     "http://www.w3.org/ns/lemon/ontolex#Word","http://www.w3.org/ns/lemon/lexicog#Word"]

    def collectionConstraint(self):
        return ["http://www.w3.org/ns/lemon/lime#Lexicon"]


