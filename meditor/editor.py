
import sys
import time
import os.path
import logging
import locale
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.Qsci import QSCINTILLA_VERSION, QsciScintilla, QsciPrinter
import chardet
from mtable import MarkupTable

from .scilib import EXTENSION_LEXER

from .gaction import GlobalAction
from .util import toUtf8
from . import __home_data_path__, __data_path__, __default_basename__

logger = logging.getLogger(__name__)


FILTER = [
    'All support files (*.rst *.md *.txt);;',
    'reStructuredText files (*.rst *.rest);;',
    'Markdown files (*.md *.markdown);;',
    'Text files (*.txt)',
    'All files (*.*)',
]


EOL_DESCRIPTION = {
    QsciScintilla.EolWindows: 'CR+LF',
    QsciScintilla.EolUnix: 'LF',
    QsciScintilla.EolMac: 'CR',
    'windows': QsciScintilla.EolWindows,
    'unix': QsciScintilla.EolUnix,
    'mac': QsciScintilla.EolMac,
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

    _settings = None
    _find_dialog = None

    _enable_lexer = True
    _filename = None
    _tab_width = 4
    _preedit_show = False
    _text_length = 0
    _pause_lexer = False
    _lexerStart = 0
    _lexerEnd = 0
    _file_encoding = 'utf8'
    _modified = False
    _min_margin_width = 3
    _font = None
    _margin_font = None
    _vim = None

    def __init__(self, settings, find_dialog, parent=None):
        super(Editor, self).__init__(parent)
        self._settings = settings
        self._find_dialog = find_dialog
        # Scintilla
        self.setFont(self.font())

        self.setMarginType(0, QsciScintilla.NumberMargin)
        fontmetrics = QtGui.QFontMetrics(self._margin_font)
        self.setMarginWidth(0, fontmetrics.width('0' * self._min_margin_width))
        self.setMarginWidth(1, 0)
        value = self._settings.value('editor/margin_color', '#ff0000', type=str)
        self._settings.setValue('editor/margin_color', value)
        self.setMarginsForegroundColor(QtGui.QColor(value))

        self.setIndentationsUseTabs(False)
        self.setAutoIndent(False)
        self.setTabWidth(self._tab_width)
        self.setIndentationGuides(True)

        value = self._settings.value('editor/edge_color', '#ffc000', type=str)
        self._settings.setValue('editor/edge_color', value)
        self.setEdgeColor(QtGui.QColor(value))
        value = self._settings.value('editor/edge_column', 80, type=int)
        self._settings.setValue('editor/edge_column', value)
        self.setEdgeColumn(value)
        value = self._settings.value('editor/edge_visible', True, type=bool)
        self._settings.setValue('editor/edge_visible', value)
        if value:
            self.setEdgeMode(QsciScintilla.EdgeLine)

        self.setWrapMode(QsciScintilla.WrapCharacter)
        self.setUtf8(True)

        value = self._settings.value('editor/caretline_color', '#ffffcd', type=str)
        self._settings.setValue('editor/caretline_color', value)
        self.setCaretLineBackgroundColor(QtGui.QColor(value))
        value = self._settings.value('editor/caretline_visible', True, type=bool)
        self._settings.setValue('editor/caretline_visible', value)
        self.setCaretLineVisible(value)

        self.setWrapVisualFlags(QsciScintilla.WrapFlagByBorder)

        self.cursorPositionChanged.connect(self.onCursorPositionChanged)
        self.linesChanged.connect(self.onLinesChanged)
        self.textChanged.connect(self.onTextChanged)

        # Font Quality
        value = self._settings.value('editor/font_quality', 'cleartype', type=str)
        self._settings.setValue('editor/font_quality', value)
        if value == 'none':
            self.SendScintilla(QsciScintilla.SCI_SETFONTQUALITY,
                               QsciScintilla.SC_EFF_QUALITY_NON_ANTIALIASED)
        elif value == 'standard':
            self.SendScintilla(QsciScintilla.SCI_SETFONTQUALITY,
                               QsciScintilla.SC_EFF_QUALITY_ANTIALIASED)
        elif value == 'cleartype':
            self.SendScintilla(QsciScintilla.SCI_SETFONTQUALITY,
                               QsciScintilla.SC_EFF_QUALITY_LCD_OPTIMIZED)
        else:
            self.SendScintilla(QsciScintilla.SCI_SETFONTQUALITY,
                               QsciScintilla.SC_EFF_QUALITY_DEFAULT)

        self.createAction()

    @staticmethod
    def canOpened(filepath):
        basename, ext = os.path.splitext(filepath)
        if not ext:
            ext = basename
        return ext in EXTENSION_LEXER

    def closeEvent(self, event):
        g_action = GlobalAction()
        g_action.unregister_by_widget(self)

    def focusInEvent(self, event):
        super(Editor, self).focusInEvent(event)
        self.menuAboutToShow()

    def createAction(self):
        g_action = GlobalAction()

        action = QtWidgets.QAction(self.tr('&Undo'), self)
        action.triggered.connect(partial(self.do_action, 'undo'))
        cmd = g_action.register('undo', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Undo)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-undo'))
        cmd.setEnabled(False)
        cmd.setText(self.tr('Undo'))

        action = QtWidgets.QAction(self.tr('&Redo'), self)
        action.triggered.connect(partial(self.do_action, 'redo'))
        cmd = g_action.register('redo', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Redo)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-redo'))
        cmd.setEnabled(False)
        cmd.setText(self.tr('Redo'))

        action = QtWidgets.QAction(self.tr('Cu&t'), self)
        action.triggered.connect(partial(self.do_action, 'cut'))
        cmd = g_action.register('cut', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Cut)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-cut'))
        cmd.setEnabled(False)
        cmd.setText(self.tr('Cut'))

        action = QtWidgets.QAction(self.tr('&Copy'), self)
        action.triggered.connect(partial(self.do_action, 'copy'))
        cmd = g_action.register('copy', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Copy)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-copy'))
        cmd.setEnabled(False)
        cmd.setText(self.tr('Copy'))

        action = QtWidgets.QAction(self.tr('&Copy Table'), self)
        action.triggered.connect(partial(self.do_action, 'copy_table'))
        cmd = g_action.register('copy_table', action, 'editor')
        cmd.setEnabled(False)
        cmd.setText(self.tr('Copy Table'))

        action = QtWidgets.QAction(self.tr('&Paste'), self)
        action.triggered.connect(partial(self.do_action, 'paste'))
        cmd = g_action.register('paste', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Paste)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-paste'))
        cmd.setEnabled(False)
        cmd.setText(self.tr('Paste'))

        action = QtWidgets.QAction(self.tr('&Delete'), self)
        action.triggered.connect(partial(self.do_action, 'delete'))
        cmd = g_action.register('delete', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Delete)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-delete'))
        cmd.setEnabled(False)
        cmd.setText(self.tr('Delete'))

        action = QtWidgets.QAction(self.tr('Select &All'), self)
        action.triggered.connect(partial(self.do_action, 'selectall'))
        cmd = g_action.register('select_all', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.SelectAll)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-select-all'))
        cmd.setText(self.tr('Select All'))

        action = QtWidgets.QAction(self.tr('&Find or Replace'), self)
        action.triggered.connect(partial(self.do_action, 'find'))
        cmd = g_action.register('find', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.Find)
        cmd.setIcon(QtGui.QIcon.fromTheme('edit-find'))
        cmd.setText(self.tr('Find or Replace'))

        action = QtWidgets.QAction(self.tr('Find Next'), self)
        action.triggered.connect(partial(self.do_action, 'findnext'))
        cmd = g_action.register('find_next', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.FindNext)
        cmd.setText(self.tr('Find Next'))

        action = QtWidgets.QAction(self.tr('Find Previous'), self)
        action.triggered.connect(partial(self.do_action, 'findprev'))
        cmd = g_action.register('find_prev', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.FindPrevious)
        cmd.setText(self.tr('Find Previous'))

        action = QtWidgets.QAction(self.tr('Replace Next'), self)
        action.triggered.connect(partial(self.do_action, 'replacenext'))
        cmd = g_action.register('replace_next', action, 'editor')
        cmd.setShortcut('F4')
        cmd.setText(self.tr('Replace Next'))

        action = QtWidgets.QAction(self.tr('Indent'), self)
        action.triggered.connect(partial(self.do_action, 'indent'))
        cmd = g_action.register('indent', action, 'editor')
        cmd.setShortcut('TAB')
        cmd.setIcon(QtGui.QIcon.fromTheme('format-indent-more'))
        cmd.setText(self.tr('Indent'))

        action = QtWidgets.QAction(self.tr('Unindent'), self)
        action.triggered.connect(partial(self.do_action, 'unindent'))
        cmd = g_action.register('unindent', action, 'editor')
        cmd.setShortcut('Shift+TAB')
        cmd.setIcon(QtGui.QIcon.fromTheme('format-indent-less'))
        cmd.setText(self.tr('Unindent'))

        action = QtWidgets.QAction(self.tr('Zoom In'), self)
        action.triggered.connect(partial(self.do_action, 'zoom_in'))
        cmd = g_action.register('zoom_in', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.ZoomIn)
        cmd.setIcon(QtGui.QIcon.fromTheme('zoom-in'))
        cmd.setText(self.tr('Zoom In'))

        action = QtWidgets.QAction(self.tr('Zoom Original'), self)
        action.triggered.connect(partial(self.do_action, 'zoom_original'))
        cmd = g_action.register('zoom_original', action, 'editor')
        cmd.setIcon(QtGui.QIcon.fromTheme('zoom-original'))
        cmd.setText(self.tr('Zoom Original'))

        action = QtWidgets.QAction(self.tr('Zoom Out'), self)
        action.triggered.connect(partial(self.do_action, 'zoom_out'))
        cmd = g_action.register('zoom_out', action, 'editor')
        cmd.setShortcut(QtGui.QKeySequence.ZoomOut)
        cmd.setIcon(QtGui.QIcon.fromTheme('zoom-out'))
        cmd.setText(self.tr('Zoom Out'))

        action = QtWidgets.QAction(self.tr('Format Table'), self)
        action.triggered.connect(partial(self.do_action, 'format_table'))
        cmd = g_action.register('format_table', action, 'editor')
        cmd.setText(self.tr('Format Table'))

        action = QtWidgets.QAction(self.tr('delimeter "|"'), self)
        action.triggered.connect(partial(self.do_action, 'format_table_vline'))
        cmd = g_action.register('format_table_vline', action, 'editor')
        cmd.setText(self.tr('delimeter "|"'))

        action = QtWidgets.QAction(self.tr('delimeter "<SPACE>"'), self)
        action.triggered.connect(partial(self.do_action, 'format_table_space'))
        cmd = g_action.register('format_table_space', action, 'editor')
        cmd.setText(self.tr('delimeter "<SPACE>"'))

        action = QtWidgets.QAction(self.tr('delimeter ","'), self)
        action.triggered.connect(partial(self.do_action, 'format_table_comma'))
        cmd = g_action.register('format_table_comma', action, 'editor')
        cmd.setText(self.tr('delimeter ","'))

        action = QtWidgets.QAction(self.tr('delimeter "<TAB>"'), self)
        action.triggered.connect(partial(self.do_action, 'format_table_tab'))
        cmd = g_action.register('format_table_tab', action, 'editor')
        cmd.setText(self.tr('delimeter "<TAB>"'))

    def action(self, act_id):
        g_action = GlobalAction()
        return g_action.get('' + act_id)

    def inputMethodEvent(self, event):
        if self.isReadOnly():
            return
        input_string = event.preeditString()
        if input_string:
            self._pause_lexer = True
            self._preedit_show = True
        else:
            self._pause_lexer = False
            self._preedit_show = False

        if self._vim:
            input_string = event.preeditString() or event.commitString()
            if self._vim.handle(-1, input_string, self):
                return

        super(Editor, self).inputMethodEvent(event)

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

    def menuEdit(self, menu):
        menu.addAction(self.action('undo'))
        menu.addAction(self.action('redo'))
        menu.addSeparator()
        menu.addAction(self.action('cut'))

        submenu = menu.addMenu(QtGui.QIcon.fromTheme('edit-copy'), 'Copy')
        submenu.addAction(self.action('copy'))
        submenu.addAction(self.action('copy_table'))

        menu.addAction(self.action('paste'))
        menu.addAction(self.action('delete'))
        menu.addSeparator()
        menu.addAction(self.action('select_all'))
        menu.addSeparator()
        menu.addAction(self.action('find'))
        menu.addAction(self.action('find_next'))
        menu.addAction(self.action('find_prev'))
        menu.addAction(self.action('replace_next'))
        menu.addSeparator()
        menu.addAction(self.action('indent'))
        menu.addAction(self.action('unindent'))

        menu.addSeparator()
        submenu = menu.addMenu('Format Table')
        submenu.addAction(self.action('format_table_vline'))
        submenu.addAction(self.action('format_table_comma'))
        submenu.addAction(self.action('format_table_tab'))
        submenu.addAction(self.action('format_table_space'))

        menu.addSeparator()
        menu.addAction(self.action('zoom_in'))
        menu.addAction(self.action('zoom_original'))
        menu.addAction(self.action('zoom_out'))

    def menuAboutToShow(self):
        self.do_copy_available(self.hasSelectedText())
        self.do_selection_changed()
        self.do_modification_changed(None)
        self.action('replace_next').setEnabled(not self.isReadOnly())

    def onCopyAvailable(self, value):
        self.do_copy_available(value)

    def onSelectionChanged(self):
        self.do_selection_changed()

    def onModificationChanged(self, value):
        self.do_modification_changed(value)

    def onCursorPositionChanged(self, line, index):
        cursor = 'Ln %s/%s Col %s/80' % (line + 1, self.lines(), index + 1)
        self.statusChanged.emit('cursor:%s' % cursor)

    def onLinesChanged(self):
        self.do_set_margin_width()

    def onTextChanged(self):
        if not self._preedit_show:
            text_length = len(self.text())
            if abs(text_length - self._text_length) > 5:
                self.inputPreviewRequest.emit()
                self._text_length = text_length
        value = self.toFriendlyValue(self.length())
        self.statusChanged.emit('length:%s' % value)

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

    def detect_file_encoding(self, filename=None):
        ansi_encoding = locale.getpreferredencoding()

        if filename and os.path.exists(filename):
            encoding = ''
            with open(filename, 'rb') as f:
                encoding = chardet.detect(f.read()).get('encoding')
                if not encoding:
                    raise ValueError('can not detect file encoding: %s' % filename)

            encoding = encoding.upper()
            if encoding in ['ASCII', 'GB2312']:
                encoding = ansi_encoding
        else:
            encoding = ansi_encoding
        return encoding

    def read(self, filename, encoding=None):
        try:
            if encoding is None:
                encoding = self.detect_file_encoding(filename)
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
            err_bak = filename + '.error.bak'
            try:
                text = self.getValue()
                with open(err_bak, 'wt', encoding=self.encoding(), newline='') as f:
                    f.write(text)
                if os.path.exists(filename):
                    os.remove(filename)
                os.rename(err_bak, filename)
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
        encoding = locale.getpreferredencoding()
        for skeleton in skeletons:
            if os.path.exists(skeleton):
                encoding = self.detect_file_encoding(skeleton)
                with open(skeleton, 'r', encoding=encoding) as f:
                    text = f.read()
                break
        self._file_encoding = encoding
        self.setFileName(filepath)
        self.setValue(text)

    def status(self):
        if not self.getFileName():
            return ''
        lines = self.lines()
        line, index = self.getCursorPosition()
        cursor = 'Ln %s/%s Col %s/80' % (line + 1, lines, index + 1)
        length = self.toFriendlyValue(self.length())
        self._text_length = len(self.text())
        status = [
            'encoding:%s' % self.encoding().upper(),
            'eol:%s' % EOL_DESCRIPTION[self.eolMode()],
            'lexer:%s' % (self.lexer().language() if self.lexer() else '--'),
            'cursor:%s' % cursor,
            'length:%s' % length,
        ]
        return ';'.join(status)

    def emptyFile(self):
        self.clear()
        self.setFileName(None)
        self.setModified(False)

    def showFindDialog(self, finddialog, readonly=False):
        finddialog.setReadOnly(readonly)
        finddialog.setDefaultFocus()
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
        self._pause_lexer = pause

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
        elif action == 'copy_table':
            text = self.selectedText()
            if text:
                tables = None
                if self.lexer().language() == 'reStructuredText':
                    logger.debug('Format rst table: %s' % text)
                    tables = MarkupTable.from_rst(text)
                elif self.lexer().language() == 'Markdown':
                    logger.debug('Format md table: %s' % text)
                    tables = MarkupTable.from_md(text)
                if tables:
                    mt = tables[0]
                    text = mt.to_tab()
            clipboard = QtWidgets.qApp.clipboard()
            clipboard.setText(text)
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
        elif action.startswith('format_table'):
            self.do_format_table(action)

    def do_format_table(self, action):
        if action == 'format_table_vline':
            delimeter = '|'
        elif action == 'format_table_space':
            delimeter = ' '
        elif action == 'format_table_comma':
            delimeter = ','
        elif action == 'format_table_tab':
            delimeter = '\t'
        else:
            delimeter = '|'
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
            mt = MarkupTable.from_txt(text, delimeter)
        replaced_text = ''
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
            self.inputPreviewRequest.emit()

    def do_copy_available(self, value):
        self.action('cut').setEnabled(value and not self.isReadOnly())
        self.action('copy').setEnabled(value)
        self.action('copy_table').setEnabled(value)
        self.action('paste').setEnabled(not self.isReadOnly())
        self.action('delete').setEnabled(value and not self.isReadOnly())

    def do_selection_changed(self):
        self.action('indent').setEnabled(self.hasSelectedText() and not self.isReadOnly())
        self.action('unindent').setEnabled(self.hasSelectedText() and not self.isReadOnly())
        self.action('format_table_vline').setEnabled(self.hasSelectedText())
        self.action('format_table_comma').setEnabled(self.hasSelectedText())
        self.action('format_table_space').setEnabled(self.hasSelectedText())
        self.action('format_table_tab').setEnabled(self.hasSelectedText())

    def do_modification_changed(self, value):
        self.action('undo').setEnabled(self.isUndoAvailable())
        self.action('redo').setEnabled(self.isRedoAvailable())

    def setEnabledEditAction(self, enable):
        return
        if enable:
            self.do_modification_changed(True)
            self.do_copy_available(True)
            self.do_selection_changed()

            self.action('select_all').setEnabled(True)
            self.action('find').setEnabled(True)
            self.action('find_next').setEnabled(True)
            self.action('find_prev').setEnabled(True)
            self.action('replace_next').setEnabled(True)
        else:
            self.action('undo').setEnabled(False)
            self.action('redo').setEnabled(False)
            self.action('cut').setEnabled(False)
            self.action('copy').setEnabled(False)
            self.action('paste').setEnabled(False)
            self.action('delete').setEnabled(False)

            self.action('select_all').setEnabled(False)
            self.action('find').setEnabled(False)
            self.action('find_next').setEnabled(False)
            self.action('find_prev').setEnabled(False)
            self.action('replace_next').setEnabled(False)

    def do_set_margin_width(self):
        length = max(len('%s' % self.lines()) + 1, self._min_margin_width)
        fontmetrics = QtGui.QFontMetrics(self._margin_font)
        self.setMarginWidth(0, fontmetrics.width('0' * length))

    def do_convert_eol(self, value):
        self.convertEols(EOL_DESCRIPTION[value])
        self.setEolMode(EOL_DESCRIPTION[value])
        self.statusChanged.emit('eol:%s' % EOL_DESCRIPTION[self.eolMode()])

    def do_save(self):
        fname = self.getFileName()
        dir_name = os.path.dirname(fname)
        filename = os.path.basename(fname)
        basename, _ = os.path.splitext(filename)
        if not dir_name and basename == __default_basename__:
            self.do_save_as()
        else:
            self.save()

    def do_save_as(self, new_fname=None):
        old_fname = self.getFileName()
        dir_name = os.path.dirname(old_fname)
        if not dir_name:
            dir_name = os.getcwd()

        if new_fname is None:
            filename = os.path.basename(old_fname)
            new_fname, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
                self,
                self.tr('Save file as ...'),
                os.path.join(dir_name, filename),
                ''.join(FILTER),
            )
        if not new_fname:
            return
        new_fname = os.path.abspath(new_fname)
        _, ext = os.path.splitext(new_fname)
        if not ext:
            ext = selected_filter.split('(')[1][1:4].strip()
            new_fname = new_fname + ext

        if not new_fname:
            new_fname = old_fname
        self.save(new_fname)

        return old_fname, new_fname

    def do_close(self):
        if self.isModified():
            fname = self.getFileName()
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText(self.tr('The document "%s" has been modified.') % fname)
            msgBox.setInformativeText(
                self.tr('Do you want to save your changes?')
            )
            msgBox.setStandardButtons(
                QtWidgets.QMessageBox.Save |
                QtWidgets.QMessageBox.Discard |
                QtWidgets.QMessageBox.Cancel
            )
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Save)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.Cancel:
                return False
            if ret == QtWidgets.QMessageBox.Save:
                self.do_save()
            elif ret == QtWidgets.QMessageBox.Discard:
                pass
        return True

    def setVimEmulator(self, vim):
        self._vim = vim

    def toFriendlyValue(self, value):
        unit = ['B', 'KB', 'MB', 'GB', 'TB']
        for x in range(len(unit)):
            if value < 1024:
                break
            value /= 1024
        return '%.2f %s' % (value, unit[x])


class CodeViewer(Editor):
    """ code viewer, readonly """
    def __init__(self, settings, find_dialog, parent=None):
        super(CodeViewer, self).__init__(settings, find_dialog, parent)
        self.setReadOnly(True)
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
