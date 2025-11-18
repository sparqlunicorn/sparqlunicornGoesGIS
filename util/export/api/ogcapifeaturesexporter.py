
import os
import json
from pathlib import Path

from ...doc.docutils import DocUtils


class OGCAPIFeaturesExporter:


    @staticmethod
    def generateOGCAPIFeaturesPages(outpath,deploypath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON, contentnegotiation=False):
        apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + str(
            deploypath) + "/api/index.json\"; const apiUrl = \"" + str(
            deploypath) + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
        collectionhtmlname="indexc.html"
        collectiontable=""
        collectionsjson={}
        if contentnegotiation:
            collectionhtmlname="index.html"
        apijson = {"openapi": "3.0.1", "info": {"title": f"{deploypath} Feature Collections",
                                                "description": f"Feature Collections of {deploypath}","version":"1.0"},
                   "servers": [{"url": str(deploypath)}], "paths": {}}
        conformancejson = {"conformsTo": ["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"]}
        if ogcapi:
            apijson["paths"]["/api"] = {
                "get": {"tags": ["Capabilities"], "summary": "api documentation", "description": "api documentation",
                        "operationId": "openApi", "parameters": [], "responses": {
                        "default": {"description": "default response",
                                    "content": {"application/vnd.oai.openapi+json;version=3.0": {},
                                                "application/json": {}, "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/license/dataset"] = {}
            apijson["components"] = {"schemas": {"Conformance": {"type": "object", "properties": {
                "conformsTo": {"type": "array", "items": {"type": "string"}}}, "xml": {"name": "ConformsTo",
                                                                                       "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collection": {"type": "object", "properties": {
                                                     "id": {"type": "string", "xml": {"name": "Id",
                                                                                      "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "title": {"type": "string", "xml": {"name": "Title",
                                                                                         "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "description": {"type": "string", "xml": {"name": "Description",
                                                                                               "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                     "links": {"type": "array", "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "extent": {"$ref": "#/components/schemas/Extent"},
                                                     "itemType": {"type": "string"},
                                                     "crs": {"type": "array", "items": {"type": "string"}},
                                                     "storageCrs": {"type": "string"}}, "xml": {"name": "Collection",
                                                                                                "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collections": {"type": "object", "properties": {
                                                     "links": {"type": "array", "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "collections": {"type": "array", "xml": {"name": "Collection",
                                                                                              "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"},
                                                                     "items": {
                                                                         "$ref": "#/components/schemas/Collection"}}},
                                                                 "xml": {"name": "Collections",
                                                                         "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Extent": {"type": "object", "properties": {
                                                     "spatial": {"$ref": "#/components/schemas/Spatial"},
                                                     "temporal": {"$ref": "#/components/schemas/Temporal"}},
                                                            "xml": {"name": "Extent",
                                                                    "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Link": {"type": "object", "properties": {
                                                     "href": {"type": "string", "xml": {"attribute": True}},
                                                     "rel": {"type": "string", "xml": {"attribute": True}},
                                                     "type": {"type": "string", "xml": {"attribute": True}},
                                                     "title": {"type": "string", "xml": {"attribute": True}}},
                                                          "xml": {"name": "link","namespace": "http://www.w3.org/2005/Atom"}},
                                                 "Spatial": {"type": "object", "properties": {"bbox": {"type": "array",
                                                                                                       "items": {
                                                                                                           "type": "array",
                                                                                                           "items": {
                                                                                                               "type": "number",
                                                                                                               "format": "double"}}},
                                                                                              "crs": {"type": "string",
                                                                                                      "xml": {"attribute": True}}},
                                                             "xml": {"name": "SpatialExtent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Temporal": {"type": "object", "properties": {
                                                     "interval": {"type": "array","items": {"type": "string", "format": "date-time"}},
                                                     "trs": {"type": "string", "xml": {"attribute": True}}},
                                                              "xml": {"name": "TemporalExtent","namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "LandingPage": {"type": "object"}}}
            landingpagejson = {"title": "Landing Page", "description": "Landing Page", "links": [{
                "href": f"{deploypath}/index.json",
                "rel": "self",
                "type": "application/json",
                "title": "this document as JSON"
            }, {
                "href": f"{deploypath}/index.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "this document as HTML"
            }, {
                "href": f"{deploypath}/collections/",
                "rel": "data",
                "type": "application/json",
                "title": "Supported Feature Collections as JSON"
            }, {
                "href": f"{deploypath}/collections/{collectionhtmlname}",
                "rel": "data",
                "type": "text/html",
                "title": "Supported Feature Collections as HTML"
            }, {"href": f"{deploypath}/api/index.json", "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0", "title": "API definition"},
                {"href": f"{deploypath}/api", "rel": "service-desc", "type": "text/html",
                 "title": "API definition as HTML"},
                {"href": f"{deploypath}/conformance", "rel": "conformance", "type": "application/json",
                 "title": "OGC API conformance classes as Json"},
                {"href": f"{deploypath}/conformance", "rel": "conformance", "type": "text/html",
                 "title": "OGC API conformance classes as HTML"}]}

            apijson["paths"]["/"] = {"get": {"tags": ["Capabilities"], "summary": "landing page",
                                             "description": "Landing page of this dataset",
                                             "operationId": "landingPage", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/LandingPage"}},
                        "text/html": {"schema": {}}}}}}}
            apijson["paths"]["/conformance"] = {
                "get": {"tags": ["Capabilities"], "summary": "supported conformance classes",
                        "description": "Retrieves the supported conformance classes", "operationId": "conformance",
                        "parameters": [], "responses": {"default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Conformance"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            collectionsjson = {"collections": [], "links": [
                {"href": deploypath + "collections/index.json", "rel": "self", "type": "application/json",
                 "title": "this document as JSON"},
                {"href": deploypath + "collections/index.html", "rel": "self", "type": "text/html",
                 "title": "this document as HTML"}]}
            collectionshtml = "<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><link rel=\"stylesheet\" href=\"../style.css\"/><link rel=\"stylesheet\" href=\"https://cdn.datatables.net/2.2.1/css/dataTables.dataTables.css\" /><script src=\"https://code.jquery.com/jquery-3.7.1.js\"></script><script src=\"https://cdn.datatables.net/2.2.1/js/dataTables.js\"></script></head><body><header id=\"header\"><h1 id=\"title\">Collections of " + str(
                deploypath) + "</h1></header>{{collectiontable}}<footer id=\"footer\"><a href=\"../\">Landing page</a>&nbsp;<a href=\"index.json\">This page as JSON</a></footer><script>$(document).ready( function () {$('#collectiontable').DataTable();} );</script></body></html>"
            collectiontable = "<table id=\"collectiontable\"><thead><th>Collection</th><th>#Features</th><th>Links</th></thead><tbody>"
            apijson["paths"]["/collections"] = {"get": {"tags": ["Collections"], "summary": "describes collections",
                                                        "description": "Describes all collections provided by this service",
                                                        "operationId": "collections", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            if outpath.endswith("/"):
                outpath = outpath[0:-1]
            os.makedirs(outpath + "/api/",exist_ok=True)
            os.makedirs(outpath + "/license/",exist_ok=True)
            os.makedirs(outpath + "/collections/",exist_ok=True)
            os.makedirs(outpath + "/conformance/",exist_ok=True)
        result = list()
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
            if ogcapi:
                op = f'{outpath}/collections/{DocUtils.replaceColonFromWinPath(coll).replace(outpath, "").replace("index.geojson", "")}/'
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                try:
                    os.makedirs(op,exist_ok=True)
                    os.makedirs(op + "/items/",exist_ok=True)
                    opweb = op.replace(outpath, deploypath)
                    opwebcoll = opweb
                    if opwebcoll.endswith("/"):
                        opwebcoll = opwebcoll[0:-1]
                    opwebcoll = opwebcoll.replace("//", "/")
                    collid=coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]
                    collectionsjson["collections"].append(
                        {"id": collid,
                         "title": featurecollectionspaths[coll]["name"], "links": [
                            {"href": str(opweb.replace(".geojson", "") + "/index.json").replace("//", "/"),
                             "rel": "collection", "type": "application/json", "title": "Collection as JSON"},
                            {"href": str(opweb.replace(".geojson", "") + "/").replace("//", "/"), "rel": "collection",
                             "type": "text/html", "title": "Collection as HTML"},
                            {"href": str(opweb.replace(".geojson", "") + "/index.ttl").replace("//", "/"),
                             "rel": "collection", "type": "text/ttl", "title": "Collection as TTL"}]})
                    currentcollection = {"title": featurecollectionspaths[coll]["name"],"id": collid,"links": [], "itemType": "feature"}
                    currentcollection["links"] = [
                        {"href": opwebcoll + "/items/index.json", "rel": "items", "type": "application/json",
                         "title": "Collection as JSON"},
                        {"href": f"{opwebcoll}/items/{collectionhtmlname}", "rel": "items", "type": "text/html",
                         "title": "Collection as HTML"},
                        {"href": opwebcoll + "/items/index.ttl", "rel": "collection", "type": "text/ttl",
                         "title": "Collection as TTL"}]
                    if "bbox" in curcoll:
                        currentcollection["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                        collectionsjson["collections"][-1]["extent"] = {"spatial": {"bbox": curcoll["bbox"]}}
                    if "crs" in curcoll:
                        currentcollection["crs"] = curcoll["crs"]
                        collectionsjson["collections"][-1]["crs"] = curcoll["crs"]
                        if "extent" in currentcollection:
                            currentcollection["extent"]["spatial"]["crs"] = curcoll["crs"]
                            collectionsjson["collections"][-1]["extent"]["spatial"]["crs"] = curcoll["crs"]
                    cname=str(coll).replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:].rstrip("/")
                    apijson["paths"]["/collections/" + cname] = {
                        "get": {"tags": ["Collections"], "summary": "describes collection " + cname, "description": "Describes the collection with the id " + cname, "operationId": "collection-" + str(
                            coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]),
                                "parameters": [], "responses": {"default": {"description": "default response", "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},"example": None}}}}}}
                    opwebrep=opweb.replace(".geojson","")
                    curcollrow = f'<tr><td><a href="{opwebrep}/items/{collectionhtmlname}">"{featurecollectionspaths[coll]["name"]}</a></td><td>{len(curcoll["features"])}</td><td><a href="{opwebrep}/items/{collectionhtmlname}">[Collection as HTML]</a>&nbsp;<a href="{opwebrep}/items/">[Collection as JSON]</a>&nbsp;<a href="{opwebrep}/items/index.ttl">[Collection as TTL]</a></td></tr>'
                    with open(op + "index.json", "w", encoding="utf-8") as f:
                        json.dump(currentcollection,f)
                    with open(op + collectionhtmlname, "w", encoding="utf-8") as f:
                        f.write(f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1" /></head><body><h1>{featurecollectionspaths[coll]["name"]}</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>{curcollrow}</tbody></table></html>')
                    collectiontable += curcollrow
                except Exception as e:
                    print(e)
                if os.path.exists(coll):
                    try:
                        oppath=str(op + "/items/index.json").replace("//", "/")
                        if os.path.exists(coll.replace("//", "/")):
                            targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"),
                                                                      oppath,
                                                                      outpath)
                            p = Path(oppath)
                            p.symlink_to(targetpath)
                        spath=coll.replace("//", "/").replace("index.geojson", "index.ttl").replace(
                                f'nonns_{featurecollectionspaths[coll]["id"]}.geojson',
                                f'nonns_{featurecollectionspaths[coll]["id"]}.ttl')
                        oppath=str(op + "/items/index.ttl").replace("//", "/")
                        if os.path.exists(spath):
                            targetpath = DocUtils.generateRelativeSymlink(
                                spath,
                                oppath, outpath)
                            p = Path(oppath)
                            p.symlink_to(targetpath)
                        spath=spath.replace(".ttl",".html")
                        if os.path.exists(spath):
                            targetpath = DocUtils.generateRelativeSymlink(
                                spath,
                                str(op + "/items/"+collectionhtmlname).replace("//", "/"), outpath)
                            with open(f'{op}/items/{collectionhtmlname}', "w",encoding="utf-8") as f:
                                if "nonns" in collid:
                                    f.write(f'<html><head><meta http-equiv="refresh" content="0; url="{deploypath}/{collid}.html" /></head></html>')
                                else:
                                    f.write(f'<html><head><meta http-equiv="refresh" content="0; url="{deploypath}/{collid}/" /></head></html>')
                        #print("symlinks created")
                    except Exception as e:
                        print("symlink creation error")
                        print(e)
                    cname=str(coll).replace(outpath,"").replace("index.geojson", "").replace(".geojson", "")[1:]
                    apijson["paths"][f'/collections/{cname}/items/index.json'.replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                   "summary": "retrieves features of collection " + cname.rstrip(
                                                                                       "/"),
                                                                                   "description": "Retrieves features of collection  " + cname,
                                                                                   "operationId": "features-" + cname,
                                                                                   "parameters": [], "responses": {
                            "default": {"description": "default response",
                                        "content": {"application/geo+json": {"example": None}},
                                        "text/ttl": {"schema": {"example": None}, "example": None},
                                        "text/html": {"schema": {"example": None}, "example": None}}}}}
                    cname=str(coll).replace(outpath,"").replace("index.geojson","").replace(".geojson", "")[1:]
                    apijson["paths"][str("/collections/" + str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[
                        1:]) + "/items/{featureId}/index.json").replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                               "summary": "retrieves feature of collection " + cname.rstrip("/"),
                                                                                               "description": "Retrieves one single feature of the collection with the id " + cname,
                                                                                               "operationId": "feature-" + cname, "parameters": [
                            {"name": "featureId", "in": "path", "required": True, "schema": {"type": "string"}}],
                                                                                               "responses": {
                                                                                                   "default": {
                                                                                                       "description": "default response",
                                                                                                       "content": {
                                                                                                           "application/geo+json": {
                                                                                                               "example": None}},
                                                                                                       "text/ttl": {
                                                                                                           "schema": {
                                                                                                               "example": None},
                                                                                                           "example": None},
                                                                                                       "text/html": {
                                                                                                           "schema": {
                                                                                                               "example": None},
                                                                                                           "example": None}}}}}

                    for feat in curcoll["features"]:
                        featpath = feat["id"].replace(prefixnamespace, "").replace("//", "/")
                        try:
                            basepath=f'{op}/items/{DocUtils.shortenURI(feat["id"])}'.replace("//", "/")
                            os.makedirs(basepath)
                            #print("CHECKPATH: " + str(
                            #    str(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json").replace("//", "/")))
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json"):
                                targetpath = DocUtils.generateRelativeSymlink(featpath + "/index.json", basepath + "/index.json", outpath, True)
                                p = Path(basepath+"/index.json")
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.ttl"):
                                targetpath = DocUtils.generateRelativeSymlink(featpath + "/index.ttl", basepath+"/index.ttl", outpath, True)
                                p = Path(basepath+"/index.ttl")
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.html"):
                                targetpath = DocUtils.generateRelativeSymlink(featpath + "/index.html", basepath+"/index.html", outpath, True)
                                with open(basepath+"/index.html", "w",encoding="utf-8") as f:
                                    f.write(f"<html><head><meta http-equiv=\"refresh\" content=\"0; url={targetpath}\" /></head></html>")
                                #print("symlinks created")
                        except Exception as e:
                            print("symlink creation error")
                            print(e)
                    if mergeJSON:
                        result.append(curcoll)
            collectiontable += "</tbody></table>"
        if mergeJSON:
            with open(f"{outpath}/features.js", 'w', encoding="utf-8") as output_file:
                output_file.write("var featurecolls=")
                json.dump(result,output_file)
                # shutil.move(coll, op+"/items/index.json")
        if ogcapi:
            with open(f"{outpath}/index.json", "w", encoding="utf-8") as f:
                json.dump(landingpagejson,f)
            with open(f"{outpath}/api/index.json", "w", encoding="utf-8") as f:
                json.dump(apijson,f)
            with open(f"{outpath}/api/api.html", "w", encoding="utf-8") as f:
                f.write(apihtml)
            with open(f"{outpath}/collections/"+collectionhtmlname, "w", encoding="utf-8") as f:
                f.write(collectionshtml.replace("{{collectiontable}}", collectiontable))
            with open(f"{outpath}/collections/index.json", "w", encoding="utf-8") as f:
                json.dump(collectionsjson,f)
            with open(f"{outpath}/conformance/index.json", "w", encoding="utf-8") as f:
                json.dump(conformancejson,f)