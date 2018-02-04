
import sys
import time
import os.path
import logging
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qsci import QSCINTILLA_VERSION, QsciScintilla, QsciPrinter
import chardet
from mtable import MarkupTable

from .scilib import EXTENSION_LEXER

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
    saveRequest = QtCore.pyqtSignal('QString')
    saveAllRequest = QtCore.pyqtSignal()
    loadRequest = QtCore.pyqtSignal('QString')
    closeRequest = QtCore.pyqtSignal()
    closeAppRequest = QtCore.pyqtSignal()
    _enable_lexer = True
    _filename = None
    _tab_width = 4
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
    _min_margin_width = 3
    _font = None
    _margin_font = None
    _vim = None

    def __init__(self, find_dialog, parent=None):
        super(Editor, self).__init__(parent)
        self._find_dialog = find_dialog
        # Scintilla
        self._font = self.font()
        self._margin_font = QtGui.QFont(self._font)
        self._margin_font.setPointSize(self._font.pointSize() - 2)
        self._margin_font.setWeight(self._margin_font.Light)
        self.setMarginsFont(self._margin_font)
        self.setMarginType(0, QsciScintilla.NumberMargin)
        fontmetrics = QtGui.QFontMetrics(self._margin_font)
        self.setMarginWidth(0, fontmetrics.width('0' * self._min_margin_width))
        self.setMarginWidth(1, 0)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(False)
        self.setTabWidth(self._tab_width)
        self.setIndentationGuides(True)
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(self._edgeColumn)
        self.setWrapMode(QsciScintilla.WrapCharacter)
        self.setUtf8(True)
        self.setCaretLineVisible(True)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagByBorder)

        self.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.linesChanged.connect(self.onLinesChanged)
        self.textChanged.connect(self.onTextChanged)

        # Font Quality
        self.SendScintilla(
            QsciScintilla.SCI_SETFONTQUALITY,
            QsciScintilla.SC_EFF_QUALITY_LCD_OPTIMIZED)

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
        action.setIcon(QtGui.QIcon.fromTheme('edit-find'))
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

        action = QtWidgets.QAction(parent.tr('Show WS and EOL'), parent, checkable=True)
        action.triggered.connect(partial(do_action, 'show_ws_eol'))
        actions['show_ws_eol'] = action

        action = QtWidgets.QAction(parent.tr('Format Table'), parent)
        action.triggered.connect(partial(do_action, 'format_table'))
        actions['format_table'] = action
        return actions

    def action(self, action):
        if self._actions:
            return self._actions.get(action)

    def inputMethodEvent(self, event):
        if self.isReadOnly():
            return
        if self._vim and self._vim.handle(
                -1, event.preeditString() or event.commitString(), self):
            return

        if event.preeditString():
            self.pauseLexer(True)
        else:
            self.pauseLexer(False)

        super(Editor, self).inputMethodEvent(event)

        length = len(event.commitString())
        if length > 0:
            self._latest_input_count += length
            self._timer.start()

    def event(self, event):
        """in VIM mode, accept all shortcut event """
        if self._vim and event.type() == event.ShortcutOverride and event.key():
            event.accept()
            return True
        return super(Editor, self).event(event)

    def keyPressEvent(self, event):
        text = event.text()
        if self._vim and self._vim.handle(event.key(), text, self):
            return
        else:
            super(Editor, self).keyPressEvent(event)

        if text:
            self._latest_input_time = time.time()
            self._latest_input_count += len(text)
            self._timer.start()

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            super(Editor, self).contextMenuEvent(event)

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

    def setLexerFont(self, font):
        if not font:
            return
        lexer = self.lexer()
        if not lexer:
            return
        if lexer.language() == 'Ascii Art':
            return
        # set style 0 also will set STYLE_DEFAULT
        style = 0
        while style < QsciScintilla.STYLE_DEFAULT:
            if lexer.description(style):
                new_font = QtGui.QFont(font)
                old_font = lexer.font(style)
                new_font.setBold(old_font.bold())
                new_font.setItalic(old_font.italic())
                new_font.setUnderline(old_font.underline())
                lexer.setFont(new_font, style)
            style += 1

    def setFont(self, font):
        super(Editor, self).setFont(font)
        self._font = font
        self._margin_font = QtGui.QFont(self._font)
        self._margin_font.setPointSize(self._font.pointSize() - 2)
        self._margin_font.setWeight(self._margin_font.Light)
        self.setMarginsFont(self._margin_font)

    def zoom(self):
        return self.SendScintilla(QsciScintilla.SCI_GETZOOM)

    def getEndStyled(self):
        return self.SendScintilla(QsciScintilla.SCI_GETENDSTYLED)

    def getCharAt(self, pos):
        return self.SendScintilla(QsciScintilla.SCI_GETCHARAT, pos)

    def getStyleAt(self, pos):
        return self.SendScintilla(QsciScintilla.SCI_GETSTYLEAT, pos)

    def getCurrentPosition(self):
        return self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)

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
        menu.addAction(widget.action('format_table'))
        menu.addSeparator()
        menu.addAction(widget.action('zoom_in'))
        menu.addAction(widget.action('zoom_original'))
        menu.addAction(widget.action('zoom_out'))

    def menuAboutToShow(self, widget=None):
        if not widget:
            widget = self
        widget.action('replace_next').setEnabled(not self.isReadOnly())

    def _onAction(self, action, value):
        self.do_action(action, value)

    def _onTimerTimeout(self):
        """
        1. latest input count > 0
        2. lastest input time > interval time
        """
        now = time.time()
        if self._latest_input_count > 0:
            if not self._pauseLexer  \
                    and (now - self._latest_input_time) > self._timer_interval:
                self.inputPreviewRequest.emit()
                self._latest_input_count = 0
            else:
                self._timer.start()

    def onCopyAvailable(self, value):
        self.do_copy_available(value, self)

    def onSelectionChanged(self):
        self.do_selection_changed(self)

    def onModificationChanged(self, value):
        self.do_modification_changed(value, self)

    def onCursorPositionChanged(self, line, index):
        cursor = 'Ln %s/%s Col %s/80' % (line + 1, self.lines(), index + 1)
        self.statusChanged.emit('cursor:%s' % cursor)

    def onLinesChanged(self):
        self.do_set_margin_width()

    def onTextChanged(self):
        pass

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
        return self._filename

    def setFileName(self, path):
        """
        set filename and enable lexer
        """
        self._filename = path
        self.setLexerByFilename(self._filename)

    def enableLexer(self, enable=True):
        self._enable_lexer = enable
        if self._filename:
            self.setLexerByFilename(self._filename)

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
        if self.hasSelectedText():
            lineFrom, indexFrom, lineTo, indexTo = self.getSelection()
            self.pauseLexer(True)
            for line in range(lineFrom, lineTo + 1):
                action(line)
            self.pauseLexer(False)
        else:
            line, index = self.getCursorPosition()
            action(line)
            if inc:
                self.setCursorPosition(line, index + self._tab_width)
            else:
                self.setCursorPosition(line, max(0, index - self._tab_width))

    def linesJoin(self):
        if self.hasSelectedText():
            self.SendScintilla(QsciScintilla.SCI_TARGETFROMSELECTION)
        else:
            pos = self.getCurrentPosition()
            line, index = self.getCursorPosition()
            next_pos = self.positionFromLineIndex(line + 1, 0)
            self.SendScintilla(QsciScintilla.SCI_SETTARGETRANGE, pos, next_pos)
        self.SendScintilla(QsciScintilla.SCI_LINESJOIN)

    def delete(self, length=1):
        if length == 0:
            if self.hasSelectedText():
                self.copy()
                self.removeSelectedText()
        else:
            pos = self.getCurrentPosition()
            line, index = self.getCursorPosition()
            next_pos = self.positionFromLineIndex(line, index + length)

            self.SendScintilla(QsciScintilla.SCI_COPYRANGE, pos, next_pos)
            self.SendScintilla(QsciScintilla.SCI_DELETERANGE, pos, next_pos - pos)

    def pixelFromPosition(self, pos):
        x = self.SendScintilla(QsciScintilla.SCI_POINTXFROMPOSITION, 0, pos)
        y = self.SendScintilla(QsciScintilla.SCI_POINTYFROMPOSITION, 0, pos)
        return (x, y)

    def positionFromPixel(self, point):
        return self.SendScintilla(
            QsciScintilla.SCI_CHARPOSITIONFROMPOINTCLOSE, point[0], point[1])

    def encoding(self):
        return self._file_encoding

    def read(self, filename, encoding=None):
        try:
            with open(filename, 'rb') as f:
                encoding = chardet.detect(f.read(4096)).get('encoding')
                if not encoding or encoding == 'ascii':
                    encoding = 'utf-8'
            with open(filename, 'rt', encoding=encoding, newline='') as f:
                text = f.read()
            self._file_encoding = encoding
            self.setFileName(filename)
            self.setValue(text)
            return True
        except Exception as err:
            QtWidgets.QMessageBox.information(
                self,
                self.tr('Read file'),
                self.tr('Do not open "%s": %s') % (filename, err),
            )
        return False

    def save(self, filename=None):
        if filename and filename != self.getFileName():
            self.setFileName(filename)
        else:
            filename = self.getFileName()
        if filename:
            try:
                text = self.getValue()
                with open(filename, 'wt', encoding=self.encoding(), newline='') as f:
                    f.write(text)
                self.setModified(False)
                return True
            except Exception as err:
                QtWidgets.QMessageBox.information(
                    self,
                    self.tr('Write file'),
                    self.tr('Do not write "%s": %s') % (filename, err),
                )
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
            'encoding:%s' % self.encoding().upper(),
            'eol:%s' % EOL_DESCRIPTION[self.eolMode()],
            'lexer:%s' % (self.lexer().language() if self.lexer() else '--'),
            'cursor:%s' % cursor,
        ]
        return ';'.join(status)

    def emptyFile(self):
        self.clear()
        self.setFileName(None)
        self.setModified(False)

    def showFindDialog(self, finddialog, readonly=False):
        finddialog.setReadOnly(readonly)
        finddialog.find_next.connect(self.do_find_next)
        finddialog.find_previous.connect(self.do_find_previous)
        if not readonly:
            finddialog.replace_next.connect(self.do_replace_next)
            finddialog.replace_all.connect(self.do_replace_all)
        finddialog.exec_()
        finddialog.find_next.disconnect(self.do_find_next)
        finddialog.find_previous.disconnect(self.do_find_previous)
        if not readonly:
            finddialog.replace_next.disconnect(self.do_replace_next)
            finddialog.replace_all.disconnect(self.do_replace_all)

    def do_find_next(self, text, cs, wo):
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

    def do_find_previous(self, text, cs, wo):
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

    def do_replace_next(self, text, text2, cs, wo):
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

    def do_replace_all(self, text, text2, cs, wo):
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

    def setLexerByFilename(self, filename):
        lexer = None
        t1 = time.clock()
        if self._enable_lexer and filename:
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            LexerClass = EXTENSION_LEXER.get(ext)
            if LexerClass:
                lexer = LexerClass(self)

        self.setLexer(lexer)
        if lexer:
            self.setLexerFont(self._font)
            self.statusChanged.emit('lexer:%s' % lexer.language())
        else:
            self.statusChanged.emit('lexer:--')
        t2 = time.clock()
        logger.info('Lexer waste time: %s(%s)' % (t2 - t1, filename))

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
            self.delete(0)
        elif action == 'selectall':
            self.selectAll()
        elif action == 'find':
            self.showFindDialog(self._find_dialog)
        elif action == 'findnext':
            self.do_find_next(
                self._find_dialog.getFindText(),
                self._find_dialog.isCaseSensitive(),
                self._find_dialog.isWholeWord(),
            )
        elif action == 'findprev':
            self.do_find_previous(
                self._find_dialog.getFindText(),
                self._find_dialog.isCaseSensitive(),
                self._find_dialog.isWholeWord(),
            )
        elif action == 'replacenext':
            self.do_replace_next(
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
        elif action == 'show_ws_eol':
            self.setWhitespaceVisibility(value)
            self.setEolVisibility(value)
        elif action == 'format_table':
            if not self.hasSelectedText():
                return
            text = self.selectedText()
            mt = None
            if self.lexer():
                tables = None
                if self.lexer().language() == 'reStructuredText':
                    logger.debug('Format rst table: %s' % text)
                    tables = MarkupTable.from_rst(text)
                elif self.lexer().language() == 'Markdown':
                    logger.debug('Format md table: %s' % text)
                    tables = MarkupTable.from_md(text)
                if tables:
                    mt = tables[0]
            if not mt or mt.is_empty() or mt.is_invalid():
                logger.debug('Format text table: %s' % text)
                mt = MarkupTable.from_txt(text)
            if self.lexer():
                if self.lexer().language() == 'reStructuredText':
                    replaced_text = mt.to_rst()
                elif self.lexer().language() == 'Markdown':
                    replaced_text = mt.to_md()
            else:
                replaced_text = mt.to_rst()
            if replaced_text:
                self.replaceSelectedText(replaced_text)
                # preview immediately
                length = len(replaced_text)
                self._latest_input_count += length
                self._timer.start()

    def do_copy_available(self, value, widget):
        widget.action('cut') \
            and widget.action('cut').setEnabled(value and not self.isReadOnly())
        widget.action('copy') \
            and widget.action('copy').setEnabled(value)
        widget.action('paste') \
            and widget.action('paste').setEnabled(not self.isReadOnly())
        widget.action('delete') \
            and widget.action('delete').setEnabled(value and not self.isReadOnly())

    def do_selection_changed(self, widget):
        widget.action('indent').setEnabled(self.hasSelectedText() and not self.isReadOnly())
        widget.action('unindent').setEnabled(self.hasSelectedText() and not self.isReadOnly())
        widget.action('format_table').setEnabled(self.hasSelectedText())

    def do_modification_changed(self, value, widget):
        widget.action('undo').setEnabled(self.isUndoAvailable())
        widget.action('redo').setEnabled(self.isRedoAvailable())

    def setEnabledEditAction(self, enable, widget=None):
        return
        if widget is None:
            widget = self
        if enable:
            self.do_modification_changed(True, widget)
            self.do_copy_available(True, widget)
            self.do_selection_changed(widget)

            widget.action('select_all').setEnabled(True)
            widget.action('find').setEnabled(True)
            widget.action('find_next').setEnabled(True)
            widget.action('find_prev').setEnabled(True)
            widget.action('replace_next').setEnabled(True)
        else:
            widget.action('undo').setEnabled(False)
            widget.action('redo').setEnabled(False)
            widget.action('cut').setEnabled(False)
            widget.action('copy').setEnabled(False)
            widget.action('paste').setEnabled(False)
            widget.action('delete').setEnabled(False)

            widget.action('select_all').setEnabled(False)
            widget.action('find').setEnabled(False)
            widget.action('find_next').setEnabled(False)
            widget.action('find_prev').setEnabled(False)
            widget.action('replace_next').setEnabled(False)

    def do_set_margin_width(self):
        length = max(len('%s' % self.lines()) + 1, self._min_margin_width)
        fontmetrics = QtGui.QFontMetrics(self._margin_font)
        self.setMarginWidth(0, fontmetrics.width('0' * length))

    def setVimEmulator(self, vim):
        self._vim = vim


class CodeViewer(Editor):
    """ code viewer, readonly """
    def __init__(self, find_dialog, parent=None):
        super(CodeViewer, self).__init__(find_dialog, parent)
        self.setReadOnly(True)
        self._actions = self.createAction(self, self._onAction)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.copyAvailable.connect(self.onCopyAvailable)
        self.modificationChanged.connect(self.onModificationChanged)
        self.selectionChanged.connect(self.onSelectionChanged)

    def setValue(self, text):
        """ set all readonly text """
        self.setText(toUtf8(text))
        self.setModified(False)

    def showFindDialog(self, finddialog, readonly=True):
        super(CodeViewer, self).showFindDialog(finddialog, readonly)
