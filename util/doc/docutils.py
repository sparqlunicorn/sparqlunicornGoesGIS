from ..sparqlutils import SPARQLUtils
import os
import re
import shutil
import urllib.request
from rdflib import URIRef
from qgis.core import Qgis, QgsMessageLog

from .docconfig import DocConfig


class DocUtils:

    @staticmethod
    def zero_div(x,y):
        return y and x/y or 0


    @staticmethod
    def replaceStandardVariables(template, subject, checkdepth, indexpage, pubconfig):
        template = template.replace("{{indexpage}}", str(indexpage)).replace("{{subject}}", str(subject)).replace(
            "{{relativedepth}}", str(checkdepth)) \
            .replace("{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace(
            "{{deploypath}}", pubconfig["deploypath"]) \
            .replace("{{publishingorg}}", pubconfig["publishingorg"]).replace("{{publisher}}",
                                                                              pubconfig["publisher"]).replace(
            "{{datasettitle}}", pubconfig["datasettitle"]) \
            .replace("{{logo}}", pubconfig["logoname"])
        return template

    @staticmethod
    def checkDepthFromPath(savepath,baseurl,subject):
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        checkdepth+=1
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth))
        return checkdepth

    @staticmethod
    def createURILink(prefixes,uri):
        res = DocUtils.replaceNameSpacesInLabel(prefixes,uri)
        if res != None:
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + str(res["uri"]) + "</a>"
        else:
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + DocUtils.shortenURI(uri) + "</a>"

    @staticmethod
    def generateRelativeLinkFromGivenDepth(baseurl,checkdepth,item,withindex):
        rellink = str(item).replace(baseurl, "")
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        if withindex:
            rellink += "/index.html"
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    @staticmethod
    def checkImgMetadataRDF(g,uri):
        res={}
        for obj in g.objects(URIRef(uri),URIRef("http://www.w3.org/2003/12/exif/ns#width")):
            res["width"]=str(obj)
        for obj in g.objects(URIRef(uri),URIRef("http://www.w3.org/2003/12/exif/ns#height")):
            res["height"]=str(obj)
        return res

    @staticmethod
    def generateRelativeSymlink(linkpath, targetpath, outpath, items=False):
        if "nonns" in targetpath and targetpath.count("/")<3:
            checkdepthtarget= 1
        elif "nonns" in targetpath and not items:
            checkdepthtarget = 3
        elif "nonns" in targetpath and items:
            checkdepthtarget = 4
        else:
            checkdepthtarget = targetpath.count("/") - 1
        print("Checkdepthtarget: " + str(checkdepthtarget))
        targetrellink = DocUtils.generateRelativeLinkFromGivenDepth(targetpath, checkdepthtarget, linkpath, False)
        print("Target Rellink: " + str(targetrellink))
        print("Linkpath: " + str(linkpath))
        targetrellink = targetrellink.replace(outpath, "")
        return targetrellink.replace("//", "/")

    @staticmethod
    def getLabelForObject(obj,graph,prefixes=None,labellang=None):
        label=""
        onelabel=DocUtils.shortenURI(str(obj))
        for tup in graph.predicate_objects(obj):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                # Check for label property
                if tup[1].language==labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
        if label=="" and onelabel!=None and onelabel!="":
            if prefixes!=None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
                label=res["uri"]
            else:
                label = onelabel
        elif label=="" and (onelabel==None or onelabel=="") and prefixes!=None:
            res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
            if res!=None:
                label=res["uri"]
        return label

    @staticmethod
    def processSubjectPath(outpath,paths,path,graph):
        if "/" in path:
            addpath = ""
            try:
                for pathelem in path.split("/"):
                    addpath += pathelem + "/"
                    if not os.path.exists(outpath + addpath):
                        os.mkdir(outpath + addpath)
                if outpath + path[0:path.rfind('/')] + "/" not in paths:
                    paths[outpath + path[0:path.rfind('/')] + "/"] = []
                paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
            except Exception as e:
                print(e)
        else:
            try:
                if not os.path.exists(outpath + path):
                    os.mkdir(outpath + path)
                if outpath not in paths:
                    paths[outpath] = []
                paths[outpath].append(path + "/index.html")
            except Exception as e:
                print(e)
        if os.path.exists(outpath + path + "/index.ttl"):
            try:
                graph.parse(outpath + path + "/index.ttl")
            except Exception as e:
                print(e)
        return paths

    @staticmethod
    def replaceNameSpacesInLabel(prefixes,uri):
        nsuri=DocUtils.shortenURI(uri,True)
        if prefixes!=None and nsuri in prefixes["reversed"]:
            if nsuri==uri and nsuri in prefixes["nstolabel"]:
                return {"uri": prefixes["nstolabel"][nsuri]+" ("+str(prefixes["reversed"][nsuri])+":)",
                        "ns": prefixes["reversed"][nsuri]}
            else:
                return {"uri": str(prefixes["reversed"][nsuri]) + ":" + str(uri.replace(nsuri, "")),
                    "ns": prefixes["reversed"][nsuri]}
        return {"uri": DocUtils.shortenURI(uri),"ns": ""}

    @staticmethod
    def shortenURI(uri,ns=False):
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

    @staticmethod
    def generateRelativePathFromGivenDepth(checkdepth):
        rellink = ""
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        return rellink

    @staticmethod
    def createOfflineCompatibleVersion(outpath, myhtmltemplate, templatepath, templatename):
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        if not os.path.isdir(outpath + "/js"):
            os.mkdir(outpath + "/js")
        if not os.path.isdir(outpath + "/css"):
            os.mkdir(outpath + "/css")
        matched = re.findall(r'src="(http.*)"', myhtmltemplate)
        for match in matched:
            # download the library
            if "</script>" in match:
                for m in match.split("></script><script src="):
                    m = m.replace("\"", "").replace("/>", "")
                    m = m.replace(">", "")
                    try:
                        g = urllib.request.urlopen(m.replace("\"", ""))
                        with open(outpath + str(os.sep) + "js" + str(os.sep) + m[m.rfind("/") + 1:], 'b+w') as f:
                            f.write(g.read())
                    except Exception as e:
                        print(e)
                        if os.path.exists(templatepath + "/" + templatename + "/js/lib/" + str(m[m.rfind("/") + 1:])):
                            shutil.copy(templatepath + "/" + templatename + "/js/lib/" + str(m[m.rfind("/") + 1:]),
                                        outpath + str(os.sep) + "js" + str(os.sep) + m[m.rfind("/") + 1:])
                    myhtmltemplate = myhtmltemplate.replace(m, "{{relativepath}}js/" + m[m.rfind("/") + 1:])
            else:
                match = match.replace("\"", "")
                try:
                    g = urllib.request.urlopen(match.replace("\"", ""))
                    with open(outpath + str(os.sep) + "js" + str(os.sep) + match[match.rfind("/") + 1:], 'b+w') as f:
                        f.write(g.read())
                except Exception as e:
                    print(e)
                    if os.path.exists(
                            templatepath + "/" + templatename + "/js/lib/" + str(match[match.rfind("/") + 1:])):
                        shutil.copy(templatepath + "/" + templatename + "/js/lib/" + str(match[match.rfind("/") + 1:]),
                                    outpath + str(os.sep) + "js" + str(os.sep) + match[match.rfind("/") + 1:])
                myhtmltemplate = myhtmltemplate.replace(match, "{{relativepath}}js/" + match[match.rfind("/") + 1:])
        matched = re.findall(r'href="(http.*.css)"', myhtmltemplate)
        for match in matched:
            print(match.replace("\"", ""))
            match = match.replace("\"", "").replace("/>", "")
            match = match.replace(">", "")
            try:
                g = urllib.request.urlopen(match.replace("\"", ""))
                with open(outpath + str(os.sep) + "css" + str(os.sep) + match[match.rfind("/") + 1:], 'b+w') as f:
                    f.write(g.read())
            except Exception as e:
                if os.path.exists(templatepath + "/" + templatename + "/css/lib/" + str(match[match.rfind("/") + 1:])):
                    shutil.copy(templatepath + "/" + templatename + "/css/lib/" + str(match[match.rfind("/") + 1:]),
                                outpath + str(os.sep) + "css" + str(os.sep) + match[match.rfind("/") + 1:])
            myhtmltemplate = myhtmltemplate.replace(match, "{{relativepath}}css/" + match[match.rfind("/") + 1:])
        return myhtmltemplate

    @staticmethod
    def conditionalArrayReplace(string,conds,replace,what):
        counter=0
        result=""
        for cond in conds:
            if cond:
                result+=replace[counter]
            counter+=1
        return string.replace(what,result)

    @staticmethod
    def conditionalReplace(string,cond,what,replace):
        if cond:
            return string.replace(what,replace)
        return string

    @staticmethod
    def resolveOWLImports(graph):
        for obj in graph.objects(None,"http://www.w3.org/2002/07/owl#imports"):
            QgsMessageLog.logMessage(str(obj), "OntdocGeneration", Qgis.Info)
            try:
                graph.parse(str(obj))
            except Exception as e:
                print(e)
        return graph