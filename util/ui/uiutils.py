from ..sparqlutils import SPARQLUtils
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator, QValidator
from qgis.PyQt.QtCore import Qt, QUrl, QEvent
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon

MESSAGE_CATEGORY="UIUtils"

class UIUtils:

    urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    prefixregex = QRegExp("[a-z]+")

    nominatimurl='https://nominatim.openstreetmap.org/search?format=json&q={address}'

    sparqlvarregex=QRegExp("[A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]")

    classicon=QIcon(":/icons/resources/icons/class.png")
    classschemaicon=QIcon(":/icons/resources/icons/classschema.png")
    geoclassschemaicon=QIcon(":/icons/resources/icons/geoclassschema.png")
    classlinkicon=QIcon(":/icons/resources/icons/classlink.png")
    linkedgeoclassicon=QIcon(":/icons/resources/icons/linkedgeoclass.png")
    addicon=QIcon(":/icons/resources/icons/add.png")
    removeicon = QIcon(":/icons/resources/icons/remove.png")
    addclassicon=QIcon(":/icons/resources/icons/addclass.png")
    addgeoclassicon=QIcon(":/icons/resources/icons/addgeoclass.png")
    addgeoinstanceicon=QIcon(":/icons/resources/icons/addgeoinstance.png")
    addinstanceicon=QIcon(":/icons/resources/icons/addinstance.png")
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
    linkedgeoobjectpropertyicon=QIcon(":/icons/resources/icons/linkedgeoobjectproperty.png")
    datatypepropertyicon=QIcon(":/icons/resources/icons/datatypeproperty.png")
    geodatatypepropertyicon=QIcon(":/icons/resources/icons/geodatatypeproperty.png")
    geometrycollectionicon=QIcon(":/icons/resources/icons/geometrycollection.png")
    featurecollectionicon=QIcon(":/icons/resources/icons/featurecollection.png")
    addfeaturecollectionicon=QIcon(":/icons/resources/icons/addfeaturecollection.png")
    featurecollectionToRDFicon=QIcon(":/icons/resources/icons/featurecollectionToRDF.png")
    geoinstanceicon=QIcon(":/icons/resources/icons/geoinstance.png")
    sparqlunicornicon=QIcon(':/icons/resources/icons/sparqlunicorn.png')

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
        concept = str(item.data(256))
        if concept.startswith("http"):
            url = QUrl(concept)
            QDesktopServices.openUrl(url)

    @staticmethod
    def openTableURL(modelindex,table):
        if table.model().data(modelindex)!=None:
            concept=str(table.model().data(modelindex,256))
            if concept.startswith("http"):
                url = QUrl(concept)
                QDesktopServices.openUrl(url)

    @staticmethod
    def showTableURI(modelindex,table,statusbar):
        if table.model().data(modelindex)!=None:
            concept=str(table.model().data(modelindex,256))
            if concept.startswith("http"):
                statusbar.setText(concept)

    @staticmethod
    def fillAttributeTable(queryresult,invprefixes,dlg,searchResultModel,nodetype,triplestoreconf,checkboxtooltip="",checkstate=Qt.Checked):
        counter = 0
        for att in queryresult:
            curconcept = queryresult[att]["concept"]
            searchResultModel.insertRow(counter)
            itemchecked = QStandardItem()
            itemchecked.setFlags(Qt.ItemIsUserCheckable |
                                 Qt.ItemIsEnabled)
            itemchecked.setCheckState(checkstate)
            itemchecked.setToolTip(checkboxtooltip)
            if curconcept in SPARQLUtils.geoproperties:
                if SPARQLUtils.geoproperties[curconcept] == "DatatypeProperty":
                    itemchecked.setIcon(UIUtils.geodatatypepropertyicon)
                    itemchecked.setToolTip("Geo Datatype Property")
                    itemchecked.setText("GeoDP")
                    dlg.setWindowIcon(UIUtils.geoclassicon)
                elif SPARQLUtils.geoproperties[curconcept] == "ObjectProperty":
                    itemchecked.setIcon(UIUtils.geoobjectpropertyicon)
                    itemchecked.setToolTip("Geo Object Property")
                    itemchecked.setText("GeoOP")
                    dlg.setWindowIcon(UIUtils.geoclassicon)
            elif curconcept in SPARQLUtils.styleproperties:
                itemchecked.setIcon(UIUtils.objectpropertyicon)
                itemchecked.setToolTip("Style Object Property")
                itemchecked.setText("Style OP")
                #self.styleprop.append(curconcept)
            elif SPARQLUtils.namespaces["rdfs"] in curconcept \
                    or SPARQLUtils.namespaces["owl"] in curconcept \
                    or SPARQLUtils.namespaces["dc"] in curconcept \
                    or SPARQLUtils.namespaces["skos"] in curconcept:
                itemchecked.setIcon(UIUtils.annotationpropertyicon)
                itemchecked.setToolTip("Annotation Property")
                itemchecked.setText("AP")
            elif "valtype" in queryresult[att]:
                itemchecked.setIcon(UIUtils.datatypepropertyicon)
                itemchecked.setToolTip("DataType Property")
                itemchecked.setText("DP")
            elif "geoobjproperty" in triplestoreconf and curconcept in triplestoreconf["geoobjproperty"]:
                itemchecked.setIcon(UIUtils.objectpropertyicon)
                itemchecked.setToolTip("Linked Geo Object Property")
                itemchecked.setText("LGeoOP")
            else:
                itemchecked.setIcon(UIUtils.objectpropertyicon)
                itemchecked.setToolTip("Object Property")
                itemchecked.setText("OP")
            searchResultModel.setItem(counter, 0, itemchecked)
            item = QStandardItem()
            if "label" in queryresult[att]:
                item.setText(str(queryresult[att]["label"]) + " (" + SPARQLUtils.labelFromURI(
                    str(queryresult[att]["concept"]), invprefixes) + ") [" + str(
                    queryresult[att]["amount"]) + "%]")
            else:
                item.setText(
                    SPARQLUtils.labelFromURI(str(queryresult[att]["concept"]), invprefixes) + " (" + str(
                        queryresult[att]["amount"]) + "%)")
            item.setData(str(queryresult[att]["concept"]), 256)
            item.setToolTip("<html><b>Property URI</b> " + str(
                queryresult[att]["concept"]) + "<br>Double click to view definition in web browser")
            searchResultModel.setItem(counter, 1, item)
            itembutton = QStandardItem()
            if nodetype!=SPARQLUtils.instancenode and nodetype!=SPARQLUtils.geoinstancenode:
                if "valtype" in queryresult[att]:
                    itembutton.setText("Click to load samples... [" + str(queryresult[att]["valtype"]).replace(
                        "http://www.w3.org/2001/XMLSchema#", "xsd:").replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                                                             "rdf:").replace(
                        "http://www.opengis.net/ont/geosparql#", "geo:") + "]")
                    itembutton.setData(str(queryresult[att]["valtype"]), 256)
                else:
                    itembutton.setText("Click to load samples... [xsd:anyURI]")
                    itembutton.setData("http://www.w3.org/2001/XMLSchema#anyURI", 256)
            elif "val" in queryresult[att]:
                itembutton = QStandardItem()
                itembutton.setText(queryresult[att]["val"])
                itembutton.setData(queryresult[att]["valtype"], 256)
            searchResultModel.setItem(counter, 2, itembutton)
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
            if node.data(256)==None or (visible and not currentContext.visualRect(node.child(i).index()).isValid()):
                continue
            if node.child(i).data(257)==SPARQLUtils.geoclassnode or node.child(i).data(257)==SPARQLUtils.classnode:
                result.add("<" + str(node.child(i).data(256)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.child(i).data(256)) + "> <"+labelproperty+"> \""+str(SPARQLUtils.labelFromURI(str(node.child(i).data(256)),None))+"\" .\n")
                result.add("<" + str(node.data(256)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.data(256)) + "> <"+labelproperty+"> \""+str(SPARQLUtils.labelFromURI(str(node.data(256)),None))+"\" .\n")
                result.add("<"+str(node.child(i).data(256))+"> <"+subclassproperty+"> <"+str(node.data(256))+"> .\n")
            elif not classesonly and node.child(i).data(257)==SPARQLUtils.geoinstancenode or node.child(i).data(257)==SPARQLUtils.instancenode:
                result.add("<" + str(node.data(256)) + "> <"+typeproperty+"> <http://www.w3.org/2002/07/owl#Class> .\n")
                result.add("<" + str(node.data(256)) + "> <"+labelproperty+"> \"" + str(SPARQLUtils.labelFromURI(str(node.data(256)), None)) + "\" .\n")
                result.add("<" + str(node.child(i).data(256)) + "> <"+labelproperty+"> \"" + str(SPARQLUtils.labelFromURI(str(node.child(i).data(256)), None)) + "\" .\n")
                result.add("<"+str(node.child(i).data(256))+"> <"+typeproperty+"> <"+str(node.data(256))+"> .\n")
