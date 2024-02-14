# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib.plugins.sparql import prepareQuery
from qgis.core import Qgis, QgsMessageLog
import os
import re
import urllib
import shutil
import json

from .docutils import DocUtils
from .docconfig import DocConfig
from .docdefaults import DocDefaults
from ..export.pages.observationpage import ObservationPage
from ..export.pages.bibpage import BibPage
from ..export.pages.lexiconpage import LexiconPage
from ..export.pages.personpage import PersonPage
from ..export.pages.textannopage import TextAnnoPage
from ..export.pages.geometryviewpage import GeometryViewPage
from ..export.api.ckanexporter import CKANExporter
from ..export.api.iiifexporter import IIIFAPIExporter
from ..export.api.ogcapifeaturesexporter import OGCAPIFeaturesExporter
from ..export.data.exporter.exporterutils import ExporterUtils
from ..layerutils import LayerUtils
from ..sparqlutils import SPARQLUtils
from ..export.data.exporter.rdf.vowlexporter import OWL2VOWL
from ..export.data.exporter.rdf.voidexporter import VoidExporter

listthreshold=5
maxlistthreshold=1500

jsonindent=2

templatepath=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources/html/"))

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

featurecollectionspaths={}
iiifmanifestpaths={"default":[]}
imagetoURI={}

templates=DocDefaults.templates

def resolveTemplate(templatename):
    print(templatepath+"/"+templatename)
    if os.path.exists(templatepath+"/"+templatename+"/templateconf.json"):
        with open(templatepath+"/"+templatename+"/templateconf.json", 'r') as f:
            templatefiles = json.load(f)
            for file in templatefiles:
                if os.path.exists(templatepath +"/"+templatename+"/"+ file):
                    with open(templatepath +"/"+templatename+"/"+ file["path"], 'r') as f:
                        if "name" in file:
                            templates[file["name"]]= f.read()
                        else:
                            templates[file] = f.read()
    elif os.path.exists(templatepath+"/"+templatename+"/templates/"):
        if os.path.exists(templatepath+"/"+templatename+"/templates/layouts/") and os.path.exists(templatepath+"/"+templatename+"/templates/includes/"):
            templates["includes"]={}
            templates["layouts"] = {}
            for filename in os.listdir(templatepath+"/"+templatename+"/templates/includes/"):
                if filename.endswith(".html") or filename.endswith(".css"):
                    with open(templatepath+"/"+templatename+"/templates/includes/"+filename, 'r') as f:
                        content=f.read()
                        templates["includes"][filename.replace(".html","")] = content
                        templates[filename.replace(".html", "")] = content
            for filename in os.listdir(templatepath + "/" + templatename + "/templates/layouts/"):
                if filename.endswith(".html") or filename.endswith(".css"):
                    with open(templatepath + "/" + templatename + "/templates/layouts/" + filename, 'r') as f:
                        content=f.read()
                        templates["layouts"][filename.replace(".html", "")] = content
                        templates[filename.replace(".html", "")] = content
        else:
            for filename in os.listdir(templatepath+"/"+templatename+"/templates/"):
                if filename.endswith(".html") or filename.endswith(".css"):
                    with open(templatepath+"/"+templatename+"/templates/"+filename, 'r') as f:
                        templates[filename.replace(".html","")] = f.read()
        return False
    return True


class OntDocGeneration:

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,createcollections,baselayers,tobeaddedPerInd,maincolor,tablecolor,progress,createIndexPages=True,nonNSPagesCBox=False,createMetadataTable=False,createVOWL=False,ogcapifeatures=False,iiif=False,ckan=False,imagemetadata=False,startconcept="",deployurl="",logoname="",offlinecompat=False,exports=["ttl","json"],templatename="default"):
        self.prefixes=prefixes
        self.prefixnamespace = prefixnamespace
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.modtime=None
        self.progress=progress
        self.baselayers=baselayers
        self.tobeaddedPerInd=tobeaddedPerInd
        self.logoname=logoname
        self.offlinecompat=offlinecompat
        self.exports=exports
        self.repository=None
        QgsMessageLog.logMessage("Exports: " + str(exports), "OntdocGeneration", Qgis.Info)
        self.startconcept = None
        if startconcept!="No Start Concept":
            self.startconcept=startconcept
        self.deploypath=deployurl
        self.ogcapifeatures=ogcapifeatures
        self.iiif=iiif
        self.ckan=ckan
        self.imagemetadata=imagemetadata
        self.createVOWL=createVOWL
        self.localOptimized=True
        self.geocache={}
        self.metadatatable=createMetadataTable
        self.generatePagesForNonNS=nonNSPagesCBox
        self.geocollectionspaths=[]
        self.templatename=templatename
        resolveTemplate(templatename)
        if offlinecompat:
            global htmltemplate
            htmltemplate = self.createOfflineCompatibleVersion(outpath, templates["htmltemplate"],templatepath,templatename)
            global maptemplate
            maptemplate = self.createOfflineCompatibleVersion(outpath, templates["maptemplate"],templatepath,templatename)
            global sparqltemplate
            sparqltemplate=self.createOfflineCompatibleVersion(outpath,templates["sparqltemplate"],templatepath,templatename)
        self.maincolorcode="#c0e2c0"
        self.tablecolorcode="#810"
        self.createColl=createcollections
        if maincolor!=None:
            self.maincolorcode=maincolor
        if tablecolor!=None:
            self.tablecolorcode=tablecolor
        self.license=license
        self.licenseuri=None
        self.datasettitle=""
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


    def createOfflineCompatibleVersion(self,outpath,myhtmltemplate,templatepath,templatename):
        #QgsMessageLog.logMessage("OUTPATH: "+str(outpath), "OntdocGeneration", Qgis.Info)
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
                    m=m.replace("\"","").replace("/>","")
                    m=m.replace(">","")
                    #QgsMessageLog.logMessage("Downloader: "+ m.replace("\"", "")+" - "+ str(outpath)+str(os.sep)+"js"+str(os.sep) + m[m.rfind("/") + 1:], "OntdocGeneration", Qgis.Info)
                    try:
                        g = urllib.request.urlopen(m.replace("\"", ""))
                        with open(outpath + str(os.sep)+"js"+str(os.sep) + m[m.rfind("/") + 1:], 'b+w') as f:
                            f.write(g.read())
                    except Exception as e:
                        QgsMessageLog.logMessage(
                            "Downloader: " + str(e),
                            "OntdocGeneration", Qgis.Info)
                        QgsMessageLog.logMessage(
                            "Checking for local version of JS file..... "+templatepath+"/"+templatename+"/js/lib/"+str(m[m.rfind("/")+1:])+": "+str(os.path.exists(templatepath+"/"+templatename+"/js/lib/"+str(m[m.rfind("/")+1:]))),
                            "OntdocGeneration", Qgis.Info)
                        if os.path.exists(templatepath+"/"+templatename+"/js/lib/"+str(m[m.rfind("/")+1:])):
                            QgsMessageLog.logMessage(
                                "Found local version of JS file and copying it to export..... ",
                                "OntdocGeneration", Qgis.Info)
                            shutil.copy(templatepath+"/"+templatename+"/js/lib/"+str(m[m.rfind("/")+1:]),outpath + str(os.sep)+"js"+str(os.sep) + m[m.rfind("/") + 1:])
                    #QgsMessageLog.logMessage("Downloader: "+m.replace("\"", "")+" - "+str(dl), "OntdocGeneration", Qgis.Info)
                    myhtmltemplate=myhtmltemplate.replace(m,"{{relativepath}}js/"+m[m.rfind("/")+1:])
            else:
                match=match.replace("\"","").replace(">","")
                #QgsMessageLog.logMessage("Downloader: "+ match.replace("\"", "")+" - "+ str(outpath) + str(os.sep)+"js"+str(os.sep)+ match[match.rfind("/") + 1:],
                #                         "OntdocGeneration", Qgis.Info)
                try:
                    g = urllib.request.urlopen(match.replace("\"", ""))
                    with open(outpath + str(os.sep)+"js"+str(os.sep) + match[match.rfind("/") + 1:], 'b+w') as f:
                        f.write(g.read())
                except Exception as e:
                    QgsMessageLog.logMessage(
                    "Downloader: " + str(e),
                    "OntdocGeneration", Qgis.Info)
                    if os.path.exists(templatepath + "/" + templatename + "/js/lib/" + str(match[match.rfind("/") + 1:])):
                        QgsMessageLog.logMessage(
                            "Found local version of JS file and copying it to export..... ",
                            "OntdocGeneration", Qgis.Info)
                        shutil.copy(templatepath + "/" + templatename + "/js/lib/" + str(match[match.rfind("/") + 1:]),
                                    outpath + str(os.sep) + "js" + str(os.sep) + match[match.rfind("/") + 1:])
                #dl = QgsFileDownloader(QUrl(match.replace("\"","")), outpath + str(os.sep)+"js"+str(os.sep) + match[match.rfind("/") + 1:])
                #dl.downloadError.connect(self.downloadFailed)
                #QgsMessageLog.logMessage("Downloader: " +match.replace("\"","")+" - "+ str(dl), "OntdocGeneration", Qgis.Info)
                myhtmltemplate=myhtmltemplate.replace(match,"{{relativepath}}js/"+match[match.rfind("/")+1:])
        matched=re.findall(r'href="(http.*.css)"',myhtmltemplate)
        for match in matched:
            print(match.replace("\"",""))
            match=match.replace("\"","").replace("/>","")
            match=match.replace(">","")
            #QgsMessageLog.logMessage("Downloader: " +match.replace("\"", "")+" - "+ str(outpath) +str(os.sep)+"css"+str(os.sep)+ match[match.rfind("/") + 1:],
            #                         "OntdocGeneration", Qgis.Info)
            try:
                g = urllib.request.urlopen(match.replace("\"", ""))
                with open(outpath +str(os.sep)+"css"+str(os.sep)+ match[match.rfind("/") + 1:], 'b+w') as f:
                    f.write(g.read())
            except Exception as e:
                QgsMessageLog.logMessage(
                    "Downloader: " + str(e),
                    "OntdocGeneration", Qgis.Info)
                if os.path.exists(templatepath + "/" + templatename + "/css/lib/" + str(match[match.rfind("/") + 1:])):
                    QgsMessageLog.logMessage(
                        "Found local version of CSS file and copying it to export..... ",
                        "OntdocGeneration", Qgis.Info)
                    shutil.copy(templatepath + "/" + templatename + "/css/lib/" + str(match[match.rfind("/") + 1:]),
                                outpath + str(os.sep) + "css" + str(os.sep) + match[match.rfind("/") + 1:])
            #dl = QgsFileDownloader(QUrl(match.replace("\"", "")), outpath +str(os.sep)+"css"+str(os.sep)+ match[match.rfind("/") + 1:])
            #dl.downloadError.connect(self.downloadFailed)
            #QgsMessageLog.logMessage("Downloader: " +match.replace("\"", "")+" - "+str(dl), "OntdocGeneration", Qgis.Info)
            myhtmltemplate=myhtmltemplate.replace(match,"{{relativepath}}css/"+match[match.rfind("/")+1:])
        return myhtmltemplate

    def processLicense(self):
        #QgsMessageLog.logMessage(str(self.license), "OntdocGeneration", Qgis.Info)
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
        if currentsubject==None and allsubjects==None:
            self.progress.setLabelText(newtext + processsubject)
        else:
            self.progress.setLabelText(newtext + "\n Processed: "+str(currentsubject)+" of "+str(allsubjects)+" "+str(processsubject)+"... ("+str(round(((currentsubject/allsubjects)*100),0))+"%)")

    def replaceStandardVariables(self,template,subject,checkdepth,indexpage):
        template=template.replace("{{indexpage}}",str(indexpage)).replace("{{subject}}",str(subject)).replace("{{relativedepth}}",str(checkdepth))\
            .replace("{{versionurl}}",DocConfig.versionurl).replace("{{version}}",DocConfig.version).replace("{{deploypath}}",self.deploypath)\
            .replace("{{publishingorg}}",self.publishingorg).replace("{{publisher}}",self.publisher).replace("{{datasettitle}}",self.datasettitle)\
            .replace("{{logo}}",self.logoname)
        return template

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.outpath
        corpusid=self.namespaceshort.replace("#","")
        if self.datasettitle==None or self.datasettitle=="":
            self.datasettitle=corpusid+"_dataset"
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem={}
        voidstats = {"http://rdfs.org/ns/void#classes": 0, "http://rdfs.org/ns/void#entities": 0,
                     "http://rdfs.org/ns/void#distinctObjects": 0, "http://rdfs.org/ns/void#distinctSubjects": 0,
                     "http://rdfs.org/ns/void#properties": 0, "http://rdfs.org/ns/void#triples": 0}
        self.updateProgressBar(None, None, "Creating classtree and search index")
        if self.createVOWL:
            vowlinstance=OWL2VOWL()
            vowlinstance.convertOWL2VOWL(self.graph,outpath)
        curlicense=self.processLicense()
        self.licensehtml=curlicense
        res=self.getPropertyRelations(self.graph, outpath)
        voidstats["http://rdfs.org/ns/void#properties"]=res["preds"]
        voidstats["http://ldf.fi/void-ext#propertyClasses"] = res["predclasses"]
        voidstats["http://ldf.fi/void-ext#averagePropertyIRILength"] = res["avgpredlen"]
        voidstats["http://rdfs.org/ns/void#distinctObjects"]=res["objs"]
        predmap=res["predmap"]
        voidds=prefixnamespace+self.datasettitle
        if self.createColl:
            self.graph=self.createCollections(self.graph,prefixnamespace)
        if self.logoname!=None and self.logoname!="":
            if not os.path.isdir(outpath+"/logo/"):
                os.mkdir(outpath+"/logo/")
            shutil.copy(self.logoname,outpath+"/logo/logo."+self.logoname[self.logoname.rfind("."):])
            self.logoname=outpath+"/logo/logo."+self.logoname[self.logoname.rfind("."):]
        subjectstorender = set()
        subjectstorender.add(URIRef(voidds))
        nonnscount={}
        nscount = {}
        instancecount={}
        literaltypes={}
        blanknodes=set()
        literallangs=set()
        literals=set()
        irirefs=0
        literallength=0
        literalcount=0
        subjectlength=0
        objectlength=0
        subjectcounter=0
        objectcounter=0
        for sub in self.graph.subjects(None,None,True):
            #QgsMessageLog.logMessage(str(prefixnamespace)+" "+str(sub), "OntdocGeneration", Qgis.Info)
            if (prefixnamespace in sub and (isinstance(sub, URIRef)) or isinstance(sub, BNode)):
                subjectstorender.add(sub)
                label = DocUtils.shortenURI(str(sub))
                restriction = False
                ns = DocUtils.shortenURI(str(sub), True)
                if ns not in nscount:
                    nscount[ns] = 0
                nscount[ns] += 1
                self.graph.add((sub, URIRef("http://rdfs.org/ns/void#inDataset"),
                                URIRef(voidds)))
                if isinstance(sub, BNode):
                    blanknodes.add(str(sub))
                irirefs += 1
                subjectcounter += 1
                subjectlength += len(str(sub))
                for tup in self.graph.predicate_objects(sub):
                    if isinstance(tup[1], Literal):
                        if tup[1].datatype != None:
                            if str(tup[1].datatype) not in literaltypes:
                                literaltypes[str(tup[1].datatype)] = set()
                            literaltypes[str(tup[1].datatype)].add(str(tup[0]))
                        if tup[1].language != None:
                            literallangs.add(str(tup[1].language))
                        literallength += len(str(tup[1]))
                        literals.add(str(tup[1]))
                        literalcount += 1
                    elif isinstance(tup[1], BNode):
                        blanknodes.add(str(tup[1]))
                    else:
                        objectlength += len(str(tup[1]))
                        objectcounter += 1
                        irirefs += 1
                        ns = DocUtils.shortenURI(str(tup[1]), True)
                        if ns not in nscount:
                            nscount[ns] = 0
                        nscount[ns] += 1
                    if str(tup[0]) in SPARQLUtils.labelproperties:
                        labeltouri[str(tup[1])] = str(sub)
                        uritolabel[str(sub)] = {"label": str(tup[1])}
                        label = str(tup[1])
                    elif str(tup[0]) == self.typeproperty:
                        if str(tup[1]) not in instancecount:
                            instancecount[str(tup[1])] = 0
                        instancecount[str(tup[1])] += 1
                    elif str(tup[1]) == "http://www.w3.org/2002/07/owl#Restriction":
                        restriction = True
                    elif str(tup[0]) == "http://www.w3.org/2000/01/rdf-schema#subClassOf":
                        ressubcls = str(tup[1])
                    if isinstance(tup[1], URIRef) and prefixnamespace not in str(tup[1]):
                        ns = DocUtils.shortenURI(str(tup[1]), True)
                        if ns not in nscount:
                            nscount[ns]=0
                        nscount[ns]+=1
                        if str(tup[0]) not in nonnscount:
                            nonnscount[str(tup[0])] = {}
                        if ns not in nonnscount[str(tup[0])]:
                            nonnscount[str(tup[0])][ns] = 0
                        nonnscount[str(tup[0])][ns] += 1
                if isinstance(sub, BNode) and restriction:
                    self.graph.add((sub, URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
                                    Literal(label + " [Restriction]", lang="en")))
            voidstats["http://rdfs.org/ns/void#distinctSubjects"] += 1
        voidstats["http://rdfs.org/ns/void#entities"] = len(subjectstorender)
        voidstats["http://ldf.fi/void-ext#languages"] = len(literallangs)
        voidstats["http://ldf.fi/void-ext#distinctBlankNodes"] = len(blanknodes)
        voidstats["http://ldf.fi/void-ext#datatypes"] = len(literaltypes.keys())
        voidstats["http://ldf.fi/void-ext#distinctLiterals"] = len(literals)
        voidstats["http://ldf.fi/void-ext#averageSubjectIRILength"] = int(subjectlength / subjectcounter)
        voidstats["http://ldf.fi/void-ext#averageObjectIRILength"] = int(objectlength / objectcounter)
        voidstats["http://ldf.fi/void-ext#averageLiteralLength"] = int(literallength / literalcount)
        voidstats["http://ldf.fi/void-ext#distinctIRIReferences"] = voidstats["http://rdfs.org/ns/void#distinctSubjects"] + res["preds"] + res["objs"]
        voidstats["http://ldf.fi/void-ext#distinctRDFNodes"] = len(blanknodes) + len(literals) + voidstats["http://ldf.fi/void-ext#distinctIRIReferences"]
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
        if self.offlinecompat:
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
        voidstats["http://rdfs.org/ns/void#classes"]=len(classidset)
        voidstats["http://rdfs.org/ns/void#triples"] = len(self.graph)
        voidgraph = VoidExporter.createVoidDataset(self.datasettitle, prefixnamespace,self.namespaceshort, self.repository, self.deploypath, self.outpath,
                                                   self.licenseuri, self.modtime, self.labellang, voidstats,
                                                   subjectstorender, self.prefixes, tree, predmap, nonnscount, nscount,
                                                   instancecount, self.startconcept)
        self.voidstatshtml = VoidExporter.toHTML(voidstats, self.deploypath)
        self.graph+=voidgraph["graph"]
        subjectstorender.update(voidgraph["subjects"])
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(templates["stylesheet"].replace("%%maincolorcode%%",self.maincolorcode).replace("%%tablecolorcode%%",self.tablecolorcode))
            f.close()
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(templates["startscripts"].replace("{{baseurl}}",prefixnamespace))
            f.close()
        with open(outpath + "epsgdefs.js", 'w', encoding='utf-8') as f:
            f.write(templates["epsgdefs"])
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
            paths=DocUtils.processSubjectPath(outpath,paths,path,self.graph)
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
            paths=DocUtils.processSubjectPath(outpath,paths,path,self.graph)
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
        classlist=self.assignGeoClassesToTree(tree)
        if self.generatePagesForNonNS:
            self.getSubjectPagesForNonGraphURIs(nonnsmap, self.graph, prefixnamespace, corpusid, outpath, self.license,prefixnamespace,uritotreeitem,labeltouri)
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=jsonindent))
            f.close()
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        IIIFAPIExporter.generateIIIFAnnotations(outpath,imagetoURI)
        if self.createIndexPages:
            indpcounter=0
            for path in paths:
                if indpcounter % 10 == 0:
                    self.updateProgressBar(indpcounter, len(paths), "Creating Index Pages")
                subgraph=Graph(bind_namespaces="rdflib")
                #QgsMessageLog.logMessage("BaseURL " + str(outpath)+" "+str(path)+" "+outpath + corpusid + '_search.js', "OntdocGeneration", Qgis.Info)
                checkdepth = DocUtils.checkDepthFromPath(path, outpath, path)-1
                sfilelink=DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + '_search.js',False)
                classtreelink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + "_classtree.js",False)
                stylelink =DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,"style.css",False)
                scriptlink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "startscripts.js", False)
                epsgdefslink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "epsgdefs.js", False)
                vowllink = DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "vowl_result.js", False)
                nslink=prefixnamespace+str(self.getAccessFromBaseURL(str(outpath),str(path)))
                for sub in subjectstorender:
                    if nslink in sub:
                        for tup in self.graph.predicate_objects(sub):
                            subgraph.add((sub, tup[0], tup[1]))
                for ex in self.exports:
                    if ex in ExporterUtils.exportToFunction:
                        if ex not in ExporterUtils.rdfformats:
                            with open(path + "index."+str(ex).lower(), 'w', encoding='utf-8') as f:
                                ExporterUtils.exportToFunction[ex](subgraph,f,subjectstorender,classlist,ex.lower())
                                f.close()
                        else:
                            ExporterUtils.exportToFunction[ex](subgraph,path + "index."+str(ex).lower(),subjectstorender,classlist,ex.lower())
                #QgsMessageLog.logMessage("BaseURL " + nslink,"OntdocGeneration", Qgis.Info)
                relpath=DocUtils.generateRelativePathFromGivenDepth(checkdepth)
                indexhtml = templates["htmltemplate"].replace("{{iconprefixx}}",(relpath+"icons/" if self.offlinecompat else "")).replace("{{logo}}",self.logoname).replace("{{relativepath}}",relpath).replace("{{relativedepth}}", str(checkdepth)).replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Index page for " + nslink).replace("{{title}}","Index page for <span property=\"http://rdfs.org/ns/void#uriSpace\" content=\""+str(nslink)+"\">" + str(nslink)+"</span>").replace("{{startscriptpath}}", scriptlink).replace("{{stylepath}}", stylelink).replace("{{epsgdefspath}}", epsgdefslink)\
                    .replace("{{classtreefolderpath}}",classtreelink).replace("{{baseurlhtml}}", nslink).replace("{{scriptfolderpath}}", sfilelink).replace("{{exports}}",templates["nongeoexports"]).replace("{{bibtex}}","").replace("{{versionurl}}",DocConfig.versionurl).replace("{{version}}",DocConfig.version).replace("{{subject}}",str(voidds)).replace("{{nonnslink}}","").replace("{{subjectencoded}}",urllib.parse.quote(str(voidds)))
                if nslink==prefixnamespace:
                    indexhtml=indexhtml.replace("{{indexpage}}","true")
                else:
                    indexhtml = indexhtml.replace("{{indexpage}}", "false")
                indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"+templates["vowltemplate"].replace("{{vowlpath}}", "minivowl_result.js")
                if self.startconcept != None and path == outpath and self.startconcept in uritotreeitem:
                    if self.createColl:
                        indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                     tree["types"][uritotreeitem[self.startconcept][-1]["type"]][
                                         "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + \
                                     uritotreeitem[self.startconcept][-1][
                                         "type"] + "\"/><a property=\"http://rdfs.org/ns/void#rootResource\" resource=\"" + str(
                            self.startconcept) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                            prefixnamespace, 0, str(self.startconcept), True) + "\">" + DocUtils.shortenURI(
                            self.startconcept) + "</a></p>"
                    else:
                        indexhtml += "<p>Start exploring the graph here: <img src=\"" + \
                                     tree["types"][uritotreeitem[self.startconcept][-1]["type"]][
                                         "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + \
                                     uritotreeitem[self.startconcept][-1][
                                         "type"] + "\"/><a property=\"http://rdfs.org/ns/void#rootResource\" resource=\"" + str(
                            self.startconcept) + "\" href=\"" + DocUtils.generateRelativeLinkFromGivenDepth(
                            prefixnamespace, 0, str(self.startconcept), True) + "\">" + DocUtils.shortenURI(
                            self.startconcept) + "</a></p>"
                indexhtml+="<table about=\""+str(voidds)+"\" typeof=\"http://rdfs.org/ns/void#Dataset\" property=\"http://rdfs.org/ns/void#dataDump\" resource=\""+str(self.deploypath+"/index.ttl")+"\" class=\"description\" style =\"height: 100%; overflow: auto\" border=1 id=indextable><thead><tr><th>Class</th><th>Number of instances</th><th>Instance Example</th></tr></thead><tbody>"
                for item in tree["core"]["data"]:
                    if (item["type"]=="geoclass" or item["type"]=="class" or item["type"]=="featurecollection" or item["type"]=="geocollection") and "instancecount" in item and item["instancecount"]>0:
                        exitem=None
                        for item2 in tree["core"]["data"]:
                            if item2["parent"]==item["id"] and (item2["type"]=="instance" or item2["type"]=="geoinstance") and nslink in item2["id"]:
                                checkdepth = DocUtils.checkDepthFromPath(path, prefixnamespace, item2["id"])-1
                                exitem="<td><img src=\""+tree["types"][item2["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item2["type"]+"\"/><a href=\""+DocUtils.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,str(re.sub("_suniv[0-9]+_","",item2["id"])),True)+"\">"+str(item2["text"])+"</a></td>"
                                break
                        if exitem!=None:
                            if self.createColl:
                                indexhtml += "<tr><td><img src=\"" + tree["types"][item["type"]][
                                    "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + item[
                                                 "type"] + "\"/><a property=\"http://rdfs.org/ns/void#exampleResource\" resource=\""+str(DocUtils.shortenURI(str(item["id"]))+"_collection/")+"\" href=\"" + DocUtils.shortenURI(
                                    str(item["id"])) + "_collection/index.html\" target=\"_blank\">" + str(
                                    item["text"]) + "</a></td>"
                            else:
                                indexhtml += "<tr><td><img src=\"" + tree["types"][item["type"]][
                                    "icon"] + "\" height=\"25\" width=\"25\" alt=\"" + item[
                                                 "type"] + "\"/><a property=\"http://rdfs.org/ns/void#exampleResource\" resource=\""+str(DocUtils.shortenURI(str(item["id"]))+"_collection/")+"\" href=\"" + str(
                                    item["id"]) + "\" target=\"_blank\">" + str(item["text"]) + "</a></td>"
                            indexhtml+="<td property=\"http://rdfs.org/ns/void#classPartition\" typeof=\"http://rdfs.org/ns/void#Dataset\" resource=\""+str(voidds)+"_"+str(DocUtils.shortenURI(item["id"]))+"\"><span about=\""+str(voidds)+"_"+str(DocUtils.shortenURI(item["id"]))+"\" property=\"http://rdfs.org/ns/void#class\" resource=\""+str(item["id"])+"\"></span><span about=\""+str(voidds)+"_"+str(DocUtils.shortenURI(item["id"]))+"\" property=\"http://rdfs.org/ns/void#entities\" content=\""+str(item["instancecount"])+"\" datatype=\"http://www.w3.org/2001/XMLSchema#integer\">"+str(item["instancecount"])+"</td>"+exitem+"</tr>"
                indexhtml += "</tbody></table><script property=\"http://purl.org/dc/terms/modified\" content=\""+str(self.modtime)+"\" datatype=\"http://www.w3.org/2001/XMLSchema#dateTime\">$('#indextable').DataTable();</script>"
                indexhtml+=templates["footer"].replace("{{license}}",curlicense).replace("{{exports}}",templates["nongeoexports"]).replace("{{bibtex}}","")
                #QgsMessageLog.logMessage(path)
                indpcounter+=1
                with open(path + "index.html", 'w', encoding='utf-8') as f:
                    f.write(indexhtml)
                    f.close()
            sparqlhtml = templates["htmltemplate"].replace("{{indexpage}}", "false").replace("{{iconprefixx}}", (
                relpath + "icons/" if self.offlinecompat else "")).replace("{{deploypath}}", self.deploypath).replace(
                "{{datasettitle}}", self.datasettitle).replace("{{logo}}", "").replace("{{baseurl}}",
                                                                                       prefixnamespace).replace(
                "{{relativedepth}}", "0").replace("{{proprelationpath}}", "proprelations.js").replace("{{relativepath}}", "").replace("{{toptitle}}",
                                                                                   "SPARQL Query Editor").replace(
                "{{title}}", "SPARQL Query Editor").replace("{{startscriptpath}}", scriptlink).replace("{{stylepath}}",
                                                                                                       stylelink).replace(
                "{{vowlpath}}", vowllink) \
                .replace("{{classtreefolderpath}}", classtreelink).replace("{{baseurlhtml}}", "").replace("{{subject}}",
                                                                                                          "").replace(
                "{{nonnslink}}", "").replace("{{scriptfolderpath}}", sfilelink).replace("{{exports}}",
                                                                                        templates["nongeoexports"]).replace(
                "{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace("{{bibtex}}", "")
            sparqlhtml += templates["sparqltemplate"].replace("{{relativepath}}","")
            sparqlhtml += templates["footer"].replace("{{license}}", curlicense).replace("{{exports}}", templates["nongeoexports"]).replace(
                "{{bibtex}}", "")
            with open(outpath + "sparql.html", 'w', encoding='utf-8') as f:
                f.write(sparqlhtml)
                f.close()
        if len(iiifmanifestpaths["default"])>0:
            IIIFAPIExporter.generateIIIFCollections(self.outpath,self.deploypath,iiifmanifestpaths["default"],prefixnamespace)
            IIIFAPIExporter.generateImageGrid(self.deploypath, iiifmanifestpaths["default"], templates["imagegrid"], outpath+"imagegrid.html")
        if len(featurecollectionspaths)>0 and self.ckan:
            CKANExporter.generateCKANCollection(outpath,featurecollectionspaths)
        if len(featurecollectionspaths)>0:
            relpath=DocUtils.generateRelativePathFromGivenDepth(0)
            indexhtml = templates["htmltemplate"].replace("{{iconprefixx}}",(relpath+"icons/" if self.offlinecompat else "")).replace("{{logo}}",self.logoname).replace("{{relativepath}}",relpath).replace("{{relativedepth}}","0").replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Feature Collection Overview").replace("{{title}}","Feature Collection Overview").replace("{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{epsgdefspath}}", "epsgdefs.js")\
                    .replace("{{classtreefolderpath}}",corpusid + "_classtree.js").replace("{{baseurlhtml}}", "").replace("{{scriptfolderpath}}", corpusid + '_search.js').replace("{{exports}}",templates["nongeoexports"])
            indexhtml = indexhtml.replace("{{indexpage}}", "true")
            OGCAPIFeaturesExporter.generateOGCAPIFeaturesPages(outpath,self.deploypath, featurecollectionspaths, prefixnamespace, self.ogcapifeatures,
                                             True)
            indexhtml += "<p>This page shows feature collections present in the linked open data export</p>"
            indexhtml+="<script src=\"features.js\"></script>"
            indexhtml+=templates["maptemplate"].replace("var ajax=true","var ajax=false").replace("var featurecolls = {{myfeature}}","").replace("{{relativepath}}",DocUtils.generateRelativePathFromGivenDepth(0)).replace("{{baselayers}}",json.dumps(self.baselayers).replace("{{epsgdefspath}}", "epsgdefs.js").replace("{{dateatt}}", ""))
            indexhtml += templates["footer"].replace("{{license}}", curlicense).replace("{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}","")
            with open(outpath + "featurecollections.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()

    def getPropertyRelations(self, graph, outpath):
        predicates = {}
        predicatecounter = 0
        predicatelength = 0
        predicateClasses = 0
        objects = set()
        for pred in graph.predicates(None, None, True):
            predicates[pred] = {"from": set(), "to": set(), "triples": 0}
            for tup in graph.subject_objects(pred):
                if str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    predicateClasses += 1
                for item in graph.objects(tup[0], URIRef(self.typeproperty), True):
                    predicates[pred]["from"].add(item)
                for item in graph.objects(tup[1], URIRef(self.typeproperty), True):
                    predicates[pred]["to"].add(item)
                objects.add(str(tup[1]))
                predicates[pred]["triples"] += 1
            predicates[pred]["from"] = list(predicates[pred]["from"])
            predicates[pred]["to"] = list(predicates[pred]["to"])
            predicatecounter += 1
            predicatelength += len(str(pred))
        if self.createVOWL:
            OWL2VOWL().convertOWL2MiniVOWL(graph, outpath, "minivowl_result.js", predicates)
        with open(outpath + "proprelations.js", 'w', encoding='utf-8') as f:
            f.write("var proprelations=" + json.dumps(predicates))
            f.close()
        return {"preds": predicatecounter, "avgpredlen": str(int(predicatelength / predicatecounter)),
                "predclasses": predicateClasses, "objs": len(objects), "predmap": predicates}

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
            colluri=namespace+DocUtils.shortenURI(cls)+"_collection"
            collrelprop="http://www.w3.org/2000/01/rdf-schema#member"
            if classToFColl[cls]==len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection"), URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(self.typeproperty),URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection")))
            elif classToGeoColl[cls]==len(classToInstances[cls]):
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection"),URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection"), URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),URIRef("http://www.opengis.net/ont/geosparql#SpatialObjectCollection")))
                graph.add((URIRef(colluri), URIRef(self.typeproperty),URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection")))
            elif cls in DocConfig.classToCollectionClass:
                if "super" in DocConfig.classToCollectionClass[cls]:
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["class"]),
                               URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                               URIRef(DocConfig.classToCollectionClass[cls]["super"])))
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["super"]),
                               URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                               URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                else:
                    graph.add((URIRef(DocConfig.classToCollectionClass[cls]["class"]),
                               URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"),
                               URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
                graph.add((URIRef(colluri),URIRef(self.typeproperty),URIRef(DocConfig.classToCollectionClass[cls]["class"])))
                collrelprop=DocConfig.classToCollectionClass[cls]["prop"]
            else:
                graph.add((URIRef(colluri),URIRef(self.typeproperty),URIRef("http://www.w3.org/2004/02/skos/core#Collection")))
            graph.add((URIRef(colluri),URIRef("http://www.w3.org/2000/01/rdf-schema#label"),Literal(str(DocUtils.shortenURI(cls))+" Instances Collection",lang="en")))
            for instance in classToInstances[cls]:
                graph.add((URIRef(colluri),URIRef(collrelprop),URIRef(instance)))
        return graph


    def getClassTree(self,graph, uritolabel,classidset,uritotreeitem):
        results = graph.query(self.preparedclassquery)
        ldcontext={"@context":{
                "@version":1.1,
                "foaf":"http://xmlns.com/foaf/0.1/",
                "ct":"http://purl.org/vocab/classtree/",
                "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
                "icon":"foaf:image",
                "id":"@id",
                "parent":"rdfs:subClassOf",
                "halfgeoclass":"ct:HalfGeoClass",
                "geoclass":{"@type":"ct:icontype","@id":"ct:GeoClass"},
                "collectionclass":{"@type":"ct:icontype","@id":"ct:CollectionClass"},
                "featurecollectionclass":{"@type":"ct:icontype","@id":"ct:FeatureCollectionClass"},
                "class":"owl:Class",
                "instance":"owl:NamedIndividual",
                "geoinstance":	{"@type":"ct:Icontype","@id":"ct:GeoNamedIndividual"},
                "text":"rdfs:label",
                "type":"ct:icontype",
                "types":"ct:icontypes",
                "core": {"@type":"ct:TreeConfig","@id":"@nest"},
                "data":{"@id":"ct:treeitem","@type":"ct:TreeItem"}
        }}
        tree = {"plugins": ["defaults","search", "sort", "state", "types", "contextmenu"], "search": {"show_only_matches":True},
        "types": {
            "class": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png"},
            "geoclass": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoclass.png"},
            "halfgeoclass": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/halfgeoclass.png"},
            "collectionclass": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/collectionclass.png"},
            "geocollection": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geometrycollection.png"},
            "featurecollection": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/featurecollection.png"},
            "instance": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/instance.png"},
            "geoinstance": {
                "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoinstance.png"}
        },
        "core": {"themes":{"responsive":True},"check_callback": True, "data": []}}
        tree["@context"]=ldcontext["@context"]
        result = []
        ress = {}
        for res in results:
            #QgsMessageLog.logMessage(str(res),"OntdocGeneration",Qgis.Info)
            if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
                if "_:" not in str(res["supertype"]) and str(res["supertype"]).startswith("http"):
                    ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
                else:
                    ress[str(res["subject"])] = {"super": None, "label": res["label"]}
        #QgsMessageLog.logMessage(ress)
        for cls in ress:
            for obj in graph.subjects(URIRef(self.typeproperty), URIRef(cls),True):
                res = DocUtils.replaceNameSpacesInLabel(self.prefixes,str(obj))
                if str(obj) in uritolabel:
                    restext= uritolabel[str(obj)]["label"] + " (" + DocUtils.shortenURI(str(obj)) + ")"
                    if res!=None:
                        restext=uritolabel[str(obj)]["label"] + " (" + res["uri"] + ")"
                else:
                    restext= DocUtils.shortenURI(str(obj))
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
            res = DocUtils.replaceNameSpacesInLabel(self.prefixes,str(cls))
            if ress[cls]["super"] == None:
                restext = DocUtils.shortenURI(str(cls))
                if res != None:
                    restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": "#","type": "class","text": restext,"data":{}})
                    uritotreeitem[str(cls)] = []
                    uritotreeitem[str(cls)].append(result[-1])
            else:
                if "label" in cls and cls["label"] != None:
                    restext = ress[cls]["label"] + " (" + DocUtils.shortenURI(str(cls)) + ")"
                    if res != None:
                        restext = ress[cls]["label"] + " (" + res["uri"] + ")"
                else:
                    restext = DocUtils.shortenURI(str(cls))
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
                    clsres = DocUtils.replaceNameSpacesInLabel(self.prefixes,str(ress[cls]["super"]))
                    if clsres!=None:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class",
                                   "text": DocUtils.shortenURI(str(ress[cls]["super"]))+" (" + clsres["uri"] + ")", "data": {}}
                    else:
                        theitem={"id": str(ress[cls]["super"]), "parent": "#","type": "class","text": DocUtils.shortenURI(str(ress[cls]["super"])),"data":{}}
                    uritotreeitem[str(ress[cls]["super"])].append(theitem)
                    result.append(theitem)
                classidset.add(str(ress[cls]["super"]))
            classidset.add(str(cls))
        if len(result)==0:
            classidset.add("http://www.w3.org/2002/07/owl#Thing")
            result.append({"id": "http://www.w3.org/2002/07/owl#Thing", "parent": "#", "type": "class", "text": "Thing (owl:Thing)", "data": {}})
            for obj in graph.subjects(True):
                result.append({"id":str(obj) , "parent": "http://www.w3.org/2002/07/owl#Thing", "type": "instance", "text": DocUtils.shortenURI(str(obj)),"data": {}})
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
        return classlist

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


    def resolveTimeObject(self, pred, obj, graph, timeobj):
        #QgsMessageLog.logMessage("RESOLVE TIME OBJECT: " +str(pred)+" " + str(obj), "OntdocGeneration", Qgis.Info)
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


    def timeObjectToHTML(self, timeobj):
        timeres = None
        if "begin" in timeobj and "end" in timeobj:
            timeres = str(timeobj["begin"]) + " "
            if str(timeobj["begin"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(self.prefixes,SPARQLUtils.timeliteraltypes[str(timeobj["begin"].datatype)])
            timeres += " - " + str(timeobj["end"])
            if str(timeobj["end"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(self.prefixes,SPARQLUtils.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "begin" in timeobj and not "end" in timeobj:
            timeres = str(timeobj["begin"])
            if str(timeobj["begin"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(self.prefixes,SPARQLUtils.timeliteraltypes[str(timeobj["begin"].datatype)])
        elif "begin" not in timeobj and "end" in timeobj:
            timeres = str(timeobj["end"])
            if str(timeobj["end"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(self.prefixes,SPARQLUtils.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "timepoint" in timeobj:
            timeres = timeobj["timepoint"]
            if str(timeobj["timepoint"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(self.prefixes,SPARQLUtils.timeliteraltypes[str(timeobj["timepoint"].datatype)])
        return timeres

    def resolveTimeLiterals(self, pred, obj, graph):
        timeobj = {}
        #QgsMessageLog.logMessage("RESOLVE TIME LITERALS: "+ str(pred)+" " + str(obj), "OntdocGeneration", Qgis.Info)
        if isinstance(obj, URIRef) and (str(pred) == "http://www.w3.org/2006/time#hasTime"):
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
                        str(pobj[0]) in SPARQLUtils.geoproperties or str(pobj[1].datatype) in SPARQLUtils.geoliteraltypes):
                    geojsonrep = LayerUtils.processLiteral(str(pobj[1]), str(pobj[1].datatype), "")
        return geojsonrep

    def searchObjectConnectionsForAggregateData(self,graph,object,pred,geojsonrep,foundmedia,imageannos,textannos,image3dannos,annobodies,timeobj,label,unitlabel,nonns,inverse):
        geoprop=False
        annosource=None
        incollection=False
        if pred in SPARQLUtils.geopointerproperties:
            geoprop=True
        if pred in SPARQLUtils.collectionrelationproperties:
            incollection=True
        foundval=None
        foundunit=None
        tempvalprop=None
        onelabel=None
        bibtex=None
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                if isinstance(tup[1],Literal) and tup[1].language==self.labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
            if pred=="http://www.w3.org/ns/oa#hasSelector" and tup[0]==URIRef(self.typeproperty) and (tup[1]==URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1]==URIRef("http://www.w3.org/ns/oa#WKTSelector")):
                for svglit in graph.objects(object,URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value")):
                    if "<svg" in str(svglit):
                        imageannos.append({"value":str(svglit),"bodies":[]})
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(svglit).upper()):
                        image3dannos.append({"value":str(svglit),"bodies":[]})
            elif pred == "http://www.w3.org/ns/oa#hasSelector" and tup[0] == URIRef(
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
            if str(tup[0]) == "http://www.w3.org/ns/oa#hasSource":
                annosource = str(tup[1])
                print("Found annosource "+str(tup[1])+" from "+str(object)+" Imageannos: "+str(len(imageannos)))
            if (pred == "http://purl.org/dc/terms/isReferencedBy" or pred=="http://purl.org/spar/cito/hasCitingEntity") and tup[0] == URIRef(self.typeproperty) and ("http://purl.org/ontology/bibo/" in str(tup[1])):
                bibtex=BibPage.resolveBibtexReference(graph.predicate_objects(object),object,graph)
            if pred in SPARQLUtils.timepointerproperties:
                timeobj=self.resolveTimeLiterals(pred,object,graph)
            if not nonns:
                geojsonrep=self.resolveGeoLiterals(tup[0], tup[1], graph, geojsonrep,nonns)
            if incollection and "<svg" in str(tup[1]):
                foundmedia["image"][str(tup[1])]={}
            elif incollection and "http" in str(tup[1]):
                ext="."+''.join(filter(str.isalpha,str(tup[1]).split(".")[-1]))
                if ext in SPARQLUtils.fileextensionmap:
                    foundmedia[SPARQLUtils.fileextensionmap[ext]][str(tup[1])]={}
            if not inverse and str(tup[0])=="http://www.w3.org/2000/01/rdf-schema#member" and (object, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),URIRef("http://www.w3.org/ns/sosa/ObservationCollection")) in graph:
                for valtup in graph.predicate_objects(tup[1]):
                    if str(valtup[0]) in SPARQLUtils.unitproperties:
                        foundunit = str(valtup[1])
                    if str(valtup[0]) in SPARQLUtils.valueproperties and isinstance(valtup[1], Literal):
                        foundval = str(valtup[1])
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
                            foundunit=str(valtup[1])
                        if str(valtup[0]) in SPARQLUtils.valueproperties and isinstance(valtup[1],Literal):
                            foundval=str(valtup[1])
            if str(tup[0]) in SPARQLUtils.unitproperties:
                foundunit=tup[1]
        if foundunit!=None and foundval!=None:
            if "http" in foundunit:
                unitlabel=str(foundval)+" "+DocUtils.createURILink(self.prefixes,str(foundunit))
            else:
                unitlabel=str(foundval)+" "+str(foundunit)
            if pred=="http://www.w3.org/ns/oa#hasBody":
                #print("ADD ANNO BODY: "+str({"value":foundval,"unit":foundunit,"type":"TextualBody","format":"text/plain"}))
                annobodies.append({"value":foundval,"unit":foundunit,"type":"TextualBody","format":"text/plain"})
        if foundunit == None and foundval != None:
            if "http" in foundval:
                unitlabel = "<a href=\"" + str(foundval) + "\">" + str(DocUtils.shortenURI(foundval)) + "</a>"
            else:
                unitlabel = str(foundval)
            if pred=="http://www.w3.org/ns/oa#hasBody":
                #print("ADD ANNO BODY: "+str({"value":foundval,"type":"TextualBody","format":"text/plain"}))
                annobodies.append({"value":foundval,"type":"TextualBody","format":"text/plain"})
        if annosource != None:
            for textanno in textannos:
                textanno["src"] = annosource
            for imganno in imageannos:
                imganno["src"] = annosource
            for imganno in image3dannos:
                imganno["src"] = annosource
        if label=="" and onelabel!=None:
            label=onelabel
        return {"geojsonrep":geojsonrep,"label":label,"unitlabel":unitlabel,"foundmedia":foundmedia,"imageannos":imageannos,"textannos":textannos,"image3dannos":image3dannos,"annobodies":annobodies,"bibtex":bibtex,"timeobj":timeobj}


    def createHTMLTableValueEntry(self,subject,pred,object,ttlf,graph,baseurl,checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos,annobodies,dateprops,inverse,nonns):
        tablecontents=""
        label=""
        bibtex = None
        timeobj=None
        #QgsMessageLog.logMessage("TIME OBJ CREATEHTMLTABLEVALENTRY: "+str(timeobj), "OntdocGeneration", Qgis.Info)
        if isinstance(object,URIRef) or isinstance(object,BNode):
            if ttlf != None:
                ttlf.add((subject,URIRef(pred),object))
            label = ""
            unitlabel=""
            mydata=self.searchObjectConnectionsForAggregateData(graph,object,pred,geojsonrep,foundmedia,imageannos,textannos,image3dannos,annobodies,timeobj,label,unitlabel,nonns,inverse)
            label=mydata["label"]
            if label=="":
                label=str(DocUtils.shortenURI(str(object)))
            geojsonrep=mydata["geojsonrep"]
            foundmedia=mydata["foundmedia"]
            imageannos=mydata["imageannos"]
            textannos=mydata["textannos"]
            image3dannos=mydata["image3dannos"]
            unitlabel=mydata["unitlabel"]
            bibtex=mydata["bibtex"]
            timeobj=mydata["timeobj"]
            #QgsMessageLog.logMessage("TIME OBJ CREATEHTMLTABLEVALENTRY AFTER AGG: " + str(timeobj), "OntdocGeneration", Qgis.Info)
            annobodies=mydata["annobodies"]
            if inverse:
                rdfares = " about=\"" + str(object) + "\" resource=\"" + str(subject) + "\""
            else:
                rdfares = "resource=\"" + str(object) + "\""
            if baseurl in str(object) or isinstance(object,BNode):
                rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,str(object),True)
                tablecontents += "<span><a property=\"" + str(pred) + "\" "+rdfares+" href=\"" + rellink + "\">"+ label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(DocUtils.shortenURI(str(object))) + ")</span></a>"
                if bibtex != None:
                    tablecontents += "<details><summary>[BIBTEX]</summary><pre>" + str(bibtex) + "</pre></details>"
            else:
                res = DocUtils.replaceNameSpacesInLabel(self.prefixes,str(object))
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
                    rellink = DocUtils.generateRelativeLinkFromGivenDepth(str(baseurl), checkdepth,
                                                                      str(baseurl) + "nonns_" + DocUtils.shortenURI(
                                                                          str(object)), False)
                    tablecontents+=" <a href=\""+rellink+".html\">[x]</a>"
            if unitlabel!="":
                tablecontents+=" <span style=\"font-weight:bold\">["+str(unitlabel)+"]</span>"
            #QgsMessageLog.logMessage("TIME OBJ CREATEHTMLTABLEVALENTRY AFTER AGG BEFORE TOHTML: " + str(timeobj), "OntdocGeneration",
            #                         Qgis.Info)
            if timeobj!=None:
                res=str(self.timeObjectToHTML(timeobj))
                if res!="None":
                    tablecontents+=" <span style=\"font-weight:bold\">["+str(res)+"]</span>"
                    dateprops=timeobj
            tablecontents+="</span>"
        else:
            label=str(object)
            if ttlf != None:
                ttlf.add((subject, URIRef(pred), object))
            if isinstance(object, Literal) and object.datatype != None:
                res = DocUtils.replaceNameSpacesInLabel(self.prefixes,str(object.datatype))
                objstring=str(object).replace("<", "&lt").replace(">", "&gt;")
                if str(object.datatype)=="http://www.w3.org/2001/XMLSchema#anyURI":
                    objstring="<a href=\""+str(object)+"\">"+str(object)+"</a>"
                if str(object.datatype) in SPARQLUtils.timeliteraltypes and dateprops!=None and DocUtils.shortenURI(str(pred),True) not in SPARQLUtils.metadatanamespaces and str(pred) not in dateprops:
                    dateprops.append(str(pred))
                if res != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + self.truncateValue(objstring) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + res["uri"]+ "</a>)</small></span>"
                else:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + self.truncateValue(objstring) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + DocUtils.shortenURI(str(object.datatype)) + "</a>)</small></span>"
                geojsonrep=self.resolveGeoLiterals(URIRef(pred), object, graph, geojsonrep,nonns,subject)
            else:
                if object.language != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\" xml:lang=\"" + str(object.language) + "\">" + self.truncateValue(str(object).replace("<", "&lt").replace(">", "&gt;")) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">rdf:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/"+str(object.language)+"\" target=\"_blank\">iso6391:" + str(object.language) + "</a>)</small></span>"
                else:
                    tablecontents += self.detectStringLiteralContent(pred,object)
        return {"html":tablecontents,"geojson":geojsonrep,"foundmedia":foundmedia,"imageannos":imageannos,"textannos":textannos,"image3dannos":image3dannos,"annobodies":annobodies,"label":label,"timeobj":dateprops}

    def truncateValue(self,value,limit=150):
        if len(value)>limit:
            return "<details><summary>"+value[0:limit]+"</summary>"+str(value[limit:])+"</details>"
        return value

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
        label=DocUtils.getLabelForObject(URIRef(tup), graph,self.labellang)
        tablecontents += "<td class=\"property\">"
        if reverse:
            tablecontents+="Is "
        if baseurl in str(tup):
            rellink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth,str(tup),True)
            tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span>"
        else:
            res = DocUtils.replaceNameSpacesInLabel(self.prefixes,tup)
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
        #QgsMessageLog.logMessage("Subjectpages " + str(uristorender), "OntdocGeneration", Qgis.Info)
        nonnsuris=len(uristorender)
        counter=0
        for uri in uristorender:
            label=""
            for tup in graph.predicate_objects(URIRef(uri)):
                if str(tup[0]) in SPARQLUtils.labelproperties:
                    label = str(tup[1])
            if uri in uritotreeitem:
                res = DocUtils.replaceNameSpacesInLabel(self.prefixes,str(uri))
                label = DocUtils.getLabelForObject(URIRef(str(uri)), graph, self.labellang)
                if res != None and label != "":
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
            self.createHTML(outpath+"nonns_"+DocUtils.shortenURI(uri)+".html", None, URIRef(uri), baseurl, graph.subject_predicates(URIRef(uri),True), graph, str(corpusid) + "_search.js", str(corpusid) + "_classtree.js", None, self.license, None, Graph(),uristorender,True,label)
            counter+=1

    def polygonToPath(self, svg):
        svg = svg.replace("<polygon", "<path").replace("points=\"", "d=\"M").replace("\"></polygon>", " Z\"></polygon>")
        return svg.replace("<svg>",
                           "<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")


    def getAccessFromBaseURL(self,baseurl,savepath):
        #QgsMessageLog.logMessage("Checkdepth: " + baseurl+" "+savepath.replace(baseurl, ""), "OntdocGeneration", Qgis.Info)
        return savepath.replace(baseurl, "")

    def createHTML(self,savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,uritotreeitem,curlicense,subjectstorender,postprocessing,nonnsmap=None,nonns=False,foundlabel=""):
        tablecontents = ""
        metadatatablecontents=""
        geojsonrep=None
        epsgcode=""
        foundmedia={"audio":{},"video":{},"image":{},"mesh":{}}
        savepath = savepath.replace("\\", "/")
        checkdepth=0
        if not nonns:
            checkdepth=DocUtils.checkDepthFromPath(savepath, baseurl, subject)
        logo=""
        if self.logoname!=None and self.logoname!="":
            logo="<img src=\""+self.logoname+"\" alt=\"logo\" width=\"25\" height=\"25\"/>&nbsp;&nbsp;"
        textannos = []
        foundvals=set()
        imageannos=[]
        image3dannos=[]
        annobodies=[]
        predobjmap={}
        curtypes=set()
        comment={}
        parentclass=None
        inverse=False
        dateprops = []
        timeobj=None
        if uritotreeitem!=None and str(subject) in uritotreeitem and uritotreeitem[str(subject)][-1]["parent"].startswith("http"):
            parentclass=str(uritotreeitem[str(subject)][-1]["parent"])
            if parentclass not in uritotreeitem:
                uritotreeitem[parentclass]=[{"id": parentclass, "parent": "#","type": "class","text": DocUtils.shortenURI(str(parentclass)),"data":{}}]
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
        collections=set()
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
                if self.metadatatable and tup not in SPARQLUtils.labelproperties and DocUtils.shortenURI(str(tup),True) in SPARQLUtils.metadatanamespaces:
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
                if str(tup) == self.typeproperty:
                    for tp in predobjmap[tup]:
                        thetypes.add(str(tp))
                        curtypes.add(str(tp))
                        if str(tp) in SPARQLUtils.collectionclasses:
                            uritotreeitem[str(tp)][-1]["instancecount"] += 1
                            collections.add(SPARQLUtils.collectionclasses[str(tp)])
                        if str(tp) in DocConfig.bibtextypemappings:
                            itembibtex="<details><summary>[BIBTEX]</summary><pre>"+str(BibPage.resolveBibtexReference(graph.predicate_objects(subject),subject,graph))+"</pre></details>"
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
                    if len(predobjmap[tup]) > listthreshold:
                        thetable+="<details><summary>"+str(len(predobjmap[tup]))+" values</summary>"
                    if len(predobjmap[tup])>1:
                        thetable+="<ul>"
                    labelmap={}
                    itemcounter = 0
                    for item in predobjmap[tup]:
                        if itemcounter >= maxlistthreshold:
                            break
                        if ("POINT" in str(item).upper() or "POLYGON" in str(item).upper() or "LINESTRING" in str(item).upper()) and tup in SPARQLUtils.valueproperties and self.typeproperty in predobjmap and URIRef("http://www.w3.org/ns/oa#WKTSelector") in predobjmap[self.typeproperty]:
                            image3dannos.append(str(item))
                        elif "<svg" in str(item):
                            foundmedia["image"][str(item)]={}
                        elif "http" in str(item):
                            if isinstance(item,Literal):
                                ext = "." + ''.join(filter(str.isalpha, str(item.value).split(".")[-1]))
                            else:
                                ext = "." + ''.join(filter(str.isalpha, str(item).split(".")[-1]))
                            if ext in SPARQLUtils.fileextensionmap:
                                foundmedia[SPARQLUtils.fileextensionmap[ext]][str(item)]={}
                        elif tup in SPARQLUtils.valueproperties:
                            foundvals.add(str(item))
                        res=self.createHTMLTableValueEntry(subject, tup, item, ttlf, graph,
                                              baseurl, checkdepth,geojsonrep,foundmedia,imageannos,textannos,image3dannos,annobodies,dateprops,inverse,nonns)
                        geojsonrep = res["geojson"]
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        textannos=res["textannos"]
                        image3dannos=res["image3dannos"]
                        annobodies = res["annobodies"]
                        # print("GOT ANNO BODIES "+str(annobodies))
                        if res["timeobj"] != None and res["timeobj"] != []:
                            # print("RESTIMEOBJ: "+str(timeobj))
                            timeobj = res["timeobj"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        if len(predobjmap[tup]) > 1:
                            labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                        else:
                            labelmap[res["label"]] += str(res["html"])
                    for lab in sorted(labelmap):
                        thetable+=str(labelmap[lab])
                    if len(predobjmap[tup]) >= maxlistthreshold:
                        tablecontents += "<li>(...)</li>"
                    if len(predobjmap[tup])>1:
                        thetable+="</ul>"
                    if len(predobjmap[tup]) > listthreshold:
                        thetable+="</details>"
                    thetable+="</td>"
                else:
                    thetable += "<td class=\"wrapword\"></td>"
                thetable += "</tr>"
                if tup not in SPARQLUtils.labelproperties and DocUtils.shortenURI(str(tup), True) in SPARQLUtils.metadatanamespaces:
                    metadatatablecontents=thetable
                else:
                    tablecontents=thetable
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
                tablecontentcounter+=1
                if tablecontentcounter%2==0:
                    tablecontents += "<tr class=\"odd\">"
                else:
                    tablecontents += "<tr class=\"even\">"
                tablecontents=self.formatPredicate(tup, baseurl, checkdepth, tablecontents, graph,True)
                if len(subpredsmap[tup]) > 0:
                    tablecontents += "<td class=\"wrapword\">"
                    if len(subpredsmap[tup]) > listthreshold:
                        tablecontents+="<details><summary>"+str(len(subpredsmap[tup]))+" values</summary>"
                    if len(subpredsmap[tup]) > 1:
                        tablecontents += "<ul>"
                    labelmap={}
                    itemcounter = 0
                    for item in subpredsmap[tup]:
                        if itemcounter >= maxlistthreshold:
                            break
                        if subjectstorender!=None and item not in subjectstorender and baseurl in str(item):
                            postprocessing.add((item,URIRef(tup),subject))
                        res = self.createHTMLTableValueEntry(subject, tup, item, None, graph,
                                                             baseurl, checkdepth, geojsonrep,foundmedia,imageannos,textannos,image3dannos,annobodies,dateprops,True,nonns)
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        image3dannos=res["image3dannos"]
                        annobodies=res["annobodies"]
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
                    if len(subpredsmap[tup]) >= maxlistthreshold:
                        tablecontents+="<li>(...)</li>"
                    if len(subpredsmap[tup])>1:
                        tablecontents+="</ul>"
                    if len(subpredsmap[tup]) > listthreshold:
                        tablecontents+="</details>"
                    tablecontents += "</td>"
                else:
                    tablecontents += "<td class=\"wrapword\"></td>"
                tablecontents += "</tr>"
        if self.licenseuri!=None:
            ttlf.add((subject, URIRef("http://purl.org/dc/elements/1.1/license"), URIRef(self.licenseuri)))
        nonnslink=""
        if nonns:
            completesavepath = savepath
            nonnslink = "<div>This page describes linked instances to the concept  <a target=\"_blank\" href=\"" + str(
                subject) + "\">" + str(foundlabel) + " (" + str(DocUtils.shortenURI(
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
            rellink=DocUtils.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,searchfilename,False)
            rellink2 = DocUtils.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,classtreename,False)
            rellink3 = DocUtils.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,"style.css",False)
            rellink4 = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js", False)
            rellink5 = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "proprelations.js", False)
            epsgdefslink = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "epsgdefs.js", False)
            rellink7 = DocUtils.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "vowl_result.js", False)
            if geojsonrep != None:
                myexports=templates["geoexports"]
            else:
                myexports=templates["nongeoexports"]
            itembibtex=""
            relpath=DocUtils.generateRelativePathFromGivenDepth(checkdepth)
            if foundlabel != "":
                f.write(templates["htmltemplate"].replace("{{iconprefixx}}",(relpath+"icons/" if self.offlinecompat else "")).replace("{{deploypath}}",self.deploypath).replace("{{logo}}",logo).replace("{{relativepath}}",relpath).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{toptitle}}", foundlabel).replace(
                    "{{startscriptpath}}", rellink4).replace("{{bibtex}}",itembibtex).replace(
                    "{{epsgdefspath}}", epsgdefslink).replace("{{versionurl}}",DocConfig.versionurl).replace("{{version}}",DocConfig.version).replace("{{bibtex}}",itembibtex).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{indexpage}}","false").replace("{{title}}",
                                                                                                "<a href=\"" + str(subject) + "\">" + str(foundlabel) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}","").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{nonnslink}}",str(nonnslink)).replace("{{subject}}",str(subject)).replace("{{subjectencoded}}",urllib.parse.quote(str(subject))))
            else:
                f.write(templates["htmltemplate"].replace("{{iconprefixx}}",(relpath+"icons/" if self.offlinecompat else "")).replace("{{deploypath}}",self.deploypath).replace("{{logo}}",logo).replace("{{relativepath}}",relpath).replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{indexpage}}","false").replace("{{toptitle}}", DocUtils.shortenURI(str(subject))).replace(
                    "{{startscriptpath}}", rellink4).replace("{{bibtex}}",itembibtex).replace(
                    "{{epsgdefspath}}", epsgdefslink).replace("{{versionurl}}",DocConfig.versionurl).replace("{{version}}",DocConfig.version).replace("{{bibtex}}",itembibtex).replace("{{vowlpath}}", rellink7).replace("{{proprelationpath}}", rellink5).replace("{{stylepath}}", rellink3).replace("{{title}}","<a href=\"" + str(subject) + "\">" + DocUtils.shortenURI(str(subject)) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{description}}", "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{nonnslink}}",str(nonnslink)).replace("{{subject}}",str(subject)).replace("{{subjectencoded}}",urllib.parse.quote(str(subject))))
            for comm in comment:
                f.write(templates["htmlcommenttemplate"].replace("{{comment}}", DocUtils.shortenURI(comm) + ":" + comment[comm]))
            #for fval in foundvals:
            #    f.write(templates["htmlcommenttemplate"].replace("{{comment}}", "<b>Value:<mark>" + str(fval) + "</mark></b>"))
            if len(foundmedia["mesh"])>0 and len(image3dannos)>0:
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph,self.outpath,self.deploypath, foundmedia["mesh"], image3dannos,annobodies, str(subject),
                                                  self.prefixnamespace,imagetoURI, self.imagemetadata,SPARQLUtils.metadatanamespaces,foundlabel,comment,thetypes,predobjmap,"Model"))
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(templates["threejstemplate"].replace("{{wktstring}}",anno).replace("{{meshurls}}",str(list(foundmedia["mesh"]))))
            elif len(foundmedia["mesh"])>0 and len(image3dannos)==0:
                #QgsMessageLog.logMessage("Found 3D Model: "+str(foundmedia["mesh"]))
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph,self.outpath, self.deploypath, foundmedia["mesh"], annobodies,  image3dannos, str(subject),self.prefixnamespace,imagetoURI, self.imagemetadata,SPARQLUtils.metadatanamespaces,foundlabel,comment,thetypes,predobjmap,"Model"))
                for curitem in foundmedia["mesh"]:
                    format="ply"
                    if ".nxs" in curitem or ".nxz" in curitem:
                        format="nexus"
                    f.write(templates["3dtemplate"].replace("{{meshurl}}",curitem).replace("{{meshformat}}",format))
                    break
            elif len(foundmedia["mesh"])==0 and len(image3dannos)>0:
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(templates["threejstemplate"].replace("{{wktstring}}",anno).replace("{{meshurls}}","[]"))
            carousel="image"
            if len(foundmedia["image"])>3:
                carousel="carousel-item active"
                f.write(templates["imagecarouselheader"])
            if len(imageannos)>0 and len(foundmedia["image"])>0:
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph,self.outpath,self.deploypath,foundmedia["image"],imageannos,annobodies,str(subject),self.prefixnamespace,imagetoURI, self.imagemetadata,SPARQLUtils.metadatanamespaces,foundlabel,comment,thetypes,predobjmap,"Image"))
                for image in foundmedia["image"]:
                    annostring=""
                    for anno in imageannos:
                        annostring+=anno.replace("<svg>","<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                    f.write(templates["imageswithannotemplate"].replace("{{carousel}}",carousel+"\" style=\"position: relative;display: inline-block;").replace("{{image}}",str(image)).replace("{{svganno}}",annostring).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            elif len(foundmedia["image"])>0:
                if self.iiif:
                    iiifmanifestpaths["default"].append(
                        IIIFAPIExporter.generateIIIFManifest(graph,self.outpath,self.deploypath,foundmedia["image"],imageannos,annobodies,str(subject),self.prefixnamespace,imagetoURI, self.imagemetadata,SPARQLUtils.metadatanamespaces,foundlabel,comment,thetypes,predobjmap,"Image"))
                for image in foundmedia["image"]:
                    if image=="<svg width=":
                        continue
                    if "<svg" in image:
                        if "<svg>" in image:
                            f.write(templates["imagestemplatesvg"].replace("{{carousel}}",carousel).replace("{{image}}", str(image.replace("<svg>","<svg class=\"svgview\">"))))
                        else:
                            f.write(templates["imagestemplatesvg"].replace("{{carousel}}",carousel).replace("{{image}}",str(image)))
                    else:
                        f.write(templates["imagestemplate"].replace("{{carousel}}",carousel).replace("{{image}}",str(image)).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            if len(foundmedia["image"])>3:
                f.write(templates["imagecarouselfooter"])
            if len(textannos) > 0:
                TextAnnoPage().generatePageWidget(textannos,f)
            if len(foundmedia["audio"]) > 0 and self.iiif:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph,self.outpath,self.deploypath,foundmedia["audio"],None,None,str(subject),self.prefixnamespace,imagetoURI, self.imagemetadata,SPARQLUtils.metadatanamespaces,foundlabel,comment,thetypes,predobjmap,"Audio"))
            for audio in foundmedia["audio"]:
                f.write(templates["audiotemplate"].replace("{{audio}}",str(audio)))
            if len(foundmedia["video"]) > 0 and self.iiif:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph,self.outpath,self.deploypath,foundmedia["video"],None,None,str(subject),self.prefixnamespace,imagetoURI, self.imagemetadata,SPARQLUtils.metadatanamespaces,foundlabel,comment,thetypes,predobjmap,"Video"))
            for video in foundmedia["video"]:
                f.write(templates["videotemplate"].replace("{{video}}",str(video)))
            for type in curtypes:
                if type in SPARQLUtils.lexicontypes:
                    LexiconPage().generatePageWidget(graph,subject,f,{},False)
                if type in PersonPage.pageWidgetConstraint():
                    PersonPage().generatePageWidget(graph,subject,templates,f,True)
            self.processCollectionPages(collections, graph, subject, f)
            if geojsonrep != None and "geocollection" not in collections:
                self.geocache=GeometryViewPage().generatePageWidget(graph, templates, subject, f, uritotreeitem, geojsonrep, predobjmap, self.geocache,
                                   {"dateprops": dateprops, "timeobj": timeobj,
                                                             "epsgcode": epsgcode, "epsgdefslink": epsgdefslink,
                                                             "checkdepth": checkdepth, "hasnonnslen": len(hasnonns)})
            elif "geocollection" in collections or nonns:
                self.geocache=GeometryViewPage().generateCollectionWidget(graph, templates, subject, f, uritotreeitem,
                                                            featurecollectionspaths,
                                                            {"completesavepath":completesavepath,"nonns":nonns,"hasnonns":hasnonns,
                                                             "foundlabel":foundlabel,"localOptimized": self.localOptimized,
                                                             "dateprops": dateprops, "timeobj": timeobj,
                                                             "geocache":self.geocache,
                                                             "epsgcode": epsgcode, "epsgdefslink": epsgdefslink,
                                                             "checkdepth": checkdepth, "hasnonnslen": len(hasnonns)})
            f.write(templates["htmltabletemplate"].replace("{{tablecontent}}", tablecontents))
            if metadatatablecontentcounter>=0:
                f.write("<h5>Metadata</h5>")
                f.write(templates["htmltabletemplate"].replace("{{tablecontent}}", metadatatablecontents))
            f.write(templates["footer"].replace("{{exports}}",myexports).replace("{{license}}",curlicense).replace("{{bibtex}}",itembibtex))
            f.close()
        return [postprocessing,nonnsmap]

    def processCollectionPages(self,pagesmap,graph,subject,f):
        if "observationcollection" in pagesmap:
            ObservationPage().generateCollectionWidget(graph, templates, subject, f,{})
        if "lexicon" in pagesmap:
            LexiconPage().generateCollectionWidget(graph,templates,subject,f,{})