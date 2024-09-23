from ...doc.docconfig import DocConfig

from ...export.api.iiifexporter import IIIFAPIExporter
from rdflib import URIRef

from ...doc.docutils import DocUtils


class Model3DPage:

    @staticmethod
    def generatePageWidget(graph,foundmedia,annobodies,templates,subject,iiifmanifestpaths,image3dannos,pubconfig,imagetoURI,foundlabel,comment,thetypes,predobjmap,f,checkdepth,onlybody=False):
        has3d=False
        if len(foundmedia["mesh"]) > 0 and len(image3dannos) > 0:
            if pubconfig["apis"]["iiif"]:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, pubconfig["outpath"], pubconfig["deploypath"],
                                                         foundmedia["mesh"], image3dannos, annobodies,
                                                         str(subject), pubconfig["prefixns"], imagetoURI,
                                                         pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Model"))
            for anno in image3dannos:
                if ("POINT" in anno["value"].upper() or "POLYGON" in anno["value"].upper() or "LINESTRING" in
                        anno["value"].upper()):
                    f.write(templates["threejstemplate"].replace("{{wktstring}}", anno["value"]).replace(
                        "{{meshurls}}", str(list(foundmedia["mesh"]))).replace("{{relativepath}}",
                                                                               DocUtils.generateRelativePathFromGivenDepth(
                                                                                   checkdepth)))
        elif len(foundmedia["mesh"]) > 0 and len(image3dannos) == 0:
            # print("Found 3D Model: " + str(foundmedia["mesh"]))
            if pubconfig["apis"]["iiif"]:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, pubconfig["outpath"], pubconfig["deploypath"],
                                                         foundmedia["mesh"], image3dannos, annobodies,
                                                         str(subject), pubconfig["prefixns"], imagetoURI,
                                                         pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Model"))
            for curitem in foundmedia["mesh"]:
                format = "ply"
                if ".nxs" in curitem or ".nxz" in curitem:
                    format = "nexus"
                    has3d = True
                elif format == "gltf":
                    f.write(templates["threejstemplate"].replace("{{wktstring}}", "").replace("{{meshurls}}",
                                                                                                   str(list(
                                                                                                       foundmedia[
                                                                                                           "mesh"]))).replace(
                        "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(checkdepth)))
                f.write(templates["threejstemplate"].replace("{{wktstring}}", "").replace("{{meshurls}}",
                                                                                               str(list(foundmedia[
                                                                                                            "mesh"]))).replace(
                    "{{relativepath}}", DocUtils.generateRelativePathFromGivenDepth(checkdepth)))
                # f.write(templates["3dtemplate"].replace("{{meshurl}}",curitem).replace("{{meshformat}}",format))
                break
        elif len(foundmedia["mesh"]) == 0 and len(image3dannos) > 0:
            for anno in image3dannos:
                annoup = anno["value"].upper()
                if "POINT" in annoup or "POLYGON" in annoup or "LINESTRING" in annoup:
                    f.write(templates["threejstemplate"].replace("{{wktstring}}", anno["value"]).replace(
                        "{{meshurls}}", "[]").replace("{{relativepath}}",
                                                      DocUtils.generateRelativePathFromGivenDepth(checkdepth)))
        return has3d

    @staticmethod
    def generateCollectionWidget(self,graph,templates,subject,f):
        print("CollectionWidget")
        memberpred = URIRef("http://www.w3.org/2000/01/rdf-schema#member")
        for memberid in graph.objects(subject, memberpred, True):
            print("3d model member")
        #    Model3DPage.generatePageWidget()

    def generatePageView(self,templates,g,f):
        #f.write(str(templates["headertemplate"]))
        print("PageView")