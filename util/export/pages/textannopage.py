from rdflib import URIRef
from ...doc.docutils import DocUtils

class TextAnnoPage:

    tableheader="<thead><th>Annotation</th><th>Type</th><th>Position</th><th>Annotation Body</th></thead>"

    @staticmethod
    def generatePageWidget(graph, textannos, templates, f, pageWidget=False):
        for textanno in textannos:
            if isinstance(textanno, dict):
                if "src" in textanno:
                    f.write("<span style=\"font-weight:bold\" class=\"textanno\" start=\"" + str(
                        textanno["start"]) + "\" end=\"" + str(textanno["end"]) + "\" exact=\"" + str(
                        textanno["exact"]) + "\" src=\"" + str(textanno["src"]) + "\"><mark>" + str(
                        textanno["exact"]) + "</mark></span>")
                else:
                    f.write("<span style=\"font-weight:bold\" class=\"textanno\" start=\"" + str(
                        textanno["start"]) + "\" end=\"" + str(textanno["end"]) + "\" exact=\"" + str(
                        textanno["exact"]) + "\"><mark>" + str(textanno["exact"]) + "</mark></span>")


    @staticmethod
    def generateCollectionWidget(graph, templates, subject,prefixnamespace,outpath, f):
        print("CollectionWidget")
        f.write("<table id=\"lexicon\">"+TextAnnoPage.tableheader+"<tbody>")
        for anno in graph.subjects_objects("http://www.w3.org/ns/oa#hasSelector"):
            thetype=None
            start=None
            end=None
            exact=None
            for pred in graph.predicate_objects(anno[1]):
                if str(pred[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#":
                    thetype=str(pred[1])
                    continue
                elif str(pred[0])=="http://www.w3.org/ns/oa#start":
                    start=str(pred[1])
                elif str(pred[0]) == "http://www.w3.org/ns/oa#start":
                    end = str(pred[1])
                elif str(pred[0]) == "http://www.w3.org/ns/oa#exact":
                    exact = str(pred[1])
            annobody=" ".join(graph.objects(anno[0],URIRef("http://www.w3.org/ns/oa#hasBody")))
            #for obj in graph.objects(anno[0],URIRef("http://www.w3.org/ns/oa#hasBody")):
            #    annobody+=str(obj)+" "
            f.write("<tr><td><a href=\""+str(anno.replace(prefixnamespace,outpath))+"\">"+str(DocUtils.shortenURI(anno))+"</a></td><td><a href=\""+str(thetype)+"\">"+DocUtils.shortenURI(str(thetype))+"</a></td><td>"+str(exact)+" ["+str(start)+"-"+str(end)+"]</td><td>"+str(annobody)+"</td></tr>")
        f.write("</tbody></table>")


    def generatePageView(self, headertemplate, footertemplate, g, f):
        f.write(str(headertemplate))
        print("PageView")