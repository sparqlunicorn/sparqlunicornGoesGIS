from .docconfig import DocConfig
from .docutils import DocUtils
from rdflib import URIRef
from collections import defaultdict

class ClassTreeUtils:


    @staticmethod
    def getClassTree(graph, uritolabel, uritotreeitem, typeproperty, prefixes, preparedclassquery, instancecount, outpath,
                     pubconfig):
        results = graph.query(preparedclassquery)
        classidset=set()
        ldcontext = {"@context": {
            "@version": 1.1,
            "foaf": "http://xmlns.com/foaf/0.1/",
            "ct": "http://purl.org/vocab/classtree#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "icon": "foaf:image",
            "id": "@id",
            "parent": "rdfs:subClassOf",
            "halfgeoclass": "ct:HalfGeoClass",
            "geoclass": {"@type": "ct:icontype", "@id": "ct:GeoClass"},
            "collectionclass": {"@type": "ct:icontype", "@id": "ct:CollectionClass"},
            "featurecollectionclass": {"@type": "ct:icontype", "@id": "ct:FeatureCollectionClass"},
            "class": "owl:Class",
            "instance": "owl:NamedIndividual",
            "geoinstance": {"@type": "ct:Icontype", "@id": "ct:GeoNamedIndividual"},
            "text": "rdfs:label",
            "type": "ct:icontype",
            "types": "ct:icontypes",
            "core": {"@type": "ct:TreeConfig", "@id": "@nest"},
            "data": {"@id": "ct:treeitem", "@type": "ct:TreeItem"}
        }}
        tree = {"plugins": ["defaults", "search", "sort", "state", "types", "contextmenu"],
                "search": {"show_only_matches": True}, "types": {
                "class": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/class.png"},
                "geoclass": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoclass.png"},
                "halfgeoclass": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/halfgeoclass.png"},
                "collectionclass": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/collectionclass.png"},
                "geocollection": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geometrycollection.png"},
                "featurecollection": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/featurecollection.png"},
                "instance": {"icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/instance.png"},
                "geoinstance": {
                    "icon": "https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/geoinstance.png"}
            }, "core": {"themes": {"responsive": True}, "check_callback": True, "data": []},
                "@context": ldcontext["@context"]}
        result = []
        ress = {}
        for res in results:
            # print(res)
            if isinstance(res["subject"], URIRef):
                if isinstance(res["supertype"], URIRef):
                    ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
                else:
                    ress[str(res["subject"])] = {"super": None, "label": res["label"]}
            # if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
            #    if "_:" not in str(res["supertype"]) and str(res["supertype"]).startswith("http"):
            #        ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
            #    else:
            #        ress[str(res["subject"])] = {"super": None, "label": res["label"]}
        # print(ress)
        for cls in ress:
            clsstr = str(cls)
            for obj in graph.subjects(URIRef(typeproperty), URIRef(cls), True):
                objstr = str(obj)
                res = DocUtils.replaceNameSpacesInLabel(prefixes, objstr)
                if objstr in uritolabel:
                    if res is not None:
                        restext = f"{uritolabel[objstr]['label']} ({res['uri']})"
                    else:
                        restext = f"{uritolabel[objstr]['label']} ({DocUtils.shortenURI(objstr)})"
                else:
                    if res is not None:
                        restext = f" ({res['uri']})"
                    else:
                        restext = DocUtils.shortenURI(objstr)
                result.append({"id": objstr, "parent": cls, "type": f'{"instance" if objstr not in DocConfig.collectionclasses else "class"}', "text": restext, "data": {"from": {}, "to": {}}})
                #if objstr not in DocConfig.collectionclasses:
                #    result.append({"id": objstr, "parent": cls, "type": "instance", "text": restext, "data": {"from":{},"to":{}}})
                #else:
                #    result.append({"id": objstr, "parent": cls, "type": "class", "text": restext, "data": {"from":{},"to":{}}})
                uritotreeitem[objstr].append(result[-1])
            # print(ress[cls])
            res = DocUtils.replaceNameSpacesInLabel(prefixes, clsstr)
            if ress[cls]["super"] is None:
                restext = DocUtils.shortenURI(clsstr)
                if res is not None:
                    restext += f" ({res['uri']})"
                if cls not in uritotreeitem:
                    # print("SUPER NOT NONE: " + str({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {}}))
                    if cls in instancecount:
                        result.append({"id": cls, "parent": "#", "type": "class","instancecount":instancecount[cls], "text": restext,
                                       "data": {"from": defaultdict(lambda: defaultdict(int)), "to": defaultdict(lambda: defaultdict(int))}})
                    else:
                        result.append({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}})
                    uritotreeitem[cls].append(result[-1])
            else:
                if cls in ress and "label" in cls and ress[cls]["label"] is not None:
                    if res is not None:
                        restext = f"{ress[cls]['label']} ({res['uri']})"
                    else:
                        restext = f"{ress[cls]['label']} ({DocUtils.shortenURI(clsstr)})"
                else:
                    if res is not None:
                        restext = f" ({res['uri']})"
                    else:
                        restext = DocUtils.shortenURI(clsstr)
                if cls not in uritotreeitem:
                    if cls in instancecount:
                        result.append({"id": cls, "parent": ress[cls]["super"],"instancecount":instancecount[cls], "type": "class", "text": restext,
                                       "data": {"from": defaultdict(lambda: defaultdict(int)), "to": defaultdict(lambda: defaultdict(int))}})
                    else:
                        result.append({"id": cls, "parent": ress[cls]["super"], "type": "class", "text": restext, "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}})
                    uritotreeitem[cls].append(result[-1])
                else:
                    uritotreeitem[cls][-1]["parent"] = ress[cls]["super"]
                ressuperstr = str(ress[cls]["super"])
                if ressuperstr not in uritotreeitem:
                    # print("SUPER NOT IN URITOTREEITEM: "+str(ress[cls]["super"])+" ... adding with empty superclass statement...")
                    uritotreeitem[ressuperstr] = []
                    clsres = DocUtils.replaceNameSpacesInLabel(prefixes, ressuperstr)
                    if clsres is not None:
                        theitem = {"id": ressuperstr, "parent": "#", "type": "class",
                                   "text": f'{DocUtils.shortenURI(ressuperstr)} ({clsres["uri"]})', "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}}
                    else:
                        theitem = {"id": ressuperstr, "parent": "#", "type": "class",
                                   "text": DocUtils.shortenURI(ressuperstr), "data": {"from":defaultdict(lambda: defaultdict(int)),"to":defaultdict(lambda: defaultdict(int))}}
                    uritotreeitem[ressuperstr].append(theitem)
                    result.append(theitem)
                classidset.add(ressuperstr)
            classidset.add(clsstr)
        tree["core"]["data"] = result
        return [tree, uritotreeitem, len(classidset)]

    @staticmethod
    def assignGeoClassesToTree(tree):
        classlist = {}
        for item in tree["core"]["data"]:
            if item["type"] == "class":
                classlist[item["id"]] = {"items": 0, "geoitems": 0, "item": item}
        for item in tree["core"]["data"]:
            if item["type"] == "instance" and item["parent"] in classlist:
                classlist[item["parent"]]["items"] += 1
            elif (item["type"] == "geoinstance" or item["type"] == "featurecollection" or item[
                "type"] == "geocollection") and item["parent"] in classlist:
                classlist[item["parent"]]["items"] += 1
                classlist[item["parent"]]["geoitems"] += 1
        for item in classlist:
            if classlist[item]["items"] > 0:
                if classlist[item]["item"]["text"].endswith("]"):
                    classlist[item]["item"]["text"] = f'{classlist[item]["item"]["text"][0:classlist[item]["item"]["text"].rfind("[") - 1]} [{classlist[item]["items"]}]'
                else:
                    classlist[item]["item"]["text"] = f'{classlist[item]["item"]["text"]} [{classlist[item]["items"]}]'
            if item in DocConfig.collectionclasses:
                classlist[item]["item"]["type"] = "collectionclass"
            elif classlist[item]["items"] == classlist[item]["geoitems"] and classlist[item]["items"] > 0 and classlist[item]["geoitems"] > 0:
                classlist[item]["item"]["type"] = "geoclass"
            elif classlist[item]["items"] > classlist[item]["geoitems"] > 0:
                classlist[item]["item"]["type"] = "halfgeoclass"
            else:
                classlist[item]["item"]["type"] = "class"
        return classlist

    @staticmethod
    def checkGeoInstanceAssignment(uritotreeitem):
        for uri in uritotreeitem:
            if len(uritotreeitem[uri]) > 1:
                thetype = "instance"
                counter = 0
                if uritotreeitem[uri] is not None:
                    for item in uritotreeitem[uri]:
                        if item["type"] != "instance" or item["type"] != "class":
                            thetype = item["type"]
                        if item["type"] != "class":
                            item["id"] = f'{item["id"]}_suniv{counter}_'
                        counter += 1
                    if thetype != "instance" or thetype != "class":
                        for item in uritotreeitem[uri]:
                            item["type"] = thetype