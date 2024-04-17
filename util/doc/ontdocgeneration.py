# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from qgis.core import Qgis, QgsMessageLog
import os
import shutil
import json
import traceback

from .docutils import DocUtils
from .docconfig import DocConfig
from .docdefaults import DocDefaults
from .templateutils import TemplateUtils
from ..export.pages.indexviewpage import IndexViewPage
from ..export.api.ckanexporter import CKANExporter
from ..export.api.solidexporter import SolidExporter
from ..export.api.iiifexporter import IIIFAPIExporter
from ..export.api.ogcapifeaturesexporter import OGCAPIFeaturesExporter
from .classtreeutils import ClassTreeUtils
from .graphutils import GraphUtils
from ..sparqlutils import SPARQLUtils
from ..export.data.htmlexporter import HTMLExporter
from ..export.data.vowlexporter import OWL2VOWL
from ..export.data.voidexporter import VoidExporter

listthreshold=5
maxlistthreshold=1500

jsonindent=2

templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/html/"))

featurecollectionspaths={}
iiifmanifestpaths={"default":[]}
imagetoURI={}

templates=DocDefaults.templates

class OntDocGeneration:

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,createcollections,baselayers,tobeaddedPerInd,maincolor,tablecolor,progress,createIndexPages=True,generatePagesForNonNS=False,metadatatable=False,createVOWL=False,apis={},imagemetadata=False,startconcept="",deploypath="",logoname="",offlinecompat=False,exports=["ttl","json"],templatename="default"):
        self.pubconfig = {"prefixes": prefixes, "prefixnamespace": prefixnamespace,
                          "namespaceshort": prefixnsshort.replace("/", ""), "createIndexPages": createIndexPages,
                          "modtime": None, "outpath": outpath, "exports": exports, "apis": apis,
                          "publisher": "", "publishingorg": "",
                          "startconcept": startconcept, "metadatatable": metadatatable, "createVOWL": createVOWL,
                          "templatename": templatename, "imagemetadata": imagemetadata,
                          "datasettitle": "", "logoname": logoname, "localOptimized": True,
                          "labellang": labellang, "license": license, "deploypath": deploypath,
                          "offlinecompat": offlinecompat, "generatePagesForNonNS": generatePagesForNonNS,
                          "repository": None, "createColl": createcollections}
        self.progress=progress
        self.baselayers=baselayers
        self.tobeaddedPerInd=tobeaddedPerInd
        QgsMessageLog.logMessage("Exports: " + str(exports), "OntdocGeneration", Qgis.Info)
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
        self.subclassproperty = "http://www.w3.org/2000/01/rdf-schema#subClassO"
        keyprops=GraphUtils.determineKeyProperties(graph)
        if len(keyprops["typeproperty"])>0:
            self.typeproperty=keyprops["typeproperty"][0]
        if len(keyprops["subclassproperty"])>0:
            self.suclassproperty=keyprops["subclassproperty"][0]
        self.graph=graph
        self.graph = DocUtils.resolveOWLImports(self.graph)
        self.htmlexporter = HTMLExporter(prefixes, prefixnamespace, prefixnsshort, license, labellang, outpath,
                                         metadatatable, generatePagesForNonNS, apis, templates,
                                         self.pubconfig["namespaceshort"], self.typeproperty, imagemetadata,
                                         self.pubconfig["localOptimized"], deploypath, logoname, offlinecompat)
        for nstup in self.graph.namespaces():
            if str(nstup[1]) not in prefixes["reversed"]:
                prefixes["reversed"][str(nstup[1])]=str(nstup[0])
        self.preparedclassquery = prepareQuery(
            DocConfig.classtreequery.replace("%%typeproperty%%", "<" + self.typeproperty + ">").replace(
                "%%subclassproperty%%", "<" + self.subclassproperty + ">"))
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
        if currentsubject==None and allsubjects==None:
            self.progress.setLabelText(newtext + processsubject)
        else:
            self.progress.setLabelText(newtext + "\n Processed: "+str(currentsubject)+" of "+str(allsubjects)+" "+str(processsubject)+"... ("+str(round(((currentsubject/allsubjects)*100),0))+"%)")


    def downloadFailed(self, error):
        QgsMessageLog.logMessage("Downloader Error: " + str(error), "OntdocGeneration", Qgis.Info)

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.pubconfig["outpath"]
        self.pubconfig["corpusid"]=self.pubconfig["namespaceshort"].replace("#","")
        if self.pubconfig["datasettitle"] is None or self.pubconfig["datasettitle"]== "":
            self.pubconfig["datasettitle"]=self.pubconfig["corpusid"]+"_dataset"
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem={}
        self.updateProgressBar(None, None, "Creating classtree and search index")
        if self.pubconfig["createVOWL"]:
            vowlinstance=OWL2VOWL()
            vowlinstance.convertOWL2VOWL(self.graph,outpath)
        tmp=HTMLExporter.processLicense(self.pubconfig["license"])
        curlicense=tmp[0]
        self.licensehtml = tmp[0]
        self.licenseuri=tmp[1]
        voidds=prefixnamespace+self.pubconfig["datasettitle"].replace(" ","_")
        if self.pubconfig["createColl"]:
            self.graph=GraphUtils.createCollections(self.graph,prefixnamespace,self.typeproperty)
        if self.pubconfig["logoname"] is not None and self.pubconfig["logoname"] != "" and not self.pubconfig["logoname"].startswith("http"):
            logoname=self.pubconfig["logoname"]
            if not os.path.isdir(outpath + "/logo/"):
                os.mkdir(outpath + "/logo/")
            shutil.copy(logoname, outpath + "/logo/logo." + logoname[logoname.rfind("."):])
            self.pubconfig["logoname"] = outpath + "/logo/logo." + logoname[logoname.rfind("."):]
        res = GraphUtils.analyzeGraph(self.graph, prefixnamespace, self.typeproperty, voidds, labeltouri, uritolabel,
                                      self.pubconfig["outpath"], self.pubconfig["createVOWL"])
        subjectstorender=res["subjectstorender"]
        if os.path.exists(outpath + self.pubconfig["corpusid"] + '_search.js'):
            try:
                with open(outpath + self.pubconfig["corpusid"] + '_search.js', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=",""))
                    for key in data:
                        labeltouri[key]=data[key]
            except Exception as e:
                QgsMessageLog.logMessage("Exception occurred " + str(e), "OntdocGeneration", Qgis.Info)
        with open(outpath + self.pubconfig["corpusid"] + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=jsonindent, sort_keys=True))
            f.close()
        if self.pubconfig["offlinecompat"]:
            if os.path.exists(outpath+"icons/"):
                shutil.rmtree(outpath+"icons/")
            shutil.copytree(templatepath+"/"+self.pubconfig["templatename"]+"/icons/", outpath+"icons/")
        prevtree=[]
        if os.path.exists(outpath + self.pubconfig["corpusid"] + '_classtree.js'):
            try:
                with open(outpath + self.pubconfig["corpusid"] + '_classtree.js', 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=",""))["core"]["data"]
            except Exception as e:
                QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        classidset=set()
        tree = ClassTreeUtils.getClassTree(self.graph, uritolabel, classidset, uritotreeitem, self.typeproperty,
                                           self.pubconfig["prefixes"], self.preparedclassquery)
        for tr in prevtree:
            if tr["id"] not in classidset:
                tree["core"]["data"].append(tr)
        res["http://rdfs.org/ns/void#classes"]=len(classidset)
        res["http://rdfs.org/ns/void#triples"] = len(self.graph)
        voidgraph = VoidExporter.createVoidDataset(self.pubconfig, self.licenseuri,
                                                   res["voidstats"], subjectstorender,
                                                   tree, res["predmap"], res["nonnscount"], res["nscount"], res["instancecount"])
        self.voidstatshtml = VoidExporter.toHTML(res["voidstats"], self.pubconfig["deploypath"])
        self.graph+=voidgraph["graph"]
        subjectstorender=voidgraph["subjects"]
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(templates["stylesheet"].replace("%%maincolorcode%%",self.maincolorcode).replace("%%tablecolorcode%%",self.tablecolorcode))
            f.close()
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(templates["startscripts"].replace("{{baseurl}}",prefixnamespace))
            f.close()
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(templates["epsgdefs"])
            f.close()
        with open(outpath + self.pubconfig["corpusid"] + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=jsonindent))
            f.close()
        paths = {}
        nonnsmap={}
        postprocessing=Graph()
        subtorenderlen = len(subjectstorender)
        subtorencounter = 0
        for subj in subjectstorender:
            path = subj.replace(prefixnamespace, "")
            paths=DocUtils.processSubjectPath(outpath,paths,path,self.graph)
            if os.path.exists(outpath + path + "/index.ttl"):
                try:
                    self.graph.parse(outpath + path + "/index.ttl")
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
            res = self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                                  self.graph.subject_predicates(subj),
                                  self.graph, str(self.pubconfig["corpusid"]) + "_search.js", str(self.pubconfig["corpusid"]) + "_classtree.js",
                                  uritotreeitem, curlicense, subjectstorender, postprocessing, nonnsmap)
            postprocessing = res[0]
            nonnsmap = res[1]
            subtorencounter += 1
            if subtorencounter%250==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
        for subj in postprocessing.subjects(None,None,True):
            path = str(subj).replace(prefixnamespace, "")
            paths=DocUtils.processSubjectPath(outpath,paths,path,self.graph)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    QgsMessageLog.logMessage(e)
            self.htmlexporter.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace,
                            self.graph.subject_predicates(subj),
                            self.graph, str(self.pubconfig["corpusid"]) + "_search.js", str(self.pubconfig["corpusid"]) + "_classtree.js", uritotreeitem,
                            curlicense, subjectstorender, postprocessing)
            subtorencounter += 1
            if subtorencounter%500==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
            QgsMessageLog.logMessage(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
        ClassTreeUtils.checkGeoInstanceAssignment(uritotreeitem)
        classlist=ClassTreeUtils.assignGeoClassesToTree(tree)
        if self.pubconfig["generatePagesForNonNS"]:
            self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, self.pubconfig["corpusid"], outpath, self.pubconfig["license"],prefixnamespace,uritotreeitem,labeltouri)
        with open(outpath + self.pubconfig["corpusid"] + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=jsonindent))
            f.close()
        with open(outpath + self.pubconfig["corpusid"] + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.htmlexporter.has3d:
            if not os.path.exists(outpath + "/js"):
                os.makedirs(outpath + "/js")
            with open(outpath + "/js/corto.em.js", 'w', encoding='utf-8') as f:
                f.write(templates["corto.em"])
                f.close()
            with open(outpath + "/js/nexus.js", 'w', encoding='utf-8') as f:
                f.write(templates["nexus"])
                f.close()
        if self.pubconfig["apis"]["iiif"]:
            IIIFAPIExporter.generateIIIFAnnotations(outpath,imagetoURI)
        if self.pubconfig["createIndexPages"]:
            IndexViewPage.createIndexPages(self.pubconfig, templates, self.pubconfig["apis"], paths, subjectstorender,
                                           uritotreeitem, voidds, tree, classlist, self.graph, self.voidstatshtml,
                                           curlicense)
        if "sparqltemplate" in templates:
            sparqlhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "false", self.pubconfig)
            sparqlhtml = sparqlhtml.replace("{{iconprefixx}}",
                                            ("icons/" if self.pubconfig["offlinecompat"] else "")).replace(
                "{{baseurl}}", prefixnamespace).replace("{{relativedepth}}", "0").replace("{{relativepath}}",
                                                                                          ".").replace("{{toptitle}}",
                                                                                                       "SPARQL Query Editor").replace(
                "{{title}}", "SPARQL Query Editor").replace("{{startscriptpath}}", "startscripts.js").replace(
                "{{stylepath}}", "style.css") \
                .replace("{{classtreefolderpath}}", self.pubconfig["corpusid"] + "_classtree.js").replace(
                "{{baseurlhtml}}", "").replace(
                "{{nonnslink}}", "").replace("{{scriptfolderpath}}", self.pubconfig["corpusid"] + "_search.js").replace(
                "{{exports}}",
                templates[
                    "nongeoexports"]).replace(
                "{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace("{{bibtex}}",
                                                                                                          "").replace(
                "{{proprelationpath}}", "proprelations.js")
            sparqlhtml += templates["sparqltemplate"].replace("{{relativepath}}","")
            tempfoot = templates["footer"].replace("{{license}}", curlicense).replace("{{exports}}", templates["nongeoexports"]).replace(
                "{{bibtex}}", "")
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.pubconfig["apis"]["ogcapifeatures"], self.pubconfig["apis"]["iiif"], self.pubconfig["apis"]["ckan"]],
                                                        [
                                                            "<a href=\"" + str(
                                                                self.pubconfig["deploypath"]) + "/sparql.html?endpoint=" + str(
                                                                self.pubconfig["deploypath"]) + "\">[SPARQL]</a>&nbsp;",
                                                            "<a href=\"" + str(
                                                                self.pubconfig["deploypath"]) + "/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            "<a href=\"" + str(self.pubconfig["deploypath"]) + "/iiif/\">[IIIF]</a>&nbsp;",
                                                            "<a href=\"" + str(self.pubconfig["deploypath"]) + "/api/v3/\">[CKAN]</a>"
                                                        ], "{{apis}}")
            sparqlhtml += tempfoot
            with open(outpath + "sparql.html", 'w', encoding='utf-8') as f:
                f.write(sparqlhtml)
                f.close()
        relpath = DocUtils.generateRelativePathFromGivenDepth(0)
        if len(iiifmanifestpaths["default"])>0:
            IIIFAPIExporter.generateIIIFCollections(self.pubconfig["outpath"],self.pubconfig["deploypath"],iiifmanifestpaths["default"],prefixnamespace)
            IIIFAPIExporter.generateImageGrid(self.pubconfig["deploypath"], iiifmanifestpaths["default"], templates["imagegrid"], outpath+"imagegrid.html")
        if len(featurecollectionspaths)>0 and self.pubconfig["apis"]["ckan"]:
            CKANExporter.generateCKANCollection(outpath, self.pubconfig["deploypath"],
                                                self.htmlexporter.featurecollectionspaths, tree["core"]["data"],
                                                self.pubconfig["license"])
        if self.pubconfig["apis"]["solidexport"]:
            SolidExporter.createSolidSettings(self.graph, outpath, self.pubconfig["deploypath"], self.pubconfig["publisher"], self.pubconfig["datasettitle"],
                                              tree["core"]["data"])
        if len(self.htmlexporter.featurecollectionspaths) > 0:
            relpath=DocUtils.generateRelativePathFromGivenDepth(0)
            indexhtml = templates["htmltemplate"].replace("{{iconprefixx}}",(relpath+"icons/" if self.pubconfig["offlinecompat"] else "")).replace("{{logo}}",self.pubconfig["logoname"]).replace("{{relativepath}}",relpath).replace("{{relativedepth}}","0").replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Feature Collection Overview").replace("{{title}}","Feature Collection Overview").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{epsgdefspath}}", "epsgdefs.js")\
                    .replace("{{classtreefolderpath}}",self.pubconfig["corpusid"] + "_classtree.js").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}", self.pubconfig["corpusid"] + '_search.js').replace("{{exports}}",templates["nongeoexports"])
            indexhtml = indexhtml.replace("{{indexpage}}", "true")
            OGCAPIFeaturesExporter.generateOGCAPIFeaturesPages(outpath,self.pubconfig["deploypath"], featurecollectionspaths, prefixnamespace, self.pubconfig["apis"]["ogcapifeatures"],
                                             True)
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml+="<script src=\"features.js\"></script>"
            indexhtml+=templates["maptemplate"].replace("var ajax=true","var ajax=false").replace("var featurecolls = {{myfeature}}","").replace("{{relativepath}}",DocUtils.generateRelativePathFromGivenDepth(0)).replace("{{baselayers}}",json.dumps(self.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", ""))
            tempfoot = templates["footer"].replace("{{license}}", curlicense).replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}","")
            tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, self.pubconfig["apis"]["ogcapifeatures"], self.pubconfig["apis"]["iiif"], self.pubconfig["apis"]["ckan"]],
                                                        [
                                                            "<a href=\"sparql.html?endpoint=" + str(
                                                                self.pubconfig["deploypath"]) + "\">[SPARQL]</a>&nbsp;",
                                                            "<a href=\"/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                            "<a href=\"iiif/\">[IIIF]</a>&nbsp;",
                                                            "<a href=\"api/3/\">[CKAN]</a>"
                                                        ], "{{apis}}")
            indexhtml+=tempfoot
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()
        return subjectstorender


    def getSubjectPagesForNonGraphURIs(self,uristorender,graph,prefixnamespace,corpusid,outpath,nonnsmap,baseurl,uritotreeitem,labeltouri):
        #QgsMessageLog.logMessage("Subjectpages " + str(uristorender), "OntdocGeneration", Qgis.Info)
        nonnsuris=len(uristorender)
        counter=0
        for uri in uristorender:
            label=""
            for tup in graph.predicate_objects(URIRef(uri)):
                if str(tup[0]) in SPARQLUtils.labelproperties:
                    label = str(tup[1])
            if uri in uritotreeitem:
                res = DocUtils.replaceNameSpacesInLabel(self.pubconfig["prefixes"],str(uri))
                label = DocUtils.getLabelForObject(URIRef(str(uri)), graph,self.pubconfig["prefixes"], self.pubconfig["labellang"])
                if res is not None and label != "":
                    uritotreeitem[uri][-1]["text"] = label + " (" + res["uri"] + ")"
                elif label != "":
                    uritotreeitem[uri][-1]["text"] = label + " (" + DocUtils.shortenURI(uri) + ")"
                else:
                    uritotreeitem[uri][-1]["text"] = DocUtils.shortenURI(uri)
                uritotreeitem[uri][-1]["id"] = prefixnamespace + "nonns_" + DocUtils.shortenURI(uri) + ".html"
                labeltouri[label] = prefixnamespace + "nonns_" + DocUtils.shortenURI(uri) + ".html"
            if counter%10==0:
                self.updateProgressBar(counter,nonnsuris,"NonNS URIs")
            #QgsMessageLog.logMessage("NonNS Counter " +str(counter)+"/"+str(nonnsuris)+" "+ str(uri), "OntdocGeneration", Qgis.Info)
            self.htmlexporter.createHTML(outpath+"nonns_"+DocUtils.shortenURI(uri)+".html", None, URIRef(uri), baseurl, graph.subject_predicates(URIRef(uri),True), graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", None, self.pubconfig["license"], None, Graph(),uristorender,True,label)
            counter+=1

    def polygonToPath(self, svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>",
                           "<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")