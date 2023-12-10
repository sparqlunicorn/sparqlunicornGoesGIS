
import os
import json
import requests
from PIL import Image
from io import BytesIO

from rdflib import URIRef

from ...doc.docutils import DocUtils


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
    def generateIIIFManifest(g, outpath, deploypath, imgpaths, annos, annobodies, curind, prefixnamespace, imagetoURI, imagemetadata,metadatanamespaces, label="",
                             summary="", thetypes=None, predobjmap=None, maintype="Image"):
        print("GENERATE IIIF Manifest for " + str(outpath) + " " + str(curind) + " " + str(label) + " " + str(
            summary) + " " + str(annobodies))
        print(predobjmap)
        print(outpath)
        print(curind)
        print(DocUtils.shortenURI(curind))
        if not os.path.exists(outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json"):
            if not os.path.exists(outpath + "/iiif/mf/"):
                os.makedirs(outpath + "/iiif/mf/")
            if not os.path.exists(outpath + "/iiif/images/"):
                os.makedirs(outpath + "/iiif/images/")
            if not os.path.exists(outpath + "/iiif/svg/"):
                os.makedirs(outpath + "/iiif/svg/")
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
            pagecounter = 1
            for imgpath in imgpaths:
                if imgpath.startswith("<svg") and "http" not in imgpath:
                    f = open(outpath + "/iiif/svg/" + DocUtils.shortenURI(curind) + "_" + str(pagecounter) + ".svg", "w", encoding="utf-8")
                    f.write(str(imgpath).replace("<svg>","<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">"))
                    f.close()
                    imgpath = outpath + "/iiif/svg/" + DocUtils.shortenURI(curind) + "_" + str(pagecounter) + ".svg"
                if imgpath not in imagetoURI:
                    imagetoURI[imgpath] = {}
                if "anno" not in imagetoURI[imgpath]:
                    imagetoURI[imgpath]["anno"] = []
                height = 480
                width = 640
                if "width" not in imagetoURI[imgpath]:
                    res = DocUtils.checkImgMetadataRDF(g, imgpath)
                    if "width" in res:
                        print("Found image width in KG: " + str(res["width"]))
                        imagetoURI[imgpath]["width"] = res["width"]
                    if "height" in res:
                        imagetoURI[imgpath]["height"] = res["height"]
                        print("Found image height in KG: " + str(res["width"]))
                if imgpath not in imagetoURI or "width" not in imagetoURI[imgpath]:
                    if imagemetadata:
                        try:
                            print("Loading image for " + str(imgpath))
                            response = requests.get(imgpath)
                            im = Image.open(BytesIO(response.content))
                            print(im.size)
                            # print(type(im.size))
                            w, h = im.size
                            width = w
                            height = h
                            imagetoURI[imgpath]["width"] = w
                            imagetoURI[imgpath]["height"] = h
                        except Exception as e:
                            imagetoURI[imgpath]["width"] = 640
                            imagetoURI[imgpath]["height"] = 480
                else:
                    height = imagetoURI[imgpath]["height"]
                    width = imagetoURI[imgpath]["width"]
                curitem = {"id": imgpath + "/canvas/p" + str(pagecounter), "height": height, "width": width,
                           "type": "Canvas",
                           "label": {"en": [str(label) + " " + str(maintype) + " " + str(pagecounter + 1)]}, "items": [
                        {"id": imgpath + "/canvas/p" + str(pagecounter) + "/1", "type": "AnnotationPage", "items": [
                            {"id": imgpath + "/annotation/p" + str(pagecounter) + "/1", "type": "Annotation",
                             "motivation": "painting",
                             "body": {"id": imgpath, "type": str(maintype), "format": "image/png"},
                             "target": imgpath + "/canvas/p" + str(pagecounter)}]}], "annotations": [
                        {"id": imgpath + "/canvas/p" + str(pagecounter) + "/annopage-2", "type": "AnnotationPage",
                         "items": []}]}
                curiiifmanifest["items"].append(curitem)
                pagecounter += 1
            for pred in predobjmap:
                for objs in predobjmap[pred]:
                    if isinstance(objs, URIRef):
                        curiiifmanifest["metadata"].append({"label": {"en": [DocUtils.shortenURI(str(pred))]}, "value": {
                            "en": ["<a href=\"" + str(objs) + "\">" + str(objs) + "</a>"]}})
                    else:
                        curiiifmanifest["metadata"].append(
                            {"label": {"en": [DocUtils.shortenURI(str(pred))]}, "value": {"en": [str(objs)]}})
            # print(curiiifmanifest["metadata"])
            if summary != None and summary != "" and summary != {}:
                curiiifmanifest["summary"] = {"en": [str(summary)]}
            os.makedirs(outpath + "/iiif/mf/" + DocUtils.shortenURI(curind))
            f = open(outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json", "w", encoding="utf-8")
            f.write(json.dumps(curiiifmanifest))
            f.close()
        # if annos!=None:
        #    self.generateIIIFAnnotations(self.outpath,annos,curind,next(iter(imgpaths)))
        besttype = ""
        for typee in thetypes:
            prefix = DocUtils.shortenURI(typee, True)
            if prefix not in metadatanamespaces:
                besttype = typee
                break
        if besttype == "" and len(thetypes) > 0:
            besttype = next(iter(thetypes))
        return {"url": outpath + "/iiif/mf/" + DocUtils.shortenURI(curind) + "/manifest.json", "label": str(label),
                "class": besttype}

    @staticmethod
    def generateImageGrid(deploypath,imagespaths,imagegridtemplate,targetfile=None):
        categories=set()
        imghtml=""
        for imgpath in sorted(imagespaths, key=lambda k: k['label'], reverse=False):
            categories.add(DocUtils.shortenURI(imgpath["class"]))
            imghtml+="<li data-groups='[\"all\",\"red\",\""+str(imgpath["class"])+"\"]' style=\"width:25%;background-color:white;border-radius:25px;\"><figure class=\"col-3@sm picture-item\"><div class=\"aspect aspect--16x9\"><div class=\"aspect__inner\">"
            imghtml+="<a href=\""+str(deploypath)+"\"><img src=\"{{site.baseurl}}/assets/images/placeholder.png\" loading=\"lazy\" class=\"imgborder\" onerror=\"this.onerror=null; this.src='{{site.baseurl_root}}/assets/images/placeholder.png'\" alt=\"{{textName}}\"/></a></div></div>"
            imghtml+="<figcaption style=\"color:black\"><a href="+str(deploypath)+"/"+imgpath["url"]+"\" style=\"font-weight:bold;color:black\">"+str(imgpath["label"])+"</a></figcaption></figure></li>"
        if targetfile!=None:
            f = open(targetfile, "w")
            f.write(imagegridtemplate.replace("{{imagecontainers}}",imghtml).replace("{{categories}}",str(categories)))
            f.close()
        else:
            return imagegridtemplate.replace("{{imagecontainers}}",imghtml).replace("{{categories}}",str(categories))

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
                                             "id": deploypath + "/iiif/collection/" + DocUtils.shortenURI(curclass) + ".json",
                                             "type": "Collection", "label": {"en": ["Collection: " + str(curclass)]},
                                             "items": []}
            if imgpath["url"] not in seenurls:
                if imgpath["label"] != "":
                    collections[curclass]["items"].append({"full": outpath + "/iiif/images/" + DocUtils.shortenURI(
                        imgpath["url"].replace("/manifest.json", "")) + "/full/full/0/default.jpg","id": imgpath["url"].replace(outpath, deploypath),
                                                           "type": "Manifest", "label": {"en": [
                            imgpath["label"] + " (" + DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", "")[
                                                                      0:imgpath["url"].replace("/manifest.json","").rfind(".")]) + ")"]}})
                else:
                    collections[curclass]["items"].append({"full": outpath + "/iiif/images/" + DocUtils.shortenURI(
                        imgpath["url"].replace("/manifest.json", "")) + "/full/full/0/default.jpg","id": imgpath["url"].replace(outpath, deploypath),
                        "type": "Manifest", "label": {"en": [DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", ""))]}})
            seenurls = imgpath["url"]
        for coll in collections:
            if coll!="main":
                collections["main"]["items"].append(collections[coll])
                f=open(outpath+"/iiif/collection/"+str(DocUtils.shortenURI(coll))+".json","w",encoding="utf-8")
                f.write(json.dumps(collections[coll]))
                f.close()
        f = open(outpath + "/iiif/collection/iiifcoll.json", "w", encoding="utf-8")
        f.write(json.dumps(collections["main"]))
        f.close()
        iiifindex = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/mirador@latest/dist/mirador.min.js"></script></head><body><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500"><div id="my-mirador"/><script type="text/javascript">var mirador = Mirador.viewer({"id": "my-mirador","manifests": {"collection/iiifcoll.json": {"provider": "Harvard University"}},"windows": [{"loadedManifest": "collection/iiifcoll.json","canvasIndex": 2,"thumbnailNavigationPosition": 'far-bottom'}]});</script></body></html>"""
        f = open(outpath + "/iiif/index.html", "w", encoding="utf-8")
        f.write(iiifindex)
        f.close()