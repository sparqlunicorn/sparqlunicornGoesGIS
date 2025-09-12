from rdflib import Graph, Literal
from rdflib.namespace import RDF
import json
import random

from ...doc.docutils import DocUtils


class GraphExporter:

    @staticmethod
    def getExporterString():
        return "Linked Data (*.n3 *.nt *.trig *.ttl *.xml) Graph Data (*.cypher *.dot *.gdf *.gexf *.gml *.graphml *.jgf *.net *.tgf *.tlp)"

    @staticmethod
    def convertTTLToCypher(g, file, subjectstorender=None,classlist=None, formatt="cypher"):
        uriToNodeId,nodecounter,tgfresedges = {},0,""
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            substr=str(sub)
            substrsuri=DocUtils.shortenURI(substr)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                file.write(f"CREATE ( {substrsuri}{{ _id:'{substrsuri}', _uri:'{substr}', rdfs_label:'{substrsuri}' }})\n")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                tupstr=str(tup[1])
                if tupstr not in uriToNodeId:
                    tupstrsuri=DocUtils.shortenURI(tupstr)
                    file.write(f"CREATE ( {tupstrsuri}{{ _id:'{tupstrsuri}', _uri:'{tupstr}', rdfs_label:'{tupstrsuri}' }})\n")
                    uriToNodeId[tupstr] = nodecounter
                    nodecounter += 1
                tgfresedges += f"({uriToNodeId[substr]})-[:{DocUtils.shortenURI(tupstr)}]->({DocUtils.shortenURI(str(tup[0]))}),\n"
        file.write("\n\nCREATE ")
        file.write(tgfresedges[0:-2] + "\n")
        return None

    @staticmethod
    def convertTTLToGraphML(g, file, subjectstorender=None,classlist=None, formatt="graphml"):
        literalcounter,edgecounter=0,0
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
    <graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <key for="node" id="nodekey" yfiles.type="nodegraphics"></key><key for="edge" id="edgekey" yfiles.type="edgegraphics"></key><graph id="G" edgedefault="directed">""")
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        addednodes = set()
        for sub in subjectstorender:
            file.write(f'<node id="{sub}" uri="{sub}"><data key="nodekey"><y:ShapeNode><y:Shape shape="ellipse"></y:Shape><y:Fill color="#800080" transparent="false"></y:Fill><y:NodeLabel alignment="center" fontSize="12" fontStyle="plain" hasText="true" visible="true" width="4.0">{DocUtils.shortenURI(sub)}</y:NodeLabel></y:ShapeNode></data></node>\n')
            for tup in g.predicate_objects(sub):
                if isinstance(tup[1], Literal):
                    file.write(f'<node id="literal{literalcounter}" uri="literal{literalcounter}"><data key="nodekey"><y:ShapeNode><y:Shape shape="ellipse"></y:Shape><y:Fill color="#008000" transparent="false"></y:Fill><y:NodeLabel alignment="center" fontSize="12" fontStyle="plain" hasText="true" visible="true" width="4.0"><![CDATA[{tup[1]}]]></y:NodeLabel></y:ShapeNode></data></node>\n')
                    file.write(f'<edge id="e{edgecounter}" uri="{tup[0]}" source="{sub}" target="literal{literalcounter}"><data key="edgekey"><y:PolyLineEdge><y:EdgeLabel alignment="center" configuration="AutoFlippingLabel" fontSize="12" fontStyle="plain" hasText="true" visible="true" width="4.0">{DocUtils.shortenURI(str(tup[0]))}</y:EdgeLabel></y:PolyLineEdge></data></edge>\n')
                    literalcounter += 1
                else:
                    if tup[1] not in subjectstorender and str(tup[1]) not in addednodes:
                        file.write(f"<node id=\"{tup[1]}\" uri=\"{tup[1]}\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">{DocUtils.shortenURI(str(tup[1]))}</y:NodeLabel></y:ShapeNode></data></node>\n")
                        addednodes.add(str(tup[1]))
                    file.write(f"<edge id=\"e{edgecounter}\" uri=\"{tup[0]}\" source=\"{sub}\" target=\"{tup[1]}\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">{DocUtils.shortenURI(str(tup[1]))}</y:EdgeLabel></y:PolyLineEdge></data></edge>\n")
                edgecounter += 1
        file.write("</graph></graphml>")
        return None

    @staticmethod
    def convertTTLToGML(g, file, subjectstorender=None,classlist=None, formatt="graphml"):
        literalcounter = 0
        file.write("""graph\n[\n""")
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        addednodes = set()
        for sub in subjectstorender:
            file.write(f"node\n[\nid {sub}\nlabel \"{DocUtils.shortenURI(str(sub))}\"\n]\n")
            for tup in g.predicate_objects(sub):
                if isinstance(tup[1], Literal):
                    file.write(f"node\n[\nid literal{literalcounter}\nlabel \"{DocUtils.shortenURI(str(tup[1]))}\"\n]\n")
                    file.write(f"edge\n[\nsource {sub}\n target literal{literalcounter}\nlabel \"{DocUtils.shortenURI(str(tup[0]))}\"\n]\n")
                    literalcounter += 1
                else:
                    if tup[1] not in subjectstorender and str(tup[1]) not in addednodes:
                        file.write(f"node\n[\nid {tup[1]}\nlabel \"{DocUtils.shortenURI(str(tup[1]))}\"\n]\n")
                        addednodes.add(str(tup[1]))
                    file.write(f"edge \n[\n source {sub}\n target {tup[1]}\n label \"{DocUtils.shortenURI(str(tup[0]))}\"")
        file.write("\n]\n")
        return None

    @staticmethod
    def convertTTLToTGF(g, file, subjectstorender=None,classlist=None, formatt="tgf"):
        uriToNodeId,nodecounter,tgfresedges,sepchar = {},0,""," "
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        if formatt=="GDF":
            sepchar=","
            file.write("nodedef>name VARCHAR,label VARCHAR")
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                file.write(f'{nodecounter}{sepchar}{sub}\n')
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(f'{nodecounter}{sepchar}{tup[1]}\n')
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += f'{uriToNodeId[substr]}{sepchar}{uriToNodeId[str(tup[1])]}{sepchar}{DocUtils.shortenURI(tup[0])}\n'
        if formatt=="gdf":
            file.write("edgedef>node1 VARCHAR,node2 VARCHAR,label VARCHAR\n")
        else:
            file.write("#\n")
        file.write(tgfresedges)
        return None

    @staticmethod
    def convertTTLToNET(g, file, subjectstorender=None,classlist=None, formatt="net"):
        uriToNodeId,nodecounter,tgfresedges,sepchar = {},0,""," "
        if subjectstorender is None:
            subjectstorender = list(g.subjects(None,None,True))
        file.write(f"vertices {len(subjectstorender)}\n")
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                file.write(f'{nodecounter}{sepchar}"{DocUtils.shortenURI(substr)}"\n')
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(f'{nodecounter}{sepchar}"{DocUtils.shortenURI(str(tup[1]))}"\n')
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += f'{substr}{sepchar}{tup[1]}\n'
        file.write("\n*arcs\n")
        file.write(tgfresedges)
        return None

    @staticmethod
    def convertTTLToTLP(g, file, subjectstorender=None,classlist=None, formatt="tlp"):
        uriToNodeId,nodecounter,edgecounter,tgfresedges = {},0,0,""
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        file.write("(tlp \"2.0\"\nnodes(")
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                file.write(str(nodecounter)+" ")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(str(nodecounter)+" ")
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += f"(edge {edgecounter} {uriToNodeId[substr]} {uriToNodeId[str(tup[1])]})\n"
                edgecounter+=1
        file.write(")\n")
        file.write(tgfresedges)
        file.write("\n)\n")
        return None

    @staticmethod
    def convertTTLToJGF(g, file, subjectstorender=None,classlist=None, formatt="jgf"):
        uriToNodeId,nodecounter,edgecounter = {},0,0
        result={"graph":{"nodes":{},"edges":[]}}
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                result["graph"]["nodes"][substr]={"label":str(DocUtils.shortenURI(substr))}
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    result["graph"]["nodes"][str(tup[1])] = {"label": str(DocUtils.shortenURI(str(tup[1])))}
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                result["graph"]["edges"].append({"source":str(uriToNodeId[substr]),"target":str(uriToNodeId[str(tup[1])])})
                edgecounter+=1
        #file.write(json.dumps(result))
        json.dump(result,file)
        return None

    @staticmethod
    def convertTTLToSigmaJSON(g, file, subjectstorender=None,classlist=None, formatt="jgf"):
        uriToNodeId,nodecounter,edgecounter = {},0,0
        result={"graph":{"nodes":[],"edges":[]}}
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                result["graph"]["nodes"].append({"id":substr,"label":str(DocUtils.shortenURI(substr)),"x":random.uniform(0, 1000),"y":random.uniform(0, 1000)})
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                tup1str=str(tup[1])
                if tup1str not in uriToNodeId:
                    result["graph"]["nodes"].append({"id":tup1str,"label": str(DocUtils.shortenURI(tup1str))})
                    uriToNodeId[tup1str] = nodecounter
                    nodecounter += 1
                result["graph"]["edges"].append({"id":f'{uriToNodeId[substr]}_{uriToNodeId[tup1str]}',"label":str(DocUtils.shortenURI(str(tup[0]))),"source":str(uriToNodeId[substr]),"target":str(uriToNodeId[tup1str])})
                edgecounter+=1
        #file.write(json.dumps(result))
        json.dump(result,file)
        return None

    @staticmethod
    def convertTTLToDOT(g, file, subjectstorender=None,classlist=None, formatt="dot"):
        uriToNodeId,nodecounter,edgecounter = {},0,0
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        file.write("digraph mygraph {")
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                file.write(f'{sub} [label="{DocUtils.shortenURI(substr)}"]\n')
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(f'{tup[1]} [label="{DocUtils.shortenURI(str(tup[1]))}"]\n')
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                file.write(f'{sub} {tup[1]} [label="{DocUtils.shortenURI(str(tup[0]))}"]\n')
                edgecounter+=1
        file.write("\n}\n")
        return None

    @staticmethod
    def convertTTLToGEXF(g,file,subjectstorender,classlist=None,formatt="gexf"):
        uriToNodeId,nodecounter,edgecounter = {},0,0
        edges = "<edges>"
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<gexf xmlns=\"http://gexf.net/1.3\" xmlns:viz=\"http://gexf.net/1.3/viz\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://gexf.net/1.3 http://gexf.net/1.3/gexf.xsd\" version=\"1.3\">\n<graph mode=\"static\" defaultedgetype=\"directed\">\n<nodes>\n")
        if subjectstorender is None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            substr=str(sub)
            if substr not in uriToNodeId:
                uriToNodeId[substr] = nodecounter
                file.write(f'<node id="{nodecounter}" value="{sub}" label="{DocUtils.shortenURI(substr)}"><viz:color r="128" g="0" b="128"/></node>\n')
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                tup1str=str(tup[1])
                if isinstance(tup[1],Literal):
                    if tup1str not in uriToNodeId:
                        file.write(f"<node id=\"{nodecounter}\" value=\""+str(tup1str.replace("<","&lt;").replace(">","&gt;").replace("&","&amp;").replace("\"","'"))+"\" label=\"" + str(str(tup[1]).replace("<","&lt;").replace(">","&gt;").replace("&","&amp;").replace("\"","'")) + "\">\n")
                        if tup[0] == RDF.type:
                            file.write("<viz:color r=\"255\" g=\"165\" b=\"0\"/>\n")
                        else:
                            file.write("<viz:color r=\"0\" g=\"128\" b=\"0\"/>\n")
                        file.write("</node>")
                        uriToNodeId[tup1str] = nodecounter
                        nodecounter += 1
                    edges += f"<edge value=\"{tup[0]}\" id=\"{edgecounter}\" source=\"{uriToNodeId[substr]}\" target=\"{uriToNodeId[tup1str]}\" label=\"{DocUtils.shortenURI(str(tup[0]))}\"/>\n"
                else:
                    if tup1str not in uriToNodeId:
                        file.write(f'<node id="{nodecounter}" value="{tup[1]}" label="{DocUtils.shortenURI(tup1str)}">\n')
                        if tup[0] == RDF.type:
                            file.write("<viz:color r=\"255\" g=\"165\" b=\"0\"/>\n")
                        else:
                            file.write("<viz:color r=\"128\" g=\"0\" b=\"128\"/>\n")
                        file.write("</node>")
                        uriToNodeId[tup1str] = nodecounter
                        nodecounter += 1
                    edges += f"<edge value=\"{tup[0]}\" id=\"{edgecounter}\" source=\"{uriToNodeId[substr]}\" target=\"{uriToNodeId[tup1str]}\" label=\"{DocUtils.shortenURI(str(tup[0]))}\"/>\n"
                edgecounter+=1
        file.write("</nodes>\n")
        file.write(edges)
        file.write("</edges>\n</graph>\n</gexf>")
        return None

    @staticmethod
    def serializeRDF(g, file, subjectstorender,classlist, formatt):
        g.serialize(file, encoding="utf-8", format=formatt.lower())