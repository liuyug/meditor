
import sys
import time
import os.path
import codecs
import logging

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qsci import QSCINTILLA_VERSION, QsciScintilla, QsciPrinter

from .scilib import _SciImSupport, EXTENSION_LEXER

from .util import toUtf8
from . import __home_data_path__, __data_path__, __default_basename__

logger = logging.getLogger(__name__)

EOL_DESCRIPTION = {
    QsciScintilla.EolWindows: 'CR+LF',
    QsciScintilla.EolUnix: 'LF',
    QsciScintilla.EolMac: 'CR',
}


class Editor(QsciScintilla):
    """
    Scintilla Offical Document: http://www.scintilla.org/ScintillaDoc.html
    """
    lineInputed = QtCore.pyqtSignal()
    encodingChange = QtCore.pyqtSignal('QString')
    lexerChange = QtCore.pyqtSignal('QString')
    positionChange = QtCore.pyqtSignal('int', 'int')
    eolChange = QtCore.pyqtSignal('QString')
    enable_lexer = True
    filename = None
    input_count = 0
    find_text = None
    find_forward = True
    tabWidth = 4
    edgeColumn = 78
    cur_lexer = None
    _pauseLexer = False
    _lexerStart = 0
    _lexerEnd = 0
    _imsupport = None
    _case_sensitive = False
    _whole_word = False
    _file_encoding = ''
    _modified = False

    def __init__(self, parent=None):
        super(Editor, self).__init__(parent)
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
        self.setUtf8(True)
        self.setFont(QtGui.QFont('Monospace', 12))
        self.copy_available = False
        self.copyAvailable.connect(self.setCopyAvailable)
        self.inputMethodEventCount = 0
        self._imsupport = _SciImSupport(self)

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

    def getCharAt(self, pos):
        return self.SendScintilla(QsciScintilla.SCI_GETCHARAT, pos)

    def getStyleAt(self, pos):
        return self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, pos)

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

    def setModified(self, m):
        super(Editor, self).setModified(m)
        self._modified = m

    def isModified(self):
        return super(Editor, self).isModified() or self._modified

    def setValue(self, text):
        """
        set utf8 text
        modified state is false
        """
        self.setText(text)
        self.setCursorPosition(0, 0)
        self.setModified(False)
        self.encodingChange.emit(self._file_encoding.upper())
        self.setDefaultEolMode()

    def _qsciEolModeFromOs(self):
        if sys.platform == 'win32':
            return QsciScintilla.EolWindows
        if sys.platform == 'linux':
            return QsciScintilla.EolUnix
        else:
            return QsciScintilla.EolMac

    def _qsciEolModeFromLine(self, line):
        if line.endswith('\r\n'):
            return QsciScintilla.EolWindows
        elif line.endswith('\r'):
            return QsciScintilla.EolMac
        elif line.endswith('\n'):
            return QsciScintilla.EolUnix
        else:
            return self._qsciEolModeFromOs()

    def setDefaultEolMode(self):
        if self.lines():
            mode = self._qsciEolModeFromLine(self.text(0))
        else:
            mode = self._qsciEolModeFromOs()
        self.setEolMode(mode)
        self.eolChange.emit(EOL_DESCRIPTION[mode])
        return mode

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

    def readFile(self, filename, encoding=None):
        try:
            with open(filename, 'rb') as f:
                data = f.read()
                if not encoding:
                    if data.startswith(codecs.BOM_UTF8):
                        encoding = 'utf-8-sig'
                    elif data.startswith(codecs.BOM_UTF16):
                        encoding = 'utf-16'
                    elif data.startswith(codecs.BOM_UTF32):
                        encoding = 'utf-32'
                    else:
                        encoding = 'utf8'
            text = data.decode(encoding)
        except Exception:
            encoding = sys.getfilesystemencoding()
            logging.error('%s: %s' % (filename, encoding))
            text = data.decode(encoding)
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        self._file_encoding = encoding
        self.setValue(text)
        self.setFileName(filename)
        return True

    def writeFile(self, filename=None):
        text = self.getValue()
        if filename is None:
            filename = self.getFileName()
        else:
            self.setFileName(filename)
        if filename:
            with open(filename, 'wb') as f:
                f.write(text.encode(self._file_encoding))
                self.setModified(False)
                return True
        return False

    def newFile(self, filepath):
        """filepath:
        1. /dir/filename.ext
        2. filename.ext
        3. .ext
        """
        dir_name = os.path.dirname(filepath)
        base_name = os.path.basename(filepath)
        base_name, ext = os.path.splitext(base_name)
        if not ext:
            ext = base_name
            base_name = __default_basename__
        filepath = os.path.join(dir_name, base_name + ext)
        skeletons = [
            os.path.join(__home_data_path__, 'template', 'skeleton%s' % ext),
            os.path.join(__data_path__, 'template', 'skeleton%s' % ext),
        ]
        text = ''
        for skeleton in skeletons:
            if os.path.exists(skeleton):
                with open(skeleton, 'r', encoding='utf-8') as f:
                    text = f.read()
                break
        self.setValue(text)
        self.setFileName(filepath)

    def getStatus(self):
        status = {
            'encoding': self._file_encoding.upper(),
            'eol': EOL_DESCRIPTION[self.eolMode()],
            'language': self.lexer().language(),
        }
        return status

    def emptyFile(self):
        self.clear()
        self.setFileName(None)
        self.setModified(False)

    def delete(self):
        self.removeSelectedText()

    def find(self, finddialog, readonly=False):
        finddialog.setReadOnly(readonly)
        finddialog.find_next.connect(self.findNext)
        finddialog.find_previous.connect(self.findPrevious)
        if not readonly:
            finddialog.replace_next.connect(self.replaceNext)
            finddialog.replace_all.connect(self.replaceAll)
        finddialog.exec_()
        finddialog.find_next.disconnect(self.findNext)
        finddialog.find_previous.disconnect(self.findPrevious)
        if not readonly:
            finddialog.replace_next.disconnect(self.replaceNext)
            finddialog.replace_all.disconnect(self.replaceAll)
        self._case_sensitive = finddialog.isCaseSensitive()
        self._whole_word = finddialog.isWholeWord()

    def findNext(self, text):
        line, index = self.getCursorPosition()
        bfind = self.findFirst(
            text,
            False,  # re
            self._case_sensitive,   # cs
            self._whole_word,       # wo
            True,   # wrap
            True,   # forward
            line, index
        )
        if not bfind:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Find'),
                self.tr('Not found "%s"') % (text),
            )
        return

    def findPrevious(self, text):
        line, index = self.getCursorPosition()
        index -= len(text)
        bfind = self.findFirst(
            text,
            False,  # re
            self._case_sensitive,   # cs
            self._whole_word,       # wo
            True,   # wrap
            False,   # forward
            line, index
        )
        if not bfind:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Find'),
                self.tr('Not found "%s"') % (text),
            )
        return

    def replaceNext(self, text1, text2):
        line, index = self.getCursorPosition()
        bfind = self.findFirst(
            text1,
            False,  # re
            self._case_sensitive,   # cs
            self._whole_word,       # wo
            True,   # wrap
            True,   # forward
            line, index
        )
        if bfind:
            self.replace(text2)
        else:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Replace'),
                self.tr('Not found "%s"') % (text1),
            )
        return

    def replaceAll(self, text1, text2):
        bfind = True
        while bfind:
            line, index = self.getCursorPosition()
            bfind = self.findFirst(
                text1,
                False,  # re
                self._case_sensitive,   # cs
                self._whole_word,       # wo
                True,   # wrap
                True,   # forward
                line, index
            )
            if bfind:
                self.replace(text2)
        return

    def setStyle(self, filename):
        lexer = None
        t1 = time.clock()
        if filename:
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            LexerClass = EXTENSION_LEXER.get(ext)
            lexer = LexerClass(self)
            if lexer.language() not in ['reStructedText', 'Default']:
                lexer.setFont(QtGui.QFont('Monospace', 12))
        self.setLexer(lexer)
        if lexer:
            self.lexerChange.emit(lexer.language())
        else:
            self.lexerChange.emit('')
        t2 = time.clock()
        logger.info('Lexer waste time: %s(%s)' % (t2 - t1, filename))
        self.cur_lexer = lexer

    def pauseLexer(self, pause=True):
        self._pauseLexer = pause
        if pause:
            self._lexerStart = 0
            self._lexerEnd = 0
        elif self.cur_lexer.__module__.startswith('rsteditor.scilib'):
            self.cur_lexer.styleText(self._lexerStart, self._lexerEnd)
        else:
            # PyQt5.Qsci
            pass

    def getVersion(self):
        version = '%s.%s.%s' % (
            QSCINTILLA_VERSION >> 16 & 0xff,
            QSCINTILLA_VERSION >> 8 & 0xff,
            QSCINTILLA_VERSION & 0xff,
        )
        return version


class CodeViewer(Editor):
    """ code viewer, readonly """
    def __init__(self, parent=None):
        super(CodeViewer, self).__init__(parent)
        self.setReadOnly(True)

    def setValue(self, text):
        """ set all readonly text """
        self.setText(toUtf8(text))
        self.setCursorPosition(0, 0)
        self.setModified(False)

    def find(self, finddialog, readonly=True):
        super(CodeViewer, self).find(finddialog, readonly)
