from ...doc.docconfig import DocConfig
from ...doc.docutils import DocUtils
from rdflib import URIRef, Literal
from rdflib.namespace import TIME, SOSA

class OWLTimePage:

    @staticmethod
    def resolveTimeObject(pred, obj, graph, timeobj):
        if pred == TIME.hasBeginning:
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in DocConfig.timeproperties:
                    timeobj["begin"] = tobj2[1]
                    break
        elif pred == TIME.hasEnd:
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in DocConfig.timeproperties:
                    timeobj["end"] = tobj2[1]
                    break
        elif pred == TIME.hasTime or pred == SOSA.phenomenonTime or pred == SOSA.resultTime:
            for tobj2 in graph.predicate_objects(obj):
                if str(tobj2[0]) in DocConfig.timeproperties:
                    timeobj["timepoint"] = tobj2[1]
        return timeobj

    @staticmethod
    def timeObjectToHTML(timeobj, prefixes):
        timeres = ""
        if "begin" in timeobj:
            if "end" in timeobj:
                timeres = str(timeobj["begin"]) + " "
                if str(timeobj["begin"].datatype) in DocConfig.timeliteraltypes:
                    timeres += DocUtils.createURILink(prefixes,
                                                      DocConfig.timeliteraltypes[str(timeobj["begin"].datatype)])
                timeres += " - " + str(timeobj["end"])
                if str(timeobj["end"].datatype) in DocConfig.timeliteraltypes:
                    timeres += DocUtils.createURILink(prefixes,
                                                      DocConfig.timeliteraltypes[str(timeobj["end"].datatype)])
            else:
                timeres = str(timeobj["begin"])
                if str(timeobj["begin"].datatype) in DocConfig.timeliteraltypes:
                    timeres += DocUtils.createURILink(prefixes,
                                                      DocConfig.timeliteraltypes[str(timeobj["begin"].datatype)])
        elif "end" in timeobj:
            timeres = str(timeobj["end"])
            if str(timeobj["end"].datatype) in DocConfig.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  DocConfig.timeliteraltypes[str(timeobj["end"].datatype)])
        elif "timepoint" in timeobj:
            timeres = timeobj["timepoint"]
            if str(timeobj["timepoint"].datatype) in DocConfig.timeliteraltypes:
                timeres += DocUtils.createURILink(prefixes,
                                                  DocConfig.timeliteraltypes[str(timeobj["timepoint"].datatype)])
        return timeres

    @staticmethod
    def resolveTimeLiterals(pred, obj, graph):
        timeobj = {}
        if isinstance(obj, URIRef):
            if str(pred) in DocConfig.timepointerproperties:
                timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
            if pred == TIME.hasTime or pred == SOSA.phenomenonTime or pred == SOSA.resultTime:
                for tobj in graph.predicate_objects(obj):
                    timeobj = OWLTimePage.resolveTimeObject(tobj[0], tobj[1], graph, timeobj)
        elif isinstance(obj, Literal):
            timeobj = OWLTimePage.resolveTimeObject(pred, obj, graph, timeobj)
        return timeobj