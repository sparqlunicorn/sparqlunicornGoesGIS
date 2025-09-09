import os
import re
import shutil
from datetime import date
import urllib.request
from rdflib import URIRef, Literal

from .docconfig import DocConfig


class DocUtils:

    @staticmethod
    def zero_div(x,y):
        return y and x/y or 0

    @staticmethod
    def updateProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█',printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

    @staticmethod
    def replaceStandardVariables(template, subject, checkdepth, indexpage,pubconfig):
        template = template.replace("{{indexpage}}", str(indexpage)).replace("{{subject}}", str(subject)).replace(
            "{{relativedepth}}", str(checkdepth)) \
            .replace("{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace(
            "{{deploypath}}", pubconfig["deploypath"]) \
            .replace("{{publishingorg}}", pubconfig["publishingorg"]).replace("{{publisher}}", pubconfig["publisher"]).replace(
            "{{datasettitle}}", pubconfig["datasettitle"]) \
            .replace("{{logo}}", pubconfig["logourl"])
        return template

    @staticmethod
    def replaceCitationLink(template, foundlabel,uri,pubconfig):
        return template.replace("{{citationlink}}",f'<details><summary>[CITE]</summary><pre>@misc{{{DocUtils.shortenURI(uri)}\nauthor={pubconfig["datasettitle"]} Contributors",\ntitle="{foundlabel}",\n"url="{uri}",\nnote="[Online; documentation generated at {date.today()}]"}}</pre></details>')

    @staticmethod
    def getLDFilesFromFolder(folder):
        directory = os.fsencode(folder)
        files=[]
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith((".ttl",".owl",".n3",".nt")):
                files.append(filename)
        return files

    @staticmethod
    def getDataNamespace(g):
        print("Automatic data namespace detection")
        namespacetosub = {}
        for sub in g.subjects(None, None, True):
            ns = DocUtils.instanceToNS(sub)
            namespacetosub.setdefault(ns,set()).add(sub)
            #if ns not in namespacetosub:
            #    namespacetosub[ns] = set()
            #namespacetosub[ns].add(sub)
        maxns=None
        maxnsnum=-1
        for ns in namespacetosub:
            if len(namespacetosub[ns])>maxnsnum:
                maxnsnum=len(namespacetosub[ns])
                maxns=ns
        print("Automatically detected datanamespace "+str(maxns))
        return maxns

    @staticmethod
    def resolveWildcardPath(thepath):
        result = []
        if "/*" not in thepath:
            result.append(thepath)
            return result
        #print(thepath)
        normpath = thepath.replace("*", "")
        if os.path.exists(normpath):
            files = os.listdir(normpath)
            result=[normpath + file for file in files if file.endswith((".ttl",".owl",".n3",".nt"))]
            #for file in files:
                #print(file)
            #    if file.endswith((".ttl",".owl",".n3",".nt")):
            #        result.append(normpath + file)
        return result


    @staticmethod
    def instanceToNS(uri):
        if not uri.startswith("http"):
            return uri
        if "#" in uri:
            return uri[:uri.rfind("#") + 1]
        if "/" in uri:
            return uri[:uri.rfind("/") + 1]
        return uri


    @staticmethod
    def checkDepthFromPath(savepath,baseurl,subject):
        return subject.replace(baseurl, "").count("/")+1
        """
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        #checkdepth+=1
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth))
        return checkdepth+1
        """

    @staticmethod
    def printExecutionStats(timeexec):
        print(f"Selected Execution Statistics in order of execution:")
        totaltime=0
        for entry in timeexec:
            print(f"{entry}: {timeexec[entry]['time']} seconds", end='')
            totaltime+=timeexec[entry]['time']
            if "items" in timeexec[entry]:
                print(f" for {timeexec[entry]['items']} items, about {timeexec[entry]['time']/timeexec[entry]['items']} seconds per item", end='')
            print("\n",end="")
        print(f"Total measured execution time: {totaltime} seconds")

    @staticmethod
    def getExecutionStats(timeexec):
        res=f"\nSelected Execution Statistics in order of execution:\n"
        totaltime=0
        for entry in timeexec:
            res+=f"{entry}: {timeexec[entry]['time']} seconds\n"
            totaltime+=timeexec[entry]['time']
            if "items" in timeexec[entry]:
                res+=f" for {timeexec[entry]['items']} items, about {timeexec[entry]['time']/timeexec[entry]['items']} seconds per item\n"
            #print("\n",end="")
        return f"{res} Total measured execution time: {totaltime} seconds"

    @staticmethod
    def writeExecutionStats(timeexec,filename="buildlog.txt"):
        with open(filename,"w",encoding="utf-8") as f:
            f.write(f"Selected Execution Statistics in order of execution:\n")
            totaltime=0
            for entry in timeexec:
                f.write(f"{entry}: {timeexec[entry]['time']} seconds")
                totaltime+=timeexec[entry]['time']
                if "items" in timeexec[entry]:
                    f.write(f" for {timeexec[entry]['items']} items, about {timeexec[entry]['time']/timeexec[entry]['items']} seconds per item")
                f.write("\n")
            f.write(f"Total measured execution time: {totaltime} seconds")

    @staticmethod
    def shortenURI(uri,ns=False):
        if uri is not None:
            if ns:
                if "#" in uri:
                    return uri[0:uri.rfind('#')+1]
                if "/" in uri:
                    return uri[0:uri.rfind('/')+1]
            if uri.endswith("/"):
                uri = uri[0:-1]
            if not ns:
                if "#" in uri:
                    return uri[uri.rfind('#') + 1:]
                if "/" in uri:
                    return uri[uri.rfind('/') + 1:]
            return uri
        else:
            return ""

    @staticmethod
    def createURILink(prefixes,uri):
        res = DocUtils.replaceNameSpacesInLabel(prefixes,uri)
        if res is not None:
            return f" <a href=\"{uri}\" target=\"_blank\">{res['uri']}</a>"
        else:
            return f" <a href=\"{uri}\" target=\"_blank\">{DocUtils.shortenURI(uri)}</a>"

    @staticmethod
    def generateRelativeLinkFromGivenDepth(baseurl,checkdepth,item,withindex):
        rellink = "../"*checkdepth+str(item).replace(baseurl, "")
        #for i in range(0, checkdepth):
        #    rellink = "../" + rellink
        if withindex:
            return f'{rellink}/index.html'
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    @staticmethod
    def resolveUnitValue(graph,obj,tuppredstr,tupobjstr,foundval,foundunit):
        #print("RESOLVE UNIT VALUE: "+str(obj))
        if tuppredstr == "http://www.w3.org/ns/oa#hasSource":
            foundval = tupobjstr
        elif tuppredstr is not None and tuppredstr != "http://www.w3.org/ns/oa#hasSource" and DocConfig.valueproperties[
            tuppredstr] == "DatatypeProperty" and (isinstance(obj, Literal) or isinstance(obj, URIRef)):
            foundval = tupobjstr
        elif tuppredstr == "http://www.w3.org/ns/oa#hasTarget":
            for inttup in graph.predicate_objects(obj):
                if str(inttup[0]) == "http://www.w3.org/ns/oa#hasSelector":
                    for valtup in graph.predicate_objects(inttup[1]):
                        if str(valtup[0]) in DocConfig.unitproperties:
                            foundunit = str(valtup[1])
                        elif str(valtup[0]) in DocConfig.valueproperties and (
                                isinstance(valtup[1], Literal) or isinstance(valtup[1], URIRef)):
                            foundval = str(valtup[1])
        elif tuppredstr is not None and DocConfig.valueproperties[tuppredstr] == "DatatypeProperty":
            if tuppredstr in DocConfig.valueproperties and isinstance(obj, Literal):
                foundval = tupobjstr
        else:
            for valtup in graph.predicate_objects(obj):
                valtup0str=str(valtup[0])
                if valtup0str in DocConfig.unitproperties:
                    foundunit = str(valtup[1])
                elif valtup0str in DocConfig.valueproperties and isinstance(valtup[1], Literal):
                    foundval = str(valtup[1])
                elif valtup0str in DocConfig.strictvalueproperties and isinstance(valtup[1], URIRef):
                    #print("Valtup[1]: " + str(valtup[1]))
                    for tup2 in graph.predicate_objects(valtup[1]):
                        #print("Tup2: " + str(tup2))
                        if str(tup2[0]) in DocConfig.unitproperties:
                            foundunit = str(tup2[1])
                        elif str(tup2[0]) in DocConfig.valueproperties:
                            foundval=str(tup2[1])
        return [foundval,foundunit]


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
        if "nonns" in targetpath:
            if targetpath.count("/")<3:
                checkdepthtarget= 1
            elif not items:
                checkdepthtarget = 3
            elif items:
                checkdepthtarget = 4
        else:
            checkdepthtarget = targetpath.count("/") - 1
        #print("Checkdepthtarget: " + str(checkdepthtarget))
        targetrellink = DocUtils.generateRelativeLinkFromGivenDepth(targetpath, checkdepthtarget, linkpath, False)
        #print("Target Rellink: " + str(targetrellink))
        #print("Linkpath: " + str(linkpath))
        targetrellink = targetrellink.replace(outpath, "")
        return targetrellink.replace("//", "/")

    @staticmethod
    def getLabelForObject(obj,graph,prefixes=None,labellang=None):
        label=""
        objstr=str(obj)
        onelabel=DocUtils.shortenURI(objstr)
        for tup in graph.predicate_objects(obj):
            if str(tup[0]) in DocConfig.labelproperties:
                # Check for label property
                if tup[1].language==labellang:
                    label=str(tup[1])
                onelabel=str(tup[1])
        if label=="":
            if onelabel is not None and onelabel!="":
                if prefixes is not None:
                    res = DocUtils.replaceNameSpacesInLabel(prefixes, objstr)
                    label=res["uri"]
                else:
                    label = onelabel
            elif prefixes is not None:
                res = DocUtils.replaceNameSpacesInLabel(prefixes, objstr)
                label=res["uri"]
        return label

    @staticmethod
    def processSubjectPath(outpath,paths,path,graph):
        if "/" in path:
            addpath = ""
            #try:
            os.makedirs(outpath+path,exist_ok=True)
            #for pathelem in path.split("/"):
            #    addpath += pathelem + "/"
            #    if not os.path.exists(outpath + addpath):
            #        os.mkdir(outpath + addpath)
            paths.setdefault(outpath + path[0:path.rfind('/')] + "/",[]).append(path[0:path.rfind('/')])
            #if outpath + path[0:path.rfind('/')] + "/" not in paths:
            #    paths[outpath + path[0:path.rfind('/')] + "/"] = []
            #paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
            #except Exception as e:
            #    print(e)
        else:
            #try:
            os.makedirs(outpath+path,exist_ok=True)
            #if not os.path.exists(outpath + path):
            #    os.mkdir(outpath + path)
            paths.setdefault(outpath,[]).append(path + "/index.html")
            #if outpath not in paths:
            #    paths[outpath] = []
            #paths[outpath].append(path + "/index.html")
            #except Exception as e:
            #    print(e)
        if os.path.exists(f"{outpath}{path}/index.ttl"):
            try:
                graph.parse(f"{outpath}{path}/index.ttl")
            except Exception as e:
                print(e)
        return paths

    @staticmethod
    def replaceNameSpacesInLabel(prefixes,uri):
        nsuri=DocUtils.shortenURI(uri,True)
        if nsuri in prefixes["reversed"]:
            if nsuri==uri and nsuri in prefixes["nstolabel"]:
                return {"uri": f'{prefixes["nstolabel"][nsuri]} ({prefixes["reversed"][nsuri]}:)',"ns": prefixes["reversed"][nsuri]}
            else:
                return {"uri": f'{prefixes["reversed"][nsuri]}:{uri.replace(nsuri, "")}',"ns": prefixes["reversed"][nsuri]}
        return {"uri": DocUtils.shortenURI(uri),"ns": ""}

    @staticmethod
    def generateRelativePathFromGivenDepth(checkdepth):
        #rellink =
        #for i in range(0, checkdepth):
        #    rellink = "../" + rellink
        result="../"*checkdepth
        if result=="":
            return "."
        return result

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
                        with open(f'{outpath}{os.sep}js{os.sep}{m[m.rfind("/") + 1:]}', 'b+w') as f:
                            f.write(g.read())
                    except Exception as e:
                        print(e)
                        thepath=f"{templatepath}/{templatename}/js/lib/{m[m.rfind('/') + 1:]}"
                        if os.path.exists(thepath):
                            shutil.copy(thepath,f'{outpath}{os.sep}js{os.sep}{m[m.rfind("/") + 1:]}')
                    myhtmltemplate = myhtmltemplate.replace(m, "{{relativepath}}js/" + m[m.rfind("/") + 1:])
            else:
                match = match.replace("\"", "")
                try:
                    g = urllib.request.urlopen(match.replace("\"", ""))
                    with open(f'{outpath}{os.sep}js{os.sep}{match[match.rfind("/") + 1:]}', 'b+w') as f:
                        f.write(g.read())
                except Exception as e:
                    print(e)
                    thepath=f"{templatepath}/{templatename}/js/lib/{match[match.rfind('/') + 1:]}"
                    if os.path.exists(thepath):
                        shutil.copy(thepath,f'{outpath}{os.sep}js{os.sep}{match[match.rfind("/") + 1:]}')
                myhtmltemplate = myhtmltemplate.replace(match, "{{relativepath}}js/" + match[match.rfind("/") + 1:])
        matched = re.findall(r'href="(http.*.css)"', myhtmltemplate)
        for match in matched:
            #print(match.replace("\"", ""))
            match = match.replace("\"", "").replace("/>", "")
            match = match.replace(">", "")
            try:
                g = urllib.request.urlopen(match.replace("\"", ""))
                with open(f'{outpath}{os.sep}css{os.sep}{match[match.rfind("/") + 1:]}', 'b+w') as f:
                    f.write(g.read())
            except Exception as e:
                thepath=f"{templatepath}/{templatename}/css/lib/{match[match.rfind('/') + 1:]}"
                if os.path.exists(thepath):
                    shutil.copy(thepath,f'{outpath}{os.sep}css{os.sep}{match[match.rfind("/") + 1:]}')
            myhtmltemplate = myhtmltemplate.replace(match, "{{relativepath}}css/" + match[match.rfind("/") + 1:])
        return myhtmltemplate

    @staticmethod
    def conditionalArrayReplace(string,conds,replace,what):
        #counter=0
        #result=""
        result="".join(replace[counter] for counter, cond in enumerate(conds) if cond)
        #for cond in conds:
        #    if cond:
        #        result+=replace[counter]
        #    counter+=1
        return string.replace(what,result)

    @staticmethod
    def conditionalReplace(string,cond,what,replace):
        if cond:
            return string.replace(what,replace)
        return string

    @staticmethod
    def resolveOWLImports(graph):
        for obj in graph.objects(None,"http://www.w3.org/2002/07/owl#imports"):
            try:
                graph.parse(str(obj))
            except Exception as e:
                print(e)
        return graph

    @staticmethod
    def replaceColonFromWinPath(thepath):
        if ":/" in thepath and re.search("^[A-Z]:[\/\\\\]",thepath) is not None:
            return thepath[0:2]+thepath[3:].replace(":","_")
        else:
            return thepath.replace(":","_")