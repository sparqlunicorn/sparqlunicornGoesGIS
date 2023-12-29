
class TextAnnoPage:

    tableheader="<thead><th>Annotation</th><th>Position</th><th>Annotation Body</th></thead>"

    def generatePageWidget(self, textannos, f, onlybody=False):
        print("PageWidget")
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


    def generateCollectionWidget(self, graph, templates, subject, f):
        print("CollectionWidget")


    def generatePageView(self, headertemplate, footertemplate, g, f):
        f.write(str(headertemplate))
        print("PageView")