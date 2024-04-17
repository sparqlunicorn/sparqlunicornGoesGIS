import json
import os

from ...doc.docutils import DocUtils


class MiscExporter:

    @staticmethod
    def getExporterString():
        return "Misc Data (*.csv *.tsv *.json)"

    @staticmethod
    def detectSubjectType(g,subjectstorender):
        subjectsToType={}
        typeToFields={}
        for sub in subjectstorender:
            typeToFields[str(sub)]=set()
            for tup in g.predicate_objects(sub):
                if str(tup[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    subjectsToType[str(sub)]=str(tup[1])
                typeToFields[str(sub)].add(str(tup[0]))
            if str(sub) in subjectsToType:
                if subjectsToType[str(sub)] not in typeToFields:
                    typeToFields[subjectsToType[str(sub)]]=set()
                typeToFields[subjectsToType[str(sub)]]=typeToFields[subjectsToType[str(sub)]].union(typeToFields[str(sub)])
                del typeToFields[str(sub)]
        return [subjectsToType,typeToFields]

    @staticmethod
    def convertTTLToCSV(g, file, subjectstorender=None,classlist=None, formatt="csv"):
        sepchar=","
        if formatt=="tsv":
            sepchar="\t"
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        res=MiscExporter.detectSubjectType(g,subjectstorender)
        subjectsToType=res[0]
        typeToFields=res[1]
        typeToRes={}
        for type in typeToFields:
            typeToRes[type]=[]
        for sub in subjectstorender:
            if str(sub) not in subjectsToType:
                continue
            res={}
            for tup in g.predicate_objects(sub):
                res[str(tup[0])]=str(tup[1])
            typeToRes[subjectsToType[str(sub)]].append(res)
        for type in typeToFields:
            f=open(os.path.realpath(file.name).replace("."+formatt,"")+"_"+DocUtils.shortenURI(type)+"."+formatt,"w")
            tlist=list(typeToFields[type])
            tlistlen=len(tlist)
            for i in range(0,tlistlen):
                f.write("\""+tlist[i]+"\"")
                if i<len(tlist)-1:
                    f.write(sepchar)
            f.write("\n")
            for res in typeToRes[type]:
                for i in range(0,tlistlen):
                    col=tlist[i]
                    if col in res:
                        f.write("\""+res[col]+"\"")
                    if i<len(tlist)-1:
                        f.write(sepchar)
                f.write("\n")
            f.close()
        return None

    @staticmethod
    def convertTTLToJSON(g, file, subjectstorender=None,classlist=None, formatt="json"):
        if subjectstorender == None:
            subjectstorender = g.subjects(None, None, True)
        res = MiscExporter.detectSubjectType(g, subjectstorender)
        subjectsToType = res[0]
        typeToFields = res[1]
        typeToRes = {}
        for type in typeToFields:
            typeToRes[type] = []
        for sub in subjectstorender:
            if str(sub) not in subjectsToType:
                continue
            res = {}
            for tup in g.predicate_objects(sub):
                res[str(tup[0])] = str(tup[1])
            typeToRes[subjectsToType[str(sub)]].append(res)
        for type in typeToFields:
            f = open(os.path.realpath(file.name).replace("." + formatt, "") + "_" + DocUtils.shortenURI(
                type) + "." + formatt, "w")
            f.write("\n")
            for res in typeToRes[type]:
                f.write(json.dumps(res))
            f.close()
        return None