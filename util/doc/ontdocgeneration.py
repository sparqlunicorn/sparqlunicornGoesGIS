# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from qgis.core import Qgis, QgsMessageLog
import os
import shutil
import json
import traceback
import time
from collections import OrderedDict
from collections import defaultdict

from .docutils import DocUtils
from .docconfig import DocConfig
from .docdefaults import DocDefaults
from .templateutils import TemplateUtils
from ..export.pages.indexviewpage import IndexViewPage
from ..export.pages.sparqlpage import SPARQLPage
from ..export.api.ckanexporter import CKANExporter
from ..export.api.solidexporter import SolidExporter
from ..export.api.wfsexporter import WFSExporter
from ..export.api.iiifexporter import IIIFAPIExporter
from ..export.api.ogcapifeaturesexporter import OGCAPIFeaturesExporter
from .classtreeutils import ClassTreeUtils
from .graphutils import GraphUtils
from ..sparqlutils import SPARQLUtils
from ..export.data.htmlexporter import HTMLExporter
from ..export.data.vowlexporter import VOWLExporter
from ..export.data.voidexporter import VoidExporter

listthreshold=5
maxlistthreshold=1500

jsonindent=2

templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/html/"))
resourcepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/"))

featurecollectionspaths={}
iiifmanifestpaths={"default":[]}
imagetoURI={}

templates=DocDefaults.templates

class OntDocGeneration:

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,createcollections,baselayers,tobeaddedPerInd,maincolor,tablecolor,progress,createIndexPages=True,generatePagesForNonNS=False,metadatatable=False,createVOWL=False,apis={},imagemetadata=False,startconcept="",deploypath="",logoname="",offlinecompat=False,exports=["ttl","json"],templatename="default"):
        self.pubconfig = {"prefixes": prefixes, "prefixns": prefixnamespace,
                          "namespaceshort": prefixnsshort.replace("/", ""), "createIndexPages": createIndexPages,
                          "modtime": None, "outpath": outpath, "exports": exports, "apis": apis,
                          "publisher": "", "publishingorg": "","logourl":logoname,"collectionClass":"http://www.w3.org/2004/02/skos/core#Collection",
                          "startconcept": startconcept, "metadatatable": metadatatable, "createvowl": createVOWL,
                          "templatename": templatename, "imagemetadata": imagemetadata,
                          "datasettitle": "", "logoname": logoname, "localOptimized": True,
                          "labellang": labellang, "license": license, "deploypath": deploypath,
                          "offlinecompat": offlinecompat, "nonnspages": generatePagesForNonNS,
                          "repository": "", "createCollections": createcollections}
        self.progress=progress
        self.baselayers=baselayers
        self.tobeaddedPerInd=tobeaddedPerInd
        self.exectimes = OrderedDict()
        self.templatename = self.pubconfig["templatename"]
        #QgsMessageLog.logMessage("Exports: " + str(exports), "OntdocGeneration", Qgis.Info)
        if startconcept!="No Start Concept":
            self.pubconfig["startconcept"]=startconcept
        else:
            self.pubconfig["startconcept"]=""
        self.geocache={}
        self.geocollectionspaths=[]
        templates = TemplateUtils.resolveTemplate(templatename, templatepath)
        if offlinecompat:
            global htmltemplate
            htmltemplate = DocUtils.createOfflineCompatibleVersion(outpath, templates["htmltemplate"],templatepath,templatename)
            global maptemplate
            maptemplate = DocUtils.createOfflineCompatibleVersion(outpath, templates["maptemplate"],templatepath,templatename)
            global sparqltemplate
            sparqltemplate=DocUtils.createOfflineCompatibleVersion(outpath,templates["sparqltemplate"],templatepath,templatename)
        self.maincolorcode="#c0e2c0"
        self.tablecolorcode="#810"
        if maincolor is not None:
            self.maincolorcode=maincolor
        if tablecolor is not None:
            self.tablecolorcode=tablecolor
        self.licenseuri=None
        self.typeproperty = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.subclassproperty = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        keyprops=GraphUtils.determineKeyProperties(graph)
        if len(keyprops["typeproperty"])>0:
            self.typeproperty=keyprops["typeproperty"][0]
        if len(keyprops["subclassproperty"])>0:
            self.suclassproperty=keyprops["subclassproperty"][0]
        self.graph=graph
        self.graph = DocUtils.resolveOWLImports(self.graph)
        self.htmlexporter = HTMLExporter(self.pubconfig, templates, self.typeproperty)
        for nstup in self.graph.namespaces():
            if str(nstup[1]) not in prefixes["reversed"]:
                prefixes["reversed"][str(nstup[1])]=str(nstup[0])
        self.preparedclassquery = prepareQuery(
            DocConfig.classtreequery.replace("%%typeproperty%%", "<" + self.typeproperty + ">").replace("%%subclassproperty%%", "<" + self.subclassproperty + ">"))
        if prefixnamespace is None or prefixnsshort is None or prefixnamespace== "" or prefixnsshort== "":
            self.namespaceshort = "suni"
            self.prefixnamespace = "http://purl.org/suni/"
        if outpath is None:
            self.pubconfig["outpath"] = "suni_htmls/"
        else:
            self.pubconfig["outpath"] = self.pubconfig["outpath"].replace("\\", "/")
            if not self.pubconfig["outpath"].endswith("/"):
                self.pubconfig["outpath"] += "/"
        prefixes["reversed"]["http://purl.org/cuneiform/"] = "cunei"
        prefixes["reversed"]["http://purl.org/graphemon/"] = "graphemon"
        prefixes["reversed"]["http://www.opengis.net/ont/crs/"] = "geocrs"
        prefixes["reversed"]["http://www.ontology-of-units-of-measure.org/resource/om-2/"] = "om"
        prefixes["reversed"]["http://purl.org/meshsparql/"] = "msp"


    def updateProgressBar(self,currentsubject,allsubjects,processsubject="URIs"):
        newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
        if currentsubject is None and allsubjects is None:
            self.progress.setLabelText(newtext + processsubject)
        else:
            self.progress.setLabelText(newtext + "\n Processed: "+str(currentsubject)+" of "+str(allsubjects)+" "+str(processsubject)+"... ("+str(round(((currentsubject/allsubjects)*100),0))+"%)")


    def downloadFailed(self, error):
        QgsMessageLog.logMessage("Downloader Error: " + str(error), "OntdocGeneration", Qgis.Info)

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.pubconfig["outpath"]
        self.pubconfig["corpusid"]=self.pubconfig["namespaceshort"].replace("#","")
        if self.pubconfig["datasettitle"] is None or self.pubconfig["datasettitle"]== "":
            self.pubconfig["datasettitle"]=self.pubconfig["corpusid"].replace(" ","_")+"_dataset"
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem = defaultdict(list)
        if self.pubconfig["createvowl"]:
            vowlinstance = VOWLExporter()
            vowlinstance.convertOWL2VOWL(self.graph, outpath)
        tmp=HTMLExporter.processLicense(self.pubconfig["license"])
        curlicense=tmp[0]
        self.licensehtml = tmp[0]
        self.pubconfig["licenseuri"]=tmp[1]
        voidds = prefixnamespace + self.pubconfig["datasettitle"].replace(" ","_")
        if self.pubconfig["createCollections"]:
            start=time.time()
            ccls=self.pubconfig["collectionClass"]
            self.graph = GraphUtils.createCollections(self.graph, prefixnamespace,self.typeproperty,ccls)
            end=time.time()
            self.exectimes["Create Collections"] = {"time": end - start}
        if self.pubconfig["logourl"] is not None and self.pubconfig["logourl"] != "" and not self.pubconfig["logourl"].startswith("http"):
            logoname=self.pubconfig["logourl"]
            if not os.path.isdir(outpath + "/logo/"):
                os.mkdir(outpath + "/logo/")
            shutil.copy(logoname, f'{outpath}/logo/logo.{logoname[logoname.rfind("."):]}')
            self.pubconfig["logourl"] = f'{outpath}/logo/logo.{logoname[logoname.rfind("."):]}'
        self.updateProgressBar(0, 1, "Creating classtree and search index")
        start=time.time()
        res=GraphUtils.analyzeGraph(self.graph, prefixnamespace, self.typeproperty, voidds, labeltouri, uritolabel, self.pubconfig["outpath"], self.pubconfig["createvowl"])
        subjectstorender=res["subjectstorender"]
        end=time.time()
        self.exectimes["Graph Analysis"]={"time":end-start}
        if not self.pubconfig["apis"]["iiif"]:
            self.pubconfig["apis"]["iiif"]=res["iiif"]
        searchjspath=f'{outpath}{self.pubconfig["corpusid"]}_search.js'
        classtreepath=f'{outpath}{self.pubconfig["corpusid"]}_classtree.js'
        if os.path.exists(searchjspath):
            try:
                with open(searchjspath, 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=", ""))
                    for key in data:
                        labeltouri[key] = data[key]
            except Exception as e:
                print("Exception occurred " + str(e))
                print(traceback.format_exc())
        with open(searchjspath, 'w', encoding='utf-8') as f:
            f.write("var search=")
            json.dump(labeltouri,f, indent=2, sort_keys=True)
        if self.pubconfig["offlinecompat"]:
            if os.path.exists(outpath + "icons/"):
                shutil.rmtree(outpath + "icons/")
            shutil.copytree(f"{templatepath}/{self.templatename}/icons/", outpath + "icons/")
        prevtree = []
        if os.path.exists(classtreepath):
            try:
                with open(classtreepath, 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=", ""))["core"]["data"]
            except Exception as e:
                print("Exception occurred " + str(e))
        #classidset = set()
        start=time.time()
        clsress = ClassTreeUtils.getClassTree(self.graph, uritolabel, uritotreeitem,self.typeproperty,self.pubconfig["prefixes"],self.preparedclassquery,res["instancecount"],self.pubconfig["outpath"],self.pubconfig)
        end=time.time()
        self.exectimes["Class Tree Generation"]={"time":end-start,"items":clsress[2]}
        print(f"Class Tree Generation time for {clsress[2]} classes: {end-start} seconds")
        tree=clsress[0]
        uritotreeitem=clsress[1]
        numclasses=clsress[2]
        #print(str(tree))
        for tr in prevtree:
            if tr["id"] not in uritotreeitem:
                tree["core"]["data"].append(tr)
        res["voidstats"]["http://rdfs.org/ns/void#classes"] = numclasses
        res["voidstats"]["http://rdfs.org/ns/void#triples"] = len(self.graph)
        start=time.time()
        voidgraph = VoidExporter.createVoidDataset(self.pubconfig, self.pubconfig["licenseuri"],
                                                   res["voidstats"], subjectstorender,
                                                   tree, res["predmap"], res["nonnscount"], res["nscount"], res["instancecount"])
        self.voidstatshtml = VoidExporter.toHTML(res["voidstats"], self.pubconfig["deploypath"])
        self.graph += voidgraph["graph"]
        subjectstorender = voidgraph["subjects"]
        end=time.time()
        self.exectimes["Void stats generation"]={"time":end-start,"items":numclasses}
        print(f"Void stats generation time for {numclasses} classes: {end-start} seconds")
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(templates["style"])
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(templates["startscripts"].replace("{{baseurl}}", prefixnamespace))
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(templates["epsgdefs"])
        paths = {}
        nonnsmap = {}
        postprocessing = Graph()
        subtorencounter = 0
        start=time.time()
        for subj in subjectstorender:
            path=DocUtils.replaceColonFromWinPath(subj.replace(prefixnamespace, ""))
            # try:
            paths = DocUtils.processSubjectPath(outpath, paths, path, self.graph)
            #if os.path.exists(outpath + path + "/index.ttl"):
            #    try:
            #        self.graph.parse(outpath + path + "/index.ttl")
            #    except Exception as e:
            #        print(e)
            #        print(traceback.format_exc())
            res = self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                                  self.graph.subject_predicates(subj),
                                  self.graph, f'{self.pubconfig["corpusid"]}_search.js', f'{self.pubconfig["corpusid"]}_classtree.js',
                                  uritotreeitem, curlicense, subjectstorender, postprocessing, nonnsmap)
            postprocessing = res[0]
            nonnsmap = res[1]
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                subtorenderlen = len(subjectstorender) + len(postprocessing)
                self.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
            # except Exception as e:
            #    print("Create HTML Exception: "+str(e))
            #    print(traceback.format_exc())
        end=time.time()
        self.exectimes["HTML Generation"]={"time":end-start,"items":len(subjectstorender)}
        print(f"HTML generation time for {len(subjectstorender)} pages: {end-start} seconds, about {(end-start)/len(subjectstorender)} seconds per page")
        print("Postprocessing " + str(len(postprocessing)))
        subtorenderlen = len(subjectstorender) + len(postprocessing)
        for subj in postprocessing.subjects(None, None, True):
            path = str(subj).replace(prefixnamespace, "")
            paths = DocUtils.processSubjectPath(outpath, paths, path, self.graph)
            #if os.path.exists(outpath + path + "/index.ttl"):
            #    try:
            #        self.graph.parse(outpath + path + "/index.ttl")
            #    except Exception as e:
            #        print(e)
            #        print(traceback.format_exc())
            self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                            self.graph.subject_predicates(subj),
                            self.graph, f'{self.pubconfig["corpusid"]}_search.js', f'{self.pubconfig["corpusid"]}_classtree.js', uritotreeitem,
                            curlicense, subjectstorender, postprocessing)
            subtorencounter += 1
            if subtorencounter % 250 == 0:
                self.updateProgressBar(subtorencounter, subtorenderlen, "Processing Subject URIs")
        start=time.time()
        ClassTreeUtils.checkGeoInstanceAssignment(uritotreeitem)
        classlist = ClassTreeUtils.assignGeoClassesToTree(tree)
        end=time.time()
        self.exectimes["Finalize Classtree"]={"time":end-start}
        print(f"Finalizing class tree done in {end-start} seconds")
        if self.pubconfig["nonnspages"]:
            start = time.time()
            labeltouri = self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, self.pubconfig["corpusid"], outpath,
                                                             self.licensehtml, prefixnamespace, uritotreeitem, labeltouri)
            end=time.time()
            self.exectimes["NonNS Pages"] = {"time": end - start,"items":len(nonnsmap)}
            print(f"NonNS Page Generation time {end-start} seconds")
        self.updateProgressBar(None, None, "Finalizing Exports")
        with open(classtreepath, 'w', encoding='utf-8') as f:
            f.write("var tree=")
            json.dump(tree,f, indent=2)
        with open(searchjspath, 'w', encoding='utf-8') as f:
            f.write("var search=")
            json.dump(labeltouri,f, indent=2, sort_keys=True)
        if self.htmlexporter.has3d:
            if not os.path.exists(outpath + "/js"):
                os.makedirs(outpath + "/js")
            with open(outpath + "/js/corto.em.js", 'w', encoding='utf-8') as f:
                f.write(templates["corto.em"])
            with open(outpath + "/js/nexus.js", 'w', encoding='utf-8') as f:
                f.write(templates["nexus"])
        if self.pubconfig["apis"]["iiif"]:
            IIIFAPIExporter.generateIIIFAnnotations(outpath, self.htmlexporter.imagetoURI)
        if self.pubconfig["createIndexPages"]:
            start = time.time()
            IndexViewPage.createIndexPages(self.pubconfig,templates,self.pubconfig["apis"],paths,subjectstorender,uritotreeitem,voidds,tree,classlist,self.graph,self.voidstatshtml,curlicense)
            end=time.time()
            print(f"Index Page Creation time: {end-start} seconds")
            self.exectimes["Index Page Creation"] = {"time": end - start}
        if "layouts" in templates:
            for template in templates["layouts"]:
                if template!="main":
                    templates["layouts"][template]=TemplateUtils.resolveIncludes(template,templates)
        if "sparqltemplate" in templates:
            with open(outpath + "sparql.html", 'w', encoding='utf-8') as f:
                SPARQLPage().generatePageView(templates, self.pubconfig, curlicense, self.voidstatshtml,self.graph, f)
        relpath = DocUtils.generateRelativePathFromGivenDepth(0)
        if len(self.htmlexporter.iiifmanifestpaths["default"]) > 0:
            start=time.time()
            IIIFAPIExporter.generateIIIFCollections(self.pubconfig["outpath"], self.pubconfig["deploypath"], self.htmlexporter.iiifmanifestpaths["default"],
                                                    prefixnamespace)
            indexhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "true",self.pubconfig)
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if self.pubconfig["offlinecompat"] else "")).replace("{{baseurl}}",
                                                                                                      self.pubconfig["prefixns"]).replace(
                "{{relativepath}}", relpath).replace("{{toptitle}}", "Feature Collection Overview").replace("{{title}}",
                                                                                                            "Image Grid View").replace(
                "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}",
                                                                                                        "vowl_result.js") \
                .replace("{{classtreefolderpath}}", self.pubconfig["corpusid"] + "_classtree.js").replace("{{proprelationpath}}",
                                                                                        "proprelations.js").replace(
                "{{nonnslink}}", "").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}",
                                                                            self.pubconfig["corpusid"] + '_search.js').replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "")
            IIIFAPIExporter.generateImageGrid(self.pubconfig["outpath"], self.pubconfig["deploypath"], self.htmlexporter.iiifmanifestpaths["default"],
                                              templates["imagegrid"], indexhtml,
                                              DocUtils.replaceStandardVariables(templates["footer"], "", "0",
                                                                            "true",self.pubconfig).replace("{{license}}",
                                                                                            curlicense).replace(
                                                  "{{subject}}", "").replace("{{exports}}",
                                                                             templates["nongeoexports"]).replace(
                                                  "{{bibtex}}", "").replace("{{stats}}", self.voidstatshtml),
                                              outpath + "imagegrid.html")
            end=time.time()
            print(f"IIIF Collection Generation time: {end-start} seconds")
            self.exectimes["IIIF Collection Generation"] = {"time": end - start}
        if len(self.htmlexporter.featurecollectionspaths) > 0 and self.pubconfig["apis"]["ckan"]:
            start=time.time()
            CKANExporter.generateCKANCollection(outpath, self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths, tree["core"]["data"],
                                                self.pubconfig["license"])
            end=time.time()
            print(f"CKAN API Generation time: {end-start} seconds")
            self.exectimes["CKAN API Generation"] = {"time": end - start}
        if self.pubconfig["apis"]["solidexport"]:
            start=time.time()
            SolidExporter.createSolidSettings(self.graph, outpath, self.pubconfig["deploypath"], self.pubconfig["publisher"], self.pubconfig["datasettitle"],
                                              tree["core"]["data"])
            end=time.time()
            print(f"Solid API Generation time: {end-start} seconds")
            self.exectimes["Solid API Generation"] = {"time": end - start}
        if len(self.htmlexporter.featurecollectionspaths) > 0:
            start=time.time()
            indexhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "true",self.pubconfig)
            indexhtml = indexhtml.replace("{{iconprefixx}}",
                                          (relpath + "icons/" if self.pubconfig["offlinecompat"] else "")).replace("{{baseurl}}",
                                                                                                      self.pubconfig["prefixns"]).replace(
                "{{relativepath}}", relpath).replace("{{toptitle}}", "Feature Collection Overview").replace("{{title}}",
                                                                                                            "Feature Collection Overview").replace(
                "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{vowlpath}}",
                                                                                                        "vowl_result.js") \
                .replace("{{classtreefolderpath}}", self.pubconfig["corpusid"] + "_classtree.js").replace("{{proprelationpath}}",
                                                                                        "proprelations.js").replace(
                "{{nonnslink}}", "").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}",
                                                                            self.pubconfig["corpusid"] + '_search.js').replace(
                "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "")
            OGCAPIFeaturesExporter.generateOGCAPIFeaturesPages(outpath, self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths,
                                                               self.pubconfig["prefixns"], self.pubconfig["apis"]["ogcapifeatures"], True)
            WFSExporter.generateWFSPages(outpath,self.pubconfig["deploypath"], self.htmlexporter.featurecollectionspaths,self.licenseuri)
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.write("<p>This page shows feature collections present in the linked open data export</p><script src=\"features.js\"></script>")
                f.write(templates["maptemplate"].replace("var ajax=true", "var ajax=false").replace(
                    "var featurecolls = {{myfeature}}", "").replace("{{relativepath}}",
                                                                    DocUtils.generateRelativePathFromGivenDepth(0)).replace(
                    "{{baselayers}}",
                    json.dumps(DocConfig.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", "")))
                tempfoot = DocUtils.replaceStandardVariables(templates["footer"], "", "0", "true",self.pubconfig).replace("{{license}}",
                                                                                                         curlicense).replace(
                    "{{subject}}", "").replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace(
                    "{{stats}}", self.voidstatshtml)
                tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.pubconfig["apis"]["ogcapifeatures"], self.pubconfig["apis"]["iiif"], self.pubconfig["apis"]["ckan"]],
                                                            [
                                                                f'<a href=\"sparql.html?endpoint={self.pubconfig["deploypath"]}">[SPARQL]</a>&nbsp;',
                                                                "<a href=\"api/api.html\">[OGC API Features]</a>&nbsp;",
                                                                "<a href=\"iiif/\">[IIIF]</a>&nbsp;",
                                                                "<a href=\"api/3/\">[CKAN]</a>"
                                                            ], "{{apis}}")
                f.write(tempfoot)
            end=time.time()
            print(f"OGC API Features Generation time: {end-start} seconds")
            self.exectimes["OGC API Features Generation"] = {"time": end - start}
        return subjectstorender


    def getSubjectPagesForNonGraphURIs(self, uristorender, graph, prefixnamespace, corpusid, outpath, curlicense, baseurl,
                                       uritotreeitem, labeltouri):
        nonnsuris = len(uristorender)
        counter = 0
        # print("NONS URIS TO RENDER: "+str(uristorender))
        for uri in uristorender:
            label = ""
            if prefixnamespace not in uri:
                # print("URI: " + str(uri))
                for tup in graph.predicate_objects(URIRef(uri)):
                    if str(tup[0]) in DocConfig.labelproperties:
                        label = str(tup[1])
                suri = DocUtils.shortenURI(uri)
                if uri in uritotreeitem:
                    res = DocUtils.replaceNameSpacesInLabel(self.pubconfig["prefixes"], str(uri))
                    label = DocUtils.getLabelForObject(URIRef(str(uri)), graph, None, self.pubconfig["labellang"])
                    if res is not None and label != "":
                        uritotreeitem[uri][-1]["text"] = f'{label} ({res["uri"]})'
                    elif label != "":
                        uritotreeitem[uri][-1]["text"] = f'{label} ({suri})'
                    else:
                        uritotreeitem[uri][-1]["text"] = suri
                    uritotreeitem[uri][-1]["id"] = f'{prefixnamespace}nonns_{suri}.html'
                    labeltouri[label] = f'{prefixnamespace}nonns_{suri}.html'
                if counter % 10 == 0:
                    self.updateProgressBar(counter, nonnsuris, "NonNS URIs")
                self.htmlexporter.createHTML(f'{outpath}nonns_{suri}.html', None, URIRef(uri), baseurl,
                                graph.subject_predicates(URIRef(uri), True), graph, f"{corpusid}_search.js",
                                f"{corpusid}_classtree.js", None, curlicense, None, Graph(), uristorender, True,
                                label)
                counter += 1
        return labeltouri

    def polygonToPath(self, svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>","<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")