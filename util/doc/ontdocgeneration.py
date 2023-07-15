# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from qgis.core import Qgis, QgsMessageLog, QgsFileDownloader
from qgis.PyQt.QtCore import QUrl
import os
import re
import urllib
import shutil
import json
from pathlib import Path


from ..layerutils import LayerUtils
from ..sparqlutils import SPARQLUtils
from .pyowl2vowl import OWL2VOWL

templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/html/"))

version="SPARQLing Unicorn QGIS Plugin 0.15"

versionurl="https://github.com/sparqlunicorn/sparqlunicornGoesGIS"

bibtextypemappings={"http://purl.org/ontology/bibo/Document":"@misc","http://purl.org/ontology/bibo/Article":"@article","http://purl.org/ontology/bibo/Thesis":"@phdthesis","http://purl.org/ontology/bibo/BookSection":"@inbook","http://purl.org/ontology/bibo/Book":"@book","http://purl.org/ontology/bibo/Proceedings":"@inproceedings"}

global startscripts
startscripts = ""

global stylesheet
stylesheet = ""

global htmltemplate
htmltemplate = ""

vowltemplate= ""

jsonindent=None

imagecarouselheader="""<div id="imagecarousel" class="carousel slide" data-ride="carousel"><div class="carousel-inner" style="text-align:center">"""

imagecarouselfooter="""</div> <a class="carousel-control-prev" href="#imagecarousel" role="button" data-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="sr-only">Previous</span>
  </a>
  <a class="carousel-control-next" href="#imagecarousel" role="button" data-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="sr-only">Next</span>
  </a></div>"""

imagestemplate="""<div class="{{carousel}}">
<a href="{{image}}" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
</div>"""

imageswithannotemplate="""<div class="{{carousel}}">
<a href=\"{{image}}\" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
{{svganno}}
</div>"""

textwithannotemplate="""<div class="textanno">	
</div>"""

global videotemplate
videotemplate=""

global audiotemplate
audiotemplate=""

imagestemplatesvg="""<div class="{{carousel}}" style="max-width:485px;max-height:500px">
{{image}}
</div>
"""

threejstemplate="""	
<div id="threejs" class="threejscontainer" style="max-width:485px;max-height:500px">	
</div>	
<script>$(document).ready(function(){initThreeJS('threejs',parseWKTStringToJSON("{{wktstring}}"),{{meshurls}})})</script>	
"""

global image3dtemplate
image3dtemplate=""

nongeoexports="""<option value="csv">Comma Separated Values (CSV)</option><option value="geojson">(Geo)JSON</option><option value="json">JSON-LD</option><option value="ttl" selected>Turtle (TTL)</option>"""

geoexports="""<option value="csv">Comma Separated Values (CSV)</option><option value="geojson">(Geo)JSON</option><option value="ttl" selected>Turtle (TTL)</option><option value="wkt">Well-Known-Text (WKT)</option>"""

global maptemplate
maptemplate=""

featurecollectionspaths={}

iiifmanifestpaths={"default":[]}

nonmaptemplate="""<script>var nongeofeature = {{myfeature}}</script>"""

htmlcommenttemplate="""<p class="comment"><b>Description:</b> {{comment}}</p>"""

htmltabletemplate="""
<div style="overflow-x:auto;"><table border=1 width=100% class=description><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{{tablecontent}}</tbody></table></div>"""

global htmlfooter
htmlfooter="""<div id="footer"><div class="container-fluid"><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink2" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button>{{bibtex}}{{license}}</div></div><script>$(document).ready(function(){setSVGDimensions()})</script></body></html>"""

licensetemplate=""""""

classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
        SELECT DISTINCT ?subject ?label ?supertype\n
        WHERE {\n
           { ?individual rdf:type ?subject . } UNION { ?subject rdf:type owl:Class . } UNION { ?subject rdf:type rdfs:Class . }.\n
           OPTIONAL { ?subject rdfs:subClassOf ?supertype } .\n
           OPTIONAL { ?subject rdfs:label ?label. filter(langMatches(lang(?label),\"en\")) }
           OPTIONAL { ?subject rdfs:label ?label }.\n
            FILTER (\n
                (\n
                ?subject != owl:Class &&\n
                ?subject != rdf:List &&\n
                ?subject != rdf:Property &&\n
                ?subject != rdfs:Class &&\n
                ?subject != rdfs:Datatype &&\n
                ?subject != rdfs:ContainerMembershipProperty &&\n
                ?subject != owl:DatatypeProperty &&\n
                ?subject != owl:AnnotationProperty &&\n
                ?subject != owl:Restriction &&\n
                ?subject != owl:ObjectProperty &&\n
                ?subject != owl:NamedIndividual &&\n
                ?subject != owl:Ontology) )\n
        }"""

def resolveTemplate(templatename):
    QgsMessageLog.logMessage("Templatename " + str(templatename), "OntdocGeneration", Qgis.Info)
    QgsMessageLog.logMessage("Templatename " + str(templatepath+"/"+templatename)+" - "+str(os.path.exists(templatepath+"/"+templatename)), "OntdocGeneration", Qgis.Info)
    if os.path.exists(templatepath+"/"+templatename):
        QgsMessageLog.logMessage("Postprocessingggg " + str("""subdir"""), "OntdocGeneration", Qgis.Info)
        if os.path.exists(templatepath+"/"+templatename+"/css/style.css"):
            with open(templatepath+"/"+templatename+"/css/style.css", 'r') as file:
                global stylesheet
                stylesheet=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/js/startscripts.js"):
            with open(templatepath+"/"+templatename+"/js/startscripts.js", 'r') as file:
                global startscripts
                startscripts=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/js/epsgdefs.js"):
            with open(templatepath+"/"+templatename+"/js/epsgdefs.js", 'r') as file:
                global epsgdefs
                epsgdefs=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/header.html"):
            with open(templatepath+"/"+templatename+"/templates/header.html", 'r') as file:
                global htmltemplate
                htmltemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/footer.html"):
            with open(templatepath+"/"+templatename+"/templates/footer.html", 'r') as file:
                global htmlfooter
                htmlfooter=file.read()
        if os.path.exists(templatepath + "/" + templatename + "/templates/geoexports.html"):
            with open(templatepath + "/" + templatename + "/templates/geoexports.html", 'r') as file:
                global geoexports
                geoexports = file.read()
        if os.path.exists(templatepath + "/" + templatename + "/templates/nongeoexports.html"):
            with open(templatepath + "/" + templatename + "/templates/nongeoexports.html", 'r') as file:
                global nongeoexports
                nongeoexports = file.read()
        if os.path.exists(templatepath + "/" + templatename + "/templates/3dtemplate.html"):
            with open(templatepath + "/" + templatename + "/templates/3dtemplate.html", 'r') as file:
                global image3dtemplate
                image3dtemplate = file.read()
        if os.path.exists(templatepath + "/" + templatename + "/templates/threejstemplate.html"):
            with open(templatepath + "/" + templatename + "/templates/threejstemplate.html", 'r') as file:
                global threejstemplate
                threejstemplate = file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/vowlwrapper.html"):
            with open(templatepath+"/"+templatename+"/templates/vowlwrapper.html", 'r') as file:
                global vowltemplate
                vowltemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/audiotemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/audiotemplate.html", 'r') as file:
                global audiotemplate
                audiotemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/videotemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/videotemplate.html", 'r') as file:
                global videotemplate
                videotemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/maptemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/maptemplate.html", 'r') as file:
                global maptemplate
                maptemplate=file.read()
        return True
    return False


class OntDocGeneration:

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,createcollections,baselayers,tobeaddedPerInd,maincolor,tablecolor,progress,createIndexPages=True,nonNSPagesCBox=False,createMetadataTable=False,createVOWL=False,ogcapifeatures=False,iiif=False,startconcept="",deployurl="",logoname="",offlinecompat=False,exports=["ttl","json"],templatename="default"):
        self.prefixes=prefixes
        self.prefixnamespace = prefixnamespace
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.progress=progress
        self.baselayers=baselayers
        self.tobeaddedPerInd=tobeaddedPerInd
        self.logoname=logoname
        self.offlinecompat=offlinecompat
        self.exports=exports
        self.startconcept = None
        if startconcept!="No Start Concept":
            self.startconcept=startconcept
        self.deploypath=deployurl
        self.ogcapifeatures=ogcapifeatures
        self.iiif=iiif
        self.createVOWL=createVOWL
        self.localOptimized=True
        self.geocache={}
        self.metadatatable=createMetadataTable
        self.exportToFunction={"graphml":self.convertTTLToGraphML,"tgf":self.convertTTLToTGF}
        self.generatePagesForNonNS=nonNSPagesCBox
        self.geocollectionspaths=[]
        self.templatename=templatename
        resolveTemplate(templatename)
        if offlinecompat:
            global htmltemplate
            htmltemplate = self.createOfflineCompatibleVersion(outpath, htmltemplate)
            global maptemplate
            maptemplate = self.createOfflineCompatibleVersion(outpath, maptemplate)
        self.maincolorcode="#c0e2c0"
        self.tablecolorcode="#810"
        self.createColl=createcollections
        if maincolor!=None:
            self.maincolorcode=maincolor
        if tablecolor!=None:
            self.tablecolorcode=tablecolor
        self.license=license
        self.licenseuri=None
        self.labellang=labellang
        self.typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.createIndexPages=createIndexPages
        self.graph=graph
        for nstup in self.graph.namespaces():
            if str(nstup[1]) not in prefixes["reversed"]:
                prefixes["reversed"][str(nstup[1])]=str(nstup[0])
        self.preparedclassquery=prepareQuery(classtreequery)
        if prefixnamespace==None or prefixnsshort==None or prefixnamespace=="" or prefixnsshort=="":
            self.namespaceshort = "suni"
            self.prefixnamespace = "http://purl.org/suni/"
        if outpath==None:
            self.outpath = "suni_htmls/"
        else:
            self.outpath = self.outpath.replace("\\", "/")
            if not outpath.endswith("/"):
                self.outpath += "/"
        prefixes["reversed"]["http://purl.org/cuneiform/"] = "cunei"
        prefixes["reversed"]["http://purl.org/graphemon/"] = "graphemon"
        prefixes["reversed"]["http://www.opengis.net/ont/crs/"] = "geocrs"
        prefixes["reversed"]["http://www.ontology-of-units-of-measure.org/resource/om-2/"] = "om"
        prefixes["reversed"]["http://purl.org/meshsparql/"] = "msp"

    def downloadFailed(self, error):
        QgsMessageLog.logMessage("Downloader Error: " + str(error), "OntdocGeneration", Qgis.Info)


    def createOfflineCompatibleVersion(self,outpath,myhtmltemplate):
        QgsMessageLog.logMessage("OUTPATH: "+str(outpath), "OntdocGeneration", Qgis.Info)
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        if not os.path.isdir(outpath+"/js"):
            os.mkdir(outpath+"/js")
        if not os.path.isdir(outpath+"/css"):
            os.mkdir(outpath+"/css")
        matched=re.findall(r'src="(http.*)"',myhtmltemplate)
        for match in matched:
            #download the library
            if "</script>" in match:
                for m in match.split("></script><script src="):
                    m=m.replace("\"","")
                    QgsMessageLog.logMessage("Downloader: "+ match.replace("\"", "")+" - "+ str(outpath)+str(os.sep)+"js"+str(os.sep) + m[m.rfind("/") + 1:], "OntdocGeneration", Qgis.Info)
                    try:
                        g = urllib.request.urlopen(m.replace("\"", ""))
                        with open(outpath + str(os.sep)+"js"+str(os.sep) + m[m.rfind("/") + 1:], 'b+w') as f:
                            f.write(g.read())
                    except Exception as e:
                        QgsMessageLog.logMessage(
                            "Downloader: " + str(e),
                            "OntdocGeneration", Qgis.Info)
                    #dl = QgsFileDownloader(QUrl(m.replace("\"", "")), outpath + str(os.sep)+"js"+str(os.sep) + m[m.rfind("/") + 1:])
                    #dl.downloadError.connect(self.downloadFailed)
                    #QgsMessageLog.logMessage("Downloader: "+m.replace("\"", "")+" - "+str(dl), "OntdocGeneration", Qgis.Info)
                    myhtmltemplate=myhtmltemplate.replace(m,"{{relativepath}}js/"+m[m.rfind("/")+1:])
            else:
                match=match.replace("\"","")
                QgsMessageLog.logMessage("Downloader: "+ match.replace("\"", "")+" - "+ str(outpath) + str(os.sep)+"js"+str(os.sep)+ match[match.rfind("/") + 1:],
                                         "OntdocGeneration", Qgis.Info)
                try:
                    g = urllib.request.urlopen(match.replace("\"", ""))
                    with open(outpath + str(os.sep)+"js"+str(os.sep) + match[match.rfind("/") + 1:], 'b+w') as f:
                        f.write(g.read())
                except Exception as e:
                    QgsMessageLog.logMessage(
                    "Downloader: " + str(e),
                    "OntdocGeneration", Qgis.Info)
                #dl = QgsFileDownloader(QUrl(match.replace("\"","")), outpath + str(os.sep)+"js"+str(os.sep) + match[match.rfind("/") + 1:])
                #dl.downloadError.connect(self.downloadFailed)
                #QgsMessageLog.logMessage("Downloader: " +match.replace("\"","")+" - "+ str(dl), "OntdocGeneration", Qgis.Info)
                myhtmltemplate=myhtmltemplate.replace(match,"{{relativepath}}js/"+match[match.rfind("/")+1:])
        matched=re.findall(r'href="(http.*.css)"',myhtmltemplate)
        for match in matched:
            print(match.replace("\"",""))
            match=match.replace("\"","")
            QgsMessageLog.logMessage("Downloader: " +match.replace("\"", "")+" - "+ str(outpath) +str(os.sep)+"css"+str(os.sep)+ match[match.rfind("/") + 1:],
                                     "OntdocGeneration", Qgis.Info)
            try:
                g = urllib.request.urlopen(match.replace("\"", ""))
                with open(outpath +str(os.sep)+"css"+str(os.sep)+ match[match.rfind("/") + 1:], 'b+w') as f:
                    f.write(g.read())
            except Exception as e:
                QgsMessageLog.logMessage(
                    "Downloader: " + str(e),
                    "OntdocGeneration", Qgis.Info)
            #dl = QgsFileDownloader(QUrl(match.replace("\"", "")), outpath +str(os.sep)+"css"+str(os.sep)+ match[match.rfind("/") + 1:])
            #dl.downloadError.connect(self.downloadFailed)
            #QgsMessageLog.logMessage("Downloader: " +match.replace("\"", "")+" - "+str(dl), "OntdocGeneration", Qgis.Info)
            myhtmltemplate=myhtmltemplate.replace(match,"{{relativepath}}css/"+match[match.rfind("/")+1:])
        return myhtmltemplate

    def processLicense(self):
        QgsMessageLog.logMessage(str(self.license), "OntdocGeneration", Qgis.Info)
        if self.license==None or self.license=="" or self.license=="No License Statement":
            return ""
        if self.license.startswith("CC"):
            spl=self.license.split(" ")
            res= """<span style="float:right;margin-left:auto;margin-right:0px;text-align:right">This work is released under <a rel="license" target="_blank" href="http://creativecommons.org/licenses/"""+str(spl[1]).lower()+"/"+str(spl[2])+"""/">
            <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/"""+str(spl[1]).lower()+"""/"""+str(spl[2])+"""/80x15.png"/></a></span>"""
            self.licenseuri="http://creativecommons.org/licenses/"+str(spl[1]).lower()+"/"+str(spl[2])
            return res
        else:
            return """All rights reserved."""

    def addAdditionalTriplesForInd(self,graph,ind,tobeaddedPerInd):
        for prop in tobeaddedPerInd:
            if "value" in tobeaddedPerInd[prop] and "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"])),
                           URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                           URIRef(str(tobeaddedPerInd[prop]["uri"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"]).replace(" ", "_")),
                           URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                           URIRef(str(tobeaddedPerInd[prop]["value"]))))
            elif "value" in tobeaddedPerInd[prop] and not tobeaddedPerInd[prop]["value"].startswith("http"):
                if "type" in tobeaddedPerInd[prop]:
                    graph.add((ind,URIRef(prop),Literal(tobeaddedPerInd[prop]["value"],datatype=tobeaddedPerInd[prop]["type"])))
                elif "value" in tobeaddedPerInd[prop]:
                    graph.add((ind, URIRef(prop), Literal(tobeaddedPerInd[prop]["value"])))
            elif "value" in tobeaddedPerInd[prop] and not "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))
    def updateProgressBar(self,currentsubject,allsubjects,processsubject="URIs"):
        newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
        self.progress.setLabelText(newtext + "\n Processed: "+str(currentsubject)+" of "+str(allsubjects)+" "+str(processsubject)+"... ("+str(round(((currentsubject/allsubjects)*100),0))+"%)")

    def processSubjectPath(self,outpath,paths,path):
        if "/" in path:
            addpath = ""
            for pathelem in path.split("/"):
                addpath += pathelem + "/"
                if not os.path.isdir(outpath + addpath):
                    os.mkdir(outpath + addpath)
            if outpath + path[0:path.rfind('/')] + "/" not in paths:
                paths[outpath + path[0:path.rfind('/')] + "/"] = []
            paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
        else:
            if not os.path.isdir(outpath + path):
                os.mkdir(outpath + path)
            if outpath not in paths:
                paths[outpath] = []
            paths[outpath].append(path + "/index.html")
        if os.path.exists(outpath + path + "/index.ttl"):
            try:
                self.graph.parse(outpath + path + "/index.ttl")
            except Exception as e:
                QgsMessageLog.logMessage(e)
        return paths

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.outpath
        corpusid=self.namespaceshort.replace("#","")
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem={}
        if self.createVOWL:
            vowlinstance=OWL2VOWL()
            vowlinstance.convertOWL2VOWL(self.graph,outpath)
        curlicense=self.processLicense()
        subjectstorender = set()
        self.getPropertyRelations(self.graph, outpath)
        if self.createColl:
            self.graph=self.createCollections(self.graph,prefixnamespace)
        if self.logoname!=None and self.logoname!="":
            if not os.path.isdir(outpath+"/logo/"):
                os.mkdir(outpath+"/logo/")
            shutil.copy(self.logoname,outpath+"/logo/logo."+self.logoname[self.logoname.rfind("."):])
            self.logoname=outpath+"/logo/logo."+self.logoname[self.logoname.rfind("."):]
        for sub in self.graph.subjects(None,None,True):
            #QgsMessageLog.logMessage(str(prefixnamespace)+" "+str(sub), "OntdocGeneration", Qgis.Info)
            if prefixnamespace in str(sub) and isinstance(sub,URIRef) or isinstance(sub,BNode):
                subjectstorender.add(sub)
                self.addAdditionalTriplesForInd(self.graph,sub,self.tobeaddedPerInd)
                for tup in self.graph.predicate_objects(sub):
                    if str(tup[0]) in SPARQLUtils.labelproperties:
                        labeltouri[str(tup[1])] = str(sub)
                        uritolabel[str(sub)] = {"label":str(tup[1])}
                        break
        if os.path.exists(outpath + corpusid + '_search.js'):
            try:
                with open(outpath + corpusid + '_search.js', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=",""))
                    for key in data:
                        labeltouri[key]=data[key]
            except Exception as e:
                QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=jsonindent, sort_keys=True))
            f.close()
        if os.path.exists(outpath+"icons/"):
            shutil.rmtree(outpath+"icons/")
        shutil.copytree(templatepath+"/"+self.templatename+"/icons/", outpath+"icons/")
        prevtree=[]
        if os.path.exists(outpath + corpusid + '_classtree.js'):
            try:
                with open(outpath + corpusid + '_classtree.js', 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=",""))["core"]["data"]
            except Exception as e:
                QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        classidset=set()
        tree=self.getClassTree(self.graph, uritolabel,classidset,uritotreeitem)
        for tr in prevtree:
            if tr["id"] not in classidset:
                tree["core"]["data"].append(tr)
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(stylesheet.replace("%%maincolorcode%%",self.maincolorcode).replace("%%tablecolorcode%%",self.tablecolorcode))
            f.close()
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(startscripts.replace("{{baseurl}}",prefixnamespace))
            f.close()
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(epsgdefs)
            f.close()
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=jsonindent))
            f.close()
        pathmap = {}
        paths = {}
        nonnsmap={}
        postprocessing=Graph()
        subtorenderlen = len(subjectstorender)
        subtorencounter = 0
        for subj in subjectstorender:
            path = subj.replace(prefixnamespace, "")
            paths=self.processSubjectPath(outpath,paths,path)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    QgsMessageLog.logMessage(e)
            res=self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing,nonnsmap)
            postprocessing=res[0]
            nonnsmap=res[1]
            subtorencounter += 1
            if subtorencounter%250==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
        for subj in postprocessing.subjects(None,None,True):
            path = str(subj).replace(prefixnamespace, "")
            paths=self.processSubjectPath(outpath,paths,path)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    QgsMessageLog.logMessage(e)
            self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing)
            subtorencounter += 1
            if subtorencounter%500==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
            QgsMessageLog.logMessage(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
        self.checkGeoInstanceAssignment(uritotreeitem)
        self.assignGeoClassesToTree(tree)
        if self.generatePagesForNonNS:
            #self.detectURIsConnectedToSubjects(subjectstorender, self.graph, prefixnamespace, corpusid, outpath, self.license,prefixnamespace)
            self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, corpusid, outpath, self.license,prefixnamespace,uritotreeitem,labeltouri)
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=jsonindent))
            f.close()
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        if self.createIndexPages:
            for path in paths:
                subgraph=Graph(bind_namespaces="rdflib")
                QgsMessageLog.logMessage("BaseURL " + str(outpath)+" "+str(path)+" "+outpath + corpusid + '_search.js', "OntdocGeneration", Qgis.Info)
                checkdepth = self.checkDepthFromPath(path, outpath, path)-1
                sfilelink=self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + '_search.js',False)
                classtreelink = self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + "_classtree.js",False)
                stylelink =self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,"style.css",False)
                scriptlink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "startscripts.js", False)
                epsgdefslink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "epsgdefs.js", False)
                vowllink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "vowl_result.js", False)
                nslink=prefixnamespace+str(self.getAccessFromBaseURL(str(outpath),str(path)))
                for sub in subjectstorender:
                    if nslink in sub:
                        for tup in self.graph.predicate_objects(sub):
                            subgraph.add((sub, tup[0], tup[1]))
                if "ttl" in self.exports:
                    subgraph.serialize(path + "index.ttl", encoding="utf-8")
                for ex in self.exports:
                    if ex in self.exportToFunction:
                        with open(path + "index." + str(ex), 'w', encoding='utf-8') as f:
                            res = self.exportToFunction[ex](subgraph,f, subjectstorender)
                            f.close()
                QgsMessageLog.logMessage("BaseURL " + nslink,"OntdocGeneration", Qgis.Info)
                indexhtml = htmltemplate.replace("{{logo}}",self.logoname).replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(prefixnamespace,checkdepth)).replace("{{relativedepth}}", str(checkdepth)).replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Index page for " + nslink).replace("{{title}}","Index page for " + nslink).replace("{{startscriptpath}}", scriptlink).replace("{{stylepath}}", stylelink).replace("{{epsgdefspath}}", epsgdefslink)\
                    .replace("{{classtreefolderpath}}",classtreelink).replace("{{baseurlhtml}}", nslink).replace("{{scriptfolderpath}}", sfilelink).replace("{{exports}}",nongeoexports).replace("{{bibtex}}","").replace("{{versionurl}}",versionurl).replace("{{version}}",version)
                if nslink==prefixnamespace:
                    indexhtml=indexhtml.replace("{{indexpage}}","true")
                else:
                    indexhtml = indexhtml.replace("{{indexpage}}", "false")
                indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"+vowltemplate.replace("{{vowlpath}}", "minivowl_result.js")
                if self.startconcept != None and path == outpath and self.startconcept in uritotreeitem:
                    if self.createColl:
                        indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                     tree["types"][uritotreeitem[self.startconcept][-1]["type"]][
                                         "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + uritotreeitem[self.startconcept][-1][
                                         "type"] + "\"/><a href=\"" + self.generateRelativeLinkFromGivenDepth(
                            prefixnamespace, 0, str(self.startconcept), True) + "\">" + self.shortenURI(
                            self.startconcept) + "</a></p>"
                    else:
                        indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                     tree["types"][uritotreeitem[self.startconcept][-1]["type"]][
                                         "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + uritotreeitem[self.startconcept][-1][
                                         "type"] + "\"/><a href=\"" + self.generateRelativeLinkFromGivenDepth(
                            prefixnamespace, 0, str(self.startconcept), True) + "\">" + self.shortenURI(
                            self.startconcept) + "</a></p>"
                indexhtml+="<table class=\"description\" style =\"height: 100%; overflow: auto\" border=1 id=indextable><thead><tr><th>Class</th><th>Number of instances</th><th>Instance Example</th></tr></thead><tbody>"
                for item in tree["core"]["data"]:
                    if (item["type"]=="geoclass" or item["type"]=="class" or item["type"]=="featurecollection" or item["type"]=="geocollection") and "instancecount" in item and item["instancecount"]>0:
                        exitem=None
                        for item2 in tree["core"]["data"]:
                            if item2["parent"]==item["id"] and (item2["type"]=="instance" or item2["type"]=="geoinstance") and nslink in item2["id"]:
                                checkdepth = self.checkDepthFromPath(path, prefixnamespace, item2["id"])-1
                                exitem="<td><img src=\""+tree["types"][item2["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item2["type"]+"\"/><a href=\""+self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,str(re.sub("_suniv[0-9]+_","",item2["id"])),True)+"\">"+str(item2["text"])+"</a></td>"
                                break
                        if exitem!=None:
                            indexhtml+="<tr><td><img src=\""+tree["types"][item["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item["type"]+"\"/><a href=\""+str(item["id"])+"\" target=\"_blank\">"+str(item["text"])+"</a></td>"
                            indexhtml+="<td>"+str(item["instancecount"])+"</td>"+exitem+"</tr>"
                indexhtml += "</tbody></table><script>$('#indextable').DataTable();</script>"
                indexhtml+=htmlfooter.replace("{{license}}",curlicense).replace("{{exports}}",nongeoexports).replace("{{bibtex}}","")
                #QgsMessageLog.logMessage(path)
                with open(path + "index.html", 'w', encoding='utf-8') as f:
                    f.write(indexhtml)
                    f.close()
        if len(iiifmanifestpaths["default"]) > 0:
            self.generateIIIFCollections(self.outpath, iiifmanifestpaths["default"], prefixnamespace)
        if len(featurecollectionspaths)>0:
            indexhtml = htmltemplate.replace("{{logo}}",self.logoname).replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(prefixnamespace,0)).replace("{{relativedepth}}","0").replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Feature Collection Overview").replace("{{title}}","Feature Collection Overview").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{epsgdefspath}}", "epsgdefs.js")\
                    .replace("{{classtreefolderpath}}",corpusid + "_classtree.js").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}", corpusid + '_search.js').replace("{{exports}}",nongeoexports)
            indexhtml = indexhtml.replace("{{indexpage}}", "true")
            self.generateOGCAPIFeaturesPages(outpath, featurecollectionspaths, prefixnamespace, self.ogcapifeatures,
                                             True)
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml+="<script src=\"features.js\"></script>"
            indexhtml+=maptemplate.replace("var ajax=true","var ajax=false").replace("var featurecolls = {{myfeature}}","").replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(prefixnamespace,0)).replace("{{baselayers}}",json.dumps(self.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", ""))
            indexhtml += htmlfooter.replace("{{license}}", curlicense).replace("{{exports}}", nongeoexports).replace("{{bibtex}}","")
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()

    def getPropertyRelations(self,graph,outpath):
        predicates= {}
        predicatecounter=0
        for pred in graph.predicates(None,None,True):
            predicates[pred]={"from":set(),"to":set()}
            for tup in graph.subject_objects(pred):
                for item in graph.objects(tup[0],URIRef(self.typeproperty),True):
                    predicates[pred]["from"].add(item)
                for item in graph.objects(tup[1], URIRef(self.typeproperty),True):
                    predicates[pred]["to"].add(item)
            predicates[pred]["from"]=list(predicates[pred]["from"])
            predicates[pred]["to"] = list(predicates[pred]["to"])
            predicatecounter+=1
        if self.createVOWL:
            vowlinstance=OWL2VOWL()
            vowlinstance.convertOWL2MiniVOWL(self.graph,outpath,predicates)
        with open(outpath+"proprelations.js", 'w', encoding='utf-8') as f:
            f.write("var proprelations="+json.dumps(predicates))
            f.close()

    def convertTTLToGraphML(self, g, file, subjectstorender=None):
        literalcounter = 0
        edgecounter = 0
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
<key for="node" id="nodekey" yfiles.type="nodegraphics"></key><key for="edge" id="edgekey" yfiles.type="edgegraphics"></key><graph id="G" edgedefault="directed">""")
        if subjectstorender == None:
            subjectstorender = g.subjects()
        addednodes = set()
        for sub in subjectstorender:
            file.write("<node id=\"" + str(sub) + "\" uri=\"" + str(
                sub) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                self.shortenURI(sub)) + "</y:NodeLabel></y:ShapeNode></data></node>\n")
            for tup in g.predicate_objects(sub):
                if isinstance(tup[1], Literal):
                    file.write("<node id=\"literal" + str(literalcounter) + "\" uri=\"literal" + str(
                        literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\"><![CDATA[" + str(
                        tup[1]) + "]]></y:NodeLabel></y:ShapeNode></data></node>\n")
                    file.write("<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(tup[0]) + "\" source=\"" + str(
                        sub) + "\" target=\"literal" + str(
                        literalcounter) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                        self.shortenURI(str(tup[0]))) + "</y:EdgeLabel></y:PolyLineEdge></data></edge>\n")
                    literalcounter += 1
                else:
                    if tup[1] not in subjectstorender and str(tup[1]) not in addednodes:
                        file.write("<node id=\"" + str(tup[1]) + "\" uri=\"" + str(tup[
                                                                                       1]) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                            self.shortenURI(str(tup[1]))) + "</y:NodeLabel></y:ShapeNode></data></node>\n")
                        addednodes.add(str(tup[1]))
                    file.write("<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(tup[0]) + "\" source=\"" + str(
                        sub) + "\" target=\"" + str(tup[
                                                        1]) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                        self.shortenURI(str(tup[1]))) + "</y:EdgeLabel></y:PolyLineEdge></data></edge>\n")
                edgecounter += 1
        file.write("</graph></graphml>")
        return None

    def convertTTLToTGF(self,g,file,subjectstorender=None):
        uriToNodeId={}
        nodecounter=0
        tgfresedges=""
        if subjectstorender==None:
            subjectstorender=g.subjects()
        for sub in subjectstorender:
            uriToNodeId[str(sub)]=nodecounter
            file.write(str(nodecounter)+" "+str(sub)+"\n")
            nodecounter+=1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(str(nodecounter)+" "+str(tup[1])+"\n")
                    uriToNodeId[str(tup[1])]=nodecounter
                    nodecounter+=1
                tgfresedges+=str(uriToNodeId[str(sub)])+" "+str(uriToNodeId[str(tup[1])])+" "+str(self.shortenURI(tup[0]))+"\n"
        file.write("#\n")
        file.write(tgfresedges)
        return None

    def createCollections(self,graph,namespace):
        classToInstances={}
        classToGeoColl = {}
        classToFColl = {}
        for tup in graph.subject_objects(URIRef(self.typeproperty)):
            if namespace in str(tup[0]):
                if str(tup[1]) not in classToInstances:
                    classToInstances[str(tup[1])]=set()
                    classToFColl[str(tup[1])]=0
                    classToGeoColl[str(tup[1])] = 0
                classToInstances[str(tup[1])].add(str(tup[0]))
                isgeo=False
                isfeature = False
                for geotup in graph.predicate_objects(tup[0]):
                    if str(geotup[0]) in SPARQLUtils.geopointerproperties:
                        isfeature=True
                    elif str(geotup[0]) in SPARQLUtils.geoproperties:
                        isgeo=True
                if isgeo:
                    classToGeoColl[str(tup[1])]+=1
                if isfeature:
                    classToFColl[str(tup[1])]+=1
        for cls in classToInstances:
            colluri=namespace+self.shortenURI(cls)+"_collection"
            if classToFColl[cls]==len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection"), URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(self.typeproperty),URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection")))
            elif classToGeoColl[cls]==len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection"), URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(self.typeproperty),URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection")))
            else:
                graph.add((URIRef(colluri),URIRef(self.typeproperty),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
            graph.add((URIRef(colluri),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(str(self.shortenURI(cls))+" Instances Collection")))
            for instance in classToInstances[cls]:
                graph.add((URIRef(colluri),URIRef("http://www.w3.org/2000/01/rdf-schema#member"),URIRef(instance)))
        return graph

    def getClassTree(self,graph, uritolabel,classidset,uritotreeitem):
        results = graph.query(self.preparedclassquery)
        tree = {"plugins": ["defaults","search", "sort", "state", "types", "contextmenu"], "search": {"show_only_matches":True}, "types": {
            "default": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/instance.png"},
            "class": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png"},
            "geoclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoclass.png","valid_children":["class","halfgeoclass","geoclass","geoinstance"]},
            "halfgeoclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/halfgeoclass.png"},
            "collectionclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/collectionclass.png"},
            "geocollection": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geometrycollection.png"},
            "featurecollection": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/featurecollection.png"},
            "instance": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/instance.png"},
            "geoinstance": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoinstance.png"}
        },
        "core": {"themes":{"responsive":True},"check_callback": True, "data": []}}
        result = []
        ress = {}
        for res in results:
            #QgsMessageLog.logMessage(str(res),"OntdocGeneration",Qgis.Info)
            if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
                ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
        #QgsMessageLog.logMessage(ress)
        for cls in ress:
            for obj in graph.subjects(URIRef(self.typeproperty), URIRef(cls),True):
                res = self.replaceNameSpacesInLabel(str(obj))
                if str(obj) in uritolabel:
                    restext= uritolabel[str(obj)]["label"] + " (" + self.shortenURI(str(obj)) + ")"
                    if res!=None:
                        restext=uritolabel[str(obj)]["label"] + " (" + res["uri"] + ")"
                else:
                    restext= self.shortenURI(str(obj))
                    if res!=None:
                        restext+= " (" + res["uri"] + ")"
                if str(obj) not in SPARQLUtils.collectionclasses:
                    result.append({"id": str(obj), "parent": cls,"type": "instance","text": restext, "data":{}})
                else:
                    result.append({"id": str(obj), "parent": cls, "type": "class", "text": restext, "data": {}})
                if str(obj) not in uritotreeitem:
                    uritotreeitem[str(obj)]=[]
                uritotreeitem[str(obj)].append(result[-1])
                #classidset.add(str(obj))
            res = self.replaceNameSpacesInLabel(str(cls))
            if ress[cls]["super"] == None:
                restext = self.shortenURI(str(cls))
                if res != None:
                    restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": "#","type": "class","text": restext,"data":{}})
                    uritotreeitem[str(cls)] = []
                    uritotreeitem[str(cls)].append(result[-1])
            else:
                if "label" in cls and cls["label"] != None:
                    restext = ress[cls]["label"] + " (" + self.shortenURI(str(cls)) + ")"
                    if res != None:
                        restext = ress[cls]["label"] + " (" + res["uri"] + ")"
                else:
                    restext = self.shortenURI(str(cls))
                    if res != None:
                        restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": ress[cls]["super"],"type": "class","text": restext,"data":{}})
                    if str(cls) not in uritotreeitem:
                        uritotreeitem[str(cls)] = []
                        uritotreeitem[str(cls)].append(result[-1])
                else:
                    uritotreeitem[cls][-1]["parent"]=ress[cls]["super"]
                if str(ress[cls]["super"]) not in uritotreeitem:
                    uritotreeitem[str(ress[cls]["super"])]=[]
                    clsres = self.replaceNameSpacesInLabel(str(ress[cls]["super"]))
                    if clsres!=None:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class",
                                   "text": self.shortenURI(str(ress[cls]["super"]))+" (" + clsres["uri"] + ")", "data": {}}
                    else:
                        theitem={"id": str(ress[cls]["super"]), "parent": "#","type": "class","text": self.shortenURI(str(ress[cls]["super"])),"data":{}}
                    uritotreeitem[str(ress[cls]["super"])].append(theitem)
                    result.append(theitem)
                classidset.add(str(ress[cls]["super"]))
            classidset.add(str(cls))
        if len(result)==0:
            classidset.add("http://www.w3.org/2002/07/owl#Thing")
            result.append({"id": "http://www.w3.org/2002/07/owl#Thing", "parent": "#", "type": "class", "text": "Thing (owl:Thing)", "data": {}})
            for obj in graph.subjects(True):
                result.append({"id":str(obj) , "parent": "http://www.w3.org/2002/07/owl#Thing", "type": "instance", "text": self.shortenURI(str(obj)),"data": {}})
        tree["core"]["data"] = result
        return tree

    def assignGeoClassesToTree(self,tree):
        classlist={}
        for item in tree["core"]["data"]:
            if item["type"]=="class":
                classlist[item["id"]]={"items":0,"geoitems":0,"item":item}
        for item in tree["core"]["data"]:
            if item["type"]=="instance" and item["parent"] in classlist:
                classlist[item["parent"]]["items"]+=1
            elif (item["type"] == "geoinstance" or item["type"]=="featurecollection" or item["type"]=="geocollection") and item["parent"] in classlist:
                classlist[item["parent"]]["items"]+=1
                classlist[item["parent"]]["geoitems"]+=1
        for item in classlist:
            if classlist[item]["items"]>0:
                if classlist[item]["item"]["text"].endswith("]"):
                    classlist[item]["item"]["text"]=classlist[item]["item"]["text"][0:classlist[item]["item"]["text"].rfind("[")-1]+" ["+str(classlist[item]["items"])+"]"
                else:
                    classlist[item]["item"]["text"]=classlist[item]["item"]["text"]+" ["+str(classlist[item]["items"])+"]"
            if item in SPARQLUtils.collectionclasses:
                classlist[item]["item"]["type"] = "collectionclass"
            elif classlist[item]["items"]==classlist[item]["geoitems"] and classlist[item]["items"]>0 and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="geoclass"
            elif classlist[item]["items"]>classlist[item]["geoitems"] and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="halfgeoclass"
            else:
                classlist[item]["item"]["type"] = "class"

    def checkGeoInstanceAssignment(self,uritotreeitem):
        for uri in uritotreeitem:
            if len(uritotreeitem[uri])>1:
                thetype="instance"
                counter=0
                if uritotreeitem[uri]!=None:
                    for item in uritotreeitem[uri]:
                        if item["type"]!="instance" or item["type"]!="class":
                            thetype=item["type"]
                        if item["type"]!="class":
                            item["id"]=item["id"]+"_suniv"+str(counter)+"_"
                        counter+=1
                    if thetype!="instance" or thetype!="class":
                        for item in uritotreeitem[uri]:
                            item["type"]=thetype

    def shortenURI(self,uri,ns=False):
        if uri!=None and "#" in uri and ns:
            return uri[0:uri.rfind('#')+1]
        if uri!=None and "/" in uri and ns:
            return uri[0:uri.rfind('/')+1]
        if uri!=None and uri.endswith("/"):
            uri = uri[0:-1]
        if uri!=None and "#" in uri and not ns:
            return uri[uri.rfind('#')+1:]
        if uri!=None and "/" in uri and not ns:
            return uri[uri.rfind('/')+1:]
        return uri

    def replaceNameSpacesInLabel(self,uri):
        for ns in self.prefixes["reversed"]:
            if ns in uri:
                return {"uri": str(self.prefixes["reversed"][ns]) + ":" + str(uri.replace(ns, "")),
                        "ns": self.prefixes["reversed"][ns]}
        return None

    def generateRelativePathFromGivenDepth(self,baseurl,checkdepth):
        rellink = ""
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        return rellink

    def generateRelativeLinkFromGivenDepth(self,baseurl,checkdepth,item,withindex):
        rellink = str(item).replace(baseurl, "")
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        if withindex:
            rellink += "/index.html"
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    def resolveBibtexReference(self, predobjs, item, graph):
        bibtexmappings = {"http://purl.org/dc/elements/1.1/title": "title",
                          "http://purl.org/dc/elements/1.1/created": "year",
                          "http://purl.org/ontology/bibo/number": "number",
                          "http://purl.org/ontology/bibo/publisher": "publisher",
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
            if str(tup[0]) == "http://purl.org/dc/elements/1.1/creator":
                if "author" not in bibtexitem:
                    bibtexitem["author"] = []
                if isinstance(tup[1], URIRef):
                    bibtexitem["author"].append(self.getLabelForObject(tup[1], graph))
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
            elif str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and str(tup[1]) in bibtextypemappings:
                bibtexitem["type"] = bibtextypemappings[str(tup[1])]
            elif str(tup[0]) in bibtexmappings:
                if isinstance(tup[1], URIRef):
                    bibtexitem[bibtexmappings[str(tup[0])]] = self.getLabelForObject(tup[1], graph)
                else:
                    bibtexitem[bibtexmappings[str(tup[0])]] = str(tup[1])
        res = bibtexitem["type"] + "{" + self.shortenURI(item) + ",\n"
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

    def resolveTimeObject(self, pred, obj, graph, timeobj):
        if str(pred) == "http://www.w3.org/2006/time#hasBeginning":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in SPARQLUtils.timeproperties:
                    timeobj["begin"] = tobj2[1]
        elif str(pred) == "http://www.w3.org/2006/time#hasEnd":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in SPARQLUtils.timeproperties:
                    timeobj["end"] = tobj2[1]
        elif str(pred) == "http://www.w3.org/2006/time#hasTime":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in SPARQLUtils.timeproperties:
                    timeobj["timepoint"] = tobj2[1]
        return timeobj

    def createURILink(self, uri):
        res = self.replaceNameSpacesInLabel(uri)
        if res != None:
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + str(res["uri"]) + "</a>"
        else:
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + self.shortenURI(uri) + "</a>"

    def timeObjectToHTML(self, timeobj):
        timeres = None
        if "begin" in timeobj and "end" in timeobj:
            timeres = str(timeobj["begin"]) + " "
            if str(timeobj["begin"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += self.createURILink(SPARQLUtils.timeliteraltypes[str(timeobj["begin"].datatype)])
            timeres += " - " + str(timeobj["end"])
            if str(timeobj["end"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += self.createURILink(SPARQLUtils.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "begin" in timeobj and not "end" in timeobj:
            timeres = str(timeobj["begin"])
            if str(timeobj["begin"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += self.createURILink(SPARQLUtils.timeliteraltypes[str(timeobj["begin"].datatype)])
        elif "begin" not in timeobj and "end" in timeobj:
            timeres = str(timeobj["end"])
            if str(timeobj["end"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += self.createURILink(SPARQLUtils.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "timepoint" in timeobj:
            timeres = timeobj["timepoint"]
            if str(timeobj["timepoint"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += self.createURILink(SPARQLUtils.timeliteraltypes[str(timeobj["timepoint"].datatype)])
        return timeres

    def resolveTimeLiterals(self, pred, obj, graph):
        timeobj = {}
        if isinstance(obj, URIRef) and str(pred) == "http://www.w3.org/2006/time#hasTime":
            for tobj in graph.predicate_objects(obj):
                timeobj = self.resolveTimeObject(tobj[0], tobj[1], graph, timeobj)
        elif isinstance(obj, URIRef) and str(pred) in SPARQLUtils.timepointerproperties:
            timeobj = self.resolveTimeObject(pred, obj, graph, timeobj)
        elif isinstance(obj, Literal):
            timeobj = self.resolveTimeObject(pred, obj, graph, timeobj)
        return timeobj

    def resolveGeoLiterals(self,pred,object,graph,geojsonrep,nonns,subject=None,treeitem=None,uritotreeitem=None):
        #QgsMessageLog.logMessage("RESOLVE " + str(object), "OntdocGeneration", Qgis.Info)
        if subject!=None and isinstance(object, Literal) and (str(pred) in SPARQLUtils.geopairproperties):
            pairprop = SPARQLUtils.geopairproperties[str(pred)]["pair"]
            latorlong = SPARQLUtils.geopairproperties[str(pred)]["islong"]
            othervalue = ""
            for obj in graph.objects(subject, URIRef(pairprop)):
                othervalue = str(obj)
            if latorlong:
                geojsonrep = {"type": "Point", "coordinates": [float(str(othervalue)), float(str(object))]}
            else:
                geojsonrep = {"type": "Point", "coordinates": [float(str(object)), float(str(othervalue))]}
        elif isinstance(object, Literal) and (
                str(pred) in SPARQLUtils.geoproperties or str(object.datatype) in SPARQLUtils.geoliteraltypes):
            geojsonrep = LayerUtils.processLiteral(str(object), str(object.datatype), "")
        elif isinstance(object, URIRef) and nonns:
            for pobj in graph.predicate_objects(object):
                if isinstance(pobj[1], Literal) and (
                        str(pobj[0]) in SPARQLUtils.geoproperties or str(
                    pobj[1].datatype) in SPARQLUtils.geoliteraltypes):
                    geojsonrep = LayerUtils.processLiteral(str(pobj[1]), str(pobj[1].datatype), "")
        return geojsonrep

    def getLabelForObject(self,obj,graph,labellang=None):
        label=""
        onelabel=self.shortenURI(str(obj))
        for tup in graph.predicate_objects(obj):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                # Check for label property
                if tup[1].language==labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
        if label=="" and onelabel!=None:
            label=onelabel
        return label

    def searchObjectConnectionsForAggregateData(self, graph, object, pred, geojsonrep, foundmedia, imageannos,
                                                    textannos, image3dannos, label, unitlabel,nonns):
        geoprop = False
        annosource = None
        incollection = False
        if pred in SPARQLUtils.geopointerproperties:
            geoprop = True
        if pred in SPARQLUtils.collectionrelationproperties:
            incollection = True
        foundval = None
        foundunit = None
        tempvalprop = None
        onelabel=None
        bibtex=None
        timeobj=None
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                # Check for label property
                if tup[1].language==self.labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    self.typeproperty) and (
                    tup[1] == URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1] == URIRef(
                    "http://www.w3.org/ns/oa#WKTSelector")):
                #Check for SVG or WKT annotations (2D or 3D annotations)
                for svglit in graph.objects(object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value"),True):
                    if "<svg" in str(svglit):
                        imageannos.add(str(svglit))
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(
                            svglit).upper()):
                        image3dannos.add(str(svglit))
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    self.typeproperty) and tup[1] == URIRef(
                    "http://www.w3.org/ns/oa#TextPositionSelector"):
                # Check for text annotations
                curanno = {}
                for txtlit in graph.predicate_objects(object):
                    if str(txtlit[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#value":
                        curanno["exact"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#start":
                        curanno["start"] = str(txtlit[1])
                    elif str(txtlit[0]) == "http://www.w3.org/ns/oa#end":
                        curanno["end"] = str(txtlit[1])
                textannos.append(curanno)
            if pred == "http://www.w3.org/ns/oa#hasSource":
                annosource = str(tup[1])
            if pred == "http://purl.org/dc/terms/isReferencedBy" and tup[0] == URIRef(self.typeproperty) and ("http://purl.org/ontology/bibo/" in str(tup[1])):
                bibtex=self.resolveBibtexReference(graph.predicate_objects(object),object,graph)
            if pred in SPARQLUtils.timepointerproperties:
                timeobj = self.resolveTimeLiterals(pred, object, graph)
            if not nonns:
                geojsonrep=self.resolveGeoLiterals(tup[0], tup[1], graph, geojsonrep,nonns)
            if incollection and "<svg" in str(tup[1]):
                foundmedia["image"].add(str(tup[1]))
            elif incollection and "http" in str(tup[1]):
                ext = "." + ''.join(filter(str.isalpha, str(tup[1]).split(".")[-1]))
                if ext in SPARQLUtils.fileextensionmap:
                    foundmedia[SPARQLUtils.fileextensionmap[ext]].add(str(tup[1]))
            if str(tup[0]) in SPARQLUtils.valueproperties:
                if tempvalprop == None and str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                if str(tup[0]) != "http://www.w3.org/ns/oa#hasSource" and SPARQLUtils.valueproperties[
                    str(tup[0])] == "DatatypeProperty" and (isinstance(tup[1], Literal) or isinstance(tup[1], URIRef)):
                    tempvalprop = str(tup[0])
                    foundval = str(tup[1])
                elif str(tup[0]) == "http://www.w3.org/ns/oa#hasTarget":
                    tempvalprop = "http://www.w3.org/ns/oa#hasTarget"
                    for inttup in graph.predicate_objects(tup[1]):
                        if str(inttup[0]) == "http://www.w3.org/ns/oa#hasSelector":
                            for valtup in graph.predicate_objects(inttup[1]):
                                if str(valtup[0]) in SPARQLUtils.unitproperties:
                                    foundunit = str(valtup[1])
                                if str(valtup[0]) in SPARQLUtils.valueproperties and (
                                        isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                                    foundval = str(valtup[1])
                else:
                    for valtup in graph.predicate_objects(tup[1]):
                        if str(valtup[0]) in SPARQLUtils.unitproperties:
                            foundunit = str(valtup[1])
                        if str(valtup[0]) in SPARQLUtils.valueproperties and (
                                isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                            foundval = str(valtup[1])
            if str(tup[0]) in SPARQLUtils.unitproperties:
                foundunit = tup[1]
        if foundunit != None and foundval != None:
            if "http" in foundunit:
                unitlabel= str(foundval) + " " + self.createURILink(str(foundunit))
            else:
                unitlabel = str(foundval) + " " + str(foundunit)
        if foundunit == None and foundval != None:
            if "http" in foundval:
                unitlabel = "<a href=\"" + str(foundval) + "\">" + str(self.shortenURI(foundval)) + "</a>"
            else:
                unitlabel = str(foundval)
        if annosource != None:
            for textanno in textannos:
                textanno["src"] = annosource
        if label=="" and onelabel!=None:
            label=onelabel
        return {"geojsonrep": geojsonrep, "label": label, "unitlabel": unitlabel, "foundmedia": foundmedia,
                "imageannos": imageannos, "textannos": textannos, "image3dannos": image3dannos,"bibtex":bibtex,"timeobj":timeobj}

    def createHTMLTableValueEntry(self,subject,pred,object,ttlf,graph,baseurl,checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos,dateprops,inverse,nonns):
        tablecontents=""
        label=""
        bibtex = None
        timeobj=None
        if isinstance(object,URIRef) or isinstance(object,BNode):
            if ttlf != None:
                ttlf.add((subject,URIRef(pred),object))
            label = ""
            unitlabel=""
            mydata=self.searchObjectConnectionsForAggregateData(graph,object,pred,geojsonrep,foundmedia,imageannos,textannos,image3dannos,label,unitlabel,nonns)
            label=mydata["label"]
            if label=="":
                label=str(self.shortenURI(str(object)))
            geojsonrep=mydata["geojsonrep"]
            foundmedia=mydata["foundmedia"]
            imageannos=mydata["imageannos"]
            textannos=mydata["textannos"]
            image3dannos=mydata["image3dannos"]
            unitlabel=mydata["unitlabel"]
            bibtex=mydata["bibtex"]
            timeobj=mydata["timeobj"]
            if inverse:
                rdfares = " about=\"" + str(object) + "\" resource=\"" + str(subject) + "\""
            else:
                rdfares = "resource=\"" + str(object) + "\""
            if baseurl in str(object) or isinstance(object,BNode):
                rellink = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,str(object),True)
                tablecontents += "<span><a property=\"" + str(pred) + "\" "+rdfares+" href=\"" + rellink + "\">"+ label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(self.shortenURI(str(object))) + ")</span></a>"
                if bibtex != None:
                    tablecontents += "<details><summary>[BIBTEX]</summary><pre>" + str(bibtex) + "</pre></details>"
            else:
                res = self.replaceNameSpacesInLabel(str(object))
                if res != None:
                    tablecontents += "<span><a property=\"" + str(
                        pred) + "\" " + rdfares + " target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                         "uri"] + ")</span></a>"
                else:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" "+rdfares+" target=\"_blank\" href=\"" + str(
                    object) + "\">" + label + "</a>"
                if bibtex!=None:
                    tablecontents+="<details><summary>[BIBTEX]</summary><pre>"+str(bibtex)+"</pre></details>"
                if self.generatePagesForNonNS:
                    rellink = self.generateRelativeLinkFromGivenDepth(str(baseurl), checkdepth,
                                                                      str(baseurl) + "nonns_" + self.shortenURI(
                                                                          str(object)), False)
                    tablecontents+=" <a href=\""+rellink+".html\">[x]</a>"
            if unitlabel!="":
                tablecontents+=" <span style=\"font-weight:bold\">["+str(unitlabel)+"]</span>"
            if timeobj!=None:
                tablecontents+=" <span style=\"font-weight:bold\">["+str(self.timeObjectToHTML(timeobj))+"]</span>"
                dateprops=timeobj
            tablecontents+="</span>"
        else:
            label=str(object)
            if ttlf != None:
                ttlf.add((subject, URIRef(pred), object))
            if isinstance(object, Literal) and object.datatype != None:
                res = self.replaceNameSpacesInLabel(str(object.datatype))
                objstring=str(object).replace("<", "&lt").replace(">", "&gt;")
                if str(object.datatype)=="http://www.w3.org/2001/XMLSchema#anyURI":
                    objstring="<a href=\""+str(object)+"\">"+str(object)+"</a>"
                if str(object.datatype) in SPARQLUtils.timeliteraltypes and dateprops!=None and self.shortenURI(str(pred),True) not in SPARQLUtils.metadatanamespaces and str(pred) not in dateprops:
                    dateprops.append(str(pred))
                if res != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + objstring + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + res["uri"]+ "</a>)</small></span>"
                else:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + objstring + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + self.shortenURI(str(object.datatype)) + "</a>)</small></span>"
                geojsonrep=self.resolveGeoLiterals(URIRef(pred), object, graph, geojsonrep,nonns,subject)
            else:
                if object.language != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\" xml:lang=\"" + str(object.language) + "\">" + str(object).replace("<", "&lt").replace(">", "&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">rdf:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/"+str(object.language)+"\" target=\"_blank\">iso6391:" + str(object.language) + "</a>)</small></span>"
                else:
                    tablecontents += self.detectStringLiteralContent(pred,object)
        return {"html":tablecontents,"geojson":geojsonrep,"foundmedia":foundmedia,"imageannos":imageannos,"textannos":textannos,"image3dannos":image3dannos,"label":label,"timeobj":dateprops}

    def generateRelativeSymlink(self, linkpath, targetpath, outpath, items=False):
        if "nonns" in targetpath and not items:
            checkdepthtarget = 3
        elif "nonns" in targetpath and items:
            checkdepthtarget = 4
        else:
            checkdepthtarget = targetpath.count("/") - 1
        print("Checkdepthtarget: " + str(checkdepthtarget))
        targetrellink = self.generateRelativeLinkFromGivenDepth(targetpath, checkdepthtarget, linkpath, False)
        print("Target Rellink: " + str(targetrellink))
        print("Linkpath: " + str(linkpath))
        targetrellink = targetrellink.replace(outpath, "")
        return targetrellink.replace("//", "/")

    def generateIIIFManifest(self, outpath, imgpaths, annos, curind, prefixnamespace, label="", summary="",
                             thetypes=None, predobjmap=None, maintype="Image"):
        print("GENERATE IIIF Manifest for " + str(self.outpath) + " " + str(curind) + " " + str(label) + " " + str(
            summary) + " " + str(predobjmap))
        if not os.path.exists(self.outpath + "/iiif/mf/" + self.shortenURI(curind) + "/manifest.json"):
            if not os.path.exists(self.outpath + "/iiif/mf/"):
                os.makedirs(self.outpath + "/iiif/mf/")
            if not os.path.exists(self.outpath + "/iiif/images/"):
                os.makedirs(self.outpath + "/iiif/images/")
            print(label)
            if label != "":
                curiiifmanifest = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                   "id": self.deploypath + "/iiif/mf/" + self.shortenURI(curind) + "/manifest.json",
                                   "type": "Manifest",
                                   "label": {"en": [str(label) + " (" + self.shortenURI(curind) + ")"]}, "homepage": [
                        {"id": str(curind).replace(prefixnamespace, self.deploypath + "/"), "type": "Text",
                         "label": {"en": [str(curind).replace(prefixnamespace, self.deploypath + "/")]},
                         "format": "text/html", "language": ["en"]}], "metadata": [], "items": []}
            else:
                curiiifmanifest = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                   "id": self.deploypath + "/iiif/mf/" + self.shortenURI(curind) + "/manifest.json",
                                   "type": "Manifest", "label": {"en": [self.shortenURI(curind)]}, "homepage": [
                        {"id": str(curind).replace(prefixnamespace, self.deploypath + "/"), "type": "Text",
                         "label": {"en": [str(curind).replace(prefixnamespace, self.deploypath + "/")]},
                         "format": "text/html", "language": ["en"]}], "metadata": [], "items": []}
            pagecounter = 0
            for imgpath in imgpaths:
                curitem = {"id": imgpath + "/canvas/p" + str(pagecounter), "type": "Canvas",
                           "label": {"en": [str(label) + " " + str(maintype) + " " + str(pagecounter + 1)]},
                           "height": 100, "width": 100, "items": [
                        {"id": imgpath + "/canvas/p" + str(pagecounter) + "/1", "type": "AnnotationPage", "items": [
                            {"id": imgpath + "/annotation/p" + str(pagecounter) + "/1", "type": "Annotation",
                             "motivation": "painting",
                             "body": {"id": imgpath, "type": str(maintype), "format": "image/png"},
                             "target": imgpath + "/canvas/p" + str(pagecounter)}]}], "annotations": [
                        {"id": imgpath + "/canvas/p" + str(pagecounter) + "/annopage-2", "type": "AnnotationPage",
                         "items": [{"id": imgpath + "/canvas/p" + str(pagecounter) + "/anno-1", "type": "Annotation",
                                    "motivation": "commenting",
                                    "body": {"type": "TextualBody", "language": "en", "format": "text/html",
                                             "value": "<a href=\"" + str(curind) + "\">" + str(
                                                 self.shortenURI(curind)) + "</a>"},
                                    "target": imgpath + "/canvas/p" + str(pagecounter)}]}]}
                if annos != None:
                    annocounter = 3
                    for anno in annos:
                        curitem["annotations"].append(
                            {"id": imgpath + "/canvas/p" + str(pagecounter) + "/annopage-" + str(annocounter),
                             "type": "AnnotationPage", "items": [
                                {"id": imgpath + "/canvas/p" + str(pagecounter) + "/anno-1", "type": "Annotation",
                                 "motivation": "commenting",
                                 "body": {"type": "TextualBody", "language": "en", "format": "text/html",
                                          "value": "<a href=\"" + str(curind) + "\">" + str(
                                              self.shortenURI(curind)) + "</a>"},
                                 "target": {"source": imgpath + "/canvas/p" + str(pagecounter)},
                                 "type": "SpecificResource", "selector": {"type": "SvgSelector", "value": anno}}]})
                        annocounter += 1
                curiiifmanifest["items"].append(curitem)
                pagecounter += 1
            for pred in predobjmap:
                # print(str(pred)+" "+str(predobjmap[pred]))
                for objs in predobjmap[pred]:
                    # print(str(pred)+" "+str(objs))
                    # print(curiiifmanifest["metadata"])
                    if isinstance(objs, URIRef):
                        curiiifmanifest["metadata"].append({"label": {"en": [self.shortenURI(str(pred))]}, "value": {
                            "en": ["<a href=\"" + str(objs) + "\">" + str(objs) + "</a>"]}})
                    else:
                        curiiifmanifest["metadata"].append(
                            {"label": {"en": [self.shortenURI(str(pred))]}, "value": {"en": [str(objs)]}})
            print(curiiifmanifest["metadata"])
            if summary != None and summary != "" and summary != {}:
                curiiifmanifest["summary"] = {"en": [str(summary)]}
            # os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/")
            # os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/full/")
            # os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/full/0/")
            os.makedirs(self.outpath + "/iiif/mf/" + self.shortenURI(curind))
            f = open(self.outpath + "/iiif/mf/" + self.shortenURI(curind) + "/manifest.json", "w", encoding="utf-8")
            f.write(json.dumps(curiiifmanifest))
            f.close()
        if thetypes != None and len(thetypes) > 0:
            return {"url": self.outpath + "/iiif/mf/" + self.shortenURI(curind) + "/manifest.json", "label": str(label),
                    "class": next(iter(thetypes))}
        return {"url": self.outpath + "/iiif/mf/" + self.shortenURI(curind) + "/manifest.json", "label": str(label),
                "class": ""}

    def generateIIIFCollections(self, outpath, imagespaths, prefixnamespace):
        if not os.path.exists(outpath + "/iiif/collection/"):
            os.makedirs(outpath + "/iiif/collection/")
        if os.path.exists(outpath + "/iiif/collection/iiifcoll.json"):
            f = open(outpath + "/iiif/collection/iiifcoll.json", "r", encoding="utf-8")
            collections = json.loads(f.read())
            f.close()
        else:
            collections = {"main": {"@context": "http://iiif.io/api/presentation/3/context.json",
                                    "id": outpath + "/iiif/collection/iiifcoll.json", "type": "Collection",
                                    "label": {"en": ["Collection: " + self.shortenURI(str(prefixnamespace))]},
                                    "items": []}}
        seenurls = set()
        for imgpath in sorted(imagespaths, key=lambda k: k['label'], reverse=False):
            curclass = "main"
            if "class" in imgpath and imgpath["class"] != "":
                curclass = imgpath["class"]
                if curclass not in collections:
                    collections[curclass] = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                             "id": outpath + "/iiif/collection/" + curclass + ".json",
                                             "type": "Collection", "label": {"en": ["Collection: " + str(curclass)]},
                                             "items": []}
            if imgpath["url"] not in seenurls:
                if imgpath["label"] != "":
                    collections[curclass]["items"].append({"full": outpath + "/iiif/images/" + self.shortenURI(
                        imgpath["url"].replace("/manifest.json", "")) + "/full/full/0/default.jpg",
                                                           "id": imgpath["url"].replace(self.outpath, self.deploypath),
                                                           "type": "Manifest", "label": {"en": [
                            imgpath["label"] + " (" + self.shortenURI(imgpath["url"].replace("/manifest.json", "")[
                                                                      0:imgpath["url"].replace("/manifest.json",
                                                                                               "").rfind(
                                                                          ".")]) + ")"]}})
                else:
                    collections[curclass]["items"].append({"full": outpath + "/iiif/images/" + self.shortenURI(
                        imgpath["url"].replace("/manifest.json", "")) + "/full/full/0/default.jpg",
                                                           "id": imgpath["url"].replace(self.outpath, self.deploypath),
                                                           "type": "Manifest", "label": {
                            "en": [self.shortenURI(imgpath["url"].replace("/manifest.json", ""))]}})
            seenurls = imgpath["url"]
        for coll in collections:
            if coll != "main":
                collections["main"]["items"].append(collections[coll])
        f = open(outpath + "/iiif/collection/iiifcoll.json", "w", encoding="utf-8")
        f.write(json.dumps(collections["main"]))
        f.close()
        iiifindex = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/mirador@latest/dist/mirador.min.js"></script></head><body><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500"><div id="my-mirador"/><script type="text/javascript">var mirador = Mirador.viewer({"id": "my-mirador","manifests": {"collection/iiifcoll.json": {"provider": "Harvard University"}},"windows": [{"loadedManifest": "collection/iiifcoll.json","canvasIndex": 2,"thumbnailNavigationPosition": 'far-bottom'}]});</script></body></html>"""
        f = open(outpath + "/iiif/index.html", "w", encoding="utf-8")
        f.write(iiifindex)
        f.close()

    def generateOGCAPIFeaturesPages(self, outpath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON):
        apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + str(
            self.deploypath) + "/api/index.json\"; const apiUrl = \"" + str(
            self.deploypath) + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
        apijson = {"openapi": "3.0.1", "info": {"title": str(self.deploypath) + " Feature Collections",
                                                "description": "Feature Collections of " + str(self.deploypath)},
                   "servers": [{"url": str(self.deploypath)}], "paths": {}}
        conformancejson = {"conformsTo": ["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}
        if ogcapi:
            apijson["paths"]["/api"] = {
                "get": {"tags": ["Capabilities"], "summary": "api documentation", "description": "api documentation",
                        "operationId": "openApi", "parameters": [], "responses": {
                        "default": {"description": "default response",
                                    "content": {"application/vnd.oai.openapi+json;version=3.0": {},
                                                "application/json": {}, "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/license/dataset"] = {}
            apijson["components"] = {"schemas": {"Conformance": {"type": "object", "properties": {
                "conformsTo": {"type": "array", "items": {"type": "string"}}}, "xml": {"name": "ConformsTo",
                                                                                       "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collection": {"type": "object", "properties": {
                                                     "id": {"type": "string", "xml": {"name": "Id",
                                                                                      "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "title": {"type": "string", "xml": {"name": "Title",
                                                                                         "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "description": {"type": "string", "xml": {"name": "Description",
                                                                                               "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "links": {"type": "array", "xml": {"name": "link",
                                                                                        "namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "extent": {"$ref": "#/components/schemas/Extent"},
                                                     "itemType": {"type": "string"},
                                                     "crs": {"type": "array", "items": {"type": "string"}},
                                                     "storageCrs": {"type": "string"}}, "xml": {"name": "Collection",
                                                                                                "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collections": {"type": "object", "properties": {
                                                     "links": {"type": "array", "xml": {"name": "link",
                                                                                        "namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "collections": {"type": "array", "xml": {"name": "Collection",
                                                                                              "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"},
                                                                     "items": {
                                                                         "$ref": "#/components/schemas/Collection"}}},
                                                                 "xml": {"name": "Collections",
                                                                         "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Extent": {"type": "object", "properties": {
                                                     "spatial": {"$ref": "#/components/schemas/Spatial"},
                                                     "temporal": {"$ref": "#/components/schemas/Temporal"}},
                                                            "xml": {"name": "Extent",
                                                                    "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Link": {"type": "object", "properties": {
                                                     "href": {"type": "string", "xml": {"attribute": True}},
                                                     "rel": {"type": "string", "xml": {"attribute": True}},
                                                     "type": {"type": "string", "xml": {"attribute": True}},
                                                     "title": {"type": "string", "xml": {"attribute": True}}},
                                                          "xml": {"name": "link",
                                                                  "namespace": "http://www.w3.org/2005/Atom"}},
                                                 "Spatial": {"type": "object", "properties": {"bbox": {"type": "array",
                                                                                                       "items": {
                                                                                                           "type": "array",
                                                                                                           "items": {
                                                                                                               "type": "number",
                                                                                                               "format": "double"}}},
                                                                                              "crs": {"type": "string",
                                                                                                      "xml": {
                                                                                                          "attribute": True}}},
                                                             "xml": {"name": "SpatialExtent",
                                                                     "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Temporal": {"type": "object", "properties": {
                                                     "interval": {"type": "array",
                                                                  "items": {"type": "string", "format": "date-time"}},
                                                     "trs": {"type": "string", "xml": {"attribute": True}}},
                                                              "xml": {"name": "TemporalExtent",
                                                                      "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "LandingPage": {"type": "object"}}}
            landingpagejson = {"title": "Landing Page", "description": "Landing Page", "links": [{
                "href": str(self.deploypath) + "/index.json",
                "rel": "self",
                "type": "application/json",
                "title": "this document as JSON"
            }, {
                "href": str(self.deploypath) + "/index.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "this document as HTML"
            }, {
                "href": str(self.deploypath) + "/collections/",
                "rel": "data",
                "type": "application/json",
                "title": "Supported Feature Collections as JSON"
            }, {
                "href": str(self.deploypath) + "/collections/indexc.html",
                "rel": "data",
                "type": "text/html",
                "title": "Supported Feature Collections as HTML"
            }, {"href": str(self.deploypath) + "/api/index.json", "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0", "title": "API definition"},
                {"href": str(self.deploypath) + "/api", "rel": "service-desc", "type": "text/html",
                 "title": "API definition as HTML"},
                {"href": str(self.deploypath) + "/conformance", "rel": "conformance", "type": "application/json",
                 "title": "OGC API conformance classes as Json"},
                {"href": str(self.deploypath) + "/conformance", "rel": "conformance", "type": "text/html",
                 "title": "OGC API conformance classes as HTML"}]}

            apijson["paths"]["/"] = {"get": {"tags": ["Capabilities"], "summary": "landing page",
                                             "description": "Landing page of this dataset",
                                             "operationId": "landingPage", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/LandingPage"}},
                        "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/conformance"] = {
                "get": {"tags": ["Capabilities"], "summary": "supported conformance classes",
                        "description": "Retrieves the supported conformance classes", "operationId": "conformance",
                        "parameters": [], "responses": {"default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Conformance"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            collectionsjson = {"collections": [], "links": [
                {"href": outpath + "collections/index.json", "rel": "self", "type": "application/json",
                 "title": "this document as JSON"},
                {"href": outpath + "collections/index.html", "rel": "self", "type": "text/html",
                 "title": "this document as HTML"}]}
            collectionshtml = "<html><head></head><body><header><h1>Collections of " + str(
                self.deploypath) + "</h1></head>{{collectiontable}}<footer><a href=\"index.json\">This page as JSON</a></footer></body></html>"
            collectiontable = "<table><thead><th>Collection</th><th>Links</th></thead><tbody>"
            apijson["paths"]["/collections"] = {"get": {"tags": ["Collections"], "summary": "describes collections",
                                                        "description": "Describes all collections provided by this service",
                                                        "operationId": "collections", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            if outpath.endswith("/"):
                outpath = outpath[0:-1]
            if not os.path.exists(outpath + "/api/"):
                os.makedirs(outpath + "/api/")
            if not os.path.exists(outpath + "/license/"):
                os.makedirs(outpath + "/license/")
            if not os.path.exists(outpath + "/collections/"):
                os.makedirs(outpath + "/collections/")
            if not os.path.exists(outpath + "/conformance/"):
                os.makedirs(outpath + "/conformance/")
        result = list()
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
            if ogcapi:
                op = outpath + "/collections/" + coll.replace(outpath, "").replace("index.geojson", "") + "/"
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                if not os.path.exists(op):
                    os.makedirs(op)
                if not os.path.exists(op + "/items/"):
                    os.makedirs(op + "/items/")
                opweb = op.replace(outpath, self.deploypath)
                opwebcoll = opweb
                if opwebcoll.endswith("/"):
                    opwebcoll = opwebcoll[0:-1]
                opwebcoll = opwebcoll.replace("//", "/")
                collectionsjson["collections"].append(
                    {"id": coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:],
                     "title": featurecollectionspaths[coll]["name"], "links": [
                        {"href": str(opweb.replace(".geojson", "") + "/index.json").replace("//", "/"),
                         "rel": "collection", "type": "application/json", "title": "Collection as JSON"},
                        {"href": str(opweb.replace(".geojson", "") + "/").replace("//", "/"), "rel": "collection",
                         "type": "text/html", "title": "Collection as HTML"},
                        {"href": str(opweb.replace(".geojson", "") + "/index.ttl").replace("//", "/"),
                         "rel": "collection", "type": "text/ttl", "title": "Collection as TTL"}]})
                currentcollection = {"title": featurecollectionspaths[coll]["name"],
                                     "id": coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson",
                                                                                                          "")[1:],
                                     "links": [], "itemType": "feature"}
                currentcollection["links"] = [
                    {"href": opwebcoll + "/items/index.json", "rel": "items", "type": "application/json",
                     "title": "Collection as JSON"},
                    {"href": opwebcoll + "/items/indexc.html", "rel": "items", "type": "text/html",
                     "title": "Collection as HTML"},
                    {"href": opwebcoll + "/items/index.ttl", "rel": "collection", "type": "text/ttl",
                     "title": "Collection as TTL"}]
                if "bbox" in curcoll:
                    currentcollection["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                    collectionsjson["collections"][-1]["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                if "crs" in curcoll:
                    currentcollection["crs"] = curcoll["crs"]
                    collectionsjson["collections"][-1]["crs"] = curcoll["crs"]
                    if "extent" in currentcollection:
                        currentcollection["extent"]["spatial"]["crs"] = curcoll["crs"]
                        collectionsjson["collections"][-1]["extent"]["spatial"]["crs"] = curcoll["crs"]
                apijson["paths"]["/collections/" + str(
                    coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]).rstrip("/")] = {
                    "get": {"tags": ["Collections"], "summary": "describes collection " + str(
                        str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:])).rstrip(
                        "/"), "description": "Describes the collection with the id " + str(
                        str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:])).rstrip(
                        "/"), "operationId": "collection-" + str(
                        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]),
                            "parameters": [], "responses": {"default": {"description": "default response", "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},
                                                 "example": None}}}}}}
                curcollrow = "<tr><td><a href=\"" + opweb.replace(".geojson", "") + "/items/indexc.html\">" + str(
                    featurecollectionspaths[coll]["name"]) + "</a></td><td><a href=\"" + opweb.replace(".geojson",
                                                                                                       "") + "/items/indexc.html\">[Collection as HTML]</a>&nbsp;<a href=\"" + opweb.replace(
                    ".geojson", "") + "/items/\">[Collection as JSON]</a>&nbsp;<a href=\"" + opweb.replace(".geojson",
                                                                                                           "") + "/items/index.ttl\">[Collection as TTL]</a></td></tr>"
                f = open(op + "index.json", "w", encoding="utf-8")
                f.write(json.dumps(currentcollection))
                f.close()
                f = open(op + "indexc.html", "w", encoding="utf-8")
                f.write("<html><head></head><body><h1>" + featurecollectionspaths[coll][
                    "name"] + "</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>" + str(
                    curcollrow) + "</tbody></table></html>")
                f.close()
                collectiontable += curcollrow
                if os.path.exists(coll):
                    try:
                        if os.path.exists(coll.replace("//", "/")):
                            targetpath = self.generateRelativeSymlink(coll.replace("//", "/"),
                                                                      str(op + "/items/index.json").replace("//", "/"),
                                                                      outpath)
                            p = Path(str(op + "/items/index.json").replace("//", "/"))
                            p.symlink_to(targetpath)
                        if os.path.exists(coll.replace("//", "/").replace("index.geojson", "index.ttl").replace(
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".ttl")):
                            targetpath = self.generateRelativeSymlink(
                                coll.replace("//", "/").replace("index.geojson", "index.ttl").replace(
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".ttl"),
                                str(op + "/items/index.ttl").replace("//", "/"), outpath)
                            p = Path(str(op + "/items/index.ttl").replace("//", "/"))
                            p.symlink_to(targetpath)
                        if os.path.exists(coll.replace("//", "/").replace("index.geojson", "index.html").replace(
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".html")):
                            targetpath = self.generateRelativeSymlink(
                                coll.replace("//", "/").replace("index.geojson", "index.html").replace(
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".html"),
                                str(op + "/items/indexc.html").replace("//", "/"), outpath)
                            f = open(str(op + "/items/indexc.html"), "w")
                            f.write(
                                "<html><head><meta http-equiv=\"refresh\" content=\"0; url=" + targetpath + "\" /></head></html>")
                            f.close()
                        print("symlinks created")
                    except Exception as e:
                        print("symlink creation error")
                        print(e)
                    apijson["paths"][str("/collections/" + str(
                        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[
                        1:]) + "/items/index.json").replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                   "summary": "retrieves features of collection " + str(
                                                                                       coll.replace(outpath,
                                                                                                    "").replace(
                                                                                           "index.geojson", "").replace(
                                                                                           ".geojson", "")[1:]).rstrip(
                                                                                       "/"),
                                                                                   "description": "Retrieves features of collection  " + str(
                                                                                       coll.replace(outpath,
                                                                                                    "").replace(
                                                                                           "index.geojson", "").replace(
                                                                                           ".geojson", "")[1:]),
                                                                                   "operationId": "features-" + str(
                                                                                       coll.replace(outpath,
                                                                                                    "").replace(
                                                                                           "index.geojson", "").replace(
                                                                                           ".geojson", "")[1:]),
                                                                                   "parameters": [], "responses": {
                            "default": {"description": "default response",
                                        "content": {"application/geo+json": {"example": None}},
                                        "text/ttl": {"schema": {"example": None}, "example": None},
                                        "text/html": {"schema": {"example": None}, "example": None}}}}}
                    apijson["paths"][str("/collections/" + str(
                        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[
                        1:]) + "/items/{featureId}/index.json").replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                               "summary": "retrieves feature of collection " + str(
                                                                                                   coll.replace(outpath,
                                                                                                                "").replace(
                                                                                                       "index.geojson",
                                                                                                       "").replace(
                                                                                                       ".geojson", "")[
                                                                                                   1:]).rstrip("/"),
                                                                                               "description": "Retrieves one single feature of the collection with the id " + str(
                                                                                                   coll.replace(outpath,
                                                                                                                "").replace(
                                                                                                       "index.geojson",
                                                                                                       "").replace(
                                                                                                       ".geojson", "")[
                                                                                                   1:]),
                                                                                               "operationId": "feature-" + str(
                                                                                                   coll.replace(outpath,
                                                                                                                "").replace(
                                                                                                       "index.geojson",
                                                                                                       "").replace(
                                                                                                       ".geojson", "")[
                                                                                                   1:]), "parameters": [
                            {"name": "featureId", "in": "path", "required": True, "schema": {"type": "string"}}],
                                                                                               "responses": {
                                                                                                   "default": {
                                                                                                       "description": "default response",
                                                                                                       "content": {
                                                                                                           "application/geo+json": {
                                                                                                               "example": None}},
                                                                                                       "text/ttl": {
                                                                                                           "schema": {
                                                                                                               "example": None},
                                                                                                           "example": None},
                                                                                                       "text/html": {
                                                                                                           "schema": {
                                                                                                               "example": None},
                                                                                                           "example": None}}}}}

                    for feat in curcoll["features"]:
                        featpath = feat["id"].replace(prefixnamespace, "").replace("//", "/")
                        try:
                            os.makedirs(str(op + "/items/" + str(self.shortenURI(feat["id"]))))
                            print("CHECKPATH: " + str(
                                str(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json").replace("//", "/")))
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json"):
                                targetpath = self.generateRelativeSymlink(featpath + "/index.json", str(op + "/items/" + str(
                                    self.shortenURI(feat["id"])) + "/index.json").replace("//", "/"), outpath, True)
                                p = Path(str(op + "/items/" + str(self.shortenURI(feat["id"])) + "/index.json").replace("//", "/"))
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.ttl"):
                                targetpath = self.generateRelativeSymlink(featpath + "/index.ttl", str(op + "/items/" + str(
                                    self.shortenURI(feat["id"])) + "/index.ttl").replace("//", "/"), outpath, True)
                                p = Path(str(op + "/items/" + str(self.shortenURI(feat["id"])) + "/index.ttl").replace("//", "/"))
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.html"):
                                targetpath = self.generateRelativeSymlink(featpath + "/index.html", str(op + "/items/" + str(
                                    self.shortenURI(feat["id"])) + "/index.html").replace("//", "/"), outpath, True)
                                f = open(str(op + "/items/" + str(self.shortenURI(feat["id"]))) + "/index.html", "w")
                                f.write(
                                    "<html><head><meta http-equiv=\"refresh\" content=\"0; url=" + targetpath + "\" /></head></html>")
                                f.close()
                            print("symlinks created")
                        except Exception as e:
                            print("symlink creation error")
                            print(e)
                    if mergeJSON:
                        result.append(curcoll)
                collectiontable += "</tbody></table>"
        if mergeJSON:
            with open(outpath + "/features.js", 'w', encoding="utf-8") as output_file:
                output_file.write("var featurecolls=" + json.dumps(result))
                # shutil.move(coll, op+"/items/index.json")
        if ogcapi:
            f = open(outpath + "/index.json", "w", encoding="utf-8")
            f.write(json.dumps(landingpagejson))
            f.close()
            f = open(outpath + "/api/index.json", "w", encoding="utf-8")
            f.write(json.dumps(apijson))
            f.close()
            f = open(outpath + "/api/api.html", "w", encoding="utf-8")
            f.write(apihtml)
            f.close()
            f = open(outpath + "/collections/indexc.html", "w", encoding="utf-8")
            f.write(collectionshtml.replace("{{collectiontable}}", collectiontable))
            f.close()
            f = open(outpath + "/collections/index.json", "w", encoding="utf-8")
            f.write(json.dumps(collectionsjson))
            f.close()
            f = open(outpath + "/conformance/index.json", "w", encoding="utf-8")
            f.write(json.dumps(conformancejson))
            f.close()

    def detectStringLiteralContent(self,pred,object):
        if object.startswith("http://") or object.startswith("https://"):
            return "<span><a property=\"" + str(pred) + "\" target=\"_blank\" href=\"" + str(
                        object)+ "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object)+ "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif object.startswith("www."):
            return "<span><a property=\"" + str(pred) + "\" target=\"_blank\" href=\"http://" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">http://" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        elif re.search(r'(10[.][0-9]{2,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)', str(object)):
            return "<span><a property=\"" + str(pred) + "\" href=\"https://www.doi.org/" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#anyURI\">" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#anyURI\">xsd:anyURI</a>)</small></span>"
        elif re.search(r'[\w.]+\@[\w.]+', object):
            return "<span><a property=\"" + str(pred) + "\" href=\"mailto:" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">mailto:" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return "<span property=\"" + str(pred) + "\" content=\"" + str(object).replace("<","&lt").replace(">","&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<","&lt").replace(">","&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"


    def formatPredicate(self,tup,baseurl,checkdepth,tablecontents,graph,reverse):
        label=self.getLabelForObject(URIRef(tup), graph,self.labellang)
        tablecontents += "<td class=\"property\">"
        if reverse:
            tablecontents+="Is "
        if baseurl in str(tup):
            rellink = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth,str(tup),True)
            tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span>"
        else:
            res = self.replaceNameSpacesInLabel(tup)
            if res != None:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + " <span style=\"color: #666;\">(" + res["uri"] + ")</span></a></span>"
            else:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + "</a></span>"
        if reverse:
            tablecontents+=" of"
        tablecontents += "</td>"
        return tablecontents

    def getSubjectPagesForNonGraphURIs(self,uristorender,graph,prefixnamespace,corpusid,outpath,nonnsmap,baseurl,uritotreeitem,labeltouri):
        QgsMessageLog.logMessage("Subjectpages " + str(uristorender), "OntdocGeneration", Qgis.Info)
        nonnsuris=len(uristorender)
        counter=0
        for uri in uristorender:
            label=""
            for tup in graph.predicate_objects(URIRef(uri)):
                if str(tup[0]) in SPARQLUtils.labelproperties:
                    label = str(tup[1])
            if uri in uritotreeitem:
                res = self.replaceNameSpacesInLabel(str(uri))
                label = self.getLabelForObject(URIRef(str(uri)), graph, self.labellang)
                if res != None and label != "":
                    uritotreeitem[uri][-1]["text"] = label + " (" + res["uri"] + ")"
                elif label != "":
                    uritotreeitem[uri][-1]["text"] = label + " (" + self.shortenURI(uri) + ")"
                else:
                    uritotreeitem[uri][-1]["text"] = self.shortenURI(uri)
                uritotreeitem[uri][-1]["id"] = prefixnamespace + "nonns_" + self.shortenURI(uri) + ".html"
                labeltouri[label] = prefixnamespace + "nonns_" + self.shortenURI(uri) + ".html"
            if counter%10==0:
                self.updateProgressBar(counter,nonnsuris,"NonNS URIs")
            QgsMessageLog.logMessage("NonNS Counter " +str(counter)+"/"+str(nonnsuris)+" "+ str(uri), "OntdocGeneration", Qgis.Info)
            self.createHTML(outpath+"nonns_"+self.shortenURI(uri)+".html", None, URIRef(uri), baseurl, graph.subject_predicates(URIRef(uri),True), graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", None, self.license, None, Graph(),uristorender,True,label)
            counter+=1



    def detectURIsConnectedToSubjects(self,subjectstorender,graph,prefixnamespace,corpusid,outpath,curlicense,baseurl):
        uristorender={}
        uritolabel={}
        for sub in subjectstorender:
            onelabel=""
            label=None
            added=[]
            for tup in graph.predicate_objects(sub):
                if str(tup[0]) in SPARQLUtils.labelproperties:
                    if tup[1].language == self.labellang:
                        label = str(tup[1])
                        break
                    onelabel = str(tup[1])
                if isinstance(tup[1],URIRef) and prefixnamespace not in str(tup[1]) and "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in str(tup[1]):
                    if str(tup[1]) not in uristorender:
                        uristorender[str(tup[1])]={}
                    if str(tup[0]) not in uristorender[str(tup[1])]:
                        uristorender[str(tup[1])][str(tup[0])]=[]
                    for objtup in graph.predicate_objects(tup[1]):
                        if str(objtup[0]) in SPARQLUtils.labelproperties:
                            uritolabel[str(tup[1])] = str(objtup[1])
                    toadd={"sub":sub,"label":onelabel}
                    added.append(toadd)
                    uristorender[str(tup[1])][str(tup[0])].append(toadd)
            for item in added:
                if label!=None:
                    item["label"]=label
                else:
                    item["label"]=onelabel
        for uri in uristorender:
            thelabel=""
            if uri in uritolabel:
                thelabel=uritolabel[uri]
            self.createHTML(outpath+"nonns_"+self.shortenURI(uri)+".html", None, URIRef(uri), baseurl, graph.subject_predicates(URIRef(uri),True), graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", None, self.license, subjectstorender, Graph(),None,True,thelabel)

    def checkDepthFromPath(self,savepath,baseurl,subject):
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        checkdepth+=1
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth))
        return checkdepth

    def getAccessFromBaseURL(self,baseurl,savepath):
        #QgsMessageLog.logMessage("Checkdepth: " + baseurl+" "+savepath.replace(baseurl, ""), "OntdocGeneration", Qgis.Info)
        return savepath.replace(baseurl, "")

    def createHTML(self,savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,uritotreeitem,curlicense,subjectstorender,postprocessing,nonnsmap=None,nonns=False,foundlabel=""):
        tablecontents = ""
        metadatatablecontents=""
        isodd = False
        geojsonrep=None
        epsgcode=""
        foundmedia={"audio":set(),"video":set(),"image":set(),"mesh":set()}
        savepath = savepath.replace("\\", "/")
        checkdepth=0
        if not nonns:
            checkdepth=self.checkDepthFromPath(savepath, baseurl, subject)
        logo=""
        if self.logoname!=None and self.logoname!="":
            logo="<img src=\""+self.logoname+"\" alt=\"logo\" width=\"25\" height=\"25\"/>&nbsp;&nbsp;"
        textannos = []
        foundvals=set()
        imageannos=set()
        image3dannos=set()
        predobjmap={}
        isgeocollection=False
        comment={}
        parentclass=None
        inverse=False
        dateprops = []
        timeobj=None
        if uritotreeitem!=None and str(subject) in uritotreeitem and uritotreeitem[str(subject)][-1]["parent"].startswith("http"):
            parentclass=str(uritotreeitem[str(subject)][-1]["parent"])
            if parentclass not in uritotreeitem:
                uritotreeitem[parentclass]=[{"id": parentclass, "parent": "#","type": "class","text": self.shortenURI(str(parentclass)),"data":{}}]
            uritotreeitem[parentclass][-1]["instancecount"]=0
        ttlf = Graph(bind_namespaces="rdflib")
        if parentclass!=None:
            uritotreeitem[parentclass][-1]["data"]["to"]={}
            uritotreeitem[parentclass][-1]["data"]["from"]={}
        tablecontentcounter=-1
        metadatatablecontentcounter=-1
        foundtype=False
        hasnonns=set()
        thetypes = set()
        itembibtex = ""
        if predobjs!=None:
            for tup in sorted(predobjs,key=lambda tup: tup[0]):
                if str(tup[0]) not in predobjmap:
                    predobjmap[str(tup[0])]=[]
                predobjmap[str(tup[0])].append(tup[1])
                if parentclass!=None and str(tup[0]) not in uritotreeitem[parentclass][-1]["data"]["to"]:
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]={}
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]["instancecount"] = 0
                if parentclass!=None:
                    uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]["instancecount"]+=1
                    uritotreeitem[parentclass][-1]["instancecount"]+=1
                if isinstance(tup[1],URIRef):
                    foundtype=True
                    for item in graph.objects(tup[1],URIRef(self.typeproperty)):
                        thetypes.add(str(item))
                        if parentclass!=None:
                            if item not in uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]:
                                uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item] = 0
                            uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item]+=1
                    if baseurl not in str(tup[1]) and str(tup[0])!=self.typeproperty:
                        hasnonns.add(str(tup[1]))
                        if tup[1] not in nonnsmap:
                            nonnsmap[str(tup[1])]=set()
                        nonnsmap[str(tup[1])].add(subject)
            if not foundtype:
                print("no type")
            for tup in predobjmap:
                #QgsMessageLog.logMessage(self.shortenURI(str(tup),True),"OntdocGeneration",Qgis.Info)
                if self.metadatatable and tup not in SPARQLUtils.labelproperties and self.shortenURI(str(tup),True) in SPARQLUtils.metadatanamespaces:
                    thetable=metadatatablecontents
                    metadatatablecontentcounter+=1
                    if metadatatablecontentcounter%2==0:
                        thetable += "<tr class=\"odd\">"
                    else:
                        thetable += "<tr class=\"even\">"
                else:
                    thetable=tablecontents
                    tablecontentcounter+=1
                    if tablecontentcounter%2==0:
                        thetable += "<tr class=\"odd\">"
                    else:
                        thetable += "<tr class=\"even\">"
                if str(tup)==self.typeproperty and URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection") in predobjmap[tup]:
                    isgeocollection=True
                    uritotreeitem["http://www.opengis.net/ont/geosparql#FeatureCollection"][-1]["instancecount"] += 1
                elif str(tup)==self.typeproperty and URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection") in predobjmap[tup]:
                    isgeocollection=True
                    uritotreeitem["http://www.opengis.net/ont/geosparql#GeometryCollection"][-1]["instancecount"] += 1
                elif str(tup)==self.typeproperty:
                    for tp in predobjmap[tup]:
                        if str(tp) in bibtextypemappings:
                            itembibtex="<details><summary>[BIBTEX]</summary><pre>"+str(self.resolveBibtexReference(graph.predicate_objects(subject),subject,graph))+"</pre></details>"
                            break
                thetable=self.formatPredicate(tup, baseurl, checkdepth, thetable, graph,inverse)
                if str(tup) in SPARQLUtils.labelproperties:
                    for lab in predobjmap[tup]:
                        if lab.language==self.labellang:
                            foundlabel=lab
                    if foundlabel=="":
                        foundlabel = str(predobjmap[tup][0])
                if str(tup) in SPARQLUtils.commentproperties:
                    comment[str(tup)]=str(predobjmap[tup][0])
                if len(predobjmap[tup]) > 0:
                    thetable+="<td class=\"wrapword\">"
                    if len(predobjmap[tup])>1:
                        thetable+="<ul>"
                    labelmap={}
                    for item in predobjmap[tup]:
                        if ("POINT" in str(item).upper() or "POLYGON" in str(item).upper() or "LINESTRING" in str(item).upper()) and tup in SPARQLUtils.valueproperties and self.typeproperty in predobjmap and URIRef("http://www.w3.org/ns/oa#WKTSelector") in predobjmap[self.typeproperty]:
                            image3dannos.add(str(item))
                        elif "<svg" in str(item):
                            foundmedia["image"].add(str(item))
                        elif "http" in str(item):
                            if isinstance(item,Literal):
                                ext = "." + ''.join(filter(str.isalpha, str(item.value).split(".")[-1]))
                            else:
                                ext = "." + ''.join(filter(str.isalpha, str(item).split(".")[-1]))
                            if ext in SPARQLUtils.fileextensionmap:
                                foundmedia[SPARQLUtils.fileextensionmap[ext]].add(str(item))
                        elif tup in SPARQLUtils.valueproperties:
                            foundvals.add(str(item))
                        res=self.createHTMLTableValueEntry(subject, tup, item, ttlf, graph,
                                              baseurl, checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos,dateprops,inverse,nonns)
                        geojsonrep = res["geojson"]
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        textannos=res["textannos"]
                        image3dannos=res["image3dannos"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        if len(predobjmap[tup]) > 1:
                            labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                    for lab in sorted(labelmap):
                        thetable+=str(labelmap[lab])
                    if len(predobjmap[tup])>1:
                        thetable+="</ul>"
                    thetable+="</td>"
                else:
                    thetable += "<td class=\"wrapword\"></td>"
                thetable += "</tr>"
                if tup not in SPARQLUtils.labelproperties and self.shortenURI(str(tup), True) in SPARQLUtils.metadatanamespaces:
                    metadatatablecontents=thetable
                else:
                    tablecontents=thetable
                isodd = not isodd
        subpredsmap={}
        if subpreds!=None:
            for tup in sorted(subpreds,key=lambda tup: tup[1]):
                if str(tup[1]) not in subpredsmap:
                    subpredsmap[str(tup[1])]=[]
                subpredsmap[str(tup[1])].append(tup[0])
                if parentclass!=None and str(tup[1]) not in uritotreeitem[parentclass][-1]["data"]["from"]:
                    uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]={}
                    uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]["instancecount"] = 0
                if isinstance(tup[0],URIRef):
                    for item in graph.objects(tup[0],URIRef(self.typeproperty)):
                        if parentclass!=None:
                            if item not in uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])]:
                                uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])][item] = 0
                            uritotreeitem[parentclass][-1]["data"]["from"][str(tup[1])][item]+=1
            for tup in subpredsmap:
                if isodd:
                    tablecontents += "<tr class=\"odd\">"
                else:
                    tablecontents += "<tr class=\"even\">"
                tablecontents=self.formatPredicate(tup, baseurl, checkdepth, tablecontents, graph,True)
                if len(subpredsmap[tup]) > 0:
                    tablecontents += "<td class=\"wrapword\">"
                    if len(subpredsmap[tup]) > 1:
                        tablecontents += "<ul>"
                    labelmap={}
                    for item in subpredsmap[tup]:
                        if subjectstorender!=None and item not in subjectstorender and baseurl in str(item):
                            postprocessing.add((item,URIRef(tup),subject))
                        res = self.createHTMLTableValueEntry(subject, tup, item, None, graph,
                                                             baseurl, checkdepth, geojsonrep,foundmedia,imageannos,textannos,image3dannos,dateprops,True,nonns)
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        image3dannos=res["image3dannos"]
                        if nonns and str(tup) != self.typeproperty:
                            hasnonns.add(str(item))
                        if nonns:
                            geojsonrep=res["geojson"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        if len(subpredsmap[tup]) > 1:
                            labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                    for lab in sorted(labelmap):
                        tablecontents+=str(labelmap[lab])
                    if len(subpredsmap[tup])>1:
                        tablecontents+="</ul>"
                    tablecontents += "</td>"
                else:
                    tablecontents += "<td class=\"wrapword\"></td>"
                tablecontents += "</tr>"
                isodd = not isodd
        if self.licenseuri!=None:
            ttlf.add((subject, URIRef("http://purl.org/dc/elements/1.1/license"), URIRef(self.licenseuri)))
        nonnslink=""
        if nonns:
            completesavepath = savepath
            nonnslink = "<div>This page describes linked instances to the concept  <a target=\"_blank\" href=\"" + str(
                subject) + "\">" + str(foundlabel) + " (" + str(self.shortenURI(
                subject)) + ") </a> in this knowledge graph. It is defined <a target=\"_blank\" href=\"" + str(
                subject) + "\">here</a></div>"
        else:
            completesavepath=savepath + "/index.html"
        if not nonns:
            ttlf.serialize(savepath + "/index.ttl", encoding="utf-8")
            with open(savepath + "/index.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(predobjmap))
                f.close()
        with open(completesavepath, 'w', encoding='utf-8') as f:
            rellink=self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,searchfilename,False)
            rellink2 = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,classtreename,False)
            rellink3 = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,"style.css",False)
            rellink4 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js", False)
            rellink5 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "proprelations.js", False)
            epsgdefslink = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "epsgdefs.js", False)
            rellink7 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "vowl_result.js", False)
            if geojsonrep != None:
                myexports=geoexports
            else:
                myexports=nongeoexports
            itembibtex=""
            if foundlabel != "":
                f.write(htmltemplate.replace("{{logo}}",logo).replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(baseurl,checkdepth)).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{toptitle}}", foundlabel).replace(
                    "{{startscriptpath}}", rellink4).replace(
                    "{{epsgdefspath}}", epsgdefslink).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}",itembibtex).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{indexpage}}","false").replace("{{title}}",
                                                                                                "<a href=\"" + str(subject) + "\">" + str(foundlabel) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}","").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{nonnslink}}",str(nonnslink)).replace("{{subject}}",str(subject)))
            else:
                f.write(htmltemplate.replace("{{logo}}",logo).replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(baseurl,checkdepth)).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{indexpage}}","false").replace("{{toptitle}}", self.shortenURI(str(subject))).replace(
                    "{{startscriptpath}}", rellink4).replace(
                    "{{epsgdefspath}}", epsgdefslink).replace("{{versionurl}}",versionurl).replace("{{version}}",version).replace("{{bibtex}}",itembibtex).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{title}}","<a href=\"" + str(subject) + "\">" + self.shortenURI(str(subject)) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{description}}", "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{nonnslink}}",str(nonnslink)).replace("{{subject}}",str(subject)))
            for comm in comment:
                f.write(htmlcommenttemplate.replace("{{comment}}", self.shortenURI(comm) + ":" + comment[comm]))
            for fval in foundvals:
                f.write(htmlcommenttemplate.replace("{{comment}}", "<b>Value:<mark>" + str(fval) + "</mark></b>"))
            if len(foundmedia["mesh"])>0 and len(image3dannos)>0:
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        self.generateIIIFManifest(self.outpath, foundmedia["mesh"], image3dannos, str(subject),
                                                  self.prefixnamespace, foundlabel, comment, thetypes, predobjmap,
                                                  "Model"))
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}",str(list(foundmedia["mesh"]))))
            elif len(foundmedia["mesh"])>0 and len(image3dannos)==0:
                QgsMessageLog.logMessage("Found 3D Model: "+str(foundmedia["mesh"]))
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        self.generateIIIFManifest(self.outpath, foundmedia["mesh"], image3dannos, str(subject),
                                                  self.prefixnamespace, foundlabel, comment, thetypes, predobjmap,
                                                  "Model"))
                for curitem in foundmedia["mesh"]:
                    format="ply"
                    if ".nxs" in curitem or ".nxz" in curitem:
                        format="nexus"
                    f.write(image3dtemplate.replace("{{meshurl}}",curitem).replace("{{meshformat}}",format))
                    break
            elif len(foundmedia["mesh"])==0 and len(image3dannos)>0:
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}","[]"))
            carousel="image"
            if len(foundmedia["image"])>3:
                carousel="carousel-item active"
                f.write(imagecarouselheader)
            if len(imageannos)>0 and len(foundmedia["image"])>0:
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        self.generateIIIFManifest(self.outpath, foundmedia["image"], imageannos, str(subject),
                                                  self.prefixnamespace, foundlabel, comment, thetypes, predobjmap,
                                                  "Image"))
                for image in foundmedia["image"]:
                    annostring=""
                    for anno in imageannos:
                        annostring+=anno.replace("<svg>","<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                    f.write(imageswithannotemplate.replace("{{carousel}}",carousel+"\" style=\"position: relative;display: inline-block;").replace("{{image}}",str(image)).replace("{{svganno}}",annostring).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            elif len(foundmedia["image"])>0:
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        self.generateIIIFManifest(self.outpath, foundmedia["image"], imageannos, str(subject),
                                                  self.prefixnamespace, foundlabel, comment, thetypes, predobjmap,
                                                  "Image"))
                for image in foundmedia["image"]:
                    if image=="<svg width=":
                        continue
                    if "<svg" in image:
                        if "<svg>" in image:
                            f.write(imagestemplatesvg.replace("{{carousel}}",carousel).replace("{{image}}", str(image.replace("<svg>","<svg class=\"svgview\">"))))
                        else:
                            f.write(imagestemplatesvg.replace("{{carousel}}",carousel).replace("{{image}}",str(image)))
                    else:
                        f.write(imagestemplate.replace("{{carousel}}",carousel).replace("{{image}}",str(image)).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            if len(foundmedia["image"])>3:
                f.write(imagecarouselfooter)
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
            if len(foundmedia["audio"]) > 0 and self.iiif:
                iiifmanifestpaths["default"].append(
                    self.generateIIIFManifest(self.outpath, foundmedia["audio"], None, str(subject), self.prefixnamespace,
                                              foundlabel, comment, thetypes, predobjmap, "Audio"))
            for audio in foundmedia["audio"]:
                f.write(audiotemplate.replace("{{audio}}",str(audio)))
            if len(foundmedia["video"]) > 0 and self.iiif:
                iiifmanifestpaths["default"].append(
                    self.generateIIIFManifest(self.outpath, foundmedia["video"], None, str(subject), self.prefixnamespace,
                                              foundlabel, comment, thetypes, predobjmap, "Video"))
            for video in foundmedia["video"]:
                f.write(videotemplate.replace("{{video}}",str(video)))
            if geojsonrep != None and not isgeocollection:
                if uritotreeitem != None and str(subject) in uritotreeitem:
                    uritotreeitem[str(subject)][-1]["type"] = "geoinstance"
                props = predobjmap
                if timeobj != None:
                    for item in timeobj:
                        dateprops.append(item)
                        props[item] = str(timeobj[item])
                jsonfeat = {"type": "Feature", 'id': str(subject), 'name': foundlabel, 'dateprops': dateprops,
                            'properties': props, "geometry": geojsonrep}
                if epsgcode == "" and "crs" in geojsonrep:
                    epsgcode = "EPSG:" + geojsonrep["crs"]
                if len(hasnonns) > 0:
                    self.geocache[str(subject)] = jsonfeat
                f.write(maptemplate.replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",
                                                                                       "[" + json.dumps(
                                                                                           jsonfeat) + "]").replace(
                    "{{epsg}}", epsgcode).replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(baseurl,checkdepth)).replace("{{baselayers}}", json.dumps(self.baselayers)).replace("{{epsgdefspath}}",
                                                                                                    epsgdefslink).replace(
                    "{{dateatt}}", ""))
            elif isgeocollection or nonns:
                if foundlabel != None and foundlabel != "":
                    featcoll = {"type": "FeatureCollection", "id": subject, "name": str(foundlabel), "features": []}
                else:
                    featcoll = {"type": "FeatureCollection", "id": subject, "name": self.shortenURI(subject),
                                "features": []}
                thecrs = set()
                dateatt = ""
                if isgeocollection and not nonns:
                    memberpred = URIRef("http://www.w3.org/2000/01/rdf-schema#member")
                    for memberid in graph.objects(subject, memberpred, True):
                        for geoinstance in graph.predicate_objects(memberid, True):
                            geojsonrep = None
                            if geoinstance != None and isinstance(geoinstance[1], Literal) and (
                                    str(geoinstance[0]) in SPARQLUtils.geoproperties or str(
                                    geoinstance[1].datatype) in SPARQLUtils.geoliteraltypes):
                                geojsonrep = LayerUtils.processLiteral(str(geoinstance[1]), str(geoinstance[1].datatype), "")
                                uritotreeitem[str(subject)][-1]["type"] = "geocollection"
                            elif geoinstance != None and str(geoinstance[0]) in SPARQLUtils.geopointerproperties:
                                uritotreeitem[str(subject)][-1]["type"] = "featurecollection"
                                for geotup in graph.predicate_objects(geoinstance[1], True):
                                    if isinstance(geotup[1], Literal) and (str(geotup[0]) in SPARQLUtils.geoproperties or str(
                                            geotup[1].datatype) in SPARQLUtils.geoliteraltypes):
                                        geojsonrep = LayerUtils.processLiteral(str(geotup[1]), str(geotup[1].datatype), "")
                            if geojsonrep != None:
                                if uritotreeitem != None and str(memberid) in uritotreeitem:
                                    featcoll["features"].append({"type": "Feature", 'id': str(memberid),
                                                                 'name': uritotreeitem[str(memberid)][-1]["text"],
                                                                 'dateprops': dateprops, 'properties': {},
                                                                 "geometry": geojsonrep})
                                else:
                                    featcoll["features"].append(
                                        {"type": "Feature", 'id': str(memberid), 'name': str(memberid),
                                         'dateprops': dateprops, 'properties': {}, "geometry": geojsonrep})
                                if len(featcoll["features"][-1]["dateprops"]) > 0:
                                    dateatt = featcoll["features"][-1]["dateprops"][0]
                    if len(hasnonns) > 0:
                        self.geocache[str(subject)] = featcoll
                elif nonns:
                    for item in hasnonns:
                        if item in self.geocache:
                            featcoll["features"].append(self.geocache[item])
                            if len(self.geocache[item]["dateprops"]) > 0:
                                dateatt = self.geocache[item]["dateprops"][0]
                            if "crs" in self.geocache[item]:
                                thecrs.add(self.geocache[item]["crs"])
                if len(featcoll["features"]) > 0:
                    featcoll["numberMatched"] = len(featcoll["features"])
                    featcoll["numberReturned"] = len(featcoll["features"])
                    #featcoll["bbox"] = shapely.geometry.GeometryCollection(
                    #    [shapely.geometry.shape(feature["geometry"]) for feature in featcoll["features"]]).bounds
                    if len(thecrs) > 0:
                        featcoll["crs"] = "http://www.opengis.net/def/crs/EPSG/0/" + str(next(iter(thecrs)))
                    else:
                        featcoll["crs"] = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                    if dateatt != "":
                        for feat in featcoll["features"]:
                            if dateatt not in feat["properties"]:
                                feat["properties"][dateatt] = ""
                    if self.localOptimized:
                        f.write(maptemplate.replace("var ajax=true", "var ajax=false").replace("{{myfeature}}",
                                                                                               "[" + json.dumps(
                                                                                                   featcoll) + "]").replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(baseurl,checkdepth)).replace(
                            "{{baselayers}}", json.dumps(self.baselayers)).replace("{{epsgdefspath}}", epsgdefslink).replace(
                            "{{dateatt}}", dateatt))
                    else:
                        f.write(maptemplate.replace("{{myfeature}}", "[\"" + self.shortenURI(
                            str(completesavepath.replace(".html", ".geojson"))) + "\"]").replace("{{relativepath}}",self.generateRelativePathFromGivenDepth(baseurl,checkdepth)).replace("{{baselayers}}",
                                                                                                 json.dumps(
                                                                                                     self.baselayers)).replace(
                            "{{epsgdefspath}}", epsgdefslink).replace("{{dateatt}}", dateatt))
                    with open(completesavepath.replace(".html", ".geojson"), 'w', encoding='utf-8') as fgeo:
                        featurecollectionspaths[completesavepath.replace(".html", ".geojson")] = {
                            "name": featcoll["name"], "id": featcoll["id"]}
                        fgeo.write(json.dumps(featcoll))
                        fgeo.close()
            f.write(htmltabletemplate.replace("{{tablecontent}}", tablecontents))
            if metadatatablecontentcounter>=0:
                f.write("<h5>Metadata</h5>")
                f.write(htmltabletemplate.replace("{{tablecontent}}", metadatatablecontents))
            f.write(htmlfooter.replace("{{exports}}",myexports).replace("{{license}}",curlicense).replace("{{bibtex}}",itembibtex))
            f.close()
        return [postprocessing,nonnsmap]
