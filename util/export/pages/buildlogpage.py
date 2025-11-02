from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils


class BuildLogPage():

    def pageWidgetConstraint(self):
        print("PageWidgetConstraint")
        return []

    def collectionConstraint(self):
        return []

    def generatePageWidget(self, graph, subject, templates, f, onlybody=False):
        print("PageWidget")
        f.write(templates["buildlog"])

    def generateCollectionWidget(self, graph, templates, subject, f):
        print("CollectionWidget")


    def generatePageView(self, templates,pubconfig,curlicense,voidstatshtml, g, f):
        print("PageView")
        blhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "false",pubconfig)

        blhtml = blhtml.replace("{{iconprefixx}}", ("icons/" if pubconfig["offlinecompat"] else "")).replace(
            "{{baseurl}}", pubconfig["prefixns"]).replace("{{relativedepth}}", "0").replace("{{relativepath}}",
                                                                                      ".").replace("{{toptitle}}",
                                                                                                   "Build Statistics").replace(
            "{{title}}", "Build Statistics").replace("{{startscriptpath}}", "startscripts.js").replace(
            "{{stylepath}}", "style.css") \
            .replace("{{classtreefolderpath}}", pubconfig["corpusid"] + "_classtree.js").replace("{{baseurlhtml}}", "").replace(
            "{{nonnslink}}", "").replace("{{scriptfolderpath}}", pubconfig["corpusid"] + "_search.js").replace("{{exports}}",
                                                                                                  templates[
                                                                                                      "nongeoexports"]).replace(
            "{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace("{{bibtex}}",
                                                                                                      "").replace(
            "{{proprelationpath}}", "proprelations.js")
        f.write(blhtml)
        f.write(templates["buildlog"])
        #sparqlhtml += templates["sparqltemplate"]
        tempfoot = DocUtils.replaceStandardVariables(templates["footer"], "", "0", "false",pubconfig).replace("{{license}}",
                                                                                                curlicense).replace(
            "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace("{{citationlink}}","").replace("{{stats}}",
                                                                                         voidstatshtml)
        tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, True, pubconfig["apis"]["ogcapifeatures"], pubconfig["apis"]["iiif"],
                                                               pubconfig["apis"]["ckan"]],
                                                    [
                                                        f"<a href=\"{pubconfig['deploypath']}/sparql.html?endpoint={pubconfig['deploypath']}\">[SPARQL]</a>&nbsp;",
                                                        f"<a href=\"{pubconfig['deploypath']}/buildlog.html\">[BuildLog]</a>&nbsp;",
                                                        f"<a href=\"{pubconfig['deploypath']}/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                        f"<a href=\"{pubconfig['deploypath']}/iiif/\">[IIIF]</a>&nbsp;",
                                                        f"<a href=\"{pubconfig['deploypath']}/api/3/\">[CKAN]</a>"
                                                    ], "{{apis}}")
        f.write(tempfoot)
        #f.write(sparqlhtml)
