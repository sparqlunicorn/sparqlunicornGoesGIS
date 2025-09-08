import json
import os
import re
from .docdefaults import DocDefaults
from qgis.core import Qgis, QgsMessageLog



class TemplateUtils:

    includepattern = r'{%\s*include\s*(.*)\s*%}'

    @staticmethod
    def resolveIncludes(template,templates):
        matches=re.findall(TemplateUtils.includepattern,template)
        if len(matches)>0:
            for mat in matches:
                if mat.replace(".html","") in templates:
                    template=template.replace("{% include "+mat+" %}",templates[mat.replace(".html","")])
        return template

    @staticmethod
    def resolveTemplate(templatename,templatepath):
        templates=DocDefaults.templates
        templates["includes"] = {}
        templates["js"] = {}
        templates["layouts"] = {}
        print(f"{templatepath}/{templatename} {os.path.exists(templatepath+'/'+templatename+'/templates/')}")
        print(f"{templatepath}/{templatename} {os.path.exists(templatepath + '/' + templatename)}")
        print(os.listdir(f"{templatepath}/{templatename}"))
        if os.path.exists(f"{templatepath}/{templatename}/templateconf.json"):
            with open(f"{templatepath}/{templatename}/templateconf.json", 'r',encoding="utf-8") as f:
                templatefiles = json.load(f)
                for file in templatefiles:
                    if os.path.exists(f"{templatepath}/{templatename}/{file}"):
                        with open(f"{templatepath}/{templatename}/{file['path']}", 'r',encoding="utf-8") as f2:
                            if "name" in file:
                                templates[file["name"]]= f2.read()
                            else:
                                templates[file] = f2.read()
        elif os.path.exists(f"{templatepath}/{templatename}/templates/"):
            if os.path.exists(f"{templatepath}/{templatename}/templates/layouts/") and os.path.exists(f"{templatepath}/{templatename}/templates/includes/"):
                for filename in os.listdir(f"{templatepath}/{templatename}/templates/includes/"):
                    print("FOUND INCLUDE: "+str(filename))
                    if filename.endswith(".html") or filename.endswith(".css"):
                        with open(f"{templatepath}/{templatename}/templates/includes/{filename}", 'r',encoding="utf-8") as f:
                            content=f.read()
                            templates["includes"][filename.replace(".html","")] = content
                            templates[filename.replace(".html", "")] = content
                for filename in os.listdir(f"{templatepath}/{templatename}/js/"):
                    print("FOUND INCLUDE: "+str(filename))
                    if filename.endswith(".js"):
                        with open(f"{templatepath}/{templatename}/js/{filename}", 'r',encoding="utf-8") as f:
                            content=f.read()
                            templates["js"][filename.replace(".js","")] = content
                            templates[filename.replace(".js", "")] = content
                for filename in os.listdir(f"{templatepath}/{templatename}/templates/layouts/"):
                    print("FOUND LAYOUT: " + str(filename))
                    if filename.endswith(".html") or filename.endswith(".css"):
                        with open(f"{templatepath}/{templatename}/templates/layouts/{filename}", 'r',encoding="utf-8") as f:
                            content=f.read()
                            templates["layouts"][filename.replace(".html", "")] = content
                            templates[filename.replace(".html", "")] = content
            else:
                for filename in os.listdir(f"{templatepath}/{templatename}/templates/"):
                    if filename.endswith(".html") or filename.endswith(".css"):
                        with open(f"{templatepath}/{templatename}/templates/{filename}", 'r',encoding="utf-8") as f:
                            templates[filename.replace(".html","")] = f.read()
                if os.path.exists(f"{templatepath}/{templatename}/js/"):
                    for filename in os.listdir(f"{templatepath}/{templatename}/js/"):
                        print("FOUND INCLUDE: "+str(filename))
                        if filename.endswith(".js"):
                            with open(f"{templatepath}/{templatename}/js/{filename}", 'r',encoding="utf-8") as f:
                                content=f.read()
                                templates["js"][filename.replace(".js","")] = content
                                templates[filename.replace(".js", "")] = content
                if os.path.exists(f"{templatepath}/{templatename}/css/"):
                    for filename in os.listdir(f"{templatepath}/{templatename}/css/"):
                        print("FOUND LAYOUT: " + str(filename))
                        if filename.endswith(".css"):
                            with open(f"{templatepath}/{templatename}/css/{filename}", 'r',encoding="utf-8") as f:
                                content=f.read()
                                templates[filename.replace(".css", "")] = content
                                templates[filename.replace(".css", "")] = content
        print("Found templates.... "+str(len(templates)))
        for temp in templates:
            if temp!="includes" and temp!="layouts" and temp!="js" and templates[temp] is not None:
                templates[temp]=TemplateUtils.resolveIncludes(templates[temp],templates)
        return templates