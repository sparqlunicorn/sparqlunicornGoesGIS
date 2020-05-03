from qgis.PyQt.QtWidgets import QPlainTextEdit, QToolTip
from qgis.PyQt.QtGui import QTextCursor
import json
import requests

class ToolTipPlainText(QPlainTextEdit):      

    triplestoreconf=None
     
    selector=None

    def __init__(self,parent,triplestoreconfig,selector):
        super(self.__class__, self).__init__(parent)
        self.setMouseTracking(True)
        self.zoomIn(4)
        self.triplestoreconf=triplestoreconfig
        self.selector=selector
        
    def mouseMoveEvent(self, event):
        textCursor = self.cursorForPosition(event.pos())
        textCursor.select(QTextCursor.WordUnderCursor)
        word = textCursor.selectedText()
        print(textCursor.position())           
        if False:
            while not word.endswith(' '):
                textCursor.setPosition(textCursor.position()+1,QTextCursor.KeepAnchor)
                word = textCursor.selectedText()
            textCursor.setPosition(textCursor.position()-1,QTextCursor.KeepAnchor)
            word = textCursor.selectedText()
            if word.endswith(">"):
                textCursor.setPosition(textCursor.position()-1,QTextCursor.KeepAnchor)     
            word = textCursor.selectedText()
            print("Tooltip Word")
            #if "wikidata" in word or word.startswith("wd:"):
            #    self.getLabelsForClasses([word],self.selector.currentIndex())
            toolTipText = word
            # Put the hover over in an easy to read spot
            pos = self.cursorRect(self.textCursor()).bottomRight()
            # The pos could also be set to event.pos() if you want it directly under the mouse
            pos = self.mapToGlobal(pos)
            QToolTip.showText(event.screenPos().toPoint(), word)
        #textCursor.clearSelection()
        #self.setTextCursor(self.textCursor())
        
    def getLabelsForClasses(self,classes,endpointIndex):
        result=[]
        query=self.triplestoreconf[self.selector.currentIndex()]["classlabelquery"]
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
                if (i%50)==0:
                    print(url.replace("%%concepts%%",qidquery))
                    myResponse = json.loads(requests.get(url.replace("%%concepts%%",qidquery)).text)
                    print(myResponse)
                    for ent in myResponse["entities"]:
                        print(ent)
                        if "en" in myResponse["entities"][ent]["labels"]:
                            result.append(myResponse["entities"][ent]["labels"]["en"]["value"])                
                    qidquery=""
                else:
                    qidquery+="|"
                i=i+1
        return result[0]
