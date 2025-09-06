
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
            #print("Generate IIIF Annotations for " + str(imgpath) + " with " + str(imagetoURI[imgpath]))
            if "uri" in imagetoURI[imgpath]:
                for ur in imagetoURI[imgpath]["uri"]:
                    # print(ur)
                    sur = DocUtils.shortenURI(ur)
                    # print("Getting "+outpath+"/iiif/mf/"+sur+"/manifest.json")
                    mf=f'{outpath}/iiif/mf/{sur}/manifest.json'
                    if os.path.exists(mf) and "anno" in imagetoURI[imgpath]:
                        with open(mf, 'r', encoding="utf-8") as f:
                            curmanifest = json.load(f)
                        annocounter = 2
                        for anno in imagetoURI[imgpath]["anno"]:
                            anno["id"] = f"{imgpath}/canvas/p2/anno-{annocounter}"
                            anno["target"]["source"] = f"{imgpath}/canvas/p1"
                            if "bodies" in imagetoURI[imgpath]["uri"]:
                                anno["body"] = [anno["body"]]
                                anno["body"] += imagetoURI[imgpath]["uri"]["bodies"]
                            curmanifest["items"][0]["annotations"][0]["items"].append(anno)
                            annocounter += 1
                        with open(mf, 'w', encoding="utf-8") as f:
                            json.dump(curmanifest,f)

    @staticmethod
    def generateIIIFManifest(g, outpath, deploypath, imgpaths, annos, annobodies, curind, prefixnamespace, imagetoURI, imagemetadata,metadatanamespaces, label="",
                             summary="", thetypes=None, predobjmap=None, maintype="Image"):
        #print("GENERATE IIIF Manifest for " + str(outpath) + " " + str(curind) + " " + str(label) + " " + str(
        #    summary) + " " + str(annobodies))
        #print(predobjmap)
        #print(outpath)
        #print(curind)
        #print(DocUtils.shortenURI(curind))
        curinduri = DocUtils.shortenURI(curind)
        if not os.path.exists(outpath + "/iiif/mf/" + curinduri + "/manifest.json"):
            if not os.path.exists(outpath + "/iiif/mf/"):
                os.makedirs(outpath + "/iiif/mf/")
            if not os.path.exists(outpath + "/iiif/images/"):
                os.makedirs(outpath + "/iiif/images/")
            if not os.path.exists(outpath + "/iiif/svg/"):
                os.makedirs(outpath + "/iiif/svg/")
            #print(label)
            if label != "":
                curiiifmanifest = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                   "id": deploypath + "/iiif/mf/" + curinduri + "/manifest.json",
                                   "type": "Manifest",
                                   "label": {"en": [f"{label} ({curinduri})"]}, "homepage": [
                        {"id": str(curind).replace(prefixnamespace, deploypath + "/"), "type": "Text",
                         "label": {"en": [str(curind).replace(prefixnamespace, deploypath + "/")]},
                         "format": "text/html", "language": ["en"]}], "metadata": [], "items": []}
            else:
                curiiifmanifest = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                   "id": deploypath + "/iiif/mf/" + curinduri + "/manifest.json",
                                   "type": "Manifest", "label": {"en": [curinduri]}, "homepage": [
                        {"id": str(curind).replace(prefixnamespace, deploypath + "/"), "type": "Text",
                         "label": {"en": [str(curind).replace(prefixnamespace, deploypath + "/")]},
                         "format": "text/html", "language": ["en"]}], "metadata": [], "items": []}
            pagecounter = 1
            for imgpath in imgpaths:
                pcstr=str(pagecounter)
                if imgpath.startswith("<svg") and "http" not in imgpath:
                    with open(f"{outpath}/iiif/svg/{curinduri}_{pcstr}.svg", "w", encoding="utf-8") as f:
                        f.write(str(imgpath).replace("<svg","<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" "))
                    imgpath = f"{deploypath}/iiif/svg/{curinduri}_{pcstr}.svg"
                if imgpath not in imagetoURI:
                    imagetoURI[imgpath] = {}
                if "anno" not in imagetoURI[imgpath]:
                    imagetoURI[imgpath]["anno"] = []
                height = 480
                width = 640
                if "width" not in imagetoURI[imgpath]:
                    res = DocUtils.checkImgMetadataRDF(g, imgpath)
                    if "width" in res:
                        #print("Found image width in KG: " + str(res["width"]))
                        imagetoURI[imgpath]["width"] = res["width"]
                    if "height" in res:
                        imagetoURI[imgpath]["height"] = res["height"]
                        #print("Found image height in KG: " + str(res["width"]))
                if imgpath not in imagetoURI or "width" not in imagetoURI[imgpath]:
                    if imagemetadata:
                        try:
                            #print("Loading image for " + str(imgpath))
                            response = requests.get(imgpath)
                            im = Image.open(BytesIO(response.content))
                            #print(im.size)
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
                curitem = {"id": f"{imgpath}/canvas/p{pcstr}", "height": height, "width": width,
                           "type": "Canvas",
                           "label": {"en": [f'{label} {maintype} {pagecounter + 1}']}, "items": [
                        {"id": f"{imgpath}/canvas/p{pcstr}/1", "type": "AnnotationPage", "items": [
                            {"id": f"{imgpath}/annotation/p{pcstr}/1", "type": "Annotation",
                             "motivation": "painting",
                             "body": {"id": imgpath, "type": str(maintype), "format": "image/png"},
                             "target": f'{imgpath}/canvas/p{pcstr}'}]}], "annotations": [
                        {"id": f"{imgpath}/canvas/p{pcstr}/annopage-2", "type": "AnnotationPage",
                         "items": []}]}
                curiiifmanifest["items"].append(curitem)
                pagecounter += 1
            for pred in predobjmap:
                for objs in predobjmap[pred]:
                    if isinstance(objs, URIRef):
                        curiiifmanifest["metadata"].append({"label": {"en": [DocUtils.shortenURI(str(pred))]}, "value": {
                            "en": [f"<a href=\"{objs}\">{objs}</a>"]}})
                    else:
                        curiiifmanifest["metadata"].append({"label": {"en": [DocUtils.shortenURI(str(pred))]}, "value": {"en": [str(objs)]}})
            # print(curiiifmanifest["metadata"])
            if summary is not None and summary != "" and summary != {}:
                curiiifmanifest["summary"] = {"en": [str(summary)]}
            os.makedirs(f"{outpath}/iiif/mf/{curinduri}")
            with open(f"{outpath}/iiif/mf/{curinduri}/manifest.json", "w", encoding="utf-8") as f:
                json.dump(curiiifmanifest,f)
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
        return {"url": f"{outpath}/iiif/mf/{curinduri}/manifest.json", "imgpath": list(imgpaths.keys()), "label": str(label),
                "class": besttype,"ind":curind}

    @staticmethod
    def generateImageGrid(outpath,deploypath,imagespaths,imagegridtemplate,headertemplate,footertemplate,targetfile=None):
        categories=set()
        imghtml=""
        for imgpath in imagespaths:
            #print("IMAGEPATH: "+str(imgpath))
            categories.add(DocUtils.shortenURI(imgpath["class"]))
            for imgp in imgpath["imgpath"]:
                induri=DocUtils.shortenURI(imgpath["ind"])
                imghtml+="<li data-groups='[\"all\",\"red\",\""+str(imgpath["class"])+"\"]' style=\"width:25%;background-color:white;border-radius:25px;\"><figure class=\"col-3@sm picture-item\"><div class=\"aspect aspect--16x9\"><div class=\"aspect__inner\">"
                imghtml+=f'<a href={deploypath}/{induri}" target="_blank"><img src="{imgp}" loading="lazy" class="imgborder" alt="{imgpath["label"]}"/></a></div></div><figcaption style="color:black"><a href="{deploypath}/{induri}" style="font-weight:bold;color:black" target="_blank">'
                if imgpath["label"]!="":
                   imghtml+=f'{imgpath["label"]}</a></figcaption></figure></li>'
                else:
                   imghtml += f'{DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", ""))}</a></figcaption></figure></li>'
        if targetfile is not None:
            with open(targetfile, "w",encoding="utf-8") as f:
                f.write(headertemplate)
                f.write(imagegridtemplate.replace("{{imagecontainers}}",imghtml).replace("{{categories}}",str(categories).replace("{","").replace("}","")))
                f.write(footertemplate)
        else:
            imggrid=headertemplate
            imggrid+=imagegridtemplate.replace("{{imagecontainers}}",imghtml).replace("{{categories}}",str(categories).replace("{","").replace("}",""))
            imggrid+=footertemplate
            return imggrid

    @staticmethod
    def generateIIIFCollections(outpath, deploypath, imagespaths, prefixnamespace):
        deploypath=str(deploypath)
        apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + deploypath + "/iiif/api.json\"; const apiUrl = \"" + deploypath + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
        apijson = {"openapi": "3.0.1", "info": {"title": deploypath + " IIIF", "description": "IIIF API of " + deploypath},"servers": [{"url": deploypath}], "paths": {}}
        apijson["paths"]["/iiif/collection/"] = {"get": {"tags": ["IIIF"],
                                                                                "summary": "Retrieves IIIF Collections of "+deploypath,
                                                                                "description": "Retrieves the IIIF Collections of this IIIF API",
                                                                                "operationId": "iiif-collections","parameters": [],
                                                                                "responses": {
                                                                                    "200": {"description": "Success",
                                                                                        "content": {"text/plain": {"example": None}},
                                                                                        "application/json": {"schema": {"example": None},"example": None},
                                                                                        "text/json": {"schema": {"example": None},"example": None}}}}}
        apijson["paths"]["/iiif/{id}/manifest"] = {"get": {"tags": ["IIIF"],
                                                                                "summary": "Retrieves a IIIF manifest with a given ID",
                                                                                "description": "Retrieves a IIIF manifest with a given ID",
                                                                                "operationId": "iiif-manifest","parameters": [{"in":"path","name":"id","required":True,"schema": {"type": "string"}}],
                                                                                "responses": {
                                                                                    "200": {
                                                                                        "description": "Success",
                                                                                        "content": {"text/plain": {"example": None}},
                                                                                        "application/json": {"schema": {"example": None},"example": None},
                                                                                        "text/json": {"schema": {"example": None},"example": None}}}}}
        if not os.path.exists(outpath + "/iiif/collection/"):
            os.makedirs(outpath + "/iiif/collection/")
        if os.path.exists(outpath + "/iiif/collection/iiifcoll.json"):
            collections = {}
            with open(outpath+"/iiif/collection/iiifcoll.json","r",encoding="utf-8") as f:
                collections["main"]=json.load(f)
        else:
            collections = {"main": {"@context": "http://iiif.io/api/presentation/3/context.json",
                                    "id": f"{deploypath}/iiif/collection/iiifcoll.json", "type": "Collection",
                                    "label": {"en": ["Collection: " + DocUtils.shortenURI(str(prefixnamespace))]},
                                    "items": []}}
        seenurls = set()
        for imgpath in sorted(imagespaths, key=lambda k: k['label'], reverse=False):
            curclass = "main"
            collections.setdefault("main",{"items":[]})
            if "class" in imgpath and imgpath["class"] != "":
                curclass = imgpath["class"]
                if curclass not in collections:
                    collections[curclass] = {"@context": "http://iiif.io/api/presentation/3/context.json",
                                             "id": f"{deploypath}/iiif/collection/{DocUtils.shortenURI(curclass)}.json",
                                             "type": "Collection", "label": {"en": ["Collection: " + str(curclass)]},
                                             "items": []}
            if imgpath["url"] not in seenurls:
                if imgpath["label"] != "":
                    collections[curclass]["items"].append({"full": f'{outpath}/iiif/images/{DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", ""))}/full/full/0/default.jpg',"id": imgpath["url"].replace(outpath, deploypath),
                                                           "type": "Manifest", "label": {"en": [
                            f'{imgpath["label"]} ({DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", "")[ 0:imgpath["url"].replace("/manifest.json","").rfind(".")])})']}})
                else:
                    collections[curclass]["items"].append({"full": f'{outpath}/iiif/images/{DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", ""))}/full/full/0/default.jpg',"id": imgpath["url"].replace(outpath, deploypath),
                        "type": "Manifest", "label": {"en": [DocUtils.shortenURI(imgpath["url"].replace("/manifest.json", ""))]}})
            seenurls = imgpath["url"]
        for coll in collections:
            if coll!="main":
                collections["main"]["items"].append(collections[coll])
                with open(f"{outpath}/iiif/collection/{DocUtils.shortenURI(coll)}.json","w",encoding="utf-8") as f:
                    json.dump(collections[coll],f)
        with open(f"{outpath}/iiif/collection/iiifcoll.json", "w", encoding="utf-8") as f:
            json.dump(collections["main"],f)
        iiifindex = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://unpkg.com/mirador@latest/dist/mirador.min.js"></script></head><body><link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500"><div id="my-mirador"/><script type="text/javascript">var mirador = Mirador.viewer({"id": "my-mirador","manifests": {"collection/iiifcoll.json": {"provider": "Harvard University"}},"windows": [{"loadedManifest": "collection/iiifcoll.json","canvasIndex": 2,"thumbnailNavigationPosition": 'far-bottom'}]});</script></body></html>"""
        with open(f"{outpath}/iiif/index.html", "w", encoding="utf-8") as f:
            f.write(iiifindex)
        with open(f"{outpath}/iiif/api.html", "w", encoding="utf-8") as f:
            f.write(apihtml)
        with open(f"{outpath}/iiif/api.json", "w", encoding="utf-8") as f:
            json.dump(apijson,f)