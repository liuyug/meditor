
import time
import os.path
import logging

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerHTML, \
    QsciLexerBash, QsciPrinter

from .ui.ui_findreplace import Ui_FindReplaceDialog
from .scilib import QsciLexerRest, _SciImSupport

from .util import toUtf8
from . import __home_data_path__, __data_path__, globalvars

logger = logging.getLogger(__name__)


class FindReplaceDialog(QtWidgets.QDialog):
    find_next = QtCore.pyqtSignal(str)
    find_previous = QtCore.pyqtSignal(str)
    replace_next = QtCore.pyqtSignal(str, str)
    replace_all = QtCore.pyqtSignal(str, str)
    _readonly = False

    def __init__(self, *args, **kwargs):
        super(FindReplaceDialog, self).__init__(*args, **kwargs)
        self.ui = Ui_FindReplaceDialog()
        self.ui.setupUi(self)

        self.ui.lineEdit_find.textChanged.connect(self.enableButton)
        self.ui.lineEdit_replace.textChanged.connect(self.enableButton)

        self.ui.pushButton_close.clicked.connect(self.handleButton)
        self.ui.pushButton_find_next.clicked.connect(self.handleButton)
        self.ui.pushButton_find_previous.clicked.connect(self.handleButton)
        self.ui.pushButton_replace.clicked.connect(self.handleButton)
        self.ui.pushButton_replaceall.clicked.connect(self.handleButton)

    def setReadOnly(self, readonly):
        self._readonly = readonly

    def handleButton(self):
        if self.sender() == self.ui.pushButton_close:
            self.close()
        elif self.sender() == self.ui.pushButton_find_next:
            self.find_next.emit(self.ui.lineEdit_find.text())
        elif self.sender() == self.ui.pushButton_find_previous:
            self.find_previous.emit(self.ui.lineEdit_find.text())
        elif not self._readonly and self.sender() == self.ui.pushButton_replace:
            self.replace_next.emit(
                self.ui.lineEdit_find.text(),
                self.ui.lineEdit_replace.text())
        elif not self._readonly and self.sender() == self.ui.pushButton_replaceall:
            self.replace_all.emit(
                self.ui.lineEdit_find.text(),
                self.ui.lineEdit_replace.text())

    def enableButton(self, text):
        enable = True if text else False
        if self.sender() == self.ui.lineEdit_find:
            self.ui.pushButton_find_next.setEnabled(enable)
            self.ui.pushButton_find_previous.setEnabled(enable)
        if not self._readonly and self.sender() == self.ui.lineEdit_replace:
            self.ui.pushButton_replace.setEnabled(enable)
            self.ui.pushButton_replaceall.setEnabled(enable)

    def getFindText(self):
        return self.ui.lineEdit_find.text()

    def getReplaceText(self):
        return self.ui.lineEdit_replace.text()

    def isCaseSensitive(self):
        return self.ui.checkBox_case_sensitive.isChecked()

    def isWholeWord(self):
        return self.ui.checkBox_whole_words.isChecked()


class Editor(QsciScintilla):
    """
    Scintilla Offical Document: http://www.scintilla.org/ScintillaDoc.html
    """
    lineInputed = QtCore.pyqtSignal()
    enable_lexer = True
    filename = None
    input_count = 0
    find_text = None
    find_forward = True
    tabWidth = 4
    edgeColumn = 78
    lexers = None
    cur_lexer = None
    _pauseLexer = False
    _lexerStart = 0
    _lexerEnd = 0
    _imsupport = None

    def __init__(self, parent):
        super(Editor, self).__init__(parent)
        self.lexers = {}
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, 30)
        self.setMarginWidth(1, 5)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(False)
        self.setTabWidth(self.tabWidth)
        self.setIndentationGuides(True)
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(self.edgeColumn)
        self.setWrapMode(QsciScintilla.WrapCharacter)
        self.setEolMode(QsciScintilla.EolUnix)
        self.setUtf8(True)
        self.setFont(QtGui.QFont('Monospace', 12))
        self.copy_available = False
        self.copyAvailable.connect(self.setCopyAvailable)
        self.inputMethodEventCount = 0
        self._imsupport = _SciImSupport(self)
        self.findDialog = FindReplaceDialog(self)
        self.findDialog.find_next.connect(self.findNext)
        self.findDialog.find_previous.connect(self.findPrevious)
        self.findDialog.replace_next.connect(self.replaceNext)
        self.findDialog.replace_all.connect(self.replaceAll)

    def inputMethodQuery(self, query):
        if query == QtCore.Qt.ImMicroFocus:
            l, i = self.getCursorPosition()
            p = self.positionFromLineIndex(l, i)
            x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, p)
            y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, p)
            w = self.SendScintilla(QsciScintilla.SCI_GETCARETWIDTH)
            return QtCore.QRect(x, y, w, self.textHeight(l))
        else:
            return super(Editor, self).inputMethodQuery(query)

    def inputMethodEvent(self, event):
        """
        Use default input method event handler and don't show preeditstring

        See http://doc.trolltech.com/4.7/qinputmethodevent.html
        """
        if self.isReadOnly():
            return

        # disable preedit
        # if event.preeditString() and not event.commitString():
        #     return

        if event.preeditString():
            self.pauseLexer(True)
        else:
            self.pauseLexer(False)

        # input with preedit, from TortoiseHg
        if self._imsupport:
            self.removeSelectedText()
            self._imsupport.removepreedit()
            self._imsupport.commitstr(event.replacementStart(),
                                      event.replacementLength(),
                                      event.commitString())
            self._imsupport.insertpreedit(event.preeditString())
            for a in event.attributes():
                if a.type == QtGui.QInputMethodEvent.Cursor:
                    self._imsupport.movepreeditcursor(a.start)
            event.accept()
        else:
            super(Editor, self).inputMethodEvent(event)

        # count commit string
        if event.commitString():
            commit_text = toUtf8(event.commitString())
            if commit_text:
                self.input_count += len(commit_text)
            if self.input_count > 5:
                self.lineInputed.emit()
                self.input_count = 0

    def keyPressEvent(self, event):
        super(Editor, self).keyPressEvent(event)
        input_text = toUtf8(event.text())
        if (input_text or
            (event.key() == QtCore.Qt.Key_Enter or
             event.key() == QtCore.Qt.Key_Return)):
            self.input_count += 1
        if (self.input_count > 5 or
            (event.key() == QtCore.Qt.Key_Enter or
             event.key() == QtCore.Qt.Key_Return)):
            self.lineInputed.emit()
            self.input_count = 0
        return

    def getPrinter(self, resolution):
        return QsciPrinter(resolution)

    def print_(self, printer):
        printer.printRange(self)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            super(Editor, self).contextMenuEvent(event)

    def setCopyAvailable(self, yes):
        self.copy_available = yes

    def isCopyAvailable(self):
        return self.copy_available

    def isPasteAvailable(self):
        """ always return 1 in GTK+ """
        result = self.SendScintilla(QsciScintilla.SCI_CANPASTE)
        return True if result > 0 else False

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

    def setFileName(self, path):
        """
        set filename and enable lexer
        """
        self.filename = path
        self.setStyle(self.filename)

    def enableLexer(self, enable=True):
        self.enable_lexer = enable
        self.setStyle(self.filename)

    def getValue(self):
        """ get all text """
        return self.text()

    def setValue(self, text):
        """
        set utf8 text
        modified state is false
        """
        self.setText(toUtf8(text))
        self.setCursorPosition(0, 0)
        self.setModified(False)

    def indentLines(self, inc):
        if inc:
            action = self.indent
        else:
            action = self.unindent
        if not self.hasSelectedText():
            line, index = self.getCursorPosition()
            action(line)
            if inc:
                self.setCursorPosition(line, index + self.tabWidth)
            else:
                self.setCursorPosition(line, max(0, index - self.tabWidth))
        else:
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            self.pauseLexer(True)
            for line in range(lineFrom, lineTo + 1):
                action(line)
            self.pauseLexer(False)

    def readFile(self, filename):
        try:
            with open(filename, 'rU', encoding='utf8') as f:
                text = f.read()
        except Exception as err:
            logging.error('%s: %s' % (filename, str(err)))
            logging.error('Load again with default encoding...')
            with open(filename, 'rU') as f:
                text = f.read()
        self.setValue(text)
        self.setFileName(filename)
        return True

    def writeFile(self, filename=None):
        text = toUtf8(self.getValue())
        if filename is None:
            filename = self.getFileName()
        else:
            self.setFileName(filename)
        if filename:
            with open(filename, 'wb') as f:
                f.write(text.encode('utf-8'))
                self.setModified(False)
                return True
        return False

    def emptyFile(self):
        self.clear()
        self.setFileName(None)
        self.setModified(False)

    def delete(self):
        self.removeSelectedText()

    def find(self):
        self.findDialog.exec_()

    def findNext(self, text=None):
        find_text = text or self.findDialog.getFindText()
        line, index = self.getCursorPosition()
        bfind = self.findFirst(
            find_text,
            False,  # re
            self.findDialog.isCaseSensitive(),  # cs
            self.findDialog.isWholeWord(),   # wo
            True,   # wrap
            True,   # forward
            line, index
        )
        if not bfind:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Find'),
                self.tr('Not found "%s"') % (find_text),
            )
        return

    def findPrevious(self, text=None):
        find_text = text or self.findDialog.getFindText()
        line, index = self.getCursorPosition()
        index -= len(find_text)
        bfind = self.findFirst(
            find_text,
            False,  # re
            self.findDialog.isCaseSensitive(),  # cs
            self.findDialog.isWholeWord(),   # wo
            True,   # wrap
            False,   # forward
            line, index
        )
        if not bfind:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Find'),
                self.tr('Not found "%s"') % (find_text),
            )
        return

    def replaceNext(self, text1=None, text2=None):
        find_text = text1 or self.findDialog.getFindText()
        replace_text = text2 or self.findDialog.getReplaceText()
        line, index = self.getCursorPosition()
        bfind = self.findFirst(
            find_text,
            False,  # re
            self.findDialog.isCaseSensitive(),  # cs
            self.findDialog.isWholeWord(),   # wo
            True,   # wrap
            True,   # forward
            line, index
        )
        if bfind:
            self.replace(replace_text)
        else:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Replace'),
                self.tr('Not found "%s"') % (find_text),
            )
        return

    def replaceAll(self, text1=None, text2=None):
        find_text = text1 or self.findDialog.getFindText()
        replace_text = text2 or self.findDialog.getReplaceText()
        bfind = True
        while bfind:
            line, index = self.getCursorPosition()
            bfind = self.findFirst(
                find_text,
                False,  # re
                self.findDialog.isCaseSensitive(),  # cs
                self.findDialog.isWholeWord(),   # wo
                True,   # wrap
                True,   # forward
                line, index
            )
            if bfind:
                self.replace(replace_text)
        return

    def setStyle(self, filename):
        lexer = None
        t1 = time.clock()
        if filename and self.enable_lexer:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.html', '.htm']:
                lexer = self.lexers.get('.html')
                if not lexer:
                    lexer = QsciLexerHTML(self)
                    lexer.setFont(QtGui.QFont('Monospace', 12))
                    self.lexers['.html'] = lexer
            elif ext in ['.py']:
                lexer = self.lexers.get('.py')
                if not lexer:
                    lexer = QsciLexerPython(self)
                    lexer.setFont(QtGui.QFont('Monospace', 12))
                    self.lexers['.py'] = lexer
            elif ext in ['.sh']:
                lexer = self.lexers.get('.sh')
                if not lexer:
                    lexer = QsciLexerBash(self)
                    lexer.setFont(QtGui.QFont('Monospace', 12))
                    self.lexers['.sh'] = lexer
            elif ext in ['.rst', '.rest']:
                lexer = self.lexers.get('.rest')
                if not lexer:
                    lexer = QsciLexerRest(self)
                    lexer.setDebugLevel(globalvars.logging_level)
                    rst_prop_files = [
                        os.path.join(__home_data_path__, 'rst.properties'),
                        os.path.join(__data_path__, 'rst.properties'),
                    ]
                    for rst_prop_file in rst_prop_files:
                        if os.path.exists(rst_prop_file):
                            break
                    if os.path.exists(rst_prop_file):
                        logger.debug('Loading %s', rst_prop_file)
                        lexer.readConfig(rst_prop_file)
                    else:
                        logger.info('Not found %s', rst_prop_file)
                    self.lexers['.rest'] = lexer
                else:
                    lexer.clear()
        self.setLexer(lexer)
        t2 = time.clock()
        logger.info('Lexer waste time: %s(%s)' % (
            t2 - t1, filename))
        self.cur_lexer = lexer

    def pauseLexer(self, pause=True):
        self._pauseLexer = pause
        if pause:
            self._lexerStart = 0
            self._lexerEnd = 0
        else:
            self.cur_lexer.styleText(self._lexerStart, self._lexerEnd)


class CodeViewer(Editor):
    """ code viewer, readonly """
    def __init__(self, *args, **kwargs):
        super(CodeViewer, self).__init__(*args, **kwargs)
        self.findDialog.setReadOnly(True)
        self.setReadOnly(True)

    def setValue(self, text):
        """ set all readonly text """
        self.setReadOnly(False)
        super(CodeViewer, self).setValue(text)
        self.setReadOnly(True)
