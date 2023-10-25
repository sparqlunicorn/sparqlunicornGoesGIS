from ..sparqlutils import SPARQLUtils


class DocUtils:

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
            return " <a href=\"" + str(uri) + "\" target=\"_blank\">" + SPARQLUtils.shortenURI(uri) + "</a>"

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
    def generateRelativeSymlink(linkpath, targetpath, outpath, items=False):
        if "nonns" in targetpath and not items:
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
    def getLabelForObject(obj,graph,labellang=None):
        label=""
        onelabel=SPARQLUtils.shortenURI(str(obj))
        for tup in graph.predicate_objects(obj):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                # Check for label property
                if tup[1].language==labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
        if label=="" and onelabel!=None:
            label=onelabel
        return label

    @staticmethod
    def replaceNameSpacesInLabel(prefixes,uri):
        for ns in prefixes["reversed"]:
            if ns in uri:
                return {"uri": str(prefixes["reversed"][ns]) + ":" + str(uri.replace(ns, "")),
                        "ns": prefixes["reversed"][ns]}
        return None

    @staticmethod
    def generateRelativePathFromGivenDepth(checkdepth):
        rellink = ""
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        return rellink