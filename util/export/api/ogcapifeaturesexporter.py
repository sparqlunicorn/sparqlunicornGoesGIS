
import os
import json
from pathlib import Path

from ...doc.docutils import DocUtils


class OGCAPIFeaturesExporter:

    @staticmethod
    def generateOGCAPIFeaturesPages(outpath,deploypath, featurecollectionspaths, prefixnamespace, ogcapi, mergeJSON):
        apihtml = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /><metaname=\"description\" content=\"SwaggerUI\"/><title>SwaggerUI</title><link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css\" /></head><body><div id=\"swagger-ui\"></div><script src=\"https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js\" crossorigin></script><script>const swaggerUrl = \"" + str(
            deploypath) + "/api/index.json\"; const apiUrl = \"" + str(
            deploypath) + "/\";  window.onload = () => {let swaggerJson = fetch(swaggerUrl).then(r => r.json().then(j => {j.servers[0].url = apiUrl; window.ui = SwaggerUIBundle({spec: j,dom_id: '#swagger-ui'});}));};</script></body></html>"
        apijson = {"openapi": "3.0.1", "info": {"title": str(deploypath) + " Feature Collections",
                                                "description": "Feature Collections of " + str(deploypath)},
                   "servers": [{"url": str(deploypath)}], "paths": {}}
        conformancejson = {"conformsTo": ["http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                                          "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
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
                                                     "links": {"type": "array", "xml": {"name": "link",
                                                                                        "namespace": "http://www.w3.org/2005/Atom"},
                                                               "items": {"$ref": "#/components/schemas/Link"}},
                                                     "extent": {"$ref": "#/components/schemas/Extent"},
                                                     "itemType": {"type": "string"},
                                                     "crs": {"type": "array", "items": {"type": "string"}},
                                                     "storageCrs": {"type": "string"}}, "xml": {"name": "Collection",
                                                                                                "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Collections": {"type": "object", "properties": {
                                                     "links": {"type": "array", "xml": {"name": "link",
                                                                                        "namespace": "http://www.w3.org/2005/Atom"},
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
                                                          "xml": {"name": "link",
                                                                  "namespace": "http://www.w3.org/2005/Atom"}},
                                                 "Spatial": {"type": "object", "properties": {"bbox": {"type": "array",
                                                                                                       "items": {
                                                                                                           "type": "array",
                                                                                                           "items": {
                                                                                                               "type": "number",
                                                                                                               "format": "double"}}},
                                                                                              "crs": {"type": "string",
                                                                                                      "xml": {
                                                                                                          "attribute": True}}},
                                                             "xml": {"name": "SpatialExtent",
                                                                     "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "Temporal": {"type": "object", "properties": {
                                                     "interval": {"type": "array",
                                                                  "items": {"type": "string", "format": "date-time"}},
                                                     "trs": {"type": "string", "xml": {"attribute": True}}},
                                                              "xml": {"name": "TemporalExtent",
                                                                      "namespace": "http://www.opengis.net/ogcapi-features-1/1.0"}},
                                                 "LandingPage": {"type": "object"}}}
            landingpagejson = {"title": "Landing Page", "description": "Landing Page", "links": [{
                "href": str(deploypath) + "/index.json",
                "rel": "self",
                "type": "application/json",
                "title": "this document as JSON"
            }, {
                "href": str(deploypath) + "/index.html",
                "rel": "alternate",
                "type": "text/html",
                "title": "this document as HTML"
            }, {
                "href": str(deploypath) + "/collections/",
                "rel": "data",
                "type": "application/json",
                "title": "Supported Feature Collections as JSON"
            }, {
                "href": str(deploypath) + "/collections/indexc.html",
                "rel": "data",
                "type": "text/html",
                "title": "Supported Feature Collections as HTML"
            }, {"href": str(deploypath) + "/api/index.json", "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0", "title": "API definition"},
                {"href": str(deploypath) + "/api", "rel": "service-desc", "type": "text/html",
                 "title": "API definition as HTML"},
                {"href": str(deploypath) + "/conformance", "rel": "conformance", "type": "application/json",
                 "title": "OGC API conformance classes as Json"},
                {"href": str(deploypath) + "/conformance", "rel": "conformance", "type": "text/html",
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
                {"href": outpath + "collections/index.json", "rel": "self", "type": "application/json",
                 "title": "this document as JSON"},
                {"href": outpath + "collections/index.html", "rel": "self", "type": "text/html",
                 "title": "this document as HTML"}]}
            collectionshtml = "<html><head></head><body><header><h1>Collections of " + str(
                deploypath) + "</h1></head>{{collectiontable}}<footer><a href=\"index.json\">This page as JSON</a></footer></body></html>"
            collectiontable = "<table><thead><th>Collection</th><th>Links</th></thead><tbody>"
            apijson["paths"]["/collections"] = {"get": {"tags": ["Collections"], "summary": "describes collections",
                                                        "description": "Describes all collections provided by this service",
                                                        "operationId": "collections", "parameters": [], "responses": {
                    "default": {"description": "default response", "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Collections"}},
                        "text/ttl": {"schema": {}}, "text/html": {"schema": {}}}}}}}
            if outpath.endswith("/"):
                outpath = outpath[0:-1]
            if not os.path.exists(outpath + "/api/"):
                os.makedirs(outpath + "/api/")
            if not os.path.exists(outpath + "/license/"):
                os.makedirs(outpath + "/license/")
            if not os.path.exists(outpath + "/collections/"):
                os.makedirs(outpath + "/collections/")
            if not os.path.exists(outpath + "/conformance/"):
                os.makedirs(outpath + "/conformance/")
        result = list()
        for coll in featurecollectionspaths:
            curcoll = None
            if os.path.exists(coll):
                with open(coll, 'r', encoding="utf-8") as infile:
                    curcoll = json.load(infile)
            if ogcapi:
                op = outpath + "/collections/" + coll.replace(outpath, "").replace("index.geojson", "") + "/"
                op = op.replace(".geojson", "")
                op = op.replace("//", "/")
                if not os.path.exists(op):
                    os.makedirs(op)
                if not os.path.exists(op + "/items/"):
                    os.makedirs(op + "/items/")
                opweb = op.replace(outpath, deploypath)
                opwebcoll = opweb
                if opwebcoll.endswith("/"):
                    opwebcoll = opwebcoll[0:-1]
                opwebcoll = opwebcoll.replace("//", "/")
                collectionsjson["collections"].append(
                    {"id": coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:],
                     "title": featurecollectionspaths[coll]["name"], "links": [
                        {"href": str(opweb.replace(".geojson", "") + "/index.json").replace("//", "/"),
                         "rel": "collection", "type": "application/json", "title": "Collection as JSON"},
                        {"href": str(opweb.replace(".geojson", "") + "/").replace("//", "/"), "rel": "collection",
                         "type": "text/html", "title": "Collection as HTML"},
                        {"href": str(opweb.replace(".geojson", "") + "/index.ttl").replace("//", "/"),
                         "rel": "collection", "type": "text/ttl", "title": "Collection as TTL"}]})
                currentcollection = {"title": featurecollectionspaths[coll]["name"],
                                     "id": coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson",
                                                                                                          "")[1:],
                                     "links": [], "itemType": "feature"}
                currentcollection["links"] = [
                    {"href": opwebcoll + "/items/index.json", "rel": "items", "type": "application/json",
                     "title": "Collection as JSON"},
                    {"href": opwebcoll + "/items/indexc.html", "rel": "items", "type": "text/html",
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
                apijson["paths"]["/collections/" + str(
                    coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]).rstrip("/")] = {
                    "get": {"tags": ["Collections"], "summary": "describes collection " + str(
                        str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:])).rstrip(
                        "/"), "description": "Describes the collection with the id " + str(
                        str(coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:])).rstrip(
                        "/"), "operationId": "collection-" + str(
                        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[1:]),
                            "parameters": [], "responses": {"default": {"description": "default response", "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Collections"},
                                                 "example": None}}}}}}
                curcollrow = "<tr><td><a href=\"" + opweb.replace(".geojson", "") + "/items/indexc.html\">" + str(
                    featurecollectionspaths[coll]["name"]) + "</a></td><td><a href=\"" + opweb.replace(".geojson",
                                                                                                       "") + "/items/indexc.html\">[Collection as HTML]</a>&nbsp;<a href=\"" + opweb.replace(
                    ".geojson", "") + "/items/\">[Collection as JSON]</a>&nbsp;<a href=\"" + opweb.replace(".geojson",
                                                                                                           "") + "/items/index.ttl\">[Collection as TTL]</a></td></tr>"
                f = open(op + "index.json", "w", encoding="utf-8")
                f.write(json.dumps(currentcollection))
                f.close()
                f = open(op + "indexc.html", "w", encoding="utf-8")
                f.write("<html><head></head><body><h1>" + featurecollectionspaths[coll][
                    "name"] + "</h1><table><thead><tr><th>Collection</th><th>Links</th></tr></thead><tbody>" + str(
                    curcollrow) + "</tbody></table></html>")
                f.close()
                collectiontable += curcollrow
                if os.path.exists(coll):
                    try:
                        if os.path.exists(coll.replace("//", "/")):
                            targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"),
                                                                      str(op + "/items/index.json").replace("//", "/"),
                                                                      outpath)
                            p = Path(str(op + "/items/index.json").replace("//", "/"))
                            p.symlink_to(targetpath)
                        if os.path.exists(coll.replace("//", "/").replace("index.geojson", "index.ttl").replace(
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".ttl")):
                            targetpath = DocUtils.generateRelativeSymlink(
                                coll.replace("//", "/").replace("index.geojson", "index.ttl").replace(
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".ttl"),
                                str(op + "/items/index.ttl").replace("//", "/"), outpath)
                            p = Path(str(op + "/items/index.ttl").replace("//", "/"))
                            p.symlink_to(targetpath)
                        if os.path.exists(coll.replace("//", "/").replace("index.geojson", "index.html").replace(
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                "nonns_" + featurecollectionspaths[coll]["id"] + ".html")):
                            targetpath = DocUtils.generateRelativeSymlink(
                                coll.replace("//", "/").replace("index.geojson", "index.html").replace(
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".geojson",
                                    "nonns_" + featurecollectionspaths[coll]["id"] + ".html"),
                                str(op + "/items/indexc.html").replace("//", "/"), outpath)
                            f = open(str(op + "/items/indexc.html"), "w")
                            f.write(
                                "<html><head><meta http-equiv=\"refresh\" content=\"0; url=" + targetpath + "\" /></head></html>")
                            f.close()
                        print("symlinks created")
                    except Exception as e:
                        print("symlink creation error")
                        print(e)
                    apijson["paths"][str("/collections/" + str(
                        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[
                        1:]) + "/items/index.json").replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                   "summary": "retrieves features of collection " + str(
                                                                                       coll.replace(outpath,
                                                                                                    "").replace(
                                                                                           "index.geojson", "").replace(
                                                                                           ".geojson", "")[1:]).rstrip(
                                                                                       "/"),
                                                                                   "description": "Retrieves features of collection  " + str(
                                                                                       coll.replace(outpath,
                                                                                                    "").replace(
                                                                                           "index.geojson", "").replace(
                                                                                           ".geojson", "")[1:]),
                                                                                   "operationId": "features-" + str(
                                                                                       coll.replace(outpath,
                                                                                                    "").replace(
                                                                                           "index.geojson", "").replace(
                                                                                           ".geojson", "")[1:]),
                                                                                   "parameters": [], "responses": {
                            "default": {"description": "default response",
                                        "content": {"application/geo+json": {"example": None}},
                                        "text/ttl": {"schema": {"example": None}, "example": None},
                                        "text/html": {"schema": {"example": None}, "example": None}}}}}
                    apijson["paths"][str("/collections/" + str(
                        coll.replace(outpath, "").replace("index.geojson", "").replace(".geojson", "")[
                        1:]) + "/items/{featureId}/index.json").replace("//", "/")] = {"get": {"tags": ["Data"],
                                                                                               "summary": "retrieves feature of collection " + str(
                                                                                                   coll.replace(outpath,
                                                                                                                "").replace(
                                                                                                       "index.geojson",
                                                                                                       "").replace(
                                                                                                       ".geojson", "")[
                                                                                                   1:]).rstrip("/"),
                                                                                               "description": "Retrieves one single feature of the collection with the id " + str(
                                                                                                   coll.replace(outpath,
                                                                                                                "").replace(
                                                                                                       "index.geojson",
                                                                                                       "").replace(
                                                                                                       ".geojson", "")[
                                                                                                   1:]),
                                                                                               "operationId": "feature-" + str(
                                                                                                   coll.replace(outpath,
                                                                                                                "").replace(
                                                                                                       "index.geojson",
                                                                                                       "").replace(
                                                                                                       ".geojson", "")[
                                                                                                   1:]), "parameters": [
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
                            os.makedirs(str(op + "/items/" + str(DocUtils.shortenURI(feat["id"]))))
                            print("CHECKPATH: " + str(
                                str(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json").replace("//", "/")))
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.json"):
                                targetpath = DocUtils.generateRelativeSymlink(featpath + "/index.json", str(op + "/items/" + str(
                                    DocUtils.shortenURI(feat["id"])) + "/index.json").replace("//", "/"), outpath, True)
                                p = Path(str(op + "/items/" + str(DocUtils.shortenURI(feat["id"])) + "/index.json").replace("//", "/"))
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.ttl"):
                                targetpath = DocUtils.generateRelativeSymlink(featpath + "/index.ttl", str(op + "/items/" + str(
                                    DocUtils.shortenURI(feat["id"])) + "/index.ttl").replace("//", "/"), outpath, True)
                                p = Path(str(op + "/items/" + str(DocUtils.shortenURI(feat["id"])) + "/index.ttl").replace("//", "/"))
                                p.symlink_to(targetpath)
                            if os.path.exists(feat["id"].replace(prefixnamespace, outpath + "/") + "/index.html"):
                                targetpath = DocUtils.generateRelativeSymlink(featpath + "/index.html", str(op + "/items/" + str(
                                    DocUtils.shortenURI(feat["id"])) + "/index.html").replace("//", "/"), outpath, True)
                                f = open(str(op + "/items/" + str(DocUtils.shortenURI(feat["id"]))) + "/index.html", "w")
                                f.write(
                                    "<html><head><meta http-equiv=\"refresh\" content=\"0; url=" + targetpath + "\" /></head></html>")
                                f.close()
                            print("symlinks created")
                        except Exception as e:
                            print("symlink creation error")
                            print(e)
                    if mergeJSON:
                        result.append(curcoll)
                collectiontable += "</tbody></table>"
        if mergeJSON:
            with open(outpath + "/features.js", 'w', encoding="utf-8") as output_file:
                output_file.write("var featurecolls=" + json.dumps(result))
                # shutil.move(coll, op+"/items/index.json")
        if ogcapi:
            f = open(outpath + "/index.json", "w", encoding="utf-8")
            f.write(json.dumps(landingpagejson))
            f.close()
            f = open(outpath + "/api/index.json", "w", encoding="utf-8")
            f.write(json.dumps(apijson))
            f.close()
            f = open(outpath + "/api/api.html", "w", encoding="utf-8")
            f.write(apihtml)
            f.close()
            f = open(outpath + "/collections/indexc.html", "w", encoding="utf-8")
            f.write(collectionshtml.replace("{{collectiontable}}", collectiontable))
            f.close()
            f = open(outpath + "/collections/index.json", "w", encoding="utf-8")
            f.write(json.dumps(collectionsjson))
            f.close()
            f = open(outpath + "/conformance/index.json", "w", encoding="utf-8")
            f.write(json.dumps(conformancejson))
            f.close()