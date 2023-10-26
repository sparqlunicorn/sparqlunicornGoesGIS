
import os
import json

from ...doc.docutils import DocUtils
from rdflib import URIRef


class IIIFAPIExporter:

    @staticmethod
    def generateIIIFAnnotations(outpath,imagetoURI):
        for imgpath in imagetoURI:
            print("Generate IIIF Annotations for " + str(imgpath) + " with " + str(imagetoURI[imgpath]))
            if "uri" in imagetoURI[imgpath]:
                for ur in imagetoURI[imgpath]["uri"]:
                    # print(ur)
                    sur = DocUtils.shortenURI(ur)
                    # print("Getting "+outpath+"/iiif/mf/"+sur+"/manifest.json")
                    if os.path.exists(outpath + "/iiif/mf/" + sur + "/manifest.json") and "anno" in imagetoURI[imgpath]:
                        f = open(outpath + "/iiif/mf/" + sur + "/manifest.json", 'r', encoding="utf-8")
                        curmanifest = json.loads(f.read())
                        f.close()
                        annocounter = 2
                        for anno in imagetoURI[imgpath]["anno"]:
                            anno["id"] = imgpath + "/canvas/p2/anno-" + str(annocounter)
                            anno["target"]["source"] = imgpath + "/canvas/p1"
                            if "bodies" in imagetoURI[imgpath]["uri"]:
                                anno["body"] = [anno["body"]]
                                anno["body"] += imagetoURI[imgpath]["uri"]["bodies"]
                            curmanifest["items"][0]["annotations"][0]["items"].append(anno)
                            annocounter += 1
                        f = open(outpath + "/iiif/mf/" + sur + "/manifest.json", 'w', encoding="utf-8")
                        f.write(json.dumps(curmanifest))
                        f.close()

    @staticmethod
    def generateIIIFManifest(outpath, deploypath, imgpaths, annos, curind, prefixnamespace, label="", summary="",
                             thetypes=None, predobjmap=None, maintype="Image"):
        print("GENERATE IIIF Manifest for " + str(outpath) + " " + str(curind) + " " + str(label) + " " + str(
            summary) + " " + str(predobjmap))
        if not os.path.exists(outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json"):
            if not os.path.exists(outpath + "/iiif/mf/"):
                os.makedirs(outpath + "/iiif/mf/")
            if not os.path.exists(outpath + "/iiif/images/"):
                os.makedirs(outpath + "/iiif/images/")
            print(label)
            if label != "":
                curiiifmanifest = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                   "id": deploypath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json",
                                   "type": "Manifest",
                                   "label": {"en": [str(label) + " (" + DocUtils.shortenURI(curind) + ")"]}, "homepage": [
                        {"id": str(curind).replace(prefixnamespace, deploypath + "/"), "type": "Text",
                         "label": {"en": [str(curind).replace(prefixnamespace, deploypath + "/")]},
                         "format": "text/html", "language": ["en"]}], "metadata": [], "items": []}
            else:
                curiiifmanifest = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                   "id": deploypath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json",
                                   "type": "Manifest", "label": {"en": [DocUtils.shortenURI(curind)]}, "homepage": [
                        {"id": str(curind).replace(prefixnamespace, deploypath + "/"), "type": "Text",
                         "label": {"en": [str(curind).replace(prefixnamespace, deploypath + "/")]},
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
                                                 DocUtils.shortenURI(curind)) + "</a>"},
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
                                              DocUtils.shortenURI(curind)) + "</a>"},
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
                        curiiifmanifest["metadata"].append({"label": {"en": [DocUtils.shortenURI(str(pred))]}, "value": {
                            "en": ["<a href=\"" + str(objs) + "\">" + str(objs) + "</a>"]}})
                    else:
                        curiiifmanifest["metadata"].append(
                            {"label": {"en": [DocUtils.shortenURI(str(pred))]}, "value": {"en": [str(objs)]}})
            print(curiiifmanifest["metadata"])
            if summary != None and summary != "" and summary != {}:
                curiiifmanifest["summary"] = {"en": [str(summary)]}
            # os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/")
            # os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/full/")
            # os.makedirs(self.outpath + "/iiif/images/"+self.shortenURI(imgpath)+"/full/full/0/")
            os.makedirs(outpath + "/iiif/mf/" + DocUtils.shortenURI(curind))
            f = open(outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json", "w", encoding="utf-8")
            f.write(json.dumps(curiiifmanifest))
            f.close()
        if thetypes != None and len(thetypes) > 0:
            return {"url": outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json", "label": str(label),
                    "class": next(iter(thetypes))}
        return {"url": outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json", "label": str(label),
                "class": ""}

    @staticmethod
    def generateIIIFCollections(outpath, deploypath, imagespaths, prefixnamespace):
        if not os.path.exists(outpath + "/iiif/collection/"):
            os.makedirs(outpath + "/iiif/collection/")
        if os.path.exists(outpath + "/iiif/collection/iiifcoll.json"):
            f = open(outpath + "/iiif/collection/iiifcoll.json", "r", encoding="utf-8")
            collections = json.loads(f.read())
            f.close()
        else:
            collections = {"main": {"@context": "http://iiif.io/api/presentation/3/context.json",
                                    "id": deploypath + "/iiif/collection/iiifcoll.json", "type": "Collection",
                                    "label": {"en": ["Collection: " + DocUtils.shortenURI(str(prefixnamespace))]},
                                    "items": []}}
        seenurls = set()
        for imgpath in sorted(imagespaths, key=lambda k: k['label'], reverse=False):
            curclass = "main"
            if "class" in imgpath and imgpath["class"] != "":
                curclass = imgpath["class"]
                if curclass not in collections:
                    collections[curclass] = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                             "id": deploypath + "/iiif/collection/" +DocUtils.shortenURI(curclass) + ".json",
                                             "type": "Collection", "label": {"en": ["Collection: " + str(curclass)]},
                                             "items": []}
            if imgpath["url"] not in seenurls:
                if imgpath["label"] != "":
                    collections[curclass]["items"].append({"full": outpath + "/iiif/images/" + DocUtils.shortenURI(
                        imgpath["url"].replace("/manifest.json", "")) + "/full/full/0/default.jpg",
                                                           "id": imgpath["url"].replace(outpath, deploypath),
                                                           "type": "Manifest", "label": {"en": [
                            imgpath["label"] + " (" + DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", "")[
                                                                      0:imgpath["url"].replace("/manifest.json",
                                                                                               "").rfind(
                                                                          ".")]) + ")"]}})
                else:
                    collections[curclass]["items"].append({"full": outpath + "/iiif/images/" + DocUtils.shortenURI(
                        imgpath["url"].replace("/manifest.json", "")) + "/full/full/0/default.jpg",
                                                           "id": imgpath["url"].replace(outpath, deploypath),
                                                           "type": "Manifest", "label": {
                            "en": [DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", ""))]}})
            seenurls = imgpath["url"]
        for coll in collections:
            if coll!="main":
                collections["main"]["items"].append(collections[coll])
                f=open(outpath+"/iiif/collection/"+str(coll)+".json","w",encoding="utf-8")
                f.write(json.dumps(collections[coll]))
                f.close()
        f = open(outpath + "/iiif/collection/iiifcoll.json", "w", encoding="utf-8")
        f.write(json.dumps(collections["main"]))
        f.close()
        iiifindex = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/mirador@latest/dist/mirador.min.js"></script></head><body><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500"><div id="my-mirador"/><script type="text/javascript">var mirador = Mirador.viewer({"id": "my-mirador","manifests": {"collection/iiifcoll.json": {"provider": "Harvard University"}},"windows": [{"loadedManifest": "collection/iiifcoll.json","canvasIndex": 2,"thumbnailNavigationPosition": 'far-bottom'}]});</script></body></html>"""
        f = open(outpath + "/iiif/index.html", "w", encoding="utf-8")
        f.write(iiifindex)
        f.close()