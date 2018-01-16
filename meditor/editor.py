
import sys
import time
import os.path
import logging
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qsci import QSCINTILLA_VERSION, QsciScintilla, QsciPrinter
import chardet

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
    inputPreviewRequest = QtCore.pyqtSignal()
    statusChanged = QtCore.pyqtSignal('QString')
    filesDropped = QtCore.pyqtSignal('QString')
    enable_lexer = True
    filename = None
    find_text = None
    find_forward = True
    tabWidth = 4
    cur_lexer = None
    _latest_input_count = 0
    _latest_input_time = 0
    _timer_interval = 1
    _timer = None
    _edgeColumn = 80
    _pauseLexer = False
    _lexerStart = 0
    _lexerEnd = 0
    _imsupport = None
    _file_encoding = 'utf8'
    _modified = False
    _actions = None
    _find_dialog = None
    _margin_width = 3

    def __init__(self, find_dialog, parent=None):
        super(Editor, self).__init__(parent)
        self._find_dialog = find_dialog
        # Scintilla
        self._fontmetrics = QtGui.QFontMetrics(self.font())
        self.setMarginsFont(self.font())
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, self._fontmetrics.width('0' * self._margin_width) + 6)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(False)
        self.setTabWidth(self.tabWidth)
        self.setIndentationGuides(True)
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(self._edgeColumn)
        self.setWrapMode(QsciScintilla.WrapCharacter)
        self.setUtf8(True)
        self.setCaretLineVisible(True)

        self.inputMethodEventCount = 0
        self._imsupport = _SciImSupport(self)

        self.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.linesChanged.connect(self.onLinesChanged)

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(self._timer_interval * 1000)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._onTimerTimeout)

    @staticmethod
    def canOpened(filepath):
        basename, ext = os.path.splitext(filepath)
        if not ext:
            ext = basename
        return ext.lower() in EXTENSION_LEXER

    @classmethod
    def createAction(cls, parent, do_action):
        actions = {}
        action = QtWidgets.QAction(parent.tr('&Undo'), parent)
        action.setShortcut(QtGui.QKeySequence.Undo)
        action.triggered.connect(partial(do_action, 'undo'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-undo'))
        action.setEnabled(False)
        actions['undo'] = action

        action = QtWidgets.QAction(parent.tr('&Redo'), parent)
        action.setShortcut(QtGui.QKeySequence.Redo)
        action.triggered.connect(partial(do_action, 'redo'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-redo'))
        action.setEnabled(False)
        actions['redo'] = action

        action = QtWidgets.QAction(parent.tr('Cu&t'), parent)
        action.setShortcut(QtGui.QKeySequence.Cut)
        action.triggered.connect(partial(do_action, 'cut'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-cut'))
        action.setEnabled(False)
        actions['cut'] = action

        action = QtWidgets.QAction(parent.tr('&Copy'), parent)
        action.setShortcut(QtGui.QKeySequence.Copy)
        action.triggered.connect(partial(do_action, 'copy'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        action.setEnabled(False)
        actions['copy'] = action

        action = QtWidgets.QAction(parent.tr('&Paste'), parent)
        action.setShortcut(QtGui.QKeySequence.Paste)
        action.triggered.connect(partial(do_action, 'paste'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-paste'))
        actions['paste'] = action

        action = QtWidgets.QAction(parent.tr('&Delete'), parent)
        action.setShortcut(QtGui.QKeySequence.Delete)
        action.triggered.connect(partial(do_action, 'delete'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-delete'))
        action.setEnabled(False)
        actions['delete'] = action

        action = QtWidgets.QAction(parent.tr('Select &All'), parent)
        action.setShortcut(QtGui.QKeySequence.SelectAll)
        action.triggered.connect(partial(do_action, 'selectall'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-select-all'))
        actions['select_all'] = action

        action = QtWidgets.QAction(parent.tr('&Find or Replace'), parent)
        action.setShortcut(QtGui.QKeySequence.Find)
        action.triggered.connect(partial(do_action, 'find'))
        action.setIcon(QtGui.QIcon.fromTheme('edit-find-replace'))
        actions['find'] = action

        action = QtWidgets.QAction(parent.tr('Find Next'), parent)
        action.setShortcut(QtGui.QKeySequence.FindNext)
        action.triggered.connect(partial(do_action, 'findnext'))
        actions['find_next'] = action

        action = QtWidgets.QAction(parent.tr('Find Previous'), parent)
        action.setShortcut(QtGui.QKeySequence.FindPrevious)
        action.triggered.connect(partial(do_action, 'findprev'))
        actions['find_prev'] = action

        action = QtWidgets.QAction(parent.tr('Replace Next'), parent)
        action.setShortcut('F4')
        action.triggered.connect(partial(do_action, 'replacenext'))
        actions['replace_next'] = action

        action = QtWidgets.QAction(parent.tr('Indent'), parent)
        action.setShortcut('TAB')
        action.triggered.connect(partial(do_action, 'indent'))
        action.setIcon(QtGui.QIcon.fromTheme('format-indent-more'))
        actions['indent'] = action

        action = QtWidgets.QAction(parent.tr('Unindent'), parent)
        action.setShortcut('Shift+TAB')
        action.triggered.connect(partial(do_action, 'unindent'))
        action.setIcon(QtGui.QIcon.fromTheme('format-indent-less'))
        actions['unindent'] = action

        action = QtWidgets.QAction(parent.tr('Zoom In'), parent)
        action.setShortcut(QtGui.QKeySequence.ZoomIn)
        action.triggered.connect(partial(do_action, 'zoom_in'))
        action.setIcon(QtGui.QIcon.fromTheme('zoom-in'))
        actions['zoom_in'] = action

        action = QtWidgets.QAction(parent.tr('Zoom Original'), parent)
        action.triggered.connect(partial(do_action, 'zoom_original'))
        action.setIcon(QtGui.QIcon.fromTheme('zoom-original'))
        actions['zoom_original'] = action

        action = QtWidgets.QAction(parent.tr('Zoom Out'), parent)
        action.setShortcut(QtGui.QKeySequence.ZoomOut)
        action.triggered.connect(partial(do_action, 'zoom_out'))
        action.setIcon(QtGui.QIcon.fromTheme('zoom-out'))
        actions['zoom_out'] = action

        action = QtWidgets.QAction(parent.tr('Wrap line'), parent, checkable=True)
        action.triggered.connect(partial(do_action, 'wrap_line'))
        actions['wrap_line'] = action
        return actions

    def action(self, action):
        if self._actions:
            return self._actions.get(action)

    def inputMethodQuery(self, query):
        if False and query == QtCore.Qt.ImMicroFocus:
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

        if event.preeditString():
            self.pauseLexer(True)
        else:
            self.pauseLexer(False)

        # input with preedit, from TortoiseHg
        if False and self._imsupport:
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

        length = len(event.commitString())
        self._latest_input_count += length
        if length > 0:
            self._timer.start()

    def keyPressEvent(self, event):
        super(Editor, self).keyPressEvent(event)
        self._latest_input_time = time.time()
        length = len(event.text())
        if length > 0:
            self._latest_input_count += length
            self._timer.start()
        elif event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self._latest_input_count += 1
            self._timer.start()

    def dragEnterEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            for url in mimedata.urls():
                if not url.isLocalFile():
                    return
                if not self.canOpened(os.path.abspath(url.toLocalFile())):
                    return
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            for url in mimedata.urls():
                if not url.isLocalFile():
                    return
                if not self.canOpened(os.path.abspath(url.toLocalFile())):
                    return
            event.acceptProposedAction()

    def dropEvent(self, event):
        mimedata = event.mimeData()
        urls = mimedata.urls()
        if urls:
            files = []
            for url in urls:
                fname = os.path.abspath(url.toLocalFile())
                if not self.canOpened(fname):
                    return
                files.append(fname)
            if files:
                self.filesDropped.emit(';'.join(files))
        else:
            return super(Editor, self).dropEvent(event)

    def font(self):
        font = super(Editor, self).font()
        lexer = self.lexer()
        if lexer:
            font = lexer.font(QsciScintilla.STYLE_DEFAULT)
        return font

    def setFont(self, font):
        super(Editor, self).setFont(font)
        self._fontmetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        lexer = self.lexer()
        if lexer:
            lexer.setFont(font)
            style = QsciScintilla.STYLE_DEFAULT
            while style < QsciScintilla.STYLE_LASTPREDEFINED:
                lexer.setFont(font, style)
                style += 1

    def zoom(self):
        return self.SendScintilla(QsciScintilla.SCI_GETZOOM)

    def getCharAt(self, pos):
        return self.SendScintilla(QsciScintilla.SCI_GETCHARAT, pos)

    def getStyleAt(self, pos):
        return self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, pos)

    def getPrinter(self, resolution):
        return QsciPrinter(resolution)

    def print_(self, printer):
        printer.printRange(self)

    def menuEdit(self, menu, widget=None):
        if not widget:
            widget = self
        menu.addAction(widget.action('undo'))
        menu.addAction(widget.action('redo'))
        menu.addSeparator()
        menu.addAction(widget.action('cut'))
        menu.addAction(widget.action('copy'))
        menu.addAction(widget.action('paste'))
        menu.addAction(widget.action('delete'))
        menu.addSeparator()
        menu.addAction(widget.action('select_all'))
        menu.addSeparator()
        menu.addAction(widget.action('find'))
        menu.addAction(widget.action('find_next'))
        menu.addAction(widget.action('find_prev'))
        menu.addAction(widget.action('replace_next'))
        menu.addSeparator()
        menu.addAction(widget.action('indent'))
        menu.addAction(widget.action('unindent'))
        menu.addSeparator()
        menu.addAction(widget.action('zoom_in'))
        menu.addAction(widget.action('zoom_original'))
        menu.addAction(widget.action('zoom_out'))

    def menuAboutToShow(self, widget=None):
        if not widget:
            widget = self
        widget.action('replace_next').setEnabled(True and not self.isReadOnly())
        widget.action('indent').setEnabled(self.hasSelectedText() and not self.isReadOnly())
        widget.action('unindent').setEnabled(self.hasSelectedText() and not self.isReadOnly())

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            super(Editor, self).contextMenuEvent(event)

    def _onAction(self, action, value):
        self.do_action(action, value)

    def _onTimerTimeout(self):
        now = time.time()
        if self._latest_input_count > 0:
            if not self._pauseLexer and (now - self._latest_input_time) > self._timer_interval:
                self.inputPreviewRequest.emit()
                self._latest_input_count = 0
            else:
                self._timer.start()

    def onCopyAvailable(self, value):
        self.do_copy_available(value, self)

    def onModificationChanged(self, value):
        self.do_modification_changed(value, self)

    def onCursorPositionChanged(self, line, index):
        cursor = 'Ln %s/%s Col %s/80' % (line + 1, self.lines(), index + 1)
        self.statusChanged.emit('cursor:%s' % cursor)

    def onLinesChanged(self):
        self.do_set_margin_width()

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

    def setModified(self, m):
        super(Editor, self).setModified(m)
        self._modified = m

    def isModified(self):
        return super(Editor, self).isModified() or self._modified

    def getValue(self):
        """ get all text """
        return self.text()

    def setValue(self, text):
        """
        set utf8 text
        modified state is false
        """
        self.setText(text)
        self.setCursorPosition(0, 0)
        self.setModified(False)
        self.setEolMode(self._qsciEolModeFromLine(self.text(0)))
        self.do_set_margin_width()

    def _qsciEolModeFromOs(self):
        if sys.platform == 'win32':
            return QsciScintilla.EolWindows
        if sys.platform == 'linux':
            return QsciScintilla.EolUnix
        elif sys.platform == 'darwin':
            return QsciScintilla.EolMac
        else:
            return QsciScintilla.EolUnix

    def _qsciEolModeFromLine(self, line):
        if line.endswith('\r\n'):
            return QsciScintilla.EolWindows
        elif line.endswith('\r'):
            return QsciScintilla.EolMac
        elif line.endswith('\n'):
            return QsciScintilla.EolUnix
        else:
            return self._qsciEolModeFromOs()

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
                encoding = chardet.detect(data).get('encoding')
                if not encoding or encoding == 'ascii':
                    encoding = 'utf-8'
                text = data.decode(encoding)
        except Exception as err:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Read file'),
                self.tr('Do not open "%s": %s') % (filename, err),
            )
            return False
        self._file_encoding = encoding
        self.setFileName(filename)
        self.setValue(text)
        return True

    def writeFile(self, filename=None):
        text = self.getValue()
        if filename:
            self.setFileName(filename)
        else:
            filename = self.getFileName()
        if filename:
            try:
                data = text.encode(self._file_encoding)
            except Exception as err:
                QtWidgets.QMessageBox.information(
                    self,
                    self.tr('Write file'),
                    self.tr('Do not write "%s": %s') % (filename, err),
                )
                return False
            with open(filename, 'wb') as f:
                f.write(data)
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
        self._file_encoding = 'utf-8'
        self.setFileName(filepath)
        self.setValue(text)

    def status(self):
        if not self.getFileName():
            return ''
        lines = self.lines()
        line, index = self.getCursorPosition()
        cursor = 'Ln %s/%s Col %s/80' % (line + 1, lines, index + 1)
        status = [
            'encoding:%s' % self._file_encoding.upper(),
            'eol:%s' % EOL_DESCRIPTION[self.eolMode()],
            'lexer:%s' % self.lexer().language(),
            'cursor:%s' % cursor,
        ]
        return ';'.join(status)

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

    def findNext(self, text, cs, wo):
        bfind = self.findFirst(
            text,
            False,  # re
            cs,
            wo,
            True,   # wrap
            True,   # forward
            -1, -1  # from current cursor position
        )
        if not bfind:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Find'),
                self.tr('Not found "%s"') % (text),
            )
        return

    def findPrevious(self, text, cs, wo):
        line, index = self.getCursorPosition()
        index -= len(text)
        bfind = self.findFirst(
            text,
            False,  # re
            cs,
            wo,
            True,   # wrap
            False,  # forward
            line, index,
        )
        if not bfind:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Find'),
                self.tr('Not found "%s"') % (text),
            )
        return

    def replaceNext(self, text, text2, cs, wo):
        line, index = self.getCursorPosition()
        index -= len(text)
        bfind = self.findFirst(
            text,
            False,  # re
            cs,
            wo,
            True,   # wrap
            True,   # forward
            line, index,
        )
        if bfind:
            self.replace(text2)
        else:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Replace'),
                self.tr('Not found "%s"') % (text),
            )
        return

    def replaceAll(self, text, text2, cs, wo):
        bfind = True
        while bfind:
            # line, index = self.getCursorPosition()
            bfind = self.findFirst(
                text,
                False,  # re
                cs,
                wo,
                True,   # wrap
                True,   # forward
                -1, -1,
                # line, index
            )
            if bfind:
                self.replace(text2)
        return

    def setStyle(self, filename):
        """
        1. lookup font from style: font(font, style)
        2. or return default font from defaultfont()
        """
        lexer = None
        t1 = time.clock()
        if filename:
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            LexerClass = EXTENSION_LEXER.get(ext)
            if LexerClass:
                lexer = LexerClass(self)
                lexer.setFont(self.font())

                style = QsciScintilla.STYLE_DEFAULT
                while style < QsciScintilla.STYLE_LASTPREDEFINED:
                    lexer.setFont(self.font(), style)
                    style += 1

        self.setLexer(lexer)
        if lexer:
            self.statusChanged.emit('lexer:%s' % lexer.language())
        else:
            self.statusChanged.emit('lexer:')
        t2 = time.clock()
        logger.info('Lexer waste time: %s(%s)' % (t2 - t1, filename))
        self.cur_lexer = lexer

    def pauseLexer(self, pause=True):
        self._pauseLexer = pause

    def getScintillaVersion(self):
        version = '%s.%s.%s' % (
            QSCINTILLA_VERSION >> 16 & 0xff,
            QSCINTILLA_VERSION >> 8 & 0xff,
            QSCINTILLA_VERSION & 0xff,
        )
        return version

    def do_action(self, action, value):
        if action == 'undo':
            self.undo()
        elif action == 'redo':
            self.redo()
        elif action == 'cut':
            self.cut()
        elif action == 'copy':
            self.copy()
        elif action == 'paste':
            self.paste()
        elif action == 'delete':
            self.delete()
        elif action == 'selectall':
            self.selectAll()
        elif action == 'find':
            self.find(self._find_dialog)
        elif action == 'findnext':
            self.findNext(
                self._find_dialog.getFindText(),
                self._find_dialog.isCaseSensitive(),
                self._find_dialog.isWholeWord(),
            )
        elif action == 'findprev':
            self.findPrevious(
                self._find_dialog.getFindText(),
                self._find_dialog.isCaseSensitive(),
                self._find_dialog.isWholeWord(),
            )
        elif action == 'replacenext':
            self.replaceNext(
                self._find_dialog.getFindText(),
                self._find_dialog.getReplaceText(),
                self._find_dialog.isCaseSensitive(),
                self._find_dialog.isWholeWord(),
            )
        elif action == 'indent':
            self.indentLines(True)
        elif action == 'unindent':
            self.indentLines(False)
        elif action == 'zoom_in':
            self.zoomIn()
        elif action == 'zoom_original':
            self.zoomTo(0)
        elif action == 'zoom_out':
            self.zoomOut()
        elif action == 'wrap_line':
            if value:
                self.setWrapMode(QsciScintilla.WrapCharacter)
            else:
                self.setWrapMode(QsciScintilla.WrapNone)

    def do_copy_available(self, value, widget):
        widget.action('cut') \
            and widget.action('cut').setEnabled(value and not self.isReadOnly())
        widget.action('copy') \
            and widget.action('copy').setEnabled(value)
        widget.action('paste') \
            and widget.action('paste').setEnabled(not self.isReadOnly())
        widget.action('delete') \
            and widget.action('delete').setEnabled(value and not self.isReadOnly())

    def do_modification_changed(self, value, widget):
        widget.action('undo').setEnabled(self.isUndoAvailable())
        widget.action('redo').setEnabled(self.isRedoAvailable())

    def do_set_margin_width(self):
        length = len('%s' % self.lines())
        if length > self._margin_width:
            self._margin_width = length
            self.setMarginWidth(0, self._fontmetrics.width('0' * self._margin_width) + 6)


class CodeViewer(Editor):
    """ code viewer, readonly """
    def __init__(self, find_dialog, parent=None):
        super(CodeViewer, self).__init__(find_dialog, parent)
        self.setReadOnly(True)
        self._actions = self.createAction(self, self._onAction)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.copyAvailable.connect(self.onCopyAvailable)
        self.modificationChanged.connect(self.onModificationChanged)

    def setValue(self, text):
        """ set all readonly text """
        self.setText(toUtf8(text))
        self.setCursorPosition(0, 0)
        self.setModified(False)

    def find(self, finddialog, readonly=True):
        super(CodeViewer, self).find(finddialog, readonly)
