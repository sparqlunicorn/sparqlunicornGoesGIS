from ...doc.docutils import DocUtils
from ...doc.literalutils import LiteralUtils
from ...doc.docutils import DocConfig
from ...sparqlutils import SPARQLUtils
from ..pages.bibpage import BibPage
from ..pages.owltimepage import OWLTimePage
from rdflib import URIRef, Graph, BNode, Literal
from qgis.core import Qgis, QgsMessageLog
import re
import os
import json
import urllib
import traceback

from ..api.iiifexporter import IIIFAPIExporter
from ..pages.geometryviewpage import GeometryViewPage
from ..pages.lexiconpage import LexiconPage
from ..pages.observationpage import ObservationPage
from ..pages.personpage import PersonPage


class HTMLExporter:
    listthreshold = 5
    maxlistthreshold = 1500

    featurecollectionspaths = {}
    iiifmanifestpaths = {"default": []}
    imagetoURI = {}
    geocache = {}

    def __init__(self, prefixes, prefixnamespace, prefixnsshort, license, labellang, outpath,
                 metadatatable, generatePagesForNonNS, apis,templates,namespaceshort,typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                 imagemetadata=None,localOptimized=False,
                 deploypath="", logoname="", offlinecompat=False):
        self.prefixes = prefixes
        self.prefixnamespace = prefixnamespace
        self.outpath = outpath
        self.deploypath = deploypath
        self.metadatatable = metadatatable
        self.logoname = logoname
        self.templates = templates
        self.localOptimized=localOptimized
        self.apis = apis
        self.has3d=False
        self.labellang = labellang
        self.license = license
        self.licenseuri=""
        self.publisher=""
        self.publishingorg=""
        self.datasettitle=""
        self.typeproperty=typeproperty
        self.prefixnsshort = prefixnsshort
        self.imagemetadata = imagemetadata
        self.namespaceshort = namespaceshort
        self.generatePagesForNonNS = generatePagesForNonNS
        self.offlinecompat = offlinecompat

    def replaceStandardVariables(self, template, subject, checkdepth, indexpage):
        template = template.replace("{{indexpage}}", str(indexpage)).replace("{{subject}}", str(subject)).replace(
            "{{relativedepth}}", str(checkdepth)) \
            .replace("{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace(
            "{{deploypath}}", self.deploypath) \
            .replace("{{publishingorg}}", self.publishingorg).replace("{{publisher}}", self.publisher).replace(
            "{{datasettitle}}", self.datasettitle) \
            .replace("{{logo}}", self.logoname)
        return template

    def createHTML(self, savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,
                   uritotreeitem, curlicense, subjectstorender, postprocessing, nonnsmap=None, nonns=False,
                   foundlabel=""):
        tablecontents = ""
        metadatatablecontents = ""
        geojsonrep = None
        epsgcode = ""
        foundmedia = {"audio": {}, "video": {}, "image": {}, "mesh": {}}
        savepath = savepath.replace("\\", "/")
        checkdepth = 0
        if not nonns:
            checkdepth = DocUtils.checkDepthFromPath(savepath, baseurl, subject)
        logo = ""
        if self.logoname is not None and self.logoname != "":
            logo = "<img src=\"" + self.logoname + "\" alt=\"logo\" width=\"25\" height=\"25\"/>&nbsp;&nbsp;"
        textannos = []
        foundvals = set()
        imageannos = []
        annobodies = []
        image3dannos = []
        predobjmap = {}
        curtypes = set()
        comment = {}
        parentclass = None
        inverse = False
        dateprops = []
        timeobj = None
        tablecontentcounter = -1
        metadatatablecontentcounter = -1
        if uritotreeitem is not None and str(subject) in uritotreeitem and uritotreeitem[str(subject)][-1][
            "parent"].startswith("http"):
            parentclass = str(uritotreeitem[str(subject)][-1]["parent"])
            if parentclass not in uritotreeitem:
                uritotreeitem[parentclass] = [
                    {"id": parentclass, "parent": "#", "type": "class", "text": DocUtils.shortenURI(str(parentclass)),
                     "data": {}}]
            # print(uritotreeitem[parentclass])
            uritotreeitem[parentclass][-1]["instancecount"] = 0
        ttlf = Graph(bind_namespaces="rdflib")
        # ttlf = open(savepath + "/index.ttl", "w", encoding="utf-8")
        if parentclass is not None:
            uritotreeitem[parentclass][-1]["data"]["to"] = {}
            uritotreeitem[parentclass][-1]["data"]["from"] = {}
        hasnonns = set()
        thetypes = set()
        itembibtex = ""
        collections = set()
        if predobjs is not None:
            for tup in sorted(predobjs, key=lambda tup: tup[0]):
                if str(tup[0]) not in predobjmap:
                    predobjmap[str(tup[0])] = []
                predobjmap[str(tup[0])].append(tup[1])
                if parentclass is not None and str(tup[0]) not in uritotreeitem[parentclass][-1]["data"]["to"]:
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])] = {}
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]["instancecount"] = 0
                if parentclass is not None:
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]["instancecount"] += 1
                    uritotreeitem[parentclass][-1]["instancecount"] += 1
                if isinstance(tup[1], URIRef):
                    for item in graph.objects(tup[1], URIRef(self.typeproperty)):
                        thetypes.add(str(item))
                        if parentclass is not None:
                            if item not in uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]:
                                uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item] = 0
                            uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item] += 1
                    if baseurl not in str(tup[1]) and str(tup[0]) != self.typeproperty:
                        hasnonns.add(str(tup[1]))
                        if nonnsmap is not None:
                            if str(tup[1]) not in nonnsmap:
                                nonnsmap[str(tup[1])] = set()
                            nonnsmap[str(tup[1])].add(subject)
            for tup in sorted(predobjmap):
                if self.metadatatable and tup not in DocConfig.labelproperties and DocUtils.shortenURI(str(tup),
                                                                                                       True) in DocConfig.metadatanamespaces:
                    thetable = metadatatablecontents
                    metadatatablecontentcounter += 1
                    if metadatatablecontentcounter % 2 == 0:
                        thetable += "<tr class=\"odd\">"
                    else:
                        thetable += "<tr class=\"even\">"
                else:
                    thetable = tablecontents
                    tablecontentcounter += 1
                    if tablecontentcounter % 2 == 0:
                        thetable += "<tr class=\"odd\">"
                    else:
                        thetable += "<tr class=\"even\">"
                if str(tup) == self.typeproperty:
                    for tp in predobjmap[tup]:
                        thetypes.add(str(tp))
                        curtypes.add(str(tp))
                        if str(tp) in DocConfig.collectionclasses:
                            uritotreeitem[str(tp)][-1]["instancecount"] += 1
                            collections.add(DocConfig.collectionclasses[str(tp)])
                        if str(tp) in DocConfig.bibtextypemappings:
                            itembibtex = "<details><summary>[BIBTEX]</summary><pre>" + str(
                                BibPage.resolveBibtexReference(graph.predicate_objects(subject), subject,
                                                               graph)) + "</pre></details>"
                thetable = HTMLExporter.formatPredicate(tup, baseurl, checkdepth, thetable, graph, inverse,
                                                        self.labellang, self.prefixes)
                if str(tup) in DocConfig.labelproperties:
                    for lab in predobjmap[tup]:
                        if lab.language == self.labellang:
                            foundlabel = lab
                    if foundlabel == "":
                        foundlabel = str(predobjmap[tup][0])
                if str(tup) in DocConfig.commentproperties:
                    comment[str(tup)] = str(predobjmap[tup][0])
                if len(predobjmap[tup]) > 0:
                    thetable += "<td class=\"wrapword\">"
                    if len(predobjmap[tup]) > HTMLExporter.listthreshold:
                        thetable += "<details><summary>" + str(len(predobjmap[tup])) + " values</summary>"
                    if len(predobjmap[tup]) > 1:
                        thetable += "<ul>"
                    labelmap = {}
                    itemcounter = 0
                    for item in predobjmap[tup]:
                        if itemcounter >= HTMLExporter.maxlistthreshold:
                            break
                        if ("POINT" in str(item).upper() or "POLYGON" in str(item).upper() or "LINESTRING" in str(
                                item).upper()) and tup in DocConfig.valueproperties and self.typeproperty in predobjmap and URIRef(
                            "http://www.w3.org/ns/oa#WKTSelector") in predobjmap[self.typeproperty]:
                            image3dannos.append({"value": str(item)})
                        elif "<svg" in str(item):
                            foundmedia["image"][str(item)] = {}
                        elif "http" in str(item):
                            if isinstance(item, Literal):
                                ext = "." + ''.join(filter(str.isalpha, str(item.value).split(".")[-1]))
                            else:
                                ext = "." + ''.join(filter(str.isalpha, str(item).split(".")[-1]))
                            if ext in DocConfig.fileextensionmap:
                                foundmedia[DocConfig.fileextensionmap[ext]][str(item)] = {}
                        elif tup in DocConfig.valueproperties:
                            foundvals.add((str(tup), str(item)))
                        res = HTMLExporter.createHTMLTableValueEntry(subject, tup, item, ttlf, graph,
                                                                     baseurl, checkdepth, geojsonrep, foundmedia,
                                                                     imageannos,
                                                                     textannos, image3dannos, annobodies, dateprops,
                                                                     inverse,
                                                                     nonns, self.labellang, self.typeproperty,
                                                                     self.namespaceshort, self.generatePagesForNonNS,
                                                                     self.prefixes)
                        geojsonrep = res["geojson"]
                        foundmedia = res["foundmedia"]
                        imageannos = res["imageannos"]
                        textannos = res["textannos"]
                        image3dannos = res["image3dannos"]
                        annobodies = res["annobodies"]
                        # print("GOT ANNO BODIES "+str(annobodies))
                        if res["timeobj"] != None and res["timeobj"] != []:
                            # print("RESTIMEOBJ: "+str(timeobj))
                            timeobj = res["timeobj"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]] = ""
                        if len(predobjmap[tup]) > 1:
                            labelmap[res["label"]] += "<li>" + str(res["html"]) + "</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                        itemcounter += 1
                    for lab in sorted(labelmap):
                        thetable += str(labelmap[lab])
                    if len(predobjmap[tup]) >= HTMLExporter.maxlistthreshold:
                        tablecontents += "<li>(...)</li>"
                    if len(predobjmap[tup]) > 1:
                        thetable += "</ul>"
                    if len(predobjmap[tup]) > HTMLExporter.listthreshold:
                        thetable += "</details>"
                    thetable += "</td>"
                else:
                    thetable += "<td class=\"wrapword\"></td>"
                thetable += "</tr>"
                if self.metadatatable and tup not in DocConfig.labelproperties and DocUtils.shortenURI(str(tup),
                                                                                                  True) in DocConfig.metadatanamespaces:
                    metadatatablecontents = thetable
                else:
                    tablecontents = thetable
        subpredsmap = {}
        if subpreds != None:
            for tup in sorted(subpreds, key=lambda tup: tup[1]):
                if str(tup[1]) not in subpredsmap:
                    subpredsmap[str(tup[1])] = []
                subpredsmap[str(tup[1])].append(tup[0])
                if parentclass != None and str(tup[1]) not in uritotreeitem[parentclass][-1]["data"]["from"]:
                    uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])] = {}
                    uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]["instancecount"] = 0
                if isinstance(tup[0], URIRef):
                    for item in graph.objects(tup[0], URIRef(self.typeproperty)):
                        if parentclass != None:
                            if item not in uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]:
                                uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])][item] = 0
                            uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])][item] += 1
            for tup in subpredsmap:
                tablecontentcounter += 1
                if tablecontentcounter % 2 == 0:
                    tablecontents += "<tr class=\"odd\">"
                else:
                    tablecontents += "<tr class=\"even\">"
                tablecontents = HTMLExporter.formatPredicate(tup, baseurl, checkdepth, tablecontents, graph, True,
                                                             self.labellang, self.prefixes)
                if len(subpredsmap[tup]) > 0:
                    tablecontents += "<td class=\"wrapword\">"
                    if len(subpredsmap[tup]) > HTMLExporter.listthreshold:
                        tablecontents += "<details><summary>" + str(len(subpredsmap[tup])) + " values</summary>"
                    if len(subpredsmap[tup]) > 1:
                        tablecontents += "<ul>"
                    labelmap = {}
                    itemcounter = 0
                    for item in subpredsmap[tup]:
                        if itemcounter >= HTMLExporter.maxlistthreshold:
                            break
                        if subjectstorender is not None and item not in subjectstorender and baseurl in str(item):
                            postprocessing.add((item, URIRef(tup), subject))
                        res = HTMLExporter.createHTMLTableValueEntry(subject, tup, item, None, graph,
                                                                     baseurl, checkdepth, geojsonrep, foundmedia,
                                                                     imageannos,
                                                                     textannos, image3dannos, annobodies, None, True,
                                                                     nonns, self.labellang, self.typeproperty,
                                                                     self.namespaceshort, self.generatePagesForNonNS,
                                                                     self.prefixes)
                        foundmedia = res["foundmedia"]
                        imageannos = res["imageannos"]
                        image3dannos = res["image3dannos"]
                        annobodies = res["annobodies"]
                        # print("POSTPROC ANNO BODIES "+str(annobodies))
                        if nonns and str(tup) != self.typeproperty:
                            hasnonns.add(str(item))
                        if nonns:
                            geojsonrep = res["geojson"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]] = ""
                        if len(subpredsmap[tup]) > 1:
                            labelmap[res["label"]] += "<li>" + str(res["html"]) + "</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                        itemcounter += 1
                    for lab in sorted(labelmap):
                        tablecontents += str(labelmap[lab])
                    if len(subpredsmap[tup]) >= HTMLExporter.maxlistthreshold:
                        tablecontents += "<li>(...)</li>"
                    if len(subpredsmap[tup]) > 1:
                        tablecontents += "</ul>"
                    if len(subpredsmap[tup]) > HTMLExporter.listthreshold:
                        tablecontents += "</details>"
                    tablecontents += "</td>"
                else:
                    tablecontents += "<td class=\"wrapword\"></td>"
                tablecontents += "</tr>"
        if self.licenseuri != None:
            ttlf.add((subject, URIRef("http://purl.org/dc/elements/1.1/license"), URIRef(self.licenseuri)))
        if self.apis["solidexport"] != None:
            ttlf.add((subject, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                      URIRef("http://www.w3.org/ns/ldp#Resource")))
            ttlf.add((subject, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                      URIRef("https://www.iana.org/assignments/media-types/text/turtle#Resource")))
        nonnslink = ""
        if nonns:
            QgsMessageLog.logMessage("NonNS Savepath HTMLEx Prev " +savepath, "OntdocGeneration", Qgis.Info)
            if "http:" in savepath:
                completesavepath = savepath[0:savepath.find("http:") - 1] + savepath[savepath.find("http:"):0].replace(
                    ":", "_").replace("/", "_")
            else:
                completesavepath = savepath[0:savepath.rfind("/")+1]+savepath[savepath.rfind("/")+1:].replace(":", "_").replace("/", "_")
            QgsMessageLog.logMessage("NonNS Savepath HTMLEx Post " +completesavepath, "OntdocGeneration", Qgis.Info)
            nonnslink = "<div>This page describes linked instances to the concept  <a target=\"_blank\" href=\"" + str(
                subject) + "\">" + str(foundlabel) + " (" + str(DocUtils.shortenURI(
                subject)) + ") </a> in this knowledge graph. It is defined <a target=\"_blank\" href=\"" + str(
                subject) + "\">here</a></div>"
        else:
            if "/" in savepath and ":" in savepath:
                savepath=savepath[0:savepath.find("/")]+savepath[savepath.find("/"):].replace(":","_")
            completesavepath = savepath + "/index.html"
        if not nonns:
            if os.path.exists(savepath):
                try:
                    ttlf.serialize(savepath + "/index.ttl", encoding="utf-8")
                    with open(savepath + "/index.json", 'w', encoding='utf-8') as f:
                        f.write(json.dumps(predobjmap))
                        f.close()
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
        else:
            if os.path.exists(completesavepath):
                return
        with open(completesavepath, 'w', encoding='utf-8') as f:
            searchfilelink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, searchfilename, False)
            classtreelink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, classtreename, False)
            csslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "style.css", False)
            startscriptlink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js",
                                                                          False)
            proprelationslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "proprelations.js",
                                                                            False)
            epsgdefslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "epsgdefs.js", False)
            vowlresultlink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "vowl_result.js",
                                                                         False)
            if geojsonrep != None:
                myexports = self.templates["geoexports"]
            else:
                myexports = self.templates["nongeoexports"]
            relpath = DocUtils.generateRelativePathFromGivenDepth(checkdepth)
            if foundlabel == None or foundlabel == "":
                foundlabel = DocUtils.shortenURI(str(subject))
            f.write(self.replaceStandardVariables(self.templates["htmltemplate"], subject, checkdepth, "false").replace(
                "{{iconprefixx}}", (relpath + "icons/" if self.offlinecompat else "")).replace("{{baseurl}}",
                                                                                               baseurl).replace(
                "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(checkdepth)).replace(
                "{{relativedepth}}", str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace(
                "{{toptitle}}", foundlabel).replace(
                "{{startscriptpath}}", startscriptlink).replace("{{epsgdefspath}}", epsgdefslink).replace(
                "{{bibtex}}", itembibtex).replace("{{vowlpath}}", vowlresultlink).replace("{{proprelationpath}}",
                                                                                          proprelationslink).replace(
                "{{stylepath}}", csslink).replace("{{title}}",
                                                  "<a href=\"" + str(subject) + "\">" + str(
                                                      foundlabel) + "</a>").replace(
                "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}",
                                                                                           "").replace(
                "{{scriptfolderpath}}", searchfilelink).replace("{{classtreefolderpath}}", classtreelink).replace(
                "{{exports}}", myexports).replace("{{nonnslink}}", str(nonnslink)).replace("{{subjectencoded}}",
                                                                                           urllib.parse.quote(
                                                                                               str(subject))))
            for comm in comment:
                f.write(self.templates["htmlcommenttemplate"].replace("{{comment}}",
                                                                 DocUtils.shortenURI(comm) + ":" + comment[comm]))
            # for fval in foundvals:
            #    f.write(templates["htmlcommenttemplate"].replace("{{comment}}", "<b>Value "+ DocUtils.shortenURI(str(fval[0]))+": <mark>" + str(fval[1]) + "</mark></b>"))
            if len(foundmedia["mesh"]) > 0 and len(image3dannos) > 0:
                if self.apis["iiif"]:
                    self.iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath,
                                                             foundmedia["mesh"], image3dannos, annobodies,
                                                             str(subject), self.prefixnamespace, self.imagetoURI,
                                                             self.imagemetadata, DocConfig.metadatanamespaces,
                                                             foundlabel, comment, thetypes, predobjmap, "Model"))
                for anno in image3dannos:
                    if ("POINT" in anno["value"].upper() or "POLYGON" in anno["value"].upper() or "LINESTRING" in
                            anno["value"].upper()):
                        f.write(self.templates["threejstemplate"].replace("{{wktstring}}", anno["value"]).replace(
                            "{{meshurls}}", str(list(foundmedia["mesh"]))).replace("{{relativepath}}",
                                                                                   DocUtils.generateRelativePathFromGivenDepth(
                                                                                       checkdepth)))
            elif len(foundmedia["mesh"]) > 0 and len(image3dannos) == 0:
                print("Found 3D Model: " + str(foundmedia["mesh"]))
                if self.apis["iiif"]:
                    self.iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath,
                                                             foundmedia["mesh"], image3dannos, annobodies,
                                                             str(subject), self.prefixnamespace, self.imagetoURI,
                                                             self.imagemetadata, DocConfig.metadatanamespaces,
                                                             foundlabel, comment, thetypes, predobjmap, "Model"))
                for curitem in foundmedia["mesh"]:
                    format = "ply"
                    if ".nxs" in curitem or ".nxz" in curitem:
                        format = "nexus"
                        self.has3d = True
                    elif format == "gltf":
                        f.write(self.templates["threejstemplate"].replace("{{wktstring}}", "").replace("{{meshurls}}",
                                                                                                  str(list(
                                                                                                      foundmedia[
                                                                                                          "mesh"]))).replace(
                            "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(checkdepth)))
                    f.write(self.templates["threejstemplate"].replace("{{wktstring}}", "").replace("{{meshurls}}",
                                                                                              str(list(foundmedia[
                                                                                                           "mesh"]))).replace(
                        "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(checkdepth)))
                    # f.write(templates["3dtemplate"].replace("{{meshurl}}",curitem).replace("{{meshformat}}",format))
                    break
            elif len(foundmedia["mesh"]) == 0 and len(image3dannos) > 0:
                for anno in image3dannos:
                    if ("POINT" in anno["value"].upper() or "POLYGON" in anno["value"].upper() or "LINESTRING" in
                            anno["value"].upper()):
                        f.write(self.templates["threejstemplate"].replace("{{wktstring}}", anno["value"]).replace(
                            "{{meshurls}}", "[]").replace("{{relativepath}}",
                                                          DocUtils.generateRelativePathFromGivenDepth(checkdepth)))
            carousel = "image"
            if len(foundmedia["image"]) > 3:
                carousel = "carousel-item active"
                f.write(self.templates["imagecarouselheader"])
            # if self.apis["iiif"] and len(annobodies)>0:
            #    if target not in imagetoURI:
            #        imagetoURI[target]={"uri":{str(subject):{"bodies":[]}}}
            #    if str(subject) not in imagetoURI[target]:
            #        imagetoURI[target]["uri"][str(subject)]={"bodies":[]}
            #    if str(subject) not in imagetoURI[target]:
            #        imagetoURI[target]["uri"][str(subject)]["bodies"]+=annobodies
            if len(imageannos) > 0 and len(foundmedia["image"]) > 0:
                if self.apis["iiif"]:
                    self.iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath,
                                                             foundmedia["image"], imageannos, annobodies,
                                                             str(subject), self.prefixnamespace, self.imagetoURI,
                                                             self.imagemetadata, DocConfig.metadatanamespaces,
                                                             foundlabel, comment, thetypes, predobjmap, "Image"))
                for image in foundmedia["image"]:
                    if image not in self.imagetoURI or "uri" not in self.imagetoURI[image]:
                        self.imagetoURI[image] = {"uri": {}}
                    if not str(subject) in self.imagetoURI[image]["uri"]:
                        self.imagetoURI[image]["uri"][str(subject)] = {"bodies": []}
                    annostring = ""
                    for anno in imageannos:
                        annostring += anno["value"].replace("<svg>",
                                                            "<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                    f.write(self.templates["imageswithannotemplate"].replace("{{carousel}}",
                                                                        carousel + "\" style=\"position: relative;display: inline-block;").replace(
                        "{{image}}", str(image)).replace("{{svganno}}", annostring).replace("{{imagetitle}}",
                                                                                            str(image)[
                                                                                            0:str(image).rfind(
                                                                                                '.')]))
                    if len(foundmedia["image"]) > 3:
                        carousel = "carousel-item"
            elif len(foundmedia["image"]) > 0:
                if self.apis["iiif"]:
                    self.iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath,
                                                             foundmedia["image"], imageannos, annobodies,
                                                             str(subject), self.prefixnamespace, self.imagetoURI,
                                                             self.imagemetadata, DocConfig.metadatanamespaces,
                                                             foundlabel, comment, thetypes, predobjmap, "Image"))
                for image in foundmedia["image"]:
                    if image not in self.imagetoURI or "uri" not in self.imagetoURI[image]:
                        self.imagetoURI[image] = {"uri": {}}
                    if not str(subject) in self.imagetoURI[image]["uri"]:
                        self.imagetoURI[image]["uri"][str(subject)] = {"bodies": []}
                    if image == "<svg width=":
                        continue
                    if "<svg" in image:
                        if "<svg>" in image:
                            f.write(self.templates["imagestemplatesvg"].replace("{{carousel}}", carousel).replace(
                                "{{image}}", str(image.replace("<svg>", "<svg class=\"svgview\">"))))
                        else:
                            f.write(self.templates["imagestemplatesvg"].replace("{{carousel}}", carousel).replace(
                                "{{image}}", str(image)))
                    else:
                        f.write(self.templates["imagestemplate"].replace("{{carousel}}", carousel).replace("{{image}}",
                                                                                                      str(image)).replace(
                            "{{imagetitle}}", str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"]) > 3:
                        carousel = "carousel-item"
            if len(foundmedia["image"]) > 3:
                f.write(self.templates["imagecarouselfooter"])
            if len(textannos) > 0:
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
            if len(foundmedia["audio"]) > 0 and self.apis["iiif"]:
                self.iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath, foundmedia["audio"],
                                                         None, None, str(subject), self.prefixnamespace,
                                                         self.imagetoURI,
                                                         self.imagemetadata, DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Audio"))
            for audio in foundmedia["audio"]:
                self.imagetoURI[audio] = {"uri": str(subject)}
                f.write(self.templates["audiotemplate"].replace("{{audio}}", str(audio)))
            if len(foundmedia["video"]) > 0 and self.apis["iiif"]:
                self.iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, self.outpath, self.deploypath, foundmedia["video"],
                                                         None, None, str(subject), self.prefixnamespace,
                                                         self.imagetoURI,
                                                         self.imagemetadata, DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Video"))
            for video in foundmedia["video"]:
                self.imagetoURI[video] = {"uri": str(subject)}
                f.write(self.templates["videotemplate"].replace("{{video}}", str(video)))
            for type in curtypes:
                if type in DocConfig.lexicontypes:
                    LexiconPage().generatePageWidget(graph, subject, f, {}, False)
                if type in PersonPage.pageWidgetConstraint():
                    PersonPage().generatePageWidget(graph, subject, self.templates, f, True)
            HTMLExporter.processCollectionPages(collections, graph, subject,self.templates, f)
            if geojsonrep != None and "geocollection" not in collections:
                self.geocache = GeometryViewPage().generatePageWidget(graph, self.templates, subject, f, uritotreeitem,
                                                                      geojsonrep, predobjmap, self.geocache,
                                                                      {"dateprops": dateprops, "timeobj": timeobj,
                                                                       "epsgcode": epsgcode,
                                                                       "epsgdefslink": epsgdefslink,
                                                                       "checkdepth": checkdepth,
                                                                       "hasnonnslen": len(hasnonns)})
            elif "geocollection" in collections or nonns:
                self.geocache = GeometryViewPage().generateCollectionWidget(graph, self.templates, subject, f,
                                                                            uritotreeitem,
                                                                            self.featurecollectionspaths,
                                                                            {"completesavepath": completesavepath,
                                                                             "nonns": nonns, "hasnonns": hasnonns,
                                                                             "foundlabel": foundlabel,
                                                                             "localOptimized": self.localOptimized,
                                                                             "dateprops": dateprops,
                                                                             "timeobj": timeobj,
                                                                             "geocache": self.geocache,
                                                                             "epsgcode": epsgcode,
                                                                             "epsgdefslink": epsgdefslink,
                                                                             "checkdepth": checkdepth,
                                                                             "hasnonnslen": len(hasnonns)})
            f.write(self.templates["htmltabletemplate"].replace("{{tablecontent}}", tablecontents))
            if metadatatablecontentcounter >= 0:
                f.write("<h5>Metadata</h5>")
                f.write(self.templates["htmltabletemplate"].replace("{{tablecontent}}", metadatatablecontents))
            tempfoot = self.replaceStandardVariables(self.templates["footer"], "", checkdepth, "false").replace(
                "{{exports}}",
                myexports).replace(
                "{{license}}", curlicense).replace("{{bibtex}}", "").replace("{{stats}}", "")
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot,
                                                        [True, self.apis["ogcapifeatures"], self.apis["iiif"], self.apis["ckan"]],
                                                        [
                                                            "<a href=\"" + DocUtils.generateRelativePathFromGivenDepth(
                                                                checkdepth) + "/sparql.html?endpoint=" + str(
                                                                self.deploypath) + "\">[SPARQL]</a>&nbsp;",
                                                            "<a href=\"" + DocUtils.generateRelativePathFromGivenDepth(
                                                                checkdepth) + "/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            "<a href=\"" + DocUtils.generateRelativePathFromGivenDepth(
                                                                checkdepth) + "/iiif/\">[IIIF]</a>&nbsp;",
                                                            "<a href=\"" + DocUtils.generateRelativePathFromGivenDepth(
                                                                checkdepth) + "/api/3/\">[CKAN]</a>"
                                                        ], "{{apis}}")
            f.write(tempfoot)
            f.close()
        return [postprocessing, nonnsmap]

    @staticmethod
    def processCollectionPages(pagesmap, graph, subject, templates, f):
        if "observationcollection" in pagesmap:
            ObservationPage().generateCollectionWidget(graph, templates, subject, f)
        if "lexicon" in pagesmap:
            LexiconPage().generateCollectionWidget(graph, templates, subject, f)

    @staticmethod
    def searchObjectConnectionsForAggregateData(graph, object, pred, geojsonrep, foundmedia, imageannos,
                                                textannos, image3dannos, annobodies, label, unitlabel, nonns, inverse,
                                                labellang, typeproperty, prefixes):
        geoprop = False
        annosource = None
        incollection = False
        if pred in DocConfig.geopointerproperties:
            geoprop = True
        if pred in DocConfig.collectionrelationproperties:
            incollection = True
        foundval = None
        foundunit = None
        tempvalprop = None
        onelabel = None
        bibtex = None
        timeobj = None
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in DocConfig.labelproperties:
                if tup[1].language == labellang:
                    label = str(tup[1])
                onelabel = str(tup[1])
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(typeproperty) and (
                    tup[1] == URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1] == URIRef(
                "http://www.w3.org/ns/oa#WKTSelector")):
                for svglit in graph.objects(object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value")):
                    if "<svg" in str(svglit):
                        imageannos.append({"value": str(svglit), "bodies": []})
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(
                            svglit).upper()):
                        image3dannos.append({"value": str(svglit), "bodies": []})
            elif pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    typeproperty) and tup[1] == URIRef(
                "http://www.w3.org/ns/oa#TextPositionSelector"):
                curanno = {}
                for txtlit in graph.predicate_objects(object):
                    if str(txtlit[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":
                        curanno["exact"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#start":
                        curanno["start"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#end":
                        curanno["end"] = str(txtlit[1])
                textannos.append(curanno)
            if str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                annosource = str(tup[1])
                print(
                    "Found annosource " + str(tup[1]) + " from " + str(object) + " Imageannos: " + str(len(imageannos)))
            if (
                    pred == "http://purl.org/dc/terms/isReferencedBy" or pred == "http://purl.org/spar/cito/hasCitingEntity") and \
                    tup[0] == URIRef(typeproperty) and ("http://purl.org/ontology/bibo/" in str(tup[1])):
                bibtex = BibPage.resolveBibtexReference(graph.predicate_objects(object), object, graph)
            if pred in DocConfig.timepointerproperties:
                timeobj = OWLTimePage.resolveTimeLiterals(pred, object, graph)
            if not nonns:
                geojsonrep = LiteralUtils.resolveGeoLiterals(tup[0], tup[1], graph, geojsonrep, nonns)
            if incollection and "<svg" in str(tup[1]):
                foundmedia["image"][str(tup[1])] = {}
            elif incollection and "http" in str(tup[1]):
                ext = "." + ''.join(filter(str.isalpha, str(tup[1]).split(".")[-1]))
                if ext in DocConfig.fileextensionmap:
                    foundmedia[DocConfig.fileextensionmap[ext]][str(tup[1])] = {}
            if not inverse and str(tup[0]) == "http://www.w3.org/2000/01/rdf-schema#member" and (
                    object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                    URIRef("http://www.w3.org/ns/sosa/ObservationCollection")) in graph:
                for valtup in graph.predicate_objects(tup[1]):
                    if str(valtup[0]) in DocConfig.unitproperties:
                        foundunit = str(valtup[1])
                    if str(valtup[0]) in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                        foundval = str(valtup[1])
            if str(tup[0]) in DocConfig.valueproperties:
                if tempvalprop == None and str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                if str(tup[0]) != "http://www.w3.org/ns/oa#hasSource" and DocConfig.valueproperties[
                    str(tup[0])] == "DatatypeProperty" and (isinstance(tup[1], Literal) or isinstance(tup[1], URIRef)):
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                elif str(tup[0]) == "http://www.w3.org/ns/oa#hasTarget":
                    tempvalprop = "http://www.w3.org/ns/oa#hasTarget"
                    for inttup in graph.predicate_objects(tup[1]):
                        if str(inttup[0]) == "http://www.w3.org/ns/oa#hasSelector":
                            for valtup in graph.predicate_objects(inttup[1]):
                                if str(valtup[0]) in DocConfig.unitproperties:
                                    foundunit = str(valtup[1])
                                if str(valtup[0]) in DocConfig.valueproperties and (
                                        isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                                    foundval = str(valtup[1])
                elif DocConfig.valueproperties[str(tup[0])] == "DatatypeProperty":
                    if str(tup[0]) in DocConfig.valueproperties and isinstance(tup[1], Literal):
                        tempvalprop = str(tup[0])
                        foundval = str(tup[1])
                else:
                    for valtup in graph.predicate_objects(tup[1]):
                        if str(valtup[0]) in DocConfig.unitproperties:
                            foundunit = str(valtup[1])
                        if str(valtup[0]) in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                            foundval = str(valtup[1])
            if str(tup[0]) in DocConfig.unitproperties:
                foundunit = tup[1]
        if foundunit is not None and foundval != None:
            if "http" in foundunit:
                thelabel = DocUtils.getLabelForObject(str(foundunit), graph, prefixes)
                unitlabel = str(foundval) + " <a href=\"" + str(foundunit) + "\" target=\"_blank\">" + thelabel + "</a>"
            else:
                unitlabel = str(foundval) + " " + str(foundunit)
            if pred == "http://www.w3.org/ns/oa#hasBody":
                # print("ADD ANNO BODY: "+str({"value":foundval,"unit":foundunit,"type":"TextualBody","format":"text/plain"}))
                annobodies.append({"value": foundval, "unit": foundunit, "type": "TextualBody", "format": "text/plain"})
        if foundunit is None and foundval is not None:
            if "http" in foundval:
                thelabel = DocUtils.getLabelForObject(str(foundunit), graph, prefixes)
                unitlabel = "<a href=\"" + str(foundval) + "\" target=\"_blank\">" + thelabel + "</a>"
            else:
                unitlabel = str(foundval)
            if pred == "http://www.w3.org/ns/oa#hasBody":
                # print("ADD ANNO BODY: "+str({"value":foundval,"type":"TextualBody","format":"text/plain"}))
                annobodies.append({"value": foundval, "type": "TextualBody", "format": "text/plain"})
        if annosource is not None:
            for textanno in textannos:
                textanno["src"] = annosource
            for imganno in imageannos:
                imganno["src"] = annosource
            for imganno in image3dannos:
                imganno["src"] = annosource
        if label == "" and onelabel is not None:
            label = onelabel
        return {"geojsonrep": geojsonrep, "label": label, "unitlabel": unitlabel, "foundmedia": foundmedia,
                "imageannos": imageannos, "textannos": textannos, "image3dannos": image3dannos,
                "annobodies": annobodies, "bibtex": bibtex, "timeobj": timeobj}

    @staticmethod
    def createHTMLTableValueEntry(subject, pred, object, ttlf, graph, baseurl, checkdepth, geojsonrep, foundmedia,
                                  imageannos, textannos, image3dannos, annobodies, dateprops, inverse, nonns, labellang,
                                  typeproperty, namespaceshort, generatePagesForNonNS, prefixes):
        tablecontents = ""
        label = ""
        bibtex = None
        timeobj = None
        if isinstance(object, URIRef) or isinstance(object, BNode):
            if ttlf is not None:
                ttlf.add((subject, URIRef(pred), object))
            label = ""
            unitlabel = ""
            mydata = HTMLExporter.searchObjectConnectionsForAggregateData(graph, object, pred, geojsonrep, foundmedia,
                                                                          imageannos, textannos, image3dannos,
                                                                          annobodies,
                                                                          label, unitlabel, nonns, inverse, labellang,
                                                                          typeproperty, prefixes)
            label = mydata["label"]
            if label == "":
                label = str(DocUtils.shortenURI(str(object)))
            geojsonrep = mydata["geojsonrep"]
            foundmedia = mydata["foundmedia"]
            imageannos = mydata["imageannos"]
            textannos = mydata["textannos"]
            image3dannos = mydata["image3dannos"]
            unitlabel = mydata["unitlabel"]
            bibtex = mydata["bibtex"]
            timeobj = mydata["timeobj"]
            annobodies = mydata["annobodies"]
            if inverse:
                rdfares = " about=\"" + str(object) + "\" resource=\"" + str(subject) + "\""
                microdatares = " itemref=\"" + str(object) + "\" "
            else:
                rdfares = "resource=\"" + str(object) + "\""
                microdatares = " "
            if baseurl in str(object) or isinstance(object, BNode):
                rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, str(object), True)
                tablecontents += "<span><a itemprop=\"" + str(pred) + "\"" + microdatares + "property=\"" + str(
                    pred) + "\" " + rdfares + " href=\"" + rellink + "\">" + label + " <span style=\"color: #666;\">(" + namespaceshort + ":" + str(
                    DocUtils.shortenURI(str(object))) + ")</span></a>"
                if bibtex is not None:
                    tablecontents += "<details><summary>[BIBTEX]</summary><pre>" + str(bibtex) + "</pre></details>"
            else:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(object))
                if res is not None:
                    tablecontents += "<span><a itemprop=\"" + str(pred) + "\"" + microdatares + "property=\"" + str(
                        pred) + "\" " + rdfares + " target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + " <span style=\"color: #666;\">(" + res["uri"] + ")</span></a>"
                else:
                    tablecontents += "<span><a itemprop=\"" + str(pred) + "\"" + microdatares + "property=\"" + str(
                        pred) + "\" " + rdfares + " target=\"_blank\" href=\"" + str(object) + "\">" + label + "</a>"
                if bibtex is not None:
                    tablecontents += "<details><summary>[BIBTEX]</summary><pre>" + str(bibtex) + "</pre></details>"
                if generatePagesForNonNS:
                    rellink = DocUtils.generateRelativeLinkFromGivenDepth(str(baseurl), checkdepth,
                                                                          str(baseurl) + "nonns_" + DocUtils.shortenURI(
                                                                              str(object).replace(":", "_")), False)
                    tablecontents += " <a href=\"" + rellink + ".html\">[x]</a>"
            if unitlabel != "":
                tablecontents += " <span style=\"font-weight:bold\">[" + str(unitlabel) + "]</span>"
            if timeobj is not None:
                res = str(OWLTimePage.timeObjectToHTML(timeobj, prefixes))
                if res != "None":
                    tablecontents += " <span style=\"font-weight:bold\">[" + str(res) + "]</span>"
                dateprops = timeobj
            tablecontents += "</span>"
        else:
            label = str(object)
            if ttlf is not None:
                ttlf.add((subject, URIRef(pred), object))
            if isinstance(object, Literal) and object.datatype != None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(object.datatype))
                objstring = str(object).replace("<", "&lt").replace(">", "&gt;")
                if str(object.datatype) == "http://www.w3.org/2001/XMLSchema#anyURI":
                    objstring = "<a href=\"" + str(object) + "\">" + str(object) + "</a>"
                if str(object.datatype) in DocConfig.timeliteraltypes and dateprops != None and DocUtils.shortenURI(
                        str(pred), True) not in DocConfig.metadatanamespaces and str(pred) not in dateprops:
                    dateprops.append(str(pred))
                if res != None:
                    tablecontents += "<span itemprop=\"" + str(pred) + "\" property=\"" + str(
                        pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + HTMLExporter.truncateValue(
                        objstring) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + res["uri"] + "</a>)</small></span>"
                else:
                    tablecontents += "<span itemprop=\"" + str(pred) + "\" property=\"" + str(
                        pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + HTMLExporter.truncateValue(
                        objstring) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + DocUtils.shortenURI(str(object.datatype)) + "</a>)</small></span>"
                geojsonrep = LiteralUtils.resolveGeoLiterals(URIRef(pred), object, graph, geojsonrep, nonns, subject)
            else:
                if object.language is not None:
                    tablecontents += "<span itemprop=\"" + str(pred) + "\" property=\"" + str(
                        pred) + "\" content=\"" + str(object).replace("<", "&lt").replace(">", "&gt;").replace("\"",
                                                                                                               "'") + "\" datatype=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\" xml:lang=\"" + str(
                        object.language) + "\">" + HTMLExporter.truncateValue(
                        str(object).replace("<", "&lt").replace(">",
                                                                "&gt;")) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">data:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/" + str(
                        object.language) + "\" target=\"_blank\">iso6391:" + str(
                        object.language) + "</a>)</small></span>"
                else:
                    tablecontents += HTMLExporter.detectStringLiteralContent(pred, object)
        return {"html": tablecontents, "geojson": geojsonrep, "foundmedia": foundmedia, "imageannos": imageannos,
                "textannos": textannos, "image3dannos": image3dannos, "annobodies": annobodies, "label": label,
                "timeobj": dateprops}

    @staticmethod
    def processLicense(license):
        if license == None or license == "" or license == "No License Statement":
            return ["", None]
        if license.startswith("CC"):
            spl = license.split(" ")
            res = """<span style="float:right;margin-left:auto;margin-right:0px;text-align:right">This work is released under <a rel="license" target="_blank" href="http://creativecommons.org/licenses/""" + str(
                spl[1]).lower() + "/" + str(spl[2]) + """/">
            <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/""" + str(
                spl[1]).lower() + """/""" + str(spl[2]) + """/80x15.png"/></a></span>"""
            licenseuri = "http://creativecommons.org/licenses/" + str(spl[1]).lower() + "/" + str(spl[2])
            return [res, licenseuri]
        else:
            return ["""All rights reserved.""", None]

    @staticmethod
    def formatPredicate(tup, baseurl, checkdepth, tablecontents, graph, reverse, labellang, prefixes):
        label = DocUtils.getLabelForObject(URIRef(str(tup)), graph, prefixes, labellang)
        tablecontents += "<td class=\"property\">"
        if reverse:
            tablecontents += "Is "
        if baseurl in str(tup):
            rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, str(tup), True)
            tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span>"
        else:
            res = DocUtils.replaceNameSpacesInLabel(prefixes, tup)
            if res != None:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                     "uri"] + ")</span></a> "
            else:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + "</a> "
            tablecontents += "</span>"
        if reverse:
            tablecontents += " of"
        tablecontents += "</td>"
        return tablecontents

    @staticmethod
    def truncateValue(value, limit=150):
        if len(value) > limit:
            return "<details><summary style=\"list-style-type: none;\">" + value[0:limit] + " (...)</summary>" + str(
                value[limit:]) + "</details>"
        return value

    @staticmethod
    def detectStringLiteralContent(pred, object):
        if object.startswith("http://") or object.startswith("https://"):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(
                pred) + "\" target=\"_blank\" href=\"" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif object.startswith("www."):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(
                pred) + "\" target=\"_blank\" href=\"http://" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">http://" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif re.search(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)', str(object)):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(
                pred) + "\" href=\"https://www.doi.org/" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#anyURI\">" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#anyURI\">xsd:anyURI</a>)</small></span>"
        elif re.search(r'[\w.]+\@[\w.]+', object):
            return "<span><a itemprop=\"" + str(pred) + "\" property=\"" + str(pred) + "\" href=\"mailto:" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">mailto:" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return "<span property=\"" + str(pred) + "\" content=\"" + str(object).replace("<", "&lt").replace(">",
                                                                                                           "&gt;").replace(
            "\"", "'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<",
                                                                                                          "&lt").replace(
            ">",
            "&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
