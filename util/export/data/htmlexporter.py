from ...doc.docutils import DocUtils
from ...doc.literalutils import LiteralUtils
from ...doc.docutils import DocConfig
from ...doc.docdefaults import DocDefaults
from ..pages.bibpage import BibPage
from ..pages.owltimepage import OWLTimePage
from rdflib import URIRef, Graph, BNode, Literal, XSD
from rdflib.namespace import RDF
from collections import OrderedDict
from qgis.core import Qgis, QgsMessageLog
from colletions import defaultdict
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
from ..pages.model3dpage import Model3DPage
from ..pages.textannopage import TextAnnoPage


class HTMLExporter:
    listthreshold = 5
    maxlistthreshold = 1500

    featurecollectionspaths = {}
    iiifmanifestpaths = {"default": []}
    imagetoURI = {}
    geocache = {}

    def __init__(self, pubconfig,templates,typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
        self.pubconfig=pubconfig
        self.templates=templates
        self.typeproperty=typeproperty
        self.has3d = False

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
        if self.pubconfig["logourl"] != None and self.pubconfig["logourl"] != "":
            logo = f"<img src=\"{self.pubconfig['logourl']}\" alt=\"logo\" width=\"25\" height=\"25\"/>&nbsp;&nbsp;"
        textannos = []
        foundvals = set()
        imageannos = []
        annobodies = []
        image3dannos = []
        predobjmap = OrderedDict()#defaultdict(list)
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
            uritotreeitem.setdefault(parentclass, [
                    {"id": parentclass, "parent": "#", "type": "class","instancecount":0, "text": DocUtils.shortenURI(str(parentclass)),
                     "data": {"from":{},"to":{}}}])
            #uritotreeitem[parentclass][-1]["instancecount"] = 0
        ttlf = Graph(bind_namespaces="rdflib")
        # ttlf = open(savepath + "/index.ttl", "w", encoding="utf-8")
        #if parentclass is not None:
        #    uritotreeitem[parentclass][-1]["data"]["to"] = {}
        #    uritotreeitem[parentclass][-1]["data"]["from"] = {}
        hasnonns = set()
        thetypes = set()
        itembibtex = ""
        collections = set()
        if predobjs is not None:
            for tup in sorted(predobjs, key=lambda tup: tup[0]):
                tupobjstr = str(tup[1])
                tuppredstr = str(tup[0])
                predobjmap.setdefault(tuppredstr,[]).append(tup[1])
                if parentclass is not None:
                    if tuppredstr not in uritotreeitem[parentclass][-1]["data"]["to"]:
                        uritotreeitem[parentclass][-1]["data"]["to"][tuppredstr] = {}
                        uritotreeitem[parentclass][-1]["data"]["to"][tuppredstr]["instancecount"] = 0
                    else:
                        uritotreeitem[parentclass][-1]["data"]["to"][tuppredstr]["instancecount"] += 1
                        #uritotreeitem[parentclass][-1]["instancecount"] += 1
                if isinstance(tup[1], URIRef):
                    for item in graph.objects(tup[1], URIRef(self.typeproperty)):
                        thetypes.add(str(item))
                        if parentclass is not None:
                            uritotreeitem[parentclass][-1]["data"]["to"][tuppredstr].setdefault(item,0)
                            uritotreeitem[parentclass][-1]["data"]["to"][tuppredstr][item] += 1
                    if baseurl not in tupobjstr and tuppredstr != self.typeproperty:
                        hasnonns.add(tupobjstr)
                        if nonnsmap is not None:
                            nonnsmap.setdefault(tupobjstr,set()).add(subject)
            for tup in predobjmap:
                predobjtuplen=len(predobjmap[tup])
                if self.pubconfig["metadatatable"] and tup not in DocConfig.labelproperties and DocUtils.shortenURI(tup,
                                                                                                       True) in DocConfig.metadatanamespaces:
                    thetable = metadatatablecontents
                    metadatatablecontentcounter += 1
                    thetable += f'<tr class="{"odd" if metadatatablecontentcounter % 2 == 0 else "even"}">'
                else:
                    thetable = tablecontents
                    tablecontentcounter += 1
                    thetable+=f'<tr class="{"odd" if tablecontentcounter % 2 == 0 else "even"}">'
                if tup == self.typeproperty:
                    for tp in predobjmap[tup]:
                        tpstr=str(tp)
                        thetypes.add(tpstr)
                        curtypes.add(tpstr)
                        if tpstr in DocConfig.collectionclasses:
                            #uritotreeitem[tpstr][-1]["instancecount"] += 1
                            collections.add(DocConfig.collectionclasses[tpstr])
                        elif tpstr in DocConfig.bibtextypemappings:
                            itembibtex = f"<details><summary>[BIBTEX]</summary><pre>{BibPage.resolveBibtexReference(graph.predicate_objects(subject), subject,graph)}</pre></details>"
                thetable += HTMLExporter.formatPredicate(tup, baseurl, checkdepth, graph, inverse, self.pubconfig["labellang"], self.pubconfig["prefixes"])
                if tup in DocConfig.labelproperties:
                    for lab in predobjmap[tup]:
                        if lab.language == self.pubconfig["labellang"]:
                            foundlabel = lab
                    if foundlabel == "":
                        foundlabel = str(predobjmap[tup][0])
                if tup in DocConfig.commentproperties:
                    comment[tup] = str(predobjmap[tup][0])
                if predobjtuplen > 0:
                    thetable += "<td class=\"wrapword\">"
                    if predobjtuplen > HTMLExporter.listthreshold:
                        thetable += f"<details><summary>{predobjtuplen} values</summary>"
                    if predobjtuplen > 1:
                        thetable += "<ul>"
                    labelmap = defaultdict(str)
                    itemcounter = 0
                    for item in predobjmap[tup]:
                        if itemcounter >= HTMLExporter.maxlistthreshold:
                            break
                        if tup in DocConfig.valueproperties and ("POINT" in str(item).upper() or "POLYGON" in str(item).upper() or "LINESTRING" in str(
                                item).upper()) and self.typeproperty in predobjmap and URIRef("http://www.w3.org/ns/oa#WKTSelector") in predobjmap[self.typeproperty]:
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
                            foundvals.add((tup, str(item)))
                        res = HTMLExporter.createHTMLTableValueEntry(subject, tup, item, ttlf, graph,
                                                                     baseurl, checkdepth, geojsonrep, foundmedia,
                                                                     imageannos,
                                                                     textannos, image3dannos, annobodies, dateprops,
                                                                     inverse,
                                                                     nonns, self.pubconfig["labellang"], self.typeproperty,
                                                                     self.pubconfig["namespaceshort"], self.pubconfig["nonnspages"],
                                                                     self.pubconfig["prefixes"])
                        geojsonrep = res["geojson"]
                        foundmedia = res["foundmedia"]
                        imageannos = res["imageannos"]
                        textannos = res["textannos"]
                        image3dannos = res["image3dannos"]
                        annobodies = res["annobodies"]
                        # print("GOT ANNO BODIES "+str(annobodies))
                        if res["timeobj"] is not None and res["timeobj"] != []:
                            # print("RESTIMEOBJ: "+str(timeobj))
                            timeobj = res["timeobj"]
                        #labelmap.setdefault(res["label"],"")
                        if predobjtuplen > 1:
                            labelmap[res["label"]] += f"<li>{res['html']}</li>"
                        else:
                            labelmap[res["label"]] += f"{res['html']}"
                        itemcounter += 1
                    thetable+="".join(labelmap[lab] for lab in sorted(labelmap))
                    #for lab in sorted(labelmap):
                    #    thetable += str(labelmap[lab])
                    if predobjtuplen >= HTMLExporter.maxlistthreshold:
                        tablecontents += "<li>(...)</li>"
                    if predobjtuplen > 1:
                        thetable += "</ul>"
                    if predobjtuplen > HTMLExporter.listthreshold:
                        thetable += "</details>"
                    thetable += "</td>"
                else:
                    thetable += "<td class=\"wrapword\"></td>"
                thetable += "</tr>"
                if self.pubconfig["metadatatable"] and tup not in DocConfig.labelproperties and DocUtils.shortenURI(tup,
                                                                                                       True) in DocConfig.metadatanamespaces:
                    metadatatablecontents = thetable
                else:
                    tablecontents = thetable
        subpredsmap = OrderedDict()
        if subpreds is not None:
            for tup in sorted(subpreds, key=lambda tup: tup[1]):
                tupobjstr=str(tup[1])
                subpredsmap.setdefault(tupobjstr,[]).append(tup[0])
                if parentclass is not None and tupobjstr not in uritotreeitem[parentclass][-1]["data"]["from"]:
                    uritotreeitem[parentclass][-1]["data"]["from"][tupobjstr] = {}
                    uritotreeitem[parentclass][-1]["data"]["from"][tupobjstr]["instancecount"] = 0
                if isinstance(tup[0], URIRef):
                    for item in graph.objects(tup[0], URIRef(self.typeproperty)):
                        if parentclass is not None:
                            uritotreeitem[parentclass][-1]["data"]["from"][tupobjstr].setdefault(item, 0)
                            uritotreeitem[parentclass][-1]["data"]["from"][tupobjstr][item] += 1
            for tup in subpredsmap:
                subpredtuplen=len(subpredsmap[tup])
                tablecontentcounter += 1
                tablecontents += f'<tr class="{"odd" if tablecontentcounter % 2 == 0 else "even"}">'
                #if tablecontentcounter % 2 == 0:
                #    tablecontents += "<tr class=\"odd\">"
                #else:
                #    tablecontents += "<tr class=\"even\">"
                tablecontents += HTMLExporter.formatPredicate(tup, baseurl, checkdepth, graph, True,
                                                             self.pubconfig["labellang"], self.pubconfig["prefixes"])
                if subpredtuplen > 0:
                    tablecontents += "<td class=\"wrapword\">"
                    if subpredtuplen > HTMLExporter.listthreshold:
                        tablecontents += f"<details><summary>{subpredtuplen} values</summary>"
                    if subpredtuplen > 1:
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
                                                                     nonns, self.pubconfig["labellang"], self.typeproperty,
                                                                     self.pubconfig["namespaceshort"], self.pubconfig["nonnspages"],
                                                                     self.pubconfig["prefixes"])
                        foundmedia = res["foundmedia"]
                        imageannos = res["imageannos"]
                        image3dannos = res["image3dannos"]
                        annobodies = res["annobodies"]
                        # print("POSTPROC ANNO BODIES "+str(annobodies))
                        if nonns and tup != self.typeproperty:
                            hasnonns.add(str(item))
                        if nonns:
                            geojsonrep = res["geojson"]
                        labelmap.setdefault(res["label"],"")
                        if subpredtuplen > 1:
                            labelmap[res["label"]] += f"<li>{res['html']}</li>"
                        else:
                            labelmap[res["label"]] += f"{res['html']}"
                        itemcounter += 1
                    tablecontents += "".join(labelmap[lab] for lab in sorted(labelmap))
                    #for lab in sorted(labelmap) :
                    #    tablecontents += str(labelmap[lab])
                    if subpredtuplen >= HTMLExporter.maxlistthreshold:
                        tablecontents += "<li>(...)</li>"
                    if subpredtuplen > 1:
                        tablecontents += "</ul>"
                    if subpredtuplen > HTMLExporter.listthreshold:
                        tablecontents += "</details>"
                    tablecontents += "</td>"
                else:
                    tablecontents += "<td class=\"wrapword\"></td>"
                tablecontents += "</tr>"
        if self.pubconfig["licenseuri"] is not None:
            ttlf.add((subject, URIRef("http://purl.org/dc/elements/1.1/license"), URIRef(self.pubconfig["licenseuri"])))
        if self.pubconfig["apis"]["solidexport"] is not None:
            ttlf.add((subject, RDF.type,URIRef("http://www.w3.org/ns/ldp#Resource")))
            ttlf.add((subject, RDF.type,URIRef("https://www.iana.org/assignments/media-types/text/turtle#Resource")))
        nonnslink = ""
        if nonns:
            if "http:" in savepath:
                completesavepath = savepath[0:savepath.find("http:") - 1] + savepath[savepath.find("http:"):].replace(":", "_").replace("/", "_")
            else:
                completesavepath = savepath
            nonnslink = f"<div>This page describes linked instances to the concept  <a target=\"_blank\" href=\"{subject}\">{foundlabel} ({DocUtils.shortenURI(subject)}) </a> in this knowledge graph. It is defined <a target=\"_blank\" href=\"{subject}\">here</a></div>"
        else:
            completesavepath = savepath + "/index.html"
            if os.path.exists(savepath):
                try:
                    ttlf.serialize(savepath + "/index.ttl", encoding="utf-8")
                    with open(savepath + "/index.json", 'w', encoding='utf-8') as f:
                        json.dump(predobjmap,f)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
        # try:
        with open(completesavepath, 'w', encoding='utf-8') as f:
            searchfilelink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, searchfilename, False)
            classtreelink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, classtreename, False)
            csslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "style.css", False)
            startscriptlink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js",False)
            proprelationslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "proprelations.js",False)
            epsgdefslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "epsgdefs.js", False)
            vowlresultlink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "vowl_result.js",False)
            if geojsonrep is not None:
                myexports = self.templates["geoexports"]
            else:
                myexports = self.templates["nongeoexports"]
            relpath = DocUtils.generateRelativePathFromGivenDepth(checkdepth)
            if not foundlabel:
                foundlabel = DocUtils.shortenURI(str(subject))
            f.write(DocUtils.replaceStandardVariables(self.templates["htmltemplate"], subject, checkdepth, "false",self.pubconfig).replace(
                "{{iconprefixx}}", (relpath + "icons/" if self.pubconfig["offlinecompat"] else "")).replace("{{baseurl}}",baseurl).replace(
                "{{relativepath}}", relpath).replace(
                "{{relativedepth}}", str(checkdepth)).replace("{{prefixpath}}", self.pubconfig["prefixns"]).replace(
                "{{toptitle}}", foundlabel).replace("{{startscriptpath}}", startscriptlink).replace("{{epsgdefspath}}", epsgdefslink).replace(
                "{{bibtex}}", itembibtex).replace("{{vowlpath}}", vowlresultlink).replace("{{proprelationpath}}",proprelationslink).replace(
                "{{stylepath}}", csslink).replace("{{title}}", "<a href=\"" + str(subject) + "\">" + str(foundlabel) + "</a>").replace(
                "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}","").replace(
                "{{scriptfolderpath}}", searchfilelink).replace("{{classtreefolderpath}}", classtreelink).replace(
                "{{exports}}", myexports).replace("{{nonnslink}}", str(nonnslink)).replace("{{subjectencoded}}",urllib.parse.quote(str(subject))))
            for comm in comment:
                f.write(self.templates["htmlcommenttemplate"].replace("{{comment}}",DocUtils.shortenURI(comm) + ":" + comment[comm]))
            # for fval in foundvals:
            #    f.write(templates["htmlcommenttemplate"].replace("{{comment}}", "<b>Value "+ DocUtils.shortenURI(str(fval[0]))+": <mark>" + str(fval[1]) + "</mark></b>"))
            if len(foundmedia["mesh"]) > 0:
                self.has3d=Model3DPage.generatePageWidget(graph,foundmedia,annobodies,self.templates,subject,self.iiifmanifestpaths,image3dannos,self.pubconfig,self.imagetoURI,foundlabel,comment,thetypes,predobjmap,f,checkdepth)
            if len(foundmedia["image"])> 0:
                print("found media")
                #MediaPage.generatePageWidget(foundmedia, self.iiifmanifestpaths, graph, imageannos, self.imagetoURI,
                #                             annobodies, foundlabel, comment, thetypes, predobjmap, self.templates,
                #                             subject, self.pubconfig, f)
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
                if self.pubconfig["apis"]["iiif"]:
                    self.iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph, self.pubconfig["outpath"], self.pubconfig["deploypath"],
                                                             foundmedia["image"], imageannos, annobodies,
                                                             str(subject), self.pubconfig["prefixns"], self.imagetoURI,
                                                             self.pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                             foundlabel, comment, thetypes, predobjmap, "Image"))
                for image in foundmedia["image"]:
                    if image not in self.imagetoURI or "uri" not in self.imagetoURI[image]:
                        self.imagetoURI[image] = {"uri": {}}
                    if not str(subject) in self.imagetoURI[image]["uri"]:
                        self.imagetoURI[image]["uri"][str(subject)] = {"bodies": []}
                    annostring = ""
                    for anno in imageannos:
                        annostring += anno["value"].replace("<svg>","<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                    f.write(self.templates["imageswithannotemplate"].replace("{{carousel}}",carousel + "\" style=\"position: relative;display: inline-block;").replace(
                        "{{image}}", str(image)).replace("{{svganno}}", annostring).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"]) > 3:
                        carousel = "carousel-item"
            elif len(foundmedia["image"]) > 0:
                if self.pubconfig["apis"]["iiif"]:
                    self.iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph, self.pubconfig["outpath"], self.pubconfig["deploypath"],
                                                             foundmedia["image"], imageannos, annobodies,
                                                             str(subject), self.pubconfig["prefixns"], self.imagetoURI,
                                                             self.pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
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
                TextAnnoPage.generatePageWidget(graph,textannos,self.templates,f)
            if len(foundmedia["audio"]) > 0 and self.pubconfig["apis"]["iiif"]:
                self.iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, self.pubconfig["outpath"], self.pubconfig["deploypath"], foundmedia["audio"],
                                                         None, None, str(subject), self.pubconfig["prefixns"],
                                                         self.imagetoURI,
                                                         self.pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Audio"))
            for audio in foundmedia["audio"]:
                self.imagetoURI[audio] = {"uri": str(subject)}
                f.write(self.templates["audiotemplate"].replace("{{audio}}", str(audio)))
            if len(foundmedia["video"]) > 0 and self.pubconfig["apis"]["iiif"]:
                self.iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, self.pubconfig["outpath"], self.pubconfig["deploypath"], foundmedia["video"],
                                                         None, None, str(subject), self.pubconfig["prefixns"],
                                                         self.imagetoURI,
                                                         self.pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Video"))
            for video in foundmedia["video"]:
                self.imagetoURI[video] = {"uri": str(subject)}
                f.write(self.templates["videotemplate"].replace("{{video}}", str(video)))
            for type in curtypes:
                if type in DocConfig.lexicontypes:
                    LexiconPage.generatePageWidget(graph, subject, f, False)
                if type in PersonPage.pageWidgetConstraint():
                    PersonPage.generatePageWidget(graph, subject, self.templates, f, True)
            for coll in collections:
                if coll in DocDefaults.collectionclassToFunction:
                    DocDefaults.collectionclassToFunction[coll](graph, subject, self.templates, f)
            if geojsonrep is not None and "geocollection" not in collections:
                self.geocache = GeometryViewPage().generatePageWidget(graph, subject,self.templates,  f, uritotreeitem,
                                                                      geojsonrep, predobjmap, self.geocache,
                                                                      {"dateprops": dateprops,
                                                                       "timeobj": timeobj,
                                                                       "epsgcode": epsgcode,
                                                                       "epsgdefslink": epsgdefslink,
                                                                       "checkdepth": checkdepth,
                                                                       "hasnonnslen": len(hasnonns)})
            elif "geocollection" in collections or nonns:
                self.geocache = GeometryViewPage().generateCollectionWidget(graph,  subject,self.templates, f,
                                                                            uritotreeitem,
                                                                            self.featurecollectionspaths,
                                                                            {"completesavepath": completesavepath,
                                                                             "nonns": nonns, "hasnonns": hasnonns,
                                                                             "foundlabel": foundlabel,
                                                                             "localOptimized": self.pubconfig["localOptimized"],
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
            tempfoot = DocUtils.replaceStandardVariables(self.templates["footer"], "", checkdepth, "false",self.pubconfig).replace(
                "{{exports}}",
                myexports).replace(
                "{{license}}", curlicense).replace("{{bibtex}}", "").replace("{{stats}}", "")
            tempfoot=DocUtils.replaceCitationLink(tempfoot,foundlabel,subject,self.pubconfig)
            relpath=DocUtils.generateRelativePathFromGivenDepth(checkdepth)
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot,
                                                        [True, self.pubconfig["apis"]["ogcapifeatures"], self.pubconfig["apis"]["iiif"],
                                                         self.pubconfig["apis"]["ckan"]],
                                                        [
                                                            f'<a href="{relpath}/sparql.html?endpoint="{self.pubconfig["deploypath"]}">[SPARQL]</a>&nbsp;',
                                                            f'<a href="{relpath}/api/api.html">[OGC API Features]</a>&nbsp;',
                                                            f'<a href="{relpath}/iiif/">[IIIF]</a>&nbsp;',
                                                            f'<a href="{relpath}/api/3/">[CKAN]</a>'
                                                        ], "{{apis}}")
            f.write(tempfoot)
        # except Exception as inst:
        #    print("Could not write " + str(completesavepath))
        #    print(inst)
        #    print(traceback.format_exc())
        return [postprocessing, nonnsmap]




    @staticmethod
    def searchObjectConnectionsForAggregateData(graph, object, pred, geojsonrep, foundmedia, imageannos,
                                                textannos, image3dannos, annobodies, label, unitlabel, nonns, inverse,
                                                labellang, typeproperty, prefixes):
        annosource = None
        foundval = None
        foundunit = None
        onelabel = None
        bibtex = None
        timeobj = None
        typeprop=URIRef(typeproperty)
        for tup in graph.predicate_objects(object):
            tuppredstr=str(tup[0])
            tupobjstr=str(tup[1])
            if tuppredstr in DocConfig.labelproperties:
                if tup[1].language == labellang:
                    label = tupobjstr
                onelabel = tupobjstr
            elif tuppredstr==typeproperty:
                if pred == "http://www.w3.org/ns/oa#hasSelector":
                    if tupobjstr == "http://www.w3.org/ns/oa#SvgSelector" or tupobjstr == "http://www.w3.org/ns/oa#WKTSelector":
                        for svglit in graph.objects(object, typeprop):
                            svglitstr=str(svglit)
                            if "<svg" in svglitstr:
                                imageannos.append({"value": svglitstr, "bodies": []})
                            elif "POINT" in svglitstr.upper() or "POLYGON" in svglitstr.upper() or "LINESTRING" in svglitstr.upper():
                                image3dannos.append({"value": svglitstr, "bodies": []})
                    elif tupobjstr == "http://www.w3.org/ns/oa#TextPositionSelector":
                        curanno = {}
                        for txtlit in graph.predicate_objects(object):
                            txtlitpredstr = str(txtlit[0])
                            txtlitobjstr=str(txtlit[1])
                            if txtlitpredstr == "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":
                                curanno["exact"] = txtlitobjstr
                            elif txtlitpredstr == "http://www.w3.org/ns/oa#start":
                                curanno["start"] = txtlitobjstr
                            elif txtlitpredstr == "http://www.w3.org/ns/oa#end":
                                curanno["end"] = txtlitobjstr
                        textannos.append(curanno)
                elif (pred == "http://purl.org/dc/terms/isReferencedBy" or pred == "http://purl.org/spar/cito/hasCitingEntity") and ("http://purl.org/ontology/bibo/" in tupobjstr):
                    bibtex = BibPage.resolveBibtexReference(graph.predicate_objects(object), object, graph)
            elif tuppredstr == "http://www.w3.org/2000/01/rdf-schema#member":
                if not inverse and (object, typeprop,URIRef("http://www.w3.org/ns/sosa/ObservationCollection")) in graph:
                    for valtup in graph.predicate_objects(tup[1]):
                        if str(valtup[0]) in DocConfig.unitproperties:
                            foundunit = str(valtup[1])
                        elif str(valtup[0]) in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                            foundval = str(valtup[1])
            elif tuppredstr == "http://www.w3.org/ns/oa#hasSource":
                annosource = tupobjstr
                #print("Found annosource " + tupobjstr + " from " + str(object) + " Imageannos: " + str(len(imageannos)))
            elif tuppredstr in DocConfig.valueproperties:
                res=DocUtils.resolveUnitValue(graph,tup[1],tuppredstr,tupobjstr,foundval,foundunit)
                foundval=res[0]
                foundunit=res[1]
                """
                if tempvalprop is None and tuppredstr == "http://www.w3.org/ns/oa#hasSource":
                    tempvalprop = tuppredstr
                    foundval = tupobjstr
                elif tuppredstr != "http://www.w3.org/ns/oa#hasSource" and DocConfig.valueproperties[
                tuppredstr] == "DatatypeProperty" and (isinstance(tup[1], Literal) or isinstance(tup[1], URIRef)):
                    tempvalprop = tuppredstr
                    foundval = tupobjstr
                elif tuppredstr == "http://www.w3.org/ns/oa#hasTarget":
                    tempvalprop = "http://www.w3.org/ns/oa#hasTarget"
                    for inttup in graph.predicate_objects(tup[1]):
                        if str(inttup[0]) == "http://www.w3.org/ns/oa#hasSelector":
                            for valtup in graph.predicate_objects(inttup[1]):
                                if str(valtup[0]) in DocConfig.unitproperties:
                                    foundunit = str(valtup[1])
                                elif str(valtup[0]) in DocConfig.valueproperties and (
                                        isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                                    foundval = str(valtup[1])
                elif DocConfig.valueproperties[tuppredstr] == "DatatypeProperty":
                    if tuppredstr in DocConfig.valueproperties and isinstance(tup[1], Literal):
                        tempvalprop = tuppredstr
                        foundval = tupobjstr
                else:
                    for valtup in graph.predicate_objects(tup[1]):
                        if str(valtup[0]) in DocConfig.unitproperties:
                            foundunit = str(valtup[1])
                        elif str(valtup[0]) in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                            foundval = str(valtup[1])
                """
            elif tuppredstr in DocConfig.unitproperties:
                foundunit = tup[1]
            elif pred in DocConfig.collectionrelationproperties:
                if "<svg" in tupobjstr:
                    foundmedia["image"][tupobjstr] = {}
                elif "http" in tupobjstr:
                    ext = "." + ''.join(filter(str.isalpha, tupobjstr.split(".")[-1]))
                    if ext in DocConfig.fileextensionmap:
                        foundmedia[DocConfig.fileextensionmap[ext]][tupobjstr] = {}
            elif pred in DocConfig.timepointerproperties:
                timeobj = OWLTimePage.resolveTimeLiterals(URIRef(pred), object, graph)
            elif not nonns:
                geojsonrep = LiteralUtils.resolveGeoLiterals(tup[0], tup[1], graph, geojsonrep, nonns)
        if foundval is not None:
            if foundunit is not None:
                unitlabel = f"{foundval} {foundunit}"
                if "http" in foundunit:
                    unitlabel = f"{foundval} <a href=\"{foundunit}\" target=\"_blank\">{DocUtils.getLabelForObject(foundunit, graph, prefixes)}</a>"
                if pred == "http://www.w3.org/ns/oa#hasBody":
                    # print("ADD ANNO BODY: "+str({"value":foundval,"unit":foundunit,"type":"TextualBody","format":"text/plain"}))
                    annobodies.append({"value": foundval, "unit": foundunit, "type": "TextualBody", "format": "text/plain"})
            else:
                unitlabel = str(foundval)
                if "http" in foundval:
                    unitlabel = f"<a href=\"{foundval}\" target=\"_blank\">{DocUtils.getLabelForObject(foundunit, graph, prefixes)}</a>"
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
        objstr=str(object)
        predstr=str(pred)
        if isinstance(object, URIRef) or isinstance(object, BNode):
            if ttlf is not None:
                ttlf.add((subject, URIRef(pred), object))
            unitlabel = ""
            mydata = HTMLExporter.searchObjectConnectionsForAggregateData(graph, object, predstr, geojsonrep, foundmedia,
                                                                          imageannos, textannos, image3dannos,
                                                                          annobodies,
                                                                          label, unitlabel, nonns, inverse, labellang,
                                                                          typeproperty, prefixes)
            label = mydata["label"]
            if label == "":
                label = str(DocUtils.shortenURI(objstr))
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
                rdfares = f" about=\"{objstr}\" resource=\"{subject}\""
                microdatares = f" itemref=\"{objstr}\" "
            else:
                rdfares = f"resource=\"{objstr}\""
                microdatares = " "
            if baseurl in objstr or isinstance(object, BNode):
                rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, objstr, True)
                tablecontents += f"<span><a itemprop=\"{predstr}\"{microdatares}property=\"{pred}\" {rdfares} href=\"{rellink}\">{label} <span style=\"color: #666;\">({namespaceshort}:{DocUtils.shortenURI(objstr)})</span></a>"
                if bibtex is not None:
                    tablecontents += f"<details><summary>[BIBTEX]</summary><pre>{bibtex}</pre></details>"
            else:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, objstr)
                if res["uri"] != "":
                    tablecontents += f"<span><a itemprop=\"{predstr}\"{microdatares}property=\"{predstr}\" {rdfares} target=\"_blank\" href=\"{objstr}\">{label} <span style=\"color: #666;\">({res['uri']})</span></a>"
                else:
                    tablecontents += f"<span><a itemprop=\"{predstr}\"{microdatares}property=\"{predstr}\" {rdfares} target=\"_blank\" href=\"{objstr}\">{label}</a>"
                if bibtex is not None:
                    tablecontents += f"<details><summary>[BIBTEX]</summary><pre>{bibtex}</pre></details>"
                if generatePagesForNonNS:
                    rellink = DocUtils.generateRelativeLinkFromGivenDepth(str(baseurl), checkdepth,f'{baseurl}nonns_{DocUtils.shortenURI(objstr.replace(":", "_"))}', False)
                    tablecontents += f" <a href=\"{rellink}.html\">[x]</a>"
            if unitlabel:
                tablecontents += f" <span style=\"font-weight:bold\">[{unitlabel}]</span>"
            if timeobj is not None:
                res = OWLTimePage.timeObjectToHTML(timeobj, prefixes)
                if res:
                    tablecontents += f" <span style=\"font-weight:bold\">[{res}]</span>"
                dateprops = timeobj
            tablecontents += "</span>"
        else:
            label = objstr
            if ttlf is not None:
                ttlf.add((subject, URIRef(pred), object))
            objstrrep = objstr.replace("<", "&lt").replace(">", "&gt;").replace("\"", "'")
            if isinstance(object, Literal) and object.datatype is not None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(object.datatype))
                objstring = objstr.replace("<", "&lt").replace(">", "&gt;")
                if object.datatype == XSD.anyURI:
                    objstring = f'<a href="{objstr}">{objstr}</a>'
                elif str(object.datatype) in DocConfig.timeliteraltypes and dateprops is not None and DocUtils.shortenURI(predstr, True) not in DocConfig.metadatanamespaces and str(pred) not in dateprops:
                    dateprops.append(predstr)
                tablecontents += f"<span itemprop=\"{predstr}\" property=\"{predstr}\" content=\"{objstrrep}\" datatype=\"{object.datatype}\">{HTMLExporter.truncateValue(objstring)} <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                    object.datatype) + "\">" + (res["uri"] if res is not None else DocUtils.shortenURI(
                    str(object.datatype))) + "</a>)</small></span>"
                geojsonrep = LiteralUtils.resolveGeoLiterals(URIRef(pred), object, graph, geojsonrep, nonns, subject)
            else:
                if object.language is not None:
                    tablecontents += f'<span itemprop="{predstr}" property="{predstr}" content="{objstrrep} datatype="http://www.w3.org/1999/02/22-rdf-syntax-ns#langString" xml:lang="{object.language}">"{HTMLExporter.truncateValue(objstr.replace("<", "&lt").replace(">","&gt;"))} <small>(<a style="color: #666;" target="_blank" href="http://www.w3.org/1999/02/22-rdf-syntax-ns#langString">rdf:langString</a>) (<a href="http://www.lexvo.org/page/iso639-1/"{object.language}" target="_blank">iso6391:{object.language}</a>)</small></span>'
                else:
                    tablecontents += HTMLExporter.detectStringLiteralContent(pred, object)
        return {"html": tablecontents, "geojson": geojsonrep, "foundmedia": foundmedia, "imageannos": imageannos,
                "textannos": textannos, "image3dannos": image3dannos, "annobodies": annobodies, "label": label,
                "timeobj": dateprops}

    @staticmethod
    def processLicense(license):
        if license is None or license == "" or license == "No License Statement":
            return ["", None]
        if license.startswith("CC"):
            spl = license.split(" ")
            res = f'<span style="float:right;margin-left:auto;margin-right:0px;text-align:right">This work is released under <a rel="license" target="_blank" href="http://creativecommons.org/licenses/{str(spl[1]).lower()}/{spl[2]}/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/{str(spl[1]).lower()}/{spl[2]}/80x15.png"/></a></span>'
            licenseuri = f'http://creativecommons.org/licenses/{str(spl[1]).lower()}/{spl[2]}'
            return [res, licenseuri]
        else:
            return ["""All rights reserved.""", None]

    @staticmethod
    def formatPredicate(tupstr, baseurl, checkdepth, graph, reverse, labellang, prefixes):
        label = DocUtils.getLabelForObject(URIRef(tupstr), graph, None, labellang)
        tablecontents = f'<td class="property">{"Is " if reverse else ""}'
        #if reverse:
        #    tablecontents += "Is "
        if baseurl in tupstr:
            rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, tupstr, True)
            tablecontents += f"<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"{rellink}\">{label}</a></span>"
        else:
            res = DocUtils.replaceNameSpacesInLabel(prefixes, tupstr)
            tablecontents+= f"<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"{tupstr}\">{label} "+("<span style=\"color: #666;\">(" + res["uri"] + ")</span>" if res["uri"]!="" else "")+"</a> </span>"
        return tablecontents+f'{" of" if reverse else ""}</td>'
        #if reverse:
        #    tablecontents += " of"
        #tablecontents += "</td>"
        #return tablecontents+"</td>"

    @staticmethod
    def truncateValue(value, limit=150):
        if len(value) > limit:
            return f"<details><summary style=\"list-style-type: none;\">{value[0:limit]} (...)</summary>{value[limit:]}</details>"
        return value

    @staticmethod
    def detectStringLiteralContent(pred, object):
        if object.startswith("http"):
            return f'<span><a itemprop="{pred}" property="{pred}" target="_blank" href="{object}" datatype="http://www.w3.org/2001/XMLSchema#string">{object}</a> <small>(<a style="color: #666;" target="_blank" href="http://www.w3.org/2001/XMLSchema#string">xsd:string</a>)</small></span>'
        elif object.startswith("www."):
            return f'<span><a itemprop="{pred}" property="{pred}" target="_blank" href="http://{object}" datatype="http://www.w3.org/2001/XMLSchema#string">http://{object}</a> <small>(<a style="color: #666;" target="_blank" href="http://www.w3.org/2001/XMLSchema#string">xsd:string</a>)</small></span>'
        elif re.search(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)', str(object)):
            return f'<span><a itemprop="{pred}" property="{pred}" href="https://www.doi.org/{object}" datatype="http://www.w3.org/2001/XMLSchema#anyURI">{object}</a> <small>(<a style="color: #666;" target="_blank" href="http://www.w3.org/2001/XMLSchema#anyURI">xsd:anyURI</a>)</small></span>'
        elif re.search(r'[\w.]+\@[\w.]+', object):
            return f"<span><a itemprop=\"{pred}\" property=\"{pred}\" href=\"mailto:{object}\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">mailto:{object}</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return f"<span property=\"{pred}\" content=\""+str(object).replace("<", "&lt").replace(">","&gt;").replace("\"", "'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<","&lt").replace(">","&gt;")+" <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
