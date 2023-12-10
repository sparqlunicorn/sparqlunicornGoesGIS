
import os
import json
from pathlib import Path

from ...doc.docutils import DocUtils


class CKANExporter:

    @staticmethod
    def generateCKANCollection(outpath, featurecollectionspaths,version="3"):
        if not os.path.exists(outpath + "/dataset/"):
            os.makedirs(outpath + "/dataset/")
        if not os.path.exists(outpath + "/api/"):
            os.makedirs(outpath + "/api/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/"):
            os.makedirs(outpath + "/api/"+str(version)+"/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/group_list/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/group_list/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/action_list/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/action_list/")
        if not os.path.exists(outpath + "/api/"+str(version)+"/action/tag_list/"):
            os.makedirs(outpath + "/api/"+str(version)+"/action/tag_list/")
        f = open(outpath + "/api/"+str(version)+"/action/group_list/index.json", "w")
        f.write(json.dumps({"success": True, "result": []}))
        f.close()
        f = open(outpath + "/api/"+str(version)+"/action/tag_list/index.json", "w")
        f.write(json.dumps({"success": True, "result": ["ttl", "json", "geojson", "html"]}))
        f.close()
        colls = []
        for coll in featurecollectionspaths:
            op = outpath + "/dataset/" + coll.replace(outpath, "").replace("index.geojson", "")
            op = op.replace(".geojson", "")
            op = op.replace("//", "/")
            if op.endswith("/"):
                op = op[0:-1]
            if not os.path.exists(op):
                os.makedirs(op)
            targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), str(op + ".json"),
                                                      outpath)
            p = Path(str(op + ".json").replace("//", "/"))
            p.symlink_to(targetpath)
            targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), str(op + ".ttl"),
                                                      outpath)
            p = Path(str(op + ".ttl").replace("//", "/"))
            p.symlink_to(targetpath)
            targetpath = DocUtils.generateRelativeSymlink(coll.replace("//", "/"), str(op + ".html"),
                                                      outpath)
            p = Path(str(op + ".html").replace("//", "/"))
            p.symlink_to(targetpath)
            colls.append(op[op.rfind('/') + 1:])
        f = open(outpath + "/api/action/"+str(version)+"/action_list/index.json", "w")
        f.write(json.dumps({"success": True, "result": colls}))
        f.close()