from rdflib import Graph, Literal
import json


class GraphExporter:

    rdfformats = ["TTL", "TRIX", "TRIG", "N3", "NQ", "NT", "XML", "JSON-LD"]

    @staticmethod
    def shortenURI(uri, ns=False):
        if uri != None and "#" in uri and ns:
            return uri[0:uri.rfind('#') + 1]
        if uri != None and "/" in uri and ns:
            return uri[0:uri.rfind('/') + 1]
        if uri != None and uri.endswith("/"):
            uri = uri[0:-1]
        if uri != None and "#" in uri and not ns:
            return uri[uri.rfind('#') + 1:]
        if uri != None and "/" in uri and not ns:
            return uri[uri.rfind('/') + 1:]
        return uri

    @staticmethod
    def convertTTLToCypher(g, file, subjectstorender=None, formatt="cypher"):
        uriToNodeId = {}
        nodecounter = 0
        tgfresedges = ""
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                file.write("CREATE ( " + str(GraphExporter.shortenURI(str(sub))) + "{ _id:'" + str(
                    GraphExporter.shortenURI(str(sub))) + "', _uri:'" + str(sub) + "', rdfs_label:'" + str(
                    GraphExporter.shortenURI(str(sub))) + "' })\n")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write("CREATE ( " + str(GraphExporter.shortenURI(str(tup[1]))) + "{ _id:'" + str(
                        GraphExporter.shortenURI(str(tup[1]))) + "', _uri:'" + str(tup[1]) + "', rdfs_label:'" + str(
                        GraphExporter.shortenURI(str(tup[1]))) + "' })\n")
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += "(" + str(uriToNodeId[str(sub)]) + ")-[:" + str(
                    GraphExporter.shortenURI(str(tup[1]))) + "]->(" + str(GraphExporter.shortenURI(tup[0])) + "),\n"
        file.write("\n\nCREATE ")
        file.write(tgfresedges[0:-2] + "\n")
        return None

    @staticmethod
    def convertTTLToGraphML(g, file, subjectstorender=None, formatt="graphml"):
        literalcounter = 0
        edgecounter = 0
        file.write("""<?xml version="1.0" encoding="UTF-8"?>
    <graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <key for="node" id="nodekey" yfiles.type="nodegraphics"></key><key for="edge" id="edgekey" yfiles.type="edgegraphics"></key><graph id="G" edgedefault="directed">""")
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        addednodes = set()
        for sub in subjectstorender:
            file.write("<node id=\"" + str(sub) + "\" uri=\"" + str(
                sub) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                GraphExporter.shortenURI(sub)) + "</y:NodeLabel></y:ShapeNode></data></node>\n")
            for tup in g.predicate_objects(sub):
                if isinstance(tup[1], Literal):
                    file.write("<node id=\"literal" + str(literalcounter) + "\" uri=\"literal" + str(
                        literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\"><![CDATA[" + str(
                        tup[1]) + "]]></y:NodeLabel></y:ShapeNode></data></node>\n")
                    file.write("<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(tup[0]) + "\" source=\"" + str(
                        sub) + "\" target=\"literal" + str(
                        literalcounter) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                        GraphExporter.shortenURI(str(tup[0]))) + "</y:EdgeLabel></y:PolyLineEdge></data></edge>\n")
                    literalcounter += 1
                else:
                    if tup[1] not in subjectstorender and str(tup[1]) not in addednodes:
                        file.write("<node id=\"" + str(tup[1]) + "\" uri=\"" + str(tup[
                                                                                       1]) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                            GraphExporter.shortenURI(str(tup[1]))) + "</y:NodeLabel></y:ShapeNode></data></node>\n")
                        addednodes.add(str(tup[1]))
                    file.write("<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(tup[0]) + "\" source=\"" + str(
                        sub) + "\" target=\"" + str(tup[
                                                        1]) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                        GraphExporter.shortenURI(str(tup[1]))) + "</y:EdgeLabel></y:PolyLineEdge></data></edge>\n")
                edgecounter += 1
        file.write("</graph></graphml>")
        return None

    @staticmethod
    def convertTTLToGML(g, file, subjectstorender=None, formatt="graphml"):
        literalcounter = 0
        file.write("""graph\n[\n""")
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        addednodes = set()
        for sub in subjectstorender:
            file.write("node\n[\nid "+str(sub)+"\nlabel \""+GraphExporter.shortenURI(str(sub))+"\"\n]\n")
            for tup in g.predicate_objects(sub):
                if isinstance(tup[1], Literal):
                    file.write("node\n[\nid literal"+str(literalcounter)+"\nlabel \""+GraphExporter.shortenURI(str(tup[1]))+"\"\n]\n")
                    file.write("edge\n[\nsource " + str(sub) + "\n target literal" + str(literalcounter) + "\nlabel \""+GraphExporter.shortenURI(str(tup[0]))+"\"\n]\n")
                    literalcounter += 1
                else:
                    if tup[1] not in subjectstorender and str(tup[1]) not in addednodes:
                        file.write("node\n[\nid " + str(tup[1]) + "\nlabel \"" + GraphExporter.shortenURI(str(tup[1])) + "\"\n]\n")
                        addednodes.add(str(tup[1]))
                    file.write("edge \n[\n source " + str(sub) + "\n target " + str(tup[1]) + "\n label \""+GraphExporter.shortenURI(str(tup[0]))+"\"")
        file.write("\n]\n")
        return None

    @staticmethod
    def convertTTLToTGF(g, file, subjectstorender=None, formatt="tgf"):
        uriToNodeId = {}
        nodecounter = 0
        tgfresedges = ""
        sepchar=" "
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        if formatt=="GDF":
            sepchar=","
            file.write("nodedef>name VARCHAR,label VARCHAR")
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                file.write(str(nodecounter) + sepchar + str(sub) + "\n")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(str(nodecounter) + sepchar + str(tup[1]) + "\n")
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += str(uriToNodeId[str(sub)]) + sepchar + str(uriToNodeId[str(tup[1])]) + sepchar + str(
                    GraphExporter.shortenURI(tup[0])) + "\n"
        if formatt=="gdf":
            file.write("edgedef>node1 VARCHAR,node2 VARCHAR,label VARCHAR\n")
        else:
            file.write("#\n")
        file.write(tgfresedges)
        return None

    @staticmethod
    def convertTTLToNET(g, file, subjectstorender=None, formatt="net"):
        uriToNodeId = {}
        nodecounter = 0
        tgfresedges = ""
        sepchar=" "
        if subjectstorender == None:
            subjectstorender = list(g.subjects(None,None,True))
        file.write("vertices "+str(len(subjectstorender))+"\n")
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                file.write(str(nodecounter) + sepchar +"\""+ GraphExporter.shortenURI(str(sub)) + "\"\n")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(str(nodecounter) + sepchar +"\""+ GraphExporter.shortenURI(str(tup[1])) + "\"\n")
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += str(sub) + sepchar + str(tup[1])+ "\n"
        file.write("\n*arcs\n")
        file.write(tgfresedges)
        return None

    @staticmethod
    def convertTTLToTLP(g, file, subjectstorender=None, formatt="tgf"):
        uriToNodeId = {}
        nodecounter = 0
        edgecounter=0
        tgfresedges = ""
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        file.write("(tlp \"2.0\"\nnodes(")
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                file.write(str(nodecounter)+" ")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(str(nodecounter)+" ")
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                tgfresedges += "(edge "+str(edgecounter)+" "+str(uriToNodeId[str(sub)]) + " " + str(uriToNodeId[str(tup[1])])+")\n"
                edgecounter+=1
        file.write(")\n")
        file.write(tgfresedges)
        file.write("\n)\n")
        return None

    @staticmethod
    def convertTTLToJGF(g, file, subjectstorender=None, formatt="jgf"):
        uriToNodeId = {}
        nodecounter = 0
        edgecounter=0
        result={"graph":{"nodes":{},"edges":[]}}
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                result["graph"]["nodes"][str(sub)]={"label":str(GraphExporter.shortenURI(str(sub)))}
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    result["graph"]["nodes"][str(tup[1])] = {"label": str(GraphExporter.shortenURI(str(tup[1])))}
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                result["graph"]["edges"].append({"source":str(uriToNodeId[str(sub)]),"target":str(uriToNodeId[str(tup[1])])})
                edgecounter+=1
        file.write(json.dumps(result))
        return None

    @staticmethod
    def convertTTLToDOT(g, file, subjectstorender=None, formatt="dot"):
        uriToNodeId = {}
        nodecounter = 0
        edgecounter=0
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        file.write("digraph mygraph {")
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                file.write(str(sub)+" [label=\""+str(GraphExporter.shortenURI(str(sub)))+"\"]\n")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if str(tup[1]) not in uriToNodeId:
                    file.write(str(tup[1])+" [label=\""+str(GraphExporter.shortenURI(str(tup[1])))+"\"]\n")
                    uriToNodeId[str(tup[1])] = nodecounter
                    nodecounter += 1
                file.write(str(sub) + " " + str(tup[1])+" [label=\""+str(GraphExporter.shortenURI(str(tup[0])))+"\"]\n")
                edgecounter+=1
        file.write("\n}\n")
        return None

    @staticmethod
    def convertTTLToGEXF(g,file,subjectstorender,formatt="gexf"):
        uriToNodeId = {}
        nodecounter = 0
        edges = "<edges>"
        edgecounter=0
        file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<gexf xmlns=\"http://gexf.net/1.3\" xmlns:viz=\"http://gexf.net/1.3/viz\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://gexf.net/1.3 http://gexf.net/1.3/gexf.xsd\" version=\"1.3\">\n<graph mode=\"static\" defaultedgetype=\"directed\">\n<nodes>\n")
        if subjectstorender == None:
            subjectstorender = g.subjects(None,None,True)
        for sub in subjectstorender:
            if str(sub) not in uriToNodeId:
                uriToNodeId[str(sub)] = nodecounter
                file.write("<node id=\""+str(nodecounter)+"\" value=\""+str(sub)+"\" label=\""+str(GraphExporter.shortenURI(str(sub)))+"\"><viz:color r=\"128\" g=\"0\" b=\"128\"/></node>\n")
                nodecounter += 1
            for tup in g.predicate_objects(sub):
                if isinstance(tup[1],Literal):
                    if str(tup[1]) not in uriToNodeId:
                        file.write("<node id=\"" + str(nodecounter) + "\" value=\""+str(str(tup[1]).replace("<","&lt;").replace(">","&gt;").replace("&","&amp;"))+"\" label=\"" + str(str(tup[1]).replace("<","&lt;").replace(">","&gt;").replace("&","&amp;")) + "\">\n")
                        if str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                            file.write("<viz:color r=\"255\" g=\"165\" b=\"0\"/>\n")
                        else:
                            file.write("<viz:color r=\"0\" g=\"128\" b=\"0\"/>\n")
                        file.write("</node>")
                        uriToNodeId[str(tup[1])] = nodecounter
                        nodecounter += 1
                    edges += "<edge value=\""+str(tup[0])+"\" id=\""+str(edgecounter)+"\" source=\""+str(uriToNodeId[str(sub)])+"\" target=\""+str(uriToNodeId[str(tup[1])])+"\" label=\""+str(GraphExporter.shortenURI(str(tup[0]))) + "\"/>\n"
                else:
                    if str(tup[1]) not in uriToNodeId:
                        file.write("<node id=\"" + str(nodecounter) + "\" value=\""+str(tup[1])+"\" label=\"" + str(GraphExporter.shortenURI(str(tup[1])) + "\">\n"))
                        if str(tup[0]) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                            file.write("<viz:color r=\"255\" g=\"165\" b=\"0\"/>\n")
                        else:
                            file.write("<viz:color r=\"128\" g=\"0\" b=\"128\"/>\n")
                        file.write("</node>")
                        uriToNodeId[str(tup[1])] = nodecounter
                        nodecounter += 1
                    edges += "<edge value=\""+str(tup[0])+"\" id=\""+str(edgecounter)+"\" source=\""+str(uriToNodeId[str(sub)])+"\" target=\""+str(uriToNodeId[str(tup[1])])+"\" label=\""+str(GraphExporter.shortenURI(str(tup[0]))) + "\"/>\n"
                edgecounter+=1
        file.write("</nodes>\n")
        file.write(edges)
        file.write("</edges>\n</graph>\n</gexf>")
        return None

    @staticmethod
    def serializeRDF(g, file, subjectstorender, formatt):
        g.serialize(file, encoding="utf-8", format=formatt.lower())