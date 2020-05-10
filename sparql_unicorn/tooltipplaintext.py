from qgis.PyQt.QtWidgets import QPlainTextEdit, QToolTip,QMessageBox
from qgis.PyQt.QtGui import QTextCursor
from PyQt5.QtCore import Qt
from qgis.core import QgsProject
from .varinput import VarInputDialog
import json
import re
import requests

class ToolTipPlainText(QPlainTextEdit):      

    triplestoreconf=None
     
    selector=None
	
    savedLabels={}

    def __init__(self,parent,triplestoreconfig,selector,columnvars):
        super(self.__class__, self).__init__(parent)
        self.setMouseTracking(True)
        self.zoomIn(4)
        self.triplestoreconf=triplestoreconfig
        self.selector=selector
        self.columnvars=columnvars
        self.parent=parent

    def keyPressEvent(self, event):
        print("Key: "+str(event.key()))
        print("Modifier: "+str(event.modifiers()))
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = 0
        if len(layers)>0 and event.key()==Qt.Key_Space and event.modifiers()==Qt.ControlModifier:
            self.createVarInputDialog()
            event.accept()
        else:
            super(ToolTipPlainText, self).keyPressEvent(event)
            
    def createVarInputDialog(self):
        self.interlinkdialog = VarInputDialog(self,self,self.columnvars)
        self.interlinkdialog.setMinimumSize(650, 500)
        self.interlinkdialog.setWindowTitle("Select Column as Variable")
        self.interlinkdialog.exec_()
        
    def mouseMoveEvent(self, event):
        textCursor = self.cursorForPosition(event.pos())
        textCursor.select(QTextCursor.WordUnderCursor)
        word = textCursor.selectedText()
        print(textCursor.position())    
        if not word.endswith(' '):
            textCursor.setPosition(textCursor.position()+1,QTextCursor.KeepAnchor)
            word = textCursor.selectedText()
        if word.strip()!="" and (word.startswith("wd:") or word.startswith("wdt:") or re.match("^(Q|P)[0-9]+$", word.replace(":",""))):
            while re.match("[QP:0-9]",word[-1]):
                textCursor.setPosition(textCursor.position()+1,QTextCursor.KeepAnchor)
                word = textCursor.selectedText()
            textCursor.setPosition(textCursor.position()-1,QTextCursor.KeepAnchor)
            word = textCursor.selectedText()
            if word.endswith(">"):
                textCursor.setPosition(textCursor.position()-1,QTextCursor.KeepAnchor)     
            word = textCursor.selectedText()
            print("Tooltip Word")
            if word in self.savedLabels:
                toolTipText=self.savedLabels[word]
            elif "wikidata" in word or word.startswith("wd:") or word.startswith("wdt:"):
                self.savedLabels[word]=self.getLabelsForClasses([word.replace("wd:","").replace("wdt:","")],self.selector.currentIndex())
                toolTipText=self.savedLabels[word]
            else:
               toolTipText = word
            if ":" in word and toolTipText!=word:
                toolTipText=word[word.index(":")+1:]+":"+toolTipText
            elif toolTipText!=word:
                toolTipText=word+":"+toolTipText
            # Put the hover over in an easy to read spot
            pos = self.cursorRect(self.textCursor()).bottomRight()
            # The pos could also be set to event.pos() if you want it directly under the mouse
            pos = self.mapToGlobal(pos)
            QToolTip.showText(event.screenPos().toPoint(), toolTipText)
        #textCursor.clearSelection()
        #self.setTextCursor(self.textCursor())
        
    def getLabelsForClasses(self,classes,endpointIndex):
        result=[]
        if classes[0].startswith("Q"):
            query=self.triplestoreconf[self.selector.currentIndex()]["classlabelquery"]
        elif classes[0].startswith("P"):
            query=self.triplestoreconf[self.selector.currentIndex()]["propertylabelquery"]
        print("Get Labels for Tooltip")
        #url="https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids="
        if "SELECT" in query:
            vals="VALUES ?class { "
            for qid in classes:
                vals+=qid+" "
            vals+="}\n"
            query=query.replace("%%concepts%%",vals)
            sparql = SPARQLWrapper(triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for res in results["results"]["bindings"]:
                result.append(res["class"]["value"])
        else:
            url=self.triplestoreconf[self.selector.currentIndex()]["classlabelquery"]
            i=0
            qidquery=""
            for qid in classes:
                print(qid)
                if "Q" in qid:
                    qidquery+="Q"+qid.split("Q")[1]
                if "P" in qid:
                    qidquery+="P"+qid.split("P")[1]
                if (i%50)==0:
                    print(url.replace("%%concepts%%",qidquery))
                    myResponse = json.loads(requests.get(url.replace("%%concepts%%",qidquery)).text)
                    print(myResponse)
                    if "entities" in myResponse:
                        for ent in myResponse["entities"]:
                            print(ent)
                            if "en" in myResponse["entities"][ent]["labels"]:
                                result.append(myResponse["entities"][ent]["labels"]["en"]["value"])                
                        qidquery=""
                    else:
                        qidquery+="|"
                i=i+1
        if len(result)>0:
            return result[0]
        return ""
