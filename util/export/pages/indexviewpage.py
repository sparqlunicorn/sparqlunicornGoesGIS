from rdflib import Graph, URIRef
from ...doc.docutils import DocUtils
from ..exporterutils import ExporterUtils
import re
import urllib.parse

class IndexViewPage:


    @staticmethod
    def getAccessFromBaseURL(baseurl, savepath):
        return savepath.replace(baseurl, "")


    @staticmethod
    def createIndexPages(pubconfig,templates,apis,paths,subjectstorender,uritotreeitem,voidds,tree,classlist,graph,voidstatshtml,curlicense):
        indpcounter = 0
        # print("PATHS: "+str(paths))
        # print(tree)
        for path in paths:
            if indpcounter % 10 == 0:
                DocUtils.updateProgressBar(indpcounter, len(paths), "Creating Index Pages")
            subgraph = Graph(bind_namespaces="rdflib")
            checkdepth = DocUtils.checkDepthFromPath(path, pubconfig["outpath"], path) - 1
            sfilelink = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth,
                                                                    pubconfig["corpusid"] + '_search.js', False)
            classtreelink = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth,
                                                                        pubconfig["corpusid"] + "_classtree.js", False)
            stylelink = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth, "style.css",
                                                                    False)
            scriptlink = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth,
                                                                     "startscripts.js",
                                                                     False)
            proprelations = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth,
                                                                        "proprelations.js", False)
            epsgdefslink = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth, "epsgdefs.js",
                                                                       False)
            vowllink = DocUtils.generateRelativeLinkFromGivenDepth(pubconfig["prefixns"], checkdepth, "vowl_result.js",
                                                                   False)
            nslink = pubconfig["prefixns"] + str(
                IndexViewPage.getAccessFromBaseURL(str(pubconfig["outpath"]), str(path)))
            for sub in subjectstorender:
                if nslink in sub:
                    for tup in graph.predicate_objects(sub):
                        subgraph.add((sub, tup[0], tup[1]))
                        if apis["solidexport"]:
                            subgraph.add((URIRef(sub.replace("nslink", "")),
                                          RDF.type,
                                          URIRef("http://www.w3.org/ns/ldp#Container")))
                            subgraph.add((URIRef(sub.replace("nslink", "")),
                                          RDF.type,
                                          URIRef("http://www.w3.org/ns/ldp#BasicContainer")))
                            subgraph.add((URIRef(sub.replace("nslink", "")),
                                          RDF.type,
                                          URIRef("http://www.w3.org/ns/ldp#Resource")))
            for ex in pubconfig["exports"]:
                if ex in ExporterUtils.exportToFunction:
                    if ex not in ExporterUtils.rdfformats:
                        with open(path + "index." + str(ex), 'w', encoding='utf-8') as f:
                            ExporterUtils.exportToFunction[ex](subgraph, f, subjectstorender, classlist, ex)
                            f.close()
                    else:
                        ExporterUtils.exportToFunction[ex](subgraph, path + "index." + str(ex), subjectstorender,
                                                           classlist, ex)
            relpath = DocUtils.generateRelativePathFromGivenDepth(checkdepth)
            # print("RELPATH: " + str(relpath))
            indexhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], voidds, checkdepth,
                                                          str(nslink == pubconfig["prefixns"]).lower(), pubconfig)
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if pubconfig["offlinecompat"] else "")).replace(
                "{{baseurl}}",
                pubconfig["prefixns"]).replace(
                "{{relativedepth}}", str(checkdepth)).replace("{{relativepath}}", relpath).replace("{{toptitle}}",
                                                                                                   "Index page for " + nslink).replace(
                "{{title}}", "Index page for <span property=\"http://rdfs.org/ns/void#uriSpace\" content=\"" + str(
                    nslink) + "\">" + str(nslink) + "</span>").replace("{{startscriptpath}}", scriptlink).replace(
                "{{stylepath}}", stylelink).replace("{{vowlpath}}", vowllink) \
                .replace("{{classtreefolderpath}}", classtreelink).replace("{{baseurlhtml}}", nslink).replace(
                "{{proprelationpath}}", proprelations).replace("{{nonnslink}}", "").replace("{{scriptfolderpath}}",
                                                                                            sfilelink).replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace("{{subjectencoded}}",
                                                                                             urllib.parse.quote(
                                                                                                 str(voidds)))
            indexhtml += "<p property=\"http://rdfs.org/ns/void#feature\" resource=\"http://www.w3.org/ns/formats/Turtle\">This page shows information about linked data resources in <span property=\"http://rdfs.org/ns/void#feature\" resource=\"http://www.w3.org/ns/formats/RDFa\">HTML</span>. Choose the classtree navigation or search to browse the data</p>" + \
                         templates["vowltemplate"].replace("{{vowlpath}}", "minivowl_result.js")
            if pubconfig["startconcept"] is not None and path == pubconfig["outpath"] and pubconfig[
                "startconcept"] in uritotreeitem:
                startconcept = pubconfig["startconcept"]
                if pubconfig["createCollections"]:
                    indexhtml += f"<p>Start exploring the graph here: <img src=\"{tree['types'][uritotreeitem[startconcept][-1]['type']]['icon']}\" height=\"25\" width=\"25\" alt=\"" + \
                                 uritotreeitem[startconcept][-1][
                                     "type"] + "\"/><a property=\"http://rdfs.org/ns/void#rootResource\" resource=\"" + str(
                        startconcept) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                        pubconfig["prefixns"], 0, str(startconcept), True) + "\">" + DocUtils.shortenURI(
                        startconcept) + "</a></p>"
                else:
                    indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                 tree["types"][uritotreeitem[startconcept][-1]["type"]][
                                     "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + \
                                 uritotreeitem[startconcept][-1][
                                     "type"] + "\"/><a property=\"http://rdfs.org/ns/void#rootResource\" resource=\"" + str(
                        startconcept) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                        pubconfig["prefixns"], 0, str(startconcept), True) + "\">" + DocUtils.shortenURI(
                        startconcept) + "</a></p>"
            indexhtml += "<table about=\"" + str(
                voidds) + "\" typeof=\"http://rdfs.org/ns/void#Dataset\" property=\"http://rdfs.org/ns/void#dataDump\" resource=\"" + str(
                pubconfig[
                    "deploypath"] + "/index.ttl") + "\" class=\"description\" style =\"height: 100%; overflow: auto\" border=1 id=indextable><thead><tr><th>Class</th><th>Number of instances</th><th>Instance Example</th></tr></thead><tbody>"
            for item in tree["core"]["data"]:
                if (item["type"] == "geoclass" or item["type"] == "class" or item["type"] == "featurecollection" or
                    item["type"] == "geocollection") and "instancecount" in item and item["instancecount"] > 0:
                    exitem = None
                    for item2 in tree["core"]["data"]:
                        if item2["parent"] == item["id"] and (
                                item2["type"] == "instance" or item2["type"] == "geoinstance") and nslink in item2[
                            "id"]:
                            exitem = f"<td><img src=\"{tree['types'][item2['type']]['icon']}\" height=\"25\" width=\"25\" alt=\"{item2['type']}\"/><a property=\"http://rdfs.org/ns/void#exampleResource\" resource=\"" + str(
                                DocUtils.shortenURI(
                                    str(item2["id"]))) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                                pubconfig["prefixns"], checkdepth, str(re.sub("_suniv[0-9]+_", "", item2["id"])),
                                True) + "\">" + str(item2["text"]) + "</a></td>"
                            break
                    if exitem is not None:
                        if pubconfig["createCollections"]:
                            indexhtml += "<tr><td><img src=\"" + tree["types"][item["type"]][
                                "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + item[
                                             "type"] + "\"/><a property=\"http://rdfs.org/ns/void#exampleResource\" resource=\"" + str(
                                DocUtils.shortenURI(
                                    str(item["id"])) + "_collection/") + "\" href=\"" + DocUtils.shortenURI(
                                str(item["id"])) + "_collection/index.html\" target=\"_blank\">" + str(
                                item["text"]) + "</a></td>"
                        else:
                            indexhtml += f"<tr><td><img src=\"{tree['types'][item['type']]['icon']}\" height=\"25\" width=\"25\" alt=\"{item['type']}\"/><a  href=\"{item['id']}\" target=\"_blank\">{item['text']}</a></td>"
                        indexhtml += f"<td property=\"http://rdfs.org/ns/void#classPartition\" typeof=\"http://rdfs.org/ns/void#Dataset\" resource=\"{voidds}_{DocUtils.shortenURI(item['id'])}\"><span about=\"" + str(
                            voidds) + "_" + str(DocUtils.shortenURI(
                            item["id"])) + "\" property=\"http://rdfs.org/ns/void#class\" resource=\"" + str(
                            item["id"]) + "\"></span><span about=\"" + str(voidds) + "_" + str(DocUtils.shortenURI(
                            item["id"])) + "\" property=\"http://rdfs.org/ns/void#entities\" content=\"" + str(item[
                                                                                                                   "instancecount"]) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#integer\">" + str(
                            item["instancecount"]) + "</td>" + exitem + "</tr>"
            indexhtml += f"</tbody></table><script property=\"http://purl.org/dc/terms/modified\" content=\"{pubconfig['modtime']}\" datatype=\"http://www.w3.org/2001/XMLSchema#dateTime\">$('#indextable').DataTable();</script>"
            tempfoot = DocUtils.replaceStandardVariables(templates["footer"], "", checkdepth,
                                                         str(nslink == pubconfig["prefixns"]).lower(),
                                                         pubconfig).replace(
                "{{license}}", curlicense).replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}",
                                                                                                      "").replace(
                "{{stats}}", voidstatshtml)
            tempfoot = DocUtils.replaceCitationLink(tempfoot, "Index page for " + nslink, "", pubconfig)
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot,
                                                        [True, apis["ogcapifeatures"], apis["iiif"], apis["ckan"]],
                                                        [
                                                            f"<a href=\"{DocUtils.generateRelativePathFromGivenDepth(checkdepth)}sparql.html?endpoint={pubconfig['deploypath']}\">[SPARQL]</a>&nbsp;",
                                                            f"<a href=\"{relpath}api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            f"<a href=\"{relpath}iiif/\">[IIIF]</a>&nbsp;",
                                                            f"<a href=\"{relpath}api/3/\">[CKAN]</a>"
                                                        ], "{{apis}}")
            indexhtml += tempfoot
            # print(path)
            with open(path + "index.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()