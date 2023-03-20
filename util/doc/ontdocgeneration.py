# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from qgis.core import Qgis, QgsMessageLog
import os
import re
import shutil
import json


from ..layerutils import LayerUtils
from ..sparqlutils import SPARQLUtils
from .pyowl2vowl import OWL2VOWL

templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/html/"))

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

featurecollectionspaths=set()

nonmaptemplate="""<script>var nongeofeature = {{myfeature}}</script>"""

htmlcommenttemplate="""<p class="comment"><b>Description:</b> {{comment}}</p>"""

htmltabletemplate="""
<table border=1 width=100% class=description><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{{tablecontent}}</tbody></table>"""

global htmlfooter
htmlfooter="""<div id="footer"><div class="container-fluid"><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink2" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button>{{license}}</div></div><script>$(document).ready(function(){setSVGDimensions()})</script></body></html>"""

licensetemplate=""""""

classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
        SELECT DISTINCT ?subject ?label ?supertype\n
        WHERE {\n
           { ?individual rdf:type ?subject . } UNION { ?subject rdf:type owl:Class . } .\n
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
        if os.path.exists(templatepath+"/"+templatename+"/templates/3dtemplate.html"):
            with open(templatepath+"/"+templatename+"/templates/3dtemplate.html", 'r') as file:
                global image3dtemplate
                image3dtemplate=file.read()
        if os.path.exists(templatepath+"/"+templatename+"/templates/3dtemplate.html"):
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

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,createcollections,baselayers,tobeaddedPerInd,maincolor,tablecolor,progress,createIndexPages=True,logoname="",templatename="default"):
        self.prefixes=prefixes
        self.prefixnamespace = prefixnamespace
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.progress=progress
        self.baselayers=baselayers
        self.tobeaddedPerInd=tobeaddedPerInd
        self.logoname=logoname
        self.geocollectionspaths=[]
        self.templatename=templatename
        resolveTemplate(templatename)
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
        #prefixes["reversed"]["http://purl.org/suni/"] = "suni"

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
            if "value" in tobeaddedPerInd[prop] and not tobeaddedPerInd[prop]["value"].startswith("http"):
                if "type" in tobeaddedPerInd[prop]:
                    graph.add((ind,URIRef(prop),Literal(tobeaddedPerInd[prop]["value"],datatype=tobeaddedPerInd[prop]["type"])))
                elif "value" in tobeaddedPerInd[prop]:
                    graph.add((ind, URIRef(prop), Literal(tobeaddedPerInd[prop]["value"])))
            elif "value" in tobeaddedPerInd[prop] and not "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))
            elif "value" in tobeaddedPerInd[prop] and "uri" in tobeaddedPerInd[prop]:
                graph.add((ind, URIRef(prop), URIRef(str(tobeaddedPerInd[prop]["value"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"])), URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), URIRef(str(tobeaddedPerInd[prop]["uri"]))))
                graph.add((URIRef(str(tobeaddedPerInd[prop]["value"]).replace(" ","_")),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),URIRef(str(tobeaddedPerInd[prop]["value"]))))
    def updateProgressBar(self,currentsubject,allsubjects):
        newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
        self.progress.setLabelText(newtext + "\n Processed: "+str(currentsubject)+" of "+str(allsubjects)+" URIs... ("+str(round(((currentsubject/allsubjects)*100),0))+"%)")

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
        pathmap = {}
        paths = {}
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
            postprocessing=self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing)
            subtorencounter += 1
            if subtorencounter%250==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
            #QgsMessageLog.logMessage(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path),"OntdocGeneration",Qgis.Info)
            #except Exception as e:
            #    QgsMessageLog.logMessage(e)
            #    QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        #QgsMessageLog.logMessage("Postprocessing " + str(postprocessing.subjects()), "OntdocGeneration", Qgis.Info)
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
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=jsonindent))
            f.close()
        self.detectURIsConnectedToSubjects(subjectstorender, self.graph, prefixnamespace, corpusid, outpath, self.license)
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
            subgraph.serialize(path + "index.ttl",encoding="utf-8")
            QgsMessageLog.logMessage("BaseURL " + nslink,"OntdocGeneration", Qgis.Info)
            indexhtml = htmltemplate.replace("{{logo}}",self.logoname).replace("{{relativedepth}}", str(checkdepth)).replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Index page for " + nslink).replace("{{title}}","Index page for " + nslink).replace("{{startscriptpath}}", scriptlink).replace("{{stylepath}}", stylelink).replace("{{epsgdefspath}}", epsgdefslink).replace("{{vowlpath}}", vowllink)\
                .replace("{{classtreefolderpath}}",classtreelink).replace("{{baseurlhtml}}", nslink).replace("{{scriptfolderpath}}", sfilelink).replace("{{exports}}",nongeoexports)
            if nslink==prefixnamespace:
                indexhtml=indexhtml.replace("{{indexpage}}","true")
            else:
                indexhtml = indexhtml.replace("{{indexpage}}", "false")
            indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"+vowltemplate
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
            indexhtml+=htmlfooter.replace("{{license}}",curlicense).replace("{{exports}}",nongeoexports)
            #QgsMessageLog.logMessage(path)
            with open(path + "index.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()
        if len(featurecollectionspaths)>0:
            indexhtml = htmltemplate.replace("{{logo}}",self.logoname).replace("{{relativedepth}}","0").replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Feature Collection Overview").replace("{{title}}","Feature Collection Overview").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{vowlpath}}", "vowl_result.js")\
                    .replace("{{classtreefolderpath}}",corpusid + "_classtree.js").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}", corpusid + '_search.js').replace("{{exports}}",nongeoexports)
            indexhtml = indexhtml.replace("{{indexpage}}", "true")
            self.merge_JsonFiles(featurecollectionspaths,str(outpath)+"features.js")
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml+="<script src=\"features.js\"></script>"
            indexhtml+=maptemplate.replace("var featurecolls = {{myfeature}}","").replace("{{baselayers}}",json.dumps(self.baselayers))
            indexhtml += htmlfooter.replace("{{license}}", curlicense).replace("{{exports}}", nongeoexports)
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()

    def merge_JsonFiles(self,files,outpath):
        result = list()
        for f1 in files:
            with open(f1, 'r',encoding="utf-8") as infile:
                result.append(json.load(infile))
        with open(outpath, 'w',encoding="utf-8") as output_file:
            output_file.write("var featurecolls="+json.dumps(result))

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
        with open(outpath+"proprelations.js", 'w', encoding='utf-8') as f:
            f.write("var proprelations="+json.dumps(predicates))
            f.close()

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
        if uri.endswith("/"):
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

    def generateRelativeLinkFromGivenDepth(self,baseurl,checkdepth,item,withindex):
        rellink = str(item).replace(baseurl, "")
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        if withindex:
            rellink += "/index.html"
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    def searchObjectConnectionsForAggregateData(self, graph, object, pred, geojsonrep, foundmedia, imageannos,
                                                    textannos, image3dannos, label, unitlabel):
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
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                if tup[1].language==self.labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    self.typeproperty) and (
                    tup[1] == URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1] == URIRef(
                    "http://www.w3.org/ns/oa#WKTSelector")):
                for svglit in graph.objects(object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value"),True):
                    if "<svg" in str(svglit):
                        imageannos.add(str(svglit))
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(
                            svglit).upper()):
                        image3dannos.add(str(svglit))
            if pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
                    self.typeproperty) and tup[1] == URIRef(
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
            if pred == "http://www.w3.org/ns/oa#hasSource":
                annosource = str(tup[1])
            if isinstance(tup[1], Literal) and (
                    str(tup[0]) in SPARQLUtils.geoproperties or str(tup[1].datatype) in SPARQLUtils.geoliteraltypes):
                geojsonrep = LayerUtils.processLiteral(str(tup[1]), str(tup[1].datatype), "")
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
                elif str(tup[0]) != "http://www.w3.org/ns/oa#hasTarget":
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
            res = None
            if "http" in foundunit:
                res = self.replaceNameSpacesInLabel(str(foundunit))
                if res != None:
                    unitlabel = str(foundval) + " <a href=\"" + str(foundunit) + "\" target=\"_blank\">" + str(
                        res["uri"]) + "</a>"
                else:
                    unitlabel = str(foundval) + " <a href=\"" + str(foundunit) + "\" target=\"_blank\">" + str(
                        self.shortenURI(foundunit)) + "</a>"
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
                "imageannos": imageannos, "textannos": textannos, "image3dannos": image3dannos}

    def createHTMLTableValueEntry(self,subject,pred,object,ttlf,graph,baseurl,checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos):
        tablecontents=""
        label=""
        if isinstance(object,URIRef) or isinstance(object,BNode):
            if ttlf != None:
                ttlf.add((subject,URIRef(pred),object))
            label = ""
            unitlabel=""
            mydata=self.searchObjectConnectionsForAggregateData(graph,object,pred,geojsonrep,foundmedia,imageannos,textannos,image3dannos,label,unitlabel)
            label=mydata["label"]
            if label=="":
                label=str(self.shortenURI(str(object)))
            geojsonrep=mydata["geojsonrep"]
            foundmedia=mydata["foundmedia"]
            imageannos=mydata["imageannos"]
            textannos=mydata["textannos"]
            image3dannos=mydata["image3dannos"]
            unitlabel=mydata["unitlabel"]
            if baseurl in str(object) or isinstance(object,BNode):
                rellink = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,str(object),True)
                tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(object) + "\" href=\"" + rellink + "\">"+ label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(self.shortenURI(str(object))) + ")</span></a>"
            else:
                res = self.replaceNameSpacesInLabel(str(object))
                if res != None:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(
                        object) + "\" target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                         "uri"] + ")</span></a>"
                else:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(
                        object) + "\" target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + "</a>"
            if unitlabel!="":
                tablecontents+=" <span style=\"font-weight:bold\">["+str(unitlabel)+"]</span>"
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
                if isinstance(object, Literal) and (str(pred) in SPARQLUtils.geoproperties or str(object.datatype) in SPARQLUtils.geoliteraltypes):
                    geojsonrep = LayerUtils.processLiteral(str(object), str(object.datatype), "",None,None,True)
            else:
                if object.language != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\" xml:lang=\"" + str(object.language) + "\">" + str(object).replace("<", "&lt").replace(">", "&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">rdf:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/"+str(object.language)+"\" target=\"_blank\">iso6391:" + str(object.language) + "</a>)</small></span>"
                else:
                    tablecontents += self.detectStringLiteralContent(pred,object)
        return {"html":tablecontents,"geojson":geojsonrep,"foundmedia":foundmedia,"imageannos":imageannos,"textannos":textannos,"image3dannos":image3dannos,"label":label}

    def detectStringLiteralContent(self,pred,object):
        if object.startswith("http://") or object.startswith("https://"):
            return "<span><a property=\"" + str(pred) + "\" target=\"_blank\" href=\"" + str(
                        object)+ "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object)+ "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        if object.startswith("www."):
            return "<span><a property=\"" + str(pred) + "\" target=\"_blank\" href=\"http://" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">http://" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        if re.search(r'[\w.]+\@[\w.]+', object):
            return "<span><a property=\"" + str(pred) + "\" href=\"mailto:" + str(
                object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">mailto:" + str(
                object) + "</a> <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return "<span property=\"" + str(pred) + "\" content=\"" + str(object).replace("<","&lt").replace(">","&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<","&lt").replace(">","&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"


    def formatPredicate(self,tup,baseurl,checkdepth,tablecontents,graph,reverse):
        onelabel=self.shortenURI(str(tup))
        label=None
        for obj in graph.predicate_objects(tup):
            if str(obj[0]) in SPARQLUtils.labelproperties:
                if obj[1].language==self.labellang:
                    label = str(obj[1])
                    break
                onelabel=str(obj[1])
        if label==None:
            label=onelabel
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

    def detectURIsConnectedToSubjects(self,subjectstorender,graph,prefixnamespace,corpusid,outpath,curlicense):
        uristorender={}
        for sub in subjectstorender:
            onelabel=""
            added=[]
            for tup in graph.predicate_objects(sub):
                if str(tup[0]) in SPARQLUtils.labelproperties:
                    onelabel=str(tup[1])
                if isinstance(tup[1],URIRef) and prefixnamespace not in str(tup[1]) and "http://www.w3.org/1999/02/22-rdf-syntax-ns#" not in str(tup[1]):
                    if str(tup[0]) not in uristorender:
                        uristorender[str(tup[0])]={}
                    if str(tup[1]) not in uristorender[str(tup[0])]:
                        uristorender[str(tup[0])][str(tup[1])]=[]
                    toadd={"sub":sub,"label":onelabel}
                    added.append(toadd)
                    uristorender[str(tup[0])][str(tup[1])].append(toadd)
            for item in added:
                item["label"]=onelabel
        for uri in uristorender:
            indexhtml = htmltemplate.replace("{{logo}}",self.logoname).replace("{{relativedepth}}","0").replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}",self.shortenURI(uri)).replace("{{title}}","Feature Collection Overview").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{vowlpath}}", "vowl_result.js")\
                    .replace("{{classtreefolderpath}}",corpusid + "_classtree.js").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}", corpusid + '_search.js').replace("{{exports}}",nongeoexports)
            indexhtml = indexhtml.replace("{{indexpage}}", "true")
            indexhtml+="<table border=\"1\" width=\"100%\" class=\"description\"><tr><th>Property</th><th>Value</th></tr>"
            counter=0
            for entry in uristorender[uri]:
                if counter%2==0:
                    indexhtml += "<tr class=\"odd\">"
                else:
                    indexhtml += "<tr class=\"even\">"
                indexhtml+="<td><a href=\""+str(entry)+"\">"+self.shortenURI(entry)+"</a></td><td><ul>"
                for sub in uristorender[uri][entry]:
                    if sub["label"]!="":
                        indexhtml += "<li><a href=\"" + str(sub["sub"]) + "\">" + str(sub["label"]) + "</a></li>"
                    else:
                        indexhtml+="<li><a href=\""+str(sub["sub"])+"\">"+self.shortenURI(str(sub["sub"]))+"</a></li>"
                indexhtml+="</ul></td></tr>"
                counter+=1
            indexhtml+="</table>"
            indexhtml += htmlfooter.replace("{{license}}", curlicense).replace("{{exports}}", nongeoexports)
            with open(outpath + "_"+self.shortenURI(uri)+".html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()

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

    def createHTML(self,savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,uritotreeitem,curlicense,subjectstorender,postprocessing):
        tablecontents = ""
        metadatatablecontents=""
        isodd = False
        geojsonrep=None
        epsgcode=""
        foundmedia={"audio":set(),"video":set(),"image":set(),"mesh":set()}
        savepath = savepath.replace("\\", "/")
        checkdepth=self.checkDepthFromPath(savepath, baseurl, subject)
        foundlabel = ""
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
        if str(subject) in uritotreeitem and uritotreeitem[str(subject)][-1]["parent"].startswith("http"):
            parentclass=str(uritotreeitem[str(subject)][-1]["parent"])
            if parentclass not in uritotreeitem:
                uritotreeitem[parentclass]=[{"id": parentclass, "parent": "#","type": "class","text": self.shortenURI(str(parentclass)),"data":{}}]
            uritotreeitem[parentclass][-1]["instancecount"]=0
        ttlf = Graph(bind_namespaces="rdflib")
        #ttlf = open(savepath + "/index.ttl", "w", encoding="utf-8")
        if parentclass!=None:
            uritotreeitem[parentclass][-1]["data"]["to"]={}
            uritotreeitem[parentclass][-1]["data"]["from"]={}
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
                for item in graph.objects(tup[1],URIRef(self.typeproperty)):
                    if parentclass!=None:
                        if item not in uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])]:
                            uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item] = 0
                        uritotreeitem[parentclass][-1]["data"]["to"][str(tup[0])][item]+=1
        tablecontentcounter=-1
        metadatatablecontentcounter=-1
        for tup in predobjmap:
            #QgsMessageLog.logMessage(self.shortenURI(str(tup),True),"OntdocGeneration",Qgis.Info)
            if tup not in SPARQLUtils.labelproperties and self.shortenURI(str(tup),True) in SPARQLUtils.metadatanamespaces:
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
                                          baseurl, checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos)
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
                    if item not in subjectstorender and baseurl in str(item):
                        #QgsMessageLog.logMessage("Postprocessing: " + str(item)+" - "+str(tup)+" - "+str(subject))
                        postprocessing.add((item,URIRef(tup),subject))
                    res = self.createHTMLTableValueEntry(subject, tup, item, None, graph,
                                                         baseurl, checkdepth, geojsonrep,foundmedia,imageannos,textannos,image3dannos)
                    foundmedia = res["foundmedia"]
                    imageannos=res["imageannos"]
                    image3dannos=res["image3dannos"]
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
        ttlf.serialize(savepath + "/index.ttl", encoding="utf-8")
        with open(savepath + "/index.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(predobjmap))
            f.close()
        with open(savepath + "/index.html", 'w', encoding='utf-8') as f:
            rellink=self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,searchfilename,False)
            rellink2 = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,classtreename,False)
            rellink3 = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,"style.css",False)
            rellink4 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js", False)
            rellink5 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "proprelations.js", False)
            rellink6 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "epsgdefs.js", False)
            rellink7 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "vowl_result.js", False)
            if geojsonrep != None:
                myexports=geoexports
            else:
                myexports=nongeoexports
            if foundlabel != "":
                f.write(htmltemplate.replace("{{logo}}",logo).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{toptitle}}", foundlabel).replace(
                    "{{startscriptpath}}", rellink4).replace(
                    "{{epsgdefspath}}", rellink6).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{indexpage}}","false").replace("{{title}}",
                                                                                                "<a href=\"" + str(subject) + "\">" + str(foundlabel) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}","").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{subject}}",str(subject)))
            else:
                f.write(htmltemplate.replace("{{logo}}",logo).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{indexpage}}","false").replace("{{toptitle}}", self.shortenURI(str(subject))).replace(
                    "{{startscriptpath}}", rellink4).replace(
                    "{{epsgdefspath}}", rellink6).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{title}}","<a href=\"" + str(subject) + "\">" + self.shortenURI(str(subject)) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{description}}", "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{subject}}",str(subject)))
            for comm in comment:
                f.write(htmlcommenttemplate.replace("{{comment}}", self.shortenURI(comm) + ":" + comment[comm]))
            for fval in foundvals:
                f.write(htmlcommenttemplate.replace("{{comment}}", "<b>Value:<mark>" + str(fval) + "</mark></b>"))
            if len(foundmedia["mesh"])>0 and len(image3dannos)>0:
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}",str(list(foundmedia["mesh"]))))
            elif len(foundmedia["mesh"])>0 and len(image3dannos)==0:
                QgsMessageLog.logMessage("Found 3D Model: "+str(foundmedia["mesh"]))
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
                for image in foundmedia["image"]:
                    annostring=""
                    for anno in imageannos:
                        annostring+=anno.replace("<svg>","<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                    f.write(imageswithannotemplate.replace("{{carousel}}",carousel+"\" style=\"position: relative;display: inline-block;").replace("{{image}}",str(image)).replace("{{svganno}}",annostring).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            else:
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
            for audio in foundmedia["audio"]:
                f.write(audiotemplate.replace("{{audio}}",str(audio)))
            for video in foundmedia["video"]:
                f.write(videotemplate.replace("{{video}}",str(video)))
            if geojsonrep!=None and not isgeocollection:
                if str(subject) in uritotreeitem:
                    uritotreeitem[str(subject)][-1]["type"]="geoinstance"
                jsonfeat={"type": "Feature", 'id':str(subject),'label':foundlabel, 'properties': predobjmap, "geometry": geojsonrep}
                if epsgcode=="" and "crs" in geojsonrep:
                    epsgcode="EPSG:"+geojsonrep["crs"]
                f.write(maptemplate.replace("{{myfeature}}","["+json.dumps(jsonfeat)+"]").replace("{{epsg}}",epsgcode).replace("{{baselayers}}",json.dumps(self.baselayers)))
            elif isgeocollection:
                featcoll={"type":"FeatureCollection", "id":subject,"name":self.shortenURI(subject), "features":[]}
                for memberid in graph.objects(subject,URIRef("http://www.w3.org/2000/01/rdf-schema#member")):
                    for geoinstance in graph.predicate_objects(memberid):
                        geojsonrep=None
                        if isinstance(geoinstance[1], Literal) and (str(geoinstance[0]) in SPARQLUtils.geoproperties or str(geoinstance[1].datatype) in SPARQLUtils.geoliteraltypes):
                            geojsonrep = LayerUtils.processLiteral(str(geoinstance[1]), str(geoinstance[1].datatype), "",None,None,True)
                            uritotreeitem[str(subject)][-1]["type"] = "geocollection"
                        elif str(geoinstance[0]) in SPARQLUtils.geopointerproperties:
                            uritotreeitem[str(subject)][-1]["type"] = "featurecollection"
                            for geotup in graph.predicate_objects(geoinstance[1]):
                                if isinstance(geotup[1], Literal) and (str(geotup[0]) in SPARQLUtils.geoproperties or str(geotup[1].datatype) in SPARQLUtils.geoliteraltypes):
                                    geojsonrep = LayerUtils.processLiteral(str(geotup[1]), str(geotup[1].datatype), "",None,None,True)
                        if geojsonrep!=None:
                            if str(memberid) in uritotreeitem:
                                featcoll["features"].append({"type": "Feature", 'id': str(memberid), 'label': uritotreeitem[str(memberid)][-1]["text"], 'properties': {},"geometry": geojsonrep})
                            else:
                                featcoll["features"].append({"type": "Feature", 'id': str(memberid),'label': str(memberid), 'properties': {}, "geometry": geojsonrep})
                f.write(maptemplate.replace("{{myfeature}}","["+json.dumps(featcoll)+"]").replace("{{baselayers}}",json.dumps(self.baselayers)))
                with open(savepath + "/index.geojson", 'w', encoding='utf-8') as fgeo:
                    featurecollectionspaths.add(savepath + "/index.geojson")
                    fgeo.write(json.dumps(featcoll))
                    fgeo.close()
            f.write(htmltabletemplate.replace("{{tablecontent}}", tablecontents))
            if metadatatablecontentcounter>=0:
                f.write("<h5>Metadata</h5>")
                f.write(htmltabletemplate.replace("{{tablecontent}}", metadatatablecontents))
            f.write(htmlfooter.replace("{{exports}}",myexports).replace("{{license}}",curlicense))
            f.close()
        return postprocessing
