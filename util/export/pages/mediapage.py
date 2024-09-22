from ...doc.docconfig import DocConfig

from ..api.iiifexporter import IIIFAPIExporter


class MediaPage:

    @staticmethod
    def generatePageWidget(foundmedia,iiifmanifestpaths, graph,imageannos,imagetoURI,annobodies,foundlabel,comment,thetypes,predobjmap, templates, subject, pubconfig, f, onlybody=False):
        print("PageWidget")
        carousel = "image"
        if len(foundmedia["image"]) > 3:
            carousel = "carousel-item active"
            f.write(templates["imagecarouselheader"])
        if len(imageannos) > 0 and len(foundmedia["image"]) > 0:
            if pubconfig["apis"]["iiif"]:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, pubconfig["outpath"], pubconfig["deploypath"], foundmedia["image"],
                                                         imageannos, annobodies, str(subject), pubconfig["prefixns"],
                                                         imagetoURI, pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Image"))
            for image in foundmedia["image"]:
                if image not in imagetoURI or "uri" not in imagetoURI[image]:
                    imagetoURI[image] = {"uri": {}}
                if not str(subject) in imagetoURI[image]["uri"]:
                    imagetoURI[image]["uri"][str(subject)] = {"bodies": []}
                annostring = ""
                for anno in imageannos:
                    annostring += anno["value"].replace("<svg>",
                                                        "<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                f.write(templates["imageswithannotemplate"].replace("{{carousel}}",
                                                                    carousel + "\" style=\"position: relative;display: inline-block;").replace(
                    "{{image}}", str(image)).replace("{{svganno}}", annostring).replace("{{imagetitle}}", str(image)[0:str(image).rfind('.')]))
                if len(foundmedia["image"]) > 3:
                    carousel = "carousel-item"
        elif len(foundmedia["image"]) > 0:
            if pubconfig["apis"]["iiif"]:
                iiifmanifestpaths["default"].append(
                    IIIFAPIExporter.generateIIIFManifest(graph, pubconfig["outpath"], pubconfig["deploypath"], foundmedia["image"],
                                                         imageannos, annobodies, str(subject), pubconfig["prefixns"],
                                                         imagetoURI, pubconfig["imagemetadata"], DocConfig.metadatanamespaces,
                                                         foundlabel, comment, thetypes, predobjmap, "Image"))
            for image in foundmedia["image"]:
                if image not in imagetoURI or "uri" not in imagetoURI[image]:
                    imagetoURI[image] = {"uri": {}}
                if not str(subject) in imagetoURI[image]["uri"]:
                    imagetoURI[image]["uri"][str(subject)] = {"bodies": []}
                if image == "<svg width=":
                    continue
                if "<svg" in image:
                    if "<svg>" in image:
                        f.write(templates["imagestemplatesvg"].replace("{{carousel}}", carousel).replace("{{image}}",str(image.replace("<svg>","<svg class=\"svgview\">"))))
                    else:
                        f.write(templates["imagestemplatesvg"].replace("{{carousel}}", carousel).replace("{{image}}",str(image)))
                else:
                    f.write(templates["imagestemplate"].replace("{{carousel}}", carousel).replace("{{image}}",str(image)).replace(
                        "{{imagetitle}}", str(image)[0:str(image).rfind('.')]))
                if len(foundmedia["image"]) > 3:
                    carousel = "carousel-item"
        if len(foundmedia["image"]) > 3:
            f.write(templates["imagecarouselfooter"])
        if len(foundmedia["audio"]) > 0 and pubconfig["apis"]["iiif"]:
            iiifmanifestpaths["default"].append(
                IIIFAPIExporter.generateIIIFManifest(graph, pubconfig["outpath"], pubconfig["deploypath"], foundmedia["audio"], None,
                                                     None, str(subject), pubconfig["prefixns"], imagetoURI,
                                                     pubconfig["imagemetadata"], DocConfig.metadatanamespaces, foundlabel,
                                                     comment, thetypes, predobjmap, "Audio"))
        for audio in foundmedia["audio"]:
            imagetoURI[audio] = {"uri": str(subject)}
            f.write(templates["audiotemplate"].replace("{{audio}}", str(audio)))
        if len(foundmedia["video"]) > 0 and pubconfig["apis"]["iiif"]:
            iiifmanifestpaths["default"].append(
                IIIFAPIExporter.generateIIIFManifest(graph, pubconfig["outpath"], pubconfig["deploypath"], foundmedia["video"], None,
                                                     None, str(subject), pubconfig["prefixns"], imagetoURI,
                                                     pubconfig["imagemetadata"], DocConfig.metadatanamespaces, foundlabel,
                                                     comment, thetypes, predobjmap, "Video"))
        for video in foundmedia["video"]:
            imagetoURI[video] = {"uri": str(subject)}
            f.write(templates["videotemplate"].replace("{{video}}", str(video)))

    def generateCollectionWidget(self, graph, templates, subject, f):
        print("CollectionWidget")

    def generatePageView(self, headertemplate, footertemplate, g, f):
        f.write(str(headertemplate))
        print("PageView")