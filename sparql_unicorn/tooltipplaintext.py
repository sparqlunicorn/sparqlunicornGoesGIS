from qgis.PyQt.QtWidgets import QPlainTextEdit, QToolTip
from qgis.PyQt.QtGui import QTextCursor

class ToolTipPlainText(QPlainTextEdit):      

    def __init__(self,parent=None):
        super(self.__class__, self).__init__(parent)
        self.setMouseTracking(True)
        
    def mouseMoveEvent(self, event):
        textCursor = self.cursorForPosition(event.pos())
        textCursor.select(QTextCursor.WordUnderCursor)
        word = textCursor.selectedText()
        #
            #msgBox=QMessageBox()
            #msgBox.setText(word)
            #msgBox.exec()
            
        #while not word.endswith(" "):
        #    self.setPosition(self.anchor()+1,QtGui.QTextCursor.KeepAnchor)
        #    word = textCursor.selectedText()        
        #if not word.startswith(" "):
            
        if True: #"http" in word:
            #if not word.endswith(' '):
                #self.moveCursor(QTextCursor.NextCharacter,QTextCursor.KeepAnchor)
                #word = textCursor.selectedText()
            toolTipText = word
            # Put the hover over in an easy to read spot
            pos = self.cursorRect(self.textCursor()).bottomRight()
            # The pos could also be set to event.pos() if you want it directly under the mouse
            pos = self.mapToGlobal(pos)
            QToolTip.showText(event.screenPos().toPoint(), word)
        #textCursor.clearSelection()
        #self.setTextCursor(self.textCursor())
