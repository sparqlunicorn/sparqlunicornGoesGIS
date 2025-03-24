from qgis.PyQt.QtWidgets import QPlainTextEdit, QToolTip, QMessageBox, QWidget, QTextEdit, QCompleter
from qgis.PyQt.QtGui import QTextCursor, QPainter, QColor, QTextFormat
from qgis.PyQt.QtCore import Qt, QRect, QSize, QStringListModel
from qgis.PyQt import QtCore
from qgis.core import QgsProject, QgsMapLayer
from ...dialogs.util.varinputdialog import VarInputDialog
from ...dialogs.util.searchdialog import SearchDialog
from ..sparqlutils import SPARQLUtils
import re


class SPARQLCompleter(QCompleter):
    insertText = QtCore.pyqtSignal(str)

    def __init__(self, autocomplete, parent=None):
        QCompleter.__init__(self, list(autocomplete["clsdict"].keys()) + list(autocomplete["propdict"].keys()), parent)
        self.setFilterMode(Qt.MatchFlag.MatchContains)
        self.highlighted.connect(self.setHighlighted)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected


class LineNumberArea(QWidget):

    def __init__(self, editor):
        super().__init__(editor)
        self.myeditor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.myeditor.lineNumberAreaPaintEvent(event)


class ToolTipPlainText(QPlainTextEdit):
    triplestoreconf = None

    selector = None

    errorline = None

    savedLabels = {}

    autocomplete = None

    insertedtext = ""

    changedCompleterSetting = False

    def __init__(self, parent, triplestoreconfig, selector, columnvars, prefixes, autocomplete,curtriplestoreconf,languagemap):
        super(self.__class__, self).__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.autocomplete = autocomplete
        self.autocomplete["completerClassList"] = {}
        self.changedCompleterSetting = False
        self.languagemap=languagemap
        self.curtriplestoreconf=curtriplestoreconf
        self.completer = SPARQLCompleter(autocomplete)
        self.completer.setWidget(self)
        self.completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)
        self.completer.insertText.connect(self.insertCompletion)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.setMouseTracking(True)
        self.zoomIn(4)
        self.triplestoreconf = triplestoreconfig
        self.selector = selector
        self.prefixes = prefixes
        self.columnvars = columnvars
        self.parent = parent

    def updateCompleterData(self, stringlist):
        self.completer.setModel(QStringListModel(stringlist))

    def updateNewClassList(self):
        self.changedCompleterSetting = True

    def textUnderCursor(self, tc):
        isStartOfWord = False
        if tc.atStart() or (tc.positionInBlock() == 0):
            isStartOfWord = True
        while not isStartOfWord:
            tc.movePosition(QTextCursor.PreviousCharacter, QTextCursor.KeepAnchor)
            if tc.atStart() or (tc.positionInBlock() == 0):
                isStartOfWord = True
            elif len(tc.selectedText()) > 0 and tc.selectedText()[0] == " ":
                isStartOfWord = True
        if len(tc.selectedText()) > 0 and tc.selectedText()[0] == " ":
            tc.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        print("Key: " + str(event.key()))
        print("Modifier: " + str(event.modifiers()))
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = 0
        tc = self.textCursor()
        # msgBox=QMessageBox()
        # msgBox.setText(str(selection))
        # msgBox.exec()
        if len(layers) > 0 and event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.createVarInputDialog()
            event.accept()
            return
        elif len(layers) == 0 and event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            msgBox = QMessageBox()
            msgBox.setText(
                "No layer has been loaded in QGIS. Therefore no query variables may be created from a given QGIS layer.")
            msgBox.exec()
            event.accept()
            return
        elif (
                event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return) and not self.completer.popup().isVisible() and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.buildSearchDialog(-1, -1, -1, self, True, True)
            event.accept()
            return
        elif (event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return) and self.completer.popup().isVisible():
            self.completer.insertText.emit(self.completer.getSelected())
            self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            event.accept()
            return
        QPlainTextEdit.keyPressEvent(self, event)
        seltext = self.textUnderCursor(tc)
        tc.select(QTextCursor.LineUnderCursor)
        selline = tc.selectedText().strip()
        sellinearr = selline.split(" ")
        if len(sellinearr) == 2 and (sellinearr[0].startswith("?")):
            print("subject is variable")
            self.updateCompleterData(list(self.autocomplete["propdict"].keys()))
            self.changedCompleterSetting = True
            # msgBox=QMessageBox()
            # msgBox.setText(str(list(self.autocomplete["completerClassList"].keys())))
            # msgBox.exec()
        elif len(sellinearr) == 3 and (sellinearr[0].startswith("?")):
            print("subject and predicate")
            self.updateCompleterData(
                list(self.autocomplete["clsdict"].keys()) + list(self.autocomplete["completerClassList"].keys()))
            self.changedCompleterSetting = True
            # msgBox=QMessageBox()
            # msgBox.setText(str(list(self.autocomplete["completerClassList"].keys())))
            # msgBox.exec()
        elif self.changedCompleterSetting:
            self.updateCompleterData(
                list(self.autocomplete["clsdict"].keys()) + list(self.autocomplete["propdict"].keys()) + list(
                    self.autocomplete["completerClassList"].keys()))
            self.changedCompleterSetting = False
        # msgBox=QMessageBox()
        # msgBox.setText(str(list(self.autocomplete["completerClassList"].keys()))+" - "+str(self.changedCompleterSetting))
        # msgBox.exec()
        # for m in re.finditer(r'\S+', selline):
        #    num, part = m.start(), m.group()
        #    if (part=="." and num<len(selline)-1) or (part==";" and num<len(selline)-1) or (part=="{" and num<len(selline)-1 and num!=1) or (part=="}" and num<len(selline)-1 and num!=1):
        #        tc.setPosition(tc.selectionEnd()-1)
        #        tc.insertText(os.linesep)
        cr = self.cursorRect()
        if len(seltext) > 0:
            self.completer.setCompletionPrefix(seltext)
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                        + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()
        event.accept()
        # else:
        #    super(ToolTipPlainText, self).keyPressEvent(event)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        if completion in self.autocomplete["completerClassList"]:
            tc.movePosition(QTextCursor.Left)
            tc.movePosition(QTextCursor.EndOfWord)
            tc.setPosition(tc.position() - len(self.completer.completionPrefix()), QTextCursor.MoveAnchor)
            tc.setPosition(tc.position() + len(self.completer.completionPrefix()), QTextCursor.KeepAnchor)
            tc.removeSelectedText()
            tc.insertText(self.autocomplete["completerClassList"][completion] + " ")
            self.setTextCursor(tc)
            self.completer.popup().hide()
            return
        extra = (len(completion) - len(self.completer.completionPrefix()))
        prefix = completion.index(":")
        sub = completion[0:prefix]
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.setPosition(tc.position() - len(self.completer.completionPrefix()), QTextCursor.MoveAnchor)
        tc.setPosition(tc.position() + len(self.completer.completionPrefix()), QTextCursor.KeepAnchor)
        tc.removeSelectedText()
        newprefix = True
        if not sub in self.prefixes[self.selector.currentIndex()]:
            self.prefixes[self.selector.currentIndex()] += "PREFIX " + sub + ":<" + self.autocomplete["namespaces"][
                sub] + ">\n"
        if completion in self.autocomplete["clsdict"]:
            tc.insertText(self.autocomplete["clsdict"][completion] + " ")
        elif completion in self.autocomplete["propdict"]:
            tc.insertText(self.autocomplete["propdict"][completion] + " ")
        self.setTextCursor(tc)
        self.completer.popup().hide()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QPlainTextEdit.focusInEvent(self, event)

    def buildSearchDialog(self, row, column, interlinkOrEnrich, table, propOrClass, bothOptions):
        self.currentcol = column
        self.currentrow = row
        self.interlinkdialog = SearchDialog(column, row, self.triplestoreconf, self.prefixes, interlinkOrEnrich, table,
                                            propOrClass, bothOptions)
        self.interlinkdialog.setMinimumSize(650, 400)
        self.interlinkdialog.setWindowTitle("Search Property or Class")
        self.interlinkdialog.exec_()

    def createVarInputDialog(self):
        hasVectorLayer = False
        layers = QgsProject.instance().layerTreeRoot().children()
        for layer in layers:
            if layer.layer().type() == QgsMapLayer.VectorLayer:
                hasVectorLayer = True
        if hasVectorLayer == False:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No vector layer loaded")
            msgBox.setText("No vector layer has been loaded in QGIS to create a query variable from.")
            msgBox.exec()
            return
        self.interlinkdialog = VarInputDialog(self, self, self.columnvars,self.languagemap)
        self.interlinkdialog.setMinimumSize(650, 120)
        self.interlinkdialog.setWindowTitle("Select Column as Variable")
        self.interlinkdialog.exec_()

    def mouseMoveEvent(self, event):
        textCursor = self.cursorForPosition(event.pos())
        # word=self.textUnderCursor(textCursor)
        textCursor.select(QTextCursor.WordUnderCursor)
        word = textCursor.selectedText()
        # print(textCursor.position())
        if not word.endswith(' '):
            textCursor.setPosition(textCursor.position() + 1, QTextCursor.MoveMode.KeepAnchor)
            word = textCursor.selectedText()
        if word.strip() != "" and (word.startswith("wd:") or word.startswith("wdt:") or re.match("[:]?(Q|P)[0-9]+$",
                                                                                                 word.replace(":",
                                                                                                              ""))):
            while re.match("[QP:0-9]", word[-1]):
                textCursor.setPosition(textCursor.position() + 1, QTextCursor.MoveMode.KeepAnchor)
                word = textCursor.selectedText()
            textCursor.setPosition(textCursor.position() - 1, QTextCursor.MoveMode.KeepAnchor)
            word = textCursor.selectedText()
            if word.endswith(">"):
                textCursor.setPosition(textCursor.position() - 1, QTextCursor.MoveMode.KeepAnchor)
            word = textCursor.selectedText()
            print("Tooltip Word")
            if word in self.savedLabels:
                toolTipText = self.savedLabels[word][word.replace("wd:", "http://www.wikidata.org/entity/").replace("wdt:", "http://www.wikidata.org/prop/direct/")]["label"]
            elif "wikidata" in word or word.startswith("wd:") or word.startswith("wdt:"):
                if "http" in word:
                    word = word[word.rfind("/") + 1:-1]
                self.savedLabels[word] = SPARQLUtils.getLabelsForClasses(
                    {word.replace("wd:", "http://www.wikidata.org/entity/").replace("wdt:", "http://www.wikidata.org/prop/direct/"):{}},
                    self.triplestoreconf[self.selector.currentIndex()]["classlabelquery"],
                    self.triplestoreconf[self.selector.currentIndex()],
                    self.triplestoreconf[self.selector.currentIndex()]["resource"])
                toolTipText = self.savedLabels[word][word.replace("wd:", "http://www.wikidata.org/entity/").replace("wdt:", "http://www.wikidata.org/prop/direct/")]["label"]
            else:
                toolTipText = word
            if toolTipText != word:
                toolTipText = str(word) + ": " + str(toolTipText)
            # Put the hover over in an easy to read spot
            pos = self.cursorRect(self.textCursor()).bottomRight()
            # The pos could also be set to event.pos() if you want it directly under the mouse
            pos = self.mapToGlobal(pos)
            QToolTip.showText(event.screenPos().toPoint(), toolTipText)
        # textCursor.clearSelection()
        # self.setTextCursor(self.textCursor())

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        space += 10
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(Qt.GlobalColor.blue).lighter(190)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        borderColor = QColor(Qt.GlobalColor.lightGray).lighter(120)
        painter.fillRect(event.rect(), borderColor)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                if self.errorline is not None and blockNumber == self.errorline:
                    painter.setPen(Qt.red)
                else:
                    painter.setPen(Qt.black)
                painter.drawText(0, int(top), int(self.lineNumberArea.width()), int(height), Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
