
import os.path

from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciScintilla
from PyQt4.Qsci import QsciLexerPython, QsciLexerHTML, QsciLexerBash

from rsteditor.util import toUtf8

class FindDialog(QtGui.QDialog):
    findNext = QtCore.pyqtSignal(str, int)
    findPrevious = QtCore.pyqtSignal(str, int)

    def __init__(self, *args, **kwargs):
        super(FindDialog, self).__init__(*args, **kwargs)
        label = QtGui.QLabel(self.tr('&Search for:'))
        self.lineEdit = QtGui.QLineEdit()
        label.setBuddy(self.lineEdit)

        self.wholewordCheckBox = QtGui.QCheckBox(self.tr('Match &whole word'))
        self.caseCheckBox = QtGui.QCheckBox(self.tr('&Match case'))

        self.findButton = QtGui.QPushButton(self.tr("&Find"))
        self.findButton.setDefault(True)
        self.findButton.setEnabled(False)

        closeButton = QtGui.QPushButton(self.tr('&Close'))

        self.lineEdit.textChanged.connect(self.enableFindButton)
        self.findButton.clicked.connect(self.findClicked)
        closeButton.clicked.connect(self.close)

        topLeftLayout = QtGui.QHBoxLayout()
        topLeftLayout.addWidget(label)
        topLeftLayout.addWidget(self.lineEdit)

        leftLayout = QtGui.QVBoxLayout()
        leftLayout.addLayout(topLeftLayout)
        leftLayout.addWidget(self.caseCheckBox)
        leftLayout.addWidget(self.wholewordCheckBox)

        rightLayout = QtGui.QVBoxLayout()
        rightLayout.addWidget(self.findButton)
        rightLayout.addWidget(closeButton)
        rightLayout.addStretch()

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Find"))
        self.setFixedHeight(self.sizeHint().height())

    def enableFindButton(self, text):
        self.findButton.setEnabled(not text.isEmpty())

    def findClicked(self):
        self.close()

    def getFindText(self):
        return self.lineEdit.text()

    def isCaseSensitive(self):
        return self.caseCheckBox.isChecked()

    def isWholeWord(self):
        return self.caseCheckBox.isChecked()


class Editor(QsciScintilla):
    """
    Scintilla Offical Document: http://www.scintilla.org/ScintillaDoc.html
    """
    lineInputed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)
        self.filename = None
        self.setStyle(self.filename)
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, 30)
        self.setMarginWidth(1, 5)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(78)
        self.setWrapMode(QsciScintilla.WrapCharacter)
        self.setUtf8(True)
        self.copy_available = False
        self.copyAvailable.connect(self.setCopyAvailable)
        self.input_count = 0
        self.findDialog = FindDialog(self)
        self.find_text = None
        self.find_forward = True

    def inputMethodEvent(self, event):
        super(Editor, self).inputMethodEvent(event)
        commit_text = toUtf8(event.commitString())
        if commit_text:
            self.input_count += len(commit_text)
            if self.input_count > 5:
                self.lineInputed.emit()
                self.input_count = 0
        return

    def keyPressEvent(self, event):
        super(Editor, self).keyPressEvent(event)
        input_text = toUtf8(event.text())
        if (input_text or
            ( event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return )):
            self.input_count += 1
            if (self.input_count > 5 or
                    ( event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return )):
                self.lineInputed.emit()
                self.input_count = 0
        return

    def setCopyAvailable(self, yes):
        self.copy_available = yes

    def isCopyAvailable(self):
        return self.copy_available

    def isPasteAvailable(self):
        """ always return 1 in GTK+ """
        result = self.SendScintilla(QsciScintilla.SCI_CANPASTE)
        return True if result > 1 else False

    def getHScrollValue(self):
        pos = self.horizontalScrollBar().value()
        return pos

    def getVScrollValue(self):
        pos = self.verticalScrollBar().value()
        return pos

    def getVScrollMaximum(self):
        return self.verticalScrollBar().maximum()

    def getFileName(self):
        return self.filename

    def getValue(self):
        """ get all text """
        return self.text()

    def setValue(self, text, path=None):
        """ set utf8 text """
        self.setText(toUtf8(text))
        self.setCursorPosition(1,0)
        self.filename = path
        self.setModified(False)
        self.setStyle(self.filename)

    def delete(self):
        self.removeSelectedText()

    def find(self):
        self.findDialog.exec_()
        self.find_text = self.findDialog.getFindText()
        self.findFirst(self.find_text,
                False,  # re
                self.findDialog.isCaseSensitive(),  # cs
                self.findDialog.isWholeWord(),   # wo
                True,   # wrap
                True,   # forward
                )
        return

    def findNext(self):
        line, index = self.getCursorPosition()
        self.findFirst(self.find_text,
                False,  # re
                self.findDialog.isCaseSensitive(),  # cs
                self.findDialog.isWholeWord(),   # wo
                True,   # wrap
                True,   # forward
                line, index
                )
        return

    def findPrevious(self):
        line, index = self.getCursorPosition()
        index -= len(self.find_text)
        self.findFirst(self.find_text,
                False,  # re
                self.findDialog.isCaseSensitive(),  # cs
                self.findDialog.isWholeWord(),   # wo
                True,   # wrap
                False,   # forward
                line, index
                )
        return

    def setStyle(self, filename):
        lexer = None
        if filename:
            ext = os.path.splitext(self.filename)[1].lower()
            if ext in ['.html', '.htm']:
                lexer = QsciLexerHTML(self)
            elif ext in ['.py']:
                lexer = QsciLexerPython(self)
            elif ext in ['.sh']:
                lexer = QsciLexerBash(self)
        if lexer:
            lexer.setDefaultFont(QtGui.QFont('Monospace', 12))
            self.setLexer(lexer)
        else:
            self.setLexer(None)
            self.setFont(QtGui.QFont('Monospace', 12))
        return


class CodeViewer(Editor):
    """ code viewer, readonly """
    def __init__(self, *args, **kwargs):
        super(CodeViewer, self).__init__(*args, **kwargs)
        #self.SetStyle('.html')
        self.setReadOnly(True)

    def setValue(self, text, path=None):
        """ set all readonly text """
        self.setReadOnly(False)
        super(CodeViewer, self).setValue(text, path)
        self.setReadOnly(True)
        lexer = QsciLexerHTML(self)
        lexer.setDefaultFont(QtGui.QFont('Monospace', 12))
        self.setLexer(lexer)

