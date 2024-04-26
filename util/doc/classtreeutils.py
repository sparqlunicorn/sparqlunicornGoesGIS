from .docconfig import DocConfig
from .docutils import DocUtils
from ..sparqlutils import SPARQLUtils
from rdflib import URIRef

class ClassTreeUtils:


    @staticmethod
    def getClassTree(graph, uritolabel, classidset, uritotreeitem,typeproperty,prefixes,preparedclassquery):
        results = graph.query(preparedclassquery)
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
            },
                "core": {"themes": {"responsive": True}, "check_callback": True, "data": []}}
        tree["@context"] = ldcontext["@context"]
        result = []
        ress = {}
        for res in results:
            # print(res)
            if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
                if "_:" not in str(res["supertype"]) and str(res["supertype"]).startswith("http"):
                    ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
                else:
                    ress[str(res["subject"])] = {"super": None, "label": res["label"]}
        # print(ress)
        for cls in ress:
            for obj in graph.subjects(URIRef(typeproperty), URIRef(cls), True):
                res = DocUtils.replaceNameSpacesInLabel(prefixes, str(obj))
                if str(obj) in uritolabel:
                    restext = uritolabel[str(obj)]["label"] + " (" + DocUtils.shortenURI(str(obj)) + ")"
                    if res is not None:
                        restext = uritolabel[str(obj)]["label"] + " (" + res["uri"] + ")"
                else:
                    restext = DocUtils.shortenURI(str(obj))
                    if res is not None:
                        restext += " (" + res["uri"] + ")"
                if str(obj) not in SPARQLUtils.collectionclasses:
                    result.append({"id": str(obj), "parent": cls, "type": "instance", "text": restext, "data": {}})
                else:
                    result.append({"id": str(obj), "parent": cls, "type": "class", "text": restext, "data": {}})
                if str(obj) not in uritotreeitem:
                    uritotreeitem[str(obj)] = []
                uritotreeitem[str(obj)].append(result[-1])
                # classidset.add(str(obj))
            res = DocUtils.replaceNameSpacesInLabel(prefixes, str(cls))
            if ress[cls]["super"] is None:
                restext = DocUtils.shortenURI(str(cls))
                if res is not None:
                    restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": "#", "type": "class", "text": restext, "data": {}})
                    uritotreeitem[str(cls)] = []
                    uritotreeitem[str(cls)].append(result[-1])
            else:
                if "label" in cls and ress[cls]["label"] is not None:
                    restext = ress[cls]["label"] + " (" + DocUtils.shortenURI(str(cls)) + ")"
                    if res is not None:
                        restext = ress[cls]["label"] + " (" + res["uri"] + ")"
                else:
                    restext = DocUtils.shortenURI(str(cls))
                    if res is not None:
                        restext += " (" + res["uri"] + ")"
                if cls not in uritotreeitem:
                    result.append({"id": cls, "parent": ress[cls]["super"], "type": "class", "text": restext, "data": {}})
                    if str(cls) not in uritotreeitem:
                        uritotreeitem[str(cls)] = []
                        uritotreeitem[str(cls)].append(result[-1])
                else:
                    uritotreeitem[cls][-1]["parent"] = ress[cls]["super"]
                if str(ress[cls]["super"]) not in uritotreeitem:
                    uritotreeitem[str(ress[cls]["super"])] = []
                    clsres = DocUtils.replaceNameSpacesInLabel(prefixes, str(ress[cls]["super"]))
                    if clsres is not None:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class",
                                   "text": DocUtils.shortenURI(str(ress[cls]["super"])) + " (" + clsres["uri"] + ")",
                                   "data": {}}
                    else:
                        theitem = {"id": str(ress[cls]["super"]), "parent": "#", "type": "class","text": DocUtils.shortenURI(str(ress[cls]["super"])), "data": {}}
                    uritotreeitem[str(ress[cls]["super"])].append(theitem)
                    result.append(theitem)
                classidset.add(str(ress[cls]["super"]))
            classidset.add(str(cls))
        tree["core"]["data"] = result
        return tree

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
                    classlist[item]["item"]["text"] = classlist[item]["item"]["text"][
                                                      0:classlist[item]["item"]["text"].rfind("[") - 1] + " [" + str(
                        classlist[item]["items"]) + "]"
                else:
                    classlist[item]["item"]["text"] = classlist[item]["item"]["text"] + " [" + str(
                        classlist[item]["items"]) + "]"
            if item in SPARQLUtils.collectionclasses:
                classlist[item]["item"]["type"] = "collectionclass"
            elif classlist[item]["items"] == classlist[item]["geoitems"] and classlist[item]["items"] > 0 and \
                    classlist[item]["geoitems"] > 0:
                classlist[item]["item"]["type"] = "geoclass"
            elif classlist[item]["items"] > classlist[item]["geoitems"] and classlist[item]["geoitems"] > 0:
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
                if uritotreeitem[uri] != None:
                    for item in uritotreeitem[uri]:
                        if item["type"] != "instance" or item["type"] != "class":
                            thetype = item["type"]
                        if item["type"] != "class":
                            item["id"] = item["id"] + "_suniv" + str(counter) + "_"
                        counter += 1
                    if thetype != "instance" or thetype != "class":
                        for item in uritotreeitem[uri]:
                            item["type"] = thetype