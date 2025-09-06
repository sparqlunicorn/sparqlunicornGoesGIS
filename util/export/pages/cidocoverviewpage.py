from doc.docconfig import DocConfig
from doc.docutils import DocUtils
from rdflib import URIRef, Literal
from collections import OrderedDict



class CIDOCOverviewPage:

    def pageWidgetConstraint(self):
        return ["http://www.cidoc-crm.org/cidoc-crm/E22_Man-Made_Object","http://www.cidoc-crm.org/cidoc-crm/Thing"]

    def collectionConstraint(self):
        return DocConfig.collectionclasses

    def generatePageWidget(self,graph,subject,f,onlybody=False):
        resmap=OrderedDict()
        resmap["P2_has_type"]=None
        resmap["P43_has_dimension"]=None
        resmap["P12_was_present_at"]=None
        resmap["P70_is_documented_in"]=None
        resmap["P46_is_composed_of"]=None
        resmap["P46_forms_part_of"]=None
        resmap["P108_was_produced_by"]=None
        widget="<table><thead><tr><th>Name</th><th>Type</th><th>Composed of</th><th>part of</th><th>documented in</th><th>was present at</th><th>has dimension</th</tr></thead><tbody><tr>"
        for predobj in graph.predicate_objects(subject):
            pobjstr=str(predobj[0])
            if pobjstr in resmap:
                if isinstance(predobj[1],URIRef):
                    resmap[pobjstr] = f"<a href=\"{predobj[0]}\">{DocUtils.shortenURI(pobjstr)}</a>"
                else:
                    resmap[pobjstr]=str(predobj[1])
        for val in resmap:
            if resmap[val] is not None:
                widget+=f"<td>{val}</td>"
            else:
                widget+="<td></td>"
        widget+="</tr></tbody></table>"


    def generateCollectionWidget(self,graph,subject,templates,f):
        print("CollectionWidget")

    def generatePageView(self,templates,g,f):
        print("PageView")