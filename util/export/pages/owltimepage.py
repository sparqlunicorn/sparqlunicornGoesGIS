from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils
from ...sparqlutils import SPARQLUtils
from rdflib import URIRef, Literal

class OWLTimePage:

    @staticmethod
    def resolveTimeObject(pred, obj, graph, timeobj):
        if str(pred) == "http://www.w3.org/2006/time#hasBeginning":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in SPARQLUtils.timeproperties:
                    timeobj["begin"] = tobj2[1]
        elif str(pred) == "http://www.w3.org/2006/time#hasEnd":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in SPARQLUtils.timeproperties:
                    timeobj["end"] = tobj2[1]
        elif str(pred) == "http://www.w3.org/2006/time#hasTime" or str(
                pred) == "http://www.w3.org/ns/sosa/phenomenonTime" or str(
                pred) == "http://www.w3.org/ns/sosa/resultTime":
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in SPARQLUtils.timeproperties:
                    timeobj["timepoint"] = tobj2[1]
        return timeobj

    @staticmethod
    def timeObjectToHTML(timeobj,prefixes):
        timeres = None
        if "begin" in timeobj and "end" in timeobj:
            timeres = str(timeobj["begin"]) + " "
            if str(timeobj["begin"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  SPARQLUtils.timeliteraltypes[str(timeobj["begin"].datatype)])
            timeres += " - " + str(timeobj["end"])
            if str(timeobj["end"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  SPARQLUtils.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "begin" in timeobj and not "end" in timeobj:
            timeres = str(timeobj["begin"])
            if str(timeobj["begin"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  SPARQLUtils.timeliteraltypes[str(timeobj["begin"].datatype)])
        elif "begin" not in timeobj and "end" in timeobj:
            timeres = str(timeobj["end"])
            if str(timeobj["end"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  SPARQLUtils.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "timepoint" in timeobj:
            timeres = timeobj["timepoint"]
            if str(timeobj["timepoint"].datatype) in SPARQLUtils.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  SPARQLUtils.timeliteraltypes[str(timeobj["timepoint"].datatype)])
        return timeres

    @staticmethod
    def resolveTimeLiterals(pred, obj, graph):
        timeobj = {}
        if isinstance(obj, URIRef) and (str(pred) == "http://www.w3.org/2006/time#hasTime" or str(
                pred) == "http://www.w3.org/ns/sosa/phenomenonTime" or str(
                pred) == "http://www.w3.org/ns/sosa/resultTime"):
            for tobj in graph.predicate_objects(obj):
                timeobj = OWLTimePage.resolveTimeObject(tobj[0], tobj[1], graph, timeobj)
        elif isinstance(obj, URIRef) and str(pred) in SPARQLUtils.timepointerproperties:
            timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
        elif isinstance(obj, Literal):
            timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
        return timeobj