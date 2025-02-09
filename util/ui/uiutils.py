from ..sparqlutils import SPARQLUtils
from ..doc.docconfig import DocConfig
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator, QValidator, QIcon
from qgis.PyQt.QtCore import Qt, QUrl, QEvent
from qgis.PyQt.QtGui import QDesktopServices, QStandardItemModel, QStandardItem, QIntValidator, QDoubleValidator
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import QCompleter, QLineEdit
from qgis.core import QgsMessageLog
from qgis.core import Qgis
import json

MESSAGE_CATEGORY="UIUtils"

class UIUtils:


    urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    baselayerurlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\)\{\},]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    prefixregex = QRegExp("[a-z]+")

    nominatimurl='https://nominatim.openstreetmap.org/search?format=json&q={address}'

    sparqlvarregex=QRegExp("[A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]")

    dataslot_conceptURI=256

    dataslot_nodetype=257

    dataslot_instanceamount=258

    dataslot_instancesloaded=259

    dataslot_linkedconceptrel=260

    dataslot_geoinstanceamount = 261

    dataslot_language = 262

    classicon=QIcon(":/icons/resources/icons/class.png")
    classschemaicon=QIcon(":/icons/resources/icons/classschema.png")
    geoclassschemaicon=QIcon(":/icons/resources/icons/geoclassschema.png")
    classlinkicon=QIcon(":/icons/resources/icons/classlink.png")
    ontdocicon=QIcon(":/icons/resources/icons/ontdoc.png")
    layerFromRDF=QIcon(":/icons/resources/icons/layerFromRDF.png")
    linkedgeoclassicon=QIcon(":/icons/resources/icons/linkedgeoclass.png")
    linkedgeoinstanceicon=QIcon(":/icons/resources/icons/linkedgeoinstance.png")
    linkedgeoclassschemaicon=QIcon(":/icons/resources/icons/linkedgeoclassschema.png")
    addicon=QIcon(":/icons/resources/icons/add.png")
    georelationpropertyicon = QIcon(":/icons/resources/icons/georelationproperty.png")
    geoendpointicon = QIcon(":/icons/resources/icons/geoendpoint.png")
    removeicon = QIcon(":/icons/resources/icons/remove.png")
    addclassicon=QIcon(":/icons/resources/icons/addclass.png")
    addgeoclassicon=QIcon(":/icons/resources/icons/addgeoclass.png")
    addgeoinstanceicon=QIcon(":/icons/resources/icons/addgeoinstance.png")
    addlinkedgeoinstanceicon = QIcon(":/icons/resources/icons/addlinkedgeoinstance.png")
    addlinkedgeoclassicon = QIcon(":/icons/resources/icons/addlinkedgeoclass.png")
    addinstanceicon=QIcon(":/icons/resources/icons/addinstance.png")
    allrightsreservedicon=QIcon(":/icons/resources/icons/allrightsreserved.png")
    ccbyicon=QIcon(":/icons/resources/icons/ccby.png")
    ccbysaicon=QIcon(":/icons/resources/icons/ccbysa.png")
    ccbyndicon=QIcon(":/icons/resources/icons/ccbynd.png")
    ccbyncicon=QIcon(":/icons/resources/icons/ccbync.png")
    ccbyncsaicon=QIcon(":/icons/resources/icons/ccbyncsa.png")
    ccbyncndicon=QIcon(":/icons/resources/icons/ccbyncnd.png")
    nolicenseicon=QIcon(":/icons/resources/icons/nolicense.png")
    cczeroicon=QIcon(":/icons/resources/icons/zero.png")
    countinstancesicon=QIcon(":/icons/resources/icons/countinstances.png")
    geoclassicon=QIcon(":/icons/resources/icons/geoclass.png")
    subclassicon=QIcon(":/icons/resources/icons/subclass.png")
    searchclassicon=QIcon(":/icons/resources/icons/searchclass.png")
    rdffileicon=QIcon(":/icons/resources/icons/rdffile.png")
    columnasvaricon=QIcon(":/icons/resources/icons/columnasvar.png")
    queryinstancesicon=QIcon(":/icons/resources/icons/queryinstances.png")
    bboxicon=QIcon(":/icons/resources/icons/bboxicon.png")
    instanceicon=QIcon(":/icons/resources/icons/instance.png")
    instancelinkicon=QIcon(":/icons/resources/icons/instancelink.png")
    linkeddataicon=QIcon(":/icons/resources/icons/linkeddata.png")
    validationicon=QIcon(":/icons/resources/icons/validation2.png")
    halfgeoclassicon=QIcon(":/icons/resources/icons/halfgeoclass.png")
    annotationpropertyicon=QIcon(":/icons/resources/icons/annotationproperty.png")
    geoannotationpropertyicon=QIcon(":/icons/resources/icons/geoannotationproperty.png")
    objectpropertyicon=QIcon(":/icons/resources/icons/objectproperty.png")
    geoobjectpropertyicon=QIcon(":/icons/resources/icons/geoobjectproperty.png")
    labelannotationpropertyicon = QIcon(":/icons/resources/icons/labelannotationproperty.png")
    commentannotationpropertyicon = QIcon(":/icons/resources/icons/commentannotationproperty.png")
    linkedgeoobjectpropertyicon=QIcon(":/icons/resources/icons/linkedgeoobjectproperty.png")
    relationobjectpropertyicon = QIcon(":/icons/resources/icons/relationobjectproperty.png")
    datatypepropertyicon=QIcon(":/icons/resources/icons/datatypeproperty.png")
    geodatatypepropertyicon=QIcon(":/icons/resources/icons/geodatatypeproperty.png")
    geometrycollectionicon=QIcon(":/icons/resources/icons/geometrycollection.png")
    featurecollectionicon=QIcon(":/icons/resources/icons/featurecollection.png")
    featurecollectionlinkicon=QIcon(":/icons/resources/icons/featurecollectionlink.png")
    featurecollectionschemaicon=QIcon(":/icons/resources/icons/featurecollectionschema.png")
    addfeaturecollectionicon=QIcon(":/icons/resources/icons/addfeaturecollection.png")
    featurecollectionToRDFicon=QIcon(":/icons/resources/icons/featurecollectionToRDF.png")
    geoinstanceicon=QIcon(":/icons/resources/icons/geoinstance.png")
    sparqlunicornicon=QIcon(':/icons/resources/icons/sparqlunicorn.png')

    nodetypeToIcon={
     SPARQLUtils.classnode: classicon,
     SPARQLUtils.geoclassnode: geoclassicon,
     SPARQLUtils.instancenode: instanceicon,
     SPARQLUtils.geoinstancenode: geoinstanceicon,
    }

    @staticmethod
    def createTripleStoreCBox(cbox,triplestoreconf):
        for triplestore in triplestoreconf:
            if triplestore["active"]:
                item = triplestore["name"]
                if "mandatoryvariables" in triplestore and len(triplestore["mandatoryvariables"]) > 0:
                    item += " --> "
                    for mandvar in triplestore["mandatoryvariables"]:
                        item += "?" + mandvar + " "
                isfile=False
                if "resource" in triplestore and "type" in triplestore["resource"] and triplestore["resource"]["type"]=="file":
                    if triplestore["resource"]["url"].startswith("http"):
                        item += " [URIResource]"
                    else:
                        item += " [File]"
                    cbox.addItem(UIUtils.rdffileicon, item)
                elif "type" in triplestore and triplestore["type"] == "geosparqlendpoint":
                    item += " [GeoSPARQL Endpoint]"
                    cbox.addItem(UIUtils.geoendpointicon, item)
                elif "type" in triplestore and triplestore["type"] == "sparqlendpoint":
                    item += " [SPARQL Endpoint]"
                    cbox.addItem(UIUtils.linkeddataicon, item)
                elif "type" in triplestore and triplestore["type"] == "file":
                    item += " [File]"
                    cbox.addItem(UIUtils.rdffileicon, item)
                else:
                    cbox.addItem(item)
        cbox.setCurrentIndex(0)

    @staticmethod
    def createLanguageSelectionCBox(cbox,languagemap):
        cbox.clear()
        model =QStandardItemModel()
        cbox.setModel(model)
        for lang in languagemap:
            curitem=QStandardItem()
            curitem.setText(languagemap[lang])
            curitem.setData(lang,UIUtils.dataslot_language)
            model.appendRow(curitem)
        comp=QCompleter(languagemap.values(), cbox)
        comp.setCaseSensitivity(Qt.CaseInsensitive)
        comp.setCompletionMode(QCompleter.PopupCompletion)
        cbox.setCompleter(comp)
        cbox.setCurrentIndex(0)

    @staticmethod
    def check_state(sender):
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    @staticmethod
    def openListURL(item):
        concept = str(item.data(UIUtils.dataslot_conceptURI))
        if concept.startswith("http"):
            url = QUrl(concept)
            QDesktopServices.openUrl(url)

    @staticmethod
    def openTableURL(modelindex,table):
        if table.model().data(modelindex) is not None:
            concept=str(table.model().data(modelindex,UIUtils.dataslot_conceptURI))
            if concept.startswith("http"):
                url = QUrl(concept)
                QDesktopServices.openUrl(url)

    @staticmethod
    def showTableURI(modelindex,table,statusbar):
        if table.model().data(modelindex) is not None:
            concept=str(table.model().data(modelindex,UIUtils.dataslot_conceptURI))
            if concept.startswith("http"):
                statusbar.setText(concept)

    @staticmethod
    def detectItemNodeType(itemchecked,curconcept,triplestoreconf,queryresult=None,att=None,dlg=None,text=None,tooltip=None):
        itemchecked.setData(curconcept, UIUtils.dataslot_conceptURI)
        if curconcept in DocConfig.geoproperties:
            if DocConfig.geoproperties[curconcept] == "DatatypeProperty":
                itemchecked.setIcon(UIUtils.geodatatypepropertyicon)
                itemchecked.setToolTip("Geo Datatype Property")
                itemchecked.setData(SPARQLUtils.geodatatypepropertynode,UIUtils.dataslot_nodetype)
                itemchecked.setText("GeoDP")
                if dlg is not None:
                    dlg.setWindowIcon(UIUtils.geoclassicon)
            elif DocConfig.geoproperties[curconcept] == "ObjectProperty":
                itemchecked.setIcon(UIUtils.geoobjectpropertyicon)
                itemchecked.setData(SPARQLUtils.geoobjectpropertynode,UIUtils.dataslot_nodetype)
                itemchecked.setToolTip("Geo Object Property")
                itemchecked.setText("GeoOP")
                if dlg is not None:
                    dlg.setWindowIcon(UIUtils.geoclassicon)
        elif curconcept in DocConfig.styleproperties:
            itemchecked.setIcon(UIUtils.objectpropertyicon)
            itemchecked.setData(SPARQLUtils.objectpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Style Object Property")
            itemchecked.setText("Style OP")
        elif curconcept in DocConfig.georelationproperties:
            itemchecked.setIcon(UIUtils.georelationpropertyicon)
            itemchecked.setData(SPARQLUtils.objectpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Geo Relation Property")
            itemchecked.setText("GeoRelP")
        elif curconcept in DocConfig.commentproperties:
            itemchecked.setIcon(UIUtils.commentannotationpropertyicon)
            itemchecked.setData(SPARQLUtils.annotationpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Description Property")
            itemchecked.setText("Description Property")
        elif curconcept in DocConfig.labelproperties:
            itemchecked.setIcon(UIUtils.labelannotationpropertyicon)
            itemchecked.setData(SPARQLUtils.annotationpropertynode, UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Label Property")
            itemchecked.setText("Label Property")
        elif curconcept in DocConfig.relationproperties:
            itemchecked.setIcon(UIUtils.relationobjectpropertyicon)
            itemchecked.setData(SPARQLUtils.annotationpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Relation Property")
            itemchecked.setText("Relation Property")
        elif SPARQLUtils.namespaces["rdfs"] in curconcept \
                or SPARQLUtils.namespaces["owl"] in curconcept \
                or SPARQLUtils.namespaces["dc"] in curconcept \
                or SPARQLUtils.namespaces["skos"] in curconcept:
            itemchecked.setIcon(UIUtils.annotationpropertyicon)
            itemchecked.setData(SPARQLUtils.annotationpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Annotation Property")
            itemchecked.setText("AP")
        elif att is not None and queryresult is not None \
                and "valtype" in queryresult[att]:
            itemchecked.setIcon(UIUtils.datatypepropertyicon)
            itemchecked.setData(SPARQLUtils.datatypepropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("DataType Property")
            itemchecked.setText("DP")
        elif "geoobjproperty" in triplestoreconf and curconcept in triplestoreconf["geoobjproperty"]:
            itemchecked.setIcon(UIUtils.linkedgeoobjectpropertyicon)
            itemchecked.setData(SPARQLUtils.objectpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Linked Geo Object Property")
            itemchecked.setText("LGeoOP")
        else:
            itemchecked.setIcon(UIUtils.objectpropertyicon)
            itemchecked.setData(SPARQLUtils.objectpropertynode,UIUtils.dataslot_nodetype)
            itemchecked.setToolTip("Object Property")
            itemchecked.setText("OP")
        if text is not None:
            itemchecked.setText(text)
        if tooltip is not None:
            itemchecked.setToolTip(tooltip)
        return itemchecked

    @staticmethod
    def fillAttributeTable(queryresult,invprefixes,dlg,searchResultModel,nodetype,triplestoreconf,checkboxtooltip="",checkstate=Qt.Unchecked,isclasstable=False):
        counter = 0
        for att in queryresult:
            curconcept = queryresult[att]["concept"]
            searchResultModel.insertRow(counter)
            itemchecked = QStandardItem()
            itemchecked.setFlags(Qt.ItemIsUserCheckable |
                                 Qt.ItemIsEnabled)
            itemchecked.setCheckState(checkstate)
            itemchecked.setToolTip(checkboxtooltip)
            if isclasstable:
                itemchecked.setIcon(UIUtils.classicon)
                itemchecked.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                itemchecked.setToolTip("Class")
                #itemchecked.setText("Class")
            else:
                itemchecked=UIUtils.detectItemNodeType(itemchecked,curconcept,triplestoreconf,queryresult,att,dlg)
            searchResultModel.setItem(counter, 0, itemchecked)
            item = QStandardItem()
            if "label" in queryresult[att] and queryresult[att]["label"]!="":
                thetext=str(queryresult[att]["label"]) + " (" + SPARQLUtils.labelFromURI(str(queryresult[att]["concept"]), invprefixes) + ")"
                if "amount" in queryresult[att]:
                    thetext+=" [" + str(queryresult[att]["amount"]) + "%]"
                item.setText(thetext)
            else:
                thetext=SPARQLUtils.labelFromURI(str(queryresult[att]["concept"]), invprefixes)
                if "amount" in queryresult[att]:
                    thetext+=" [" + str(queryresult[att]["amount"]) + "%]"
                item.setText(thetext)
            item.setData(str(queryresult[att]["concept"]), UIUtils.dataslot_conceptURI)
            item.setToolTip("<html><b>Property URI</b> " + str(
                queryresult[att]["concept"]) + "<br>Double click to view definition in web browser")
            searchResultModel.setItem(counter, 1, item)
            itembutton = QStandardItem()
            if nodetype is not SPARQLUtils.instancenode and nodetype is not SPARQLUtils.geoinstancenode:
                if "valtype" in queryresult[att]:
                    itembutton.setText("Click to load samples... [" + str(queryresult[att]["valtype"]).replace(
                        "http://www.w3.org/2001/XMLSchema#", "xsd:").replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                                                             "rdf:").replace(
                        "http://www.opengis.net/ont/geosparql#", "geo:") + "]")
                    itembutton.setData(str(queryresult[att]["valtype"]), UIUtils.dataslot_conceptURI)
                else:
                    itembutton.setText("Click to load samples... [xsd:anyURI]")
                    itembutton.setData("http://www.w3.org/2001/XMLSchema#anyURI", UIUtils.dataslot_conceptURI)
            elif "val" in queryresult[att]:
                itembutton = QStandardItem()
                itembutton.setText(queryresult[att]["val"])
                itembutton.setData(queryresult[att]["valtype"], UIUtils.dataslot_conceptURI)
            searchResultModel.setItem(counter, 2, itembutton)
            #itembutton = QStandardItem()
            #if "valtype" in queryresult[att]:
            #    if queryresult[att]["valtype"] in DocConfig.integertypes:
            #        itembutton=QLineEdit()
            #        itembutton.setValidator(QIntValidator(-1000000,1000000,itembutton))
            #    elif queryresult[att]["valtype"] in DocConfig.floattypes:
            #        itembutton=QLineEdit()
            #        itembutton.setValidator(QDoubleValidator(-1000000,1000000,itembutton))
            #    else:
            #        itembutton = QLineEdit()
            #searchResultModel.setItem(counter, 3, itembutton)
            counter += 1

    @staticmethod
    def iterateTree(node,result,visible,classesonly,triplestoreconf,currentContext):
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        labelproperty="http://www.w3.org/2000/01/rdf-schema#label"
        subclassproperty="http://www.w3.org/2000/01/rdf-schema#subClassOf"
        if "labelproperty" in triplestoreconf:
            labelproperty=triplestoreconf["labelproperty"]
        if "typeproperty" in triplestoreconf:
            typeproperty=triplestoreconf["typeproperty"]
        if "subclassproperty" in triplestoreconf:
            subclassproperty=triplestoreconf["subclassproperty"]
        for i in range(node.rowCount()):
            if node.child(i).hasChildren():
                UIUtils.iterateTree(node.child(i),result,visible,classesonly,triplestoreconf,currentContext)
            if node.data(UIUtils.dataslot_conceptURI) is None or (visible and not currentContext.visualRect(node.child(i).index()).isValid()):
                continue
            if node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoclassnode or node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.classnode:
                result.add("<" + str(node.child(i).data(UIUtils.dataslot_conceptURI)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.child(i).data(UIUtils.dataslot_conceptURI)) + "> <"+labelproperty+"> \""+str(SPARQLUtils.labelFromURI(str(node.child(i).data(UIUtils.dataslot_conceptURI)),None))+"\" .\n")
                result.add("<" + str(node.data(UIUtils.dataslot_conceptURI)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.data(UIUtils.dataslot_conceptURI)) + "> <"+labelproperty+"> \""+str(SPARQLUtils.labelFromURI(str(node.data(UIUtils.dataslot_conceptURI)),None))+"\" .\n")
                result.add("<"+str(node.child(i).data(UIUtils.dataslot_conceptURI))+"> <"+subclassproperty+"> <"+str(node.data(UIUtils.dataslot_conceptURI))+"> .\n")
            elif not classesonly and node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoinstancenode or node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.instancenode:
                result.add("<" + str(node.data(UIUtils.dataslot_conceptURI)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.data(UIUtils.dataslot_conceptURI)) + "> <"+labelproperty+"> \"" + str(SPARQLUtils.labelFromURI(str(node.data(UIUtils.dataslot_conceptURI)), None)) + "\" .\n")
                result.add("<" + str(node.child(i).data(UIUtils.dataslot_conceptURI)) + "> <"+labelproperty+"> \"" + str(SPARQLUtils.labelFromURI(str(node.child(i).data(UIUtils.dataslot_conceptURI)), None)) + "\" .\n")
                result.add("<"+str(node.child(i).data(UIUtils.dataslot_conceptURI))+"> <"+typeproperty+"> <"+str(node.data(UIUtils.dataslot_conceptURI))+"> .\n")

    @staticmethod
    def iterateTreeToJSON(node,result,visible,classesonly,triplestoreconf,currentContext):
        result["children"]=[]
        result["conceptURI"] = node.data(UIUtils.dataslot_conceptURI)
        if node.data(UIUtils.dataslot_instanceamount) is not None:
            result["instanceamount"] = node.data(UIUtils.dataslot_instanceamount)
        if "[" in node.text() and "]" in node.text():
            result["text"] = node.text()[0:node.text().rfind("[")]
        else:
            result["text"] = node.text()
        result["nodetype"] = node.data(UIUtils.dataslot_nodetype)
        childcounter=0
        for i in range(node.rowCount()):
            result["children"].append({})
            if node.child(i).hasChildren():
                UIUtils.iterateTreeToJSON(node.child(i),result["children"][i],visible,classesonly,triplestoreconf,currentContext)
            if node.child(i).data(UIUtils.dataslot_conceptURI) is None or (visible and not currentContext.visualRect(node.child(i).index()).isValid()):
                continue
            if node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoclassnode or node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.classnode:
                result["children"][i]["conceptURI"]=node.child(i).data(UIUtils.dataslot_conceptURI)
                if node.child(i).data(UIUtils.dataslot_instanceamount) is not None:
                    result["children"][i]["instanceamount"]=node.child(i).data(UIUtils.dataslot_instanceamount)
                if "[" in node.child(i).text() and "]" in node.child(i).text():
                    result["children"][i]["text"]=node.child(i).text()[0:node.child(i).text().rfind("[")]
                else:
                    result["children"][i]["text"]=node.child(i).text()
                result["children"][i]["nodetype"]=str(node.child(i).data(UIUtils.dataslot_nodetype))
            elif not classesonly and node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoinstancenode or node.child(i).data(UIUtils.dataslot_nodetype)==SPARQLUtils.instancenode:
                result["children"][i]["conceptURI"]=node.child(i).data(UIUtils.dataslot_conceptURI)
                if node.child(i).data(UIUtils.dataslot_instanceamount) is not None:
                    result["children"][i]["instanceamount"]=node.child(i).data(UIUtils.dataslot_instanceamount)
                if "[" in node.child(i).text() and "]" in node.child(i).text():
                    result["children"][i]["text"]=node.child(i).text()[0:node.child(i).text().rfind("[")]
                else:
                    result["children"][i]["text"]=node.child(i).text()
                result["children"][i]["nodetype"]=str(node.child(i).data(UIUtils.dataslot_nodetype))
        if result["children"]==[]:
            del result["children"]
        if "children" in result:
            for child in result["children"]:
                if child=={}:
                    result["children"].remove(child)


    @staticmethod
    def loadTreeFromJSONFile(rootNode,filepath):
        QgsMessageLog.logMessage("FILEPATH: " + str(filepath), MESSAGE_CATEGORY, Qgis.Info)
        with open(filepath, 'r') as f:
            jsontree = json.load(f)
        #QgsMessageLog.logMessage("JSONTREE: " + str(jsontree), MESSAGE_CATEGORY, Qgis.Info)
        elemcount=0
        if "children" in jsontree:
            elemcount=UIUtils.iterateTree(rootNode,jsontree["children"],elemcount)
        return elemcount

    @staticmethod
    def iterateTreeToJSTree():
        print("Tree to JSTree Export")

    @staticmethod
    def iterateTree(curnode,jsontree,elemcount):
        #QgsMessageLog.logMessage("JSONTree: " + str(jsontree), MESSAGE_CATEGORY, Qgis.Info)
        for elem in jsontree:
            #QgsMessageLog.logMessage("Elem: " + str(elem), MESSAGE_CATEGORY, Qgis.Info)
            if elem=={}:
                continue
            elemcount+=1
            curitem=QStandardItem()
            if "text" in elem:
                curitem.setText(elem["text"])
            if "nodetype" in elem:
                curitem.setData(elem["nodetype"], UIUtils.dataslot_nodetype)
                if elem["nodetype"] in UIUtils.nodetypeToIcon:
                    curitem.setIcon(UIUtils.nodetypeToIcon[elem["nodetype"]])
                else:
                    curitem.setIcon(UIUtils.classicon)
            if "conceptURI" in elem:
                curitem.setData(elem["conceptURI"],UIUtils.dataslot_conceptURI)
            if "instanceamount" in elem:
                curitem.setData(elem["instanceamount"],UIUtils.dataslot_instanceamount)
                curitem.setText(curitem.text()+"["+elem["instanceamount"]+"]")
            curnode.appendRow(curitem)
            if "children" in elem and not isinstance(elem, str) and isinstance(elem["children"], list) and elem[
                "children"] != []:
                elemcount=UIUtils.iterateTree(curitem, elem["children"], elemcount)
        return elemcount

    def treeToFlatJSON(self,rootNode):
        if rootNode.hasChildren():
            print("hasChildren")

    def mergeJSONTree(self,jsontree_one,jsontree_two):
        print("Merge class trees")
        classindex1={}




