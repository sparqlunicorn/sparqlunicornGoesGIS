import json
import os
from collections import defaultdict

from ...doc.docutils import DocUtils


class MiscExporter:

    @staticmethod
    def getExporterString():
        return "Misc Data (*.csv *.tsv *.json)"

    @staticmethod
    def detectSubjectType(g,subjectstorender):
        subjectsToType,typeToFields= {},defaultdict(set)
        for sub in subjectstorender:
            substr=str(sub)
            #typeToFields[substr]=set()
            for tup in g.predicate_objects(sub):
                if str(tup[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    subjectsToType[substr]=str(tup[1])
                typeToFields[substr].add(str(tup[0]))
            if substr in subjectsToType:
                #if subjectsToType[substr] not in typeToFields:
                #    typeToFields[subjectsToType[substr]]=set()
                typeToFields[subjectsToType[substr]]=typeToFields[subjectsToType[substr]].union(typeToFields[substr])
                del typeToFields[substr]
        return [subjectsToType,typeToFields]

    @staticmethod
    def convertTTLToCSV(g, file, subjectstorender=None,classlist=None, formatt="csv"):
        sepchar=","
        if formatt=="tsv":
            sepchar="\t"
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        subjectsToType,typeToFields=MiscExporter.detectSubjectType(g,subjectstorender)
        typeToRes={}
        for type in typeToFields:
            typeToRes[type]=[]
        for sub in subjectstorender:
            if str(sub) not in subjectsToType:
                continue
            #res=
            #for tup in g.predicate_objects(sub):
            #    res[str(tup[0])]=str(tup[1])
            typeToRes[subjectsToType[str(sub)]].append({str(tup[0]):str(tup[1]) for tup in g.predicate_objects(sub)})
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("."+formatt,"")}_{DocUtils.shortenURI(type)}.{formatt}',"w") as f:
                tlist=list(typeToFields[type])
                tlistlen=len(tlist)
                for i in range(0,tlistlen):
                    f.write(f'"{tlist[i]}"')
                    if i<len(tlist)-1:
                        f.write(sepchar)
                f.write("\n")
                for res in typeToRes[type]:
                    for i in range(0,tlistlen):
                        col=tlist[i]
                        if col in res:
                            f.write(f'"{res[col]}"')
                        if i<len(tlist)-1:
                            f.write(sepchar)
                    f.write("\n")
        return None

    @staticmethod
    def convertTTLToJSON(g, file, subjectstorender=None,classlist=None, formatt="json"):
        if subjectstorender is None:
            subjectstorender = g.subjects(None, None, True)
        subjectsToType,typeToFields = MiscExporter.detectSubjectType(g, subjectstorender)
        typeToRes = dict((el,[]) for el in typeToFields)

        for sub in subjectstorender:
            if str(sub) not in subjectsToType:
                continue
            #res=
            #for tup in g.predicate_objects(sub):
            #    res[str(tup[0])] = str(tup[1])
            typeToRes[subjectsToType[str(sub)]].append({str(tup[0]):str(tup[1]) for tup in g.predicate_objects(sub)})
        for type in typeToFields:
            with open(f'{os.path.realpath(file.name).replace("." + formatt, "")}_{DocUtils.shortenURI(type)}.{formatt}', "w") as f:
                f.write("\n")
                for res in typeToRes[type]:
                    json.dump(res,f)
        return None