
import os.path
import logging
from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from .editor import Editor, FILTER
from .gaction import GlobalAction
from . import __monospace__


logger = logging.getLogger(__name__)


class TabEditor(QtWidgets.QTabWidget):
    statusChanged = QtCore.pyqtSignal(int, 'QString')
    showMessageRequest = QtCore.pyqtSignal('QString')
    previewRequest = QtCore.pyqtSignal(int, 'QString')
    modificationChanged = QtCore.pyqtSignal(int, bool)
    verticalScrollBarChanged = QtCore.pyqtSignal(int, int)
    filenameChanged = QtCore.pyqtSignal('QString', 'QString')
    fileLoaded = QtCore.pyqtSignal(int)
    _enable_lexer = True
    _find_dialog = None
    _settings = None
    _wrap_line = True
    _show_ws_eol = False
    _single_instance = False
    _editor_font = None
    _vim_emulator = None
    _timer = None
    _timer_interval = 1

    def __init__(self, settings, find_dialog, parent=None):
        super(TabEditor, self).__init__(parent)
        self._settings = settings
        self._find_dialog = find_dialog

        self.setMovable(True)
        self.setTabsClosable(True)
        self.setDocumentMode(True)
        self.setTabBarAutoHide(True)
        self.tabBarClicked.connect(self._onTabClicked)
        self.tabCloseRequested.connect(self._onTabCloseRequest)

        self._wrap_line = self._settings.value('editor/wrap_line', True, type=bool)
        self._show_ws_eol = self._settings.value('editor/show_ws_eol', False, type=bool)
        self._single_instance = self._settings.value('editor/single_instance', False, type=bool)

        g_action = GlobalAction()

        action = QtWidgets.QAction(self.tr('&Open'), self)
        action.triggered.connect(self._onOpen)
        cmd = g_action.register('open', action, 'tab_editor')
        cmd.setShortcut(QtGui.QKeySequence.Open)
        cmd.setIcon(QtGui.QIcon.fromTheme('document-open'))
        cmd.setText(self.tr('Open'))

        action = QtWidgets.QAction(self.tr('&Save'), self)
        action.triggered.connect(self._onSave)
        cmd = g_action.register('save', action, 'tab_editor')
        cmd.setShortcut(QtGui.QKeySequence.Save)
        cmd.setIcon(QtGui.QIcon.fromTheme('document-save'))
        cmd.setText(self.tr('Save'))

        action = QtWidgets.QAction(self.tr('Save as...'), self)
        action.triggered.connect(self._onSaveAs)
        cmd = g_action.register('save_as', action, 'tab_editor')
        cmd.setShortcut(QtGui.QKeySequence.SaveAs)
        cmd.setIcon(QtGui.QIcon.fromTheme('document-save-as'))
        cmd.setText(self.tr('Save as...'))

        action = QtWidgets.QAction(self.tr('Save all'), self)
        action.triggered.connect(self._onSaveAll)
        cmd = g_action.register('save_all', action, 'tab_editor')
        cmd.setText(self.tr('Save all'))

        action = QtWidgets.QAction(self.tr('Close all'), self)
        action.triggered.connect(self._onCloseAll)
        cmd = g_action.register('close_all', action, 'tab_editor')
        cmd.setText(self.tr('Close all'))

        action = QtWidgets.QAction(self.tr('Default font'), self)
        action.triggered.connect(self._onDefaultFont)
        cmd = g_action.register('default_font', action, 'tab_editor')
        cmd.setText(self.tr('Default font'))

        action = QtWidgets.QAction(self.tr('Single Instance'), self, checkable=True)
        action.triggered.connect(self._onOneEditor)
        cmd = g_action.register('single_instance', action, 'tab_editor')
        cmd.setText(self.tr('Single Instance'))
        cmd.setCheckable(True)
        cmd.setChecked(self._single_instance)

        action = QtWidgets.QAction(self.tr('Windows (CR + LF)'), self)
        action.triggered.connect(partial(self._onConvertEol, 'windows'))
        cmd = g_action.register('eol_windows', action, 'tab_editor')
        cmd.setText(self.tr('Windows (CR + LF)'))

        action = QtWidgets.QAction(self.tr('Unix (LF)'), self)
        action.triggered.connect(partial(self._onConvertEol, 'unix'))
        cmd = g_action.register('eol_unix', action, 'tab_editor')
        cmd.setText(self.tr('Unix (LF)'))

        action = QtWidgets.QAction(self.tr('Mac (CR)'), self)
        action.triggered.connect(partial(self._onConvertEol, 'mac'))
        cmd = g_action.register('eol_mac', action, 'tab_editor')
        cmd.setText(self.tr('Mac (CR)'))

        action = QtWidgets.QAction(self.tr('Wrap Line'), self, checkable=True)
        action.triggered.connect(partial(self.do_action, 'wrap_line'))
        cmd = g_action.register('wrap_line', action, 'tab_editor')
        cmd.setCheckable(True)
        cmd.setText(self.tr('Wrap Line'))
        action.setChecked(self._wrap_line)
        cmd.setChecked(self._wrap_line)

        action = QtWidgets.QAction(self.tr('Show WS and EOL'), self, checkable=True)
        action.triggered.connect(partial(self.do_action, 'show_ws_eol'))
        cmd = g_action.register('show_ws_eol', action, 'tab_editor')
        cmd.setCheckable(True)
        cmd.setText(self.tr('Show WS and EOL'))
        action.setChecked(self._show_ws_eol)
        cmd.setChecked(self._show_ws_eol)

        value = self._settings.value('editor/font', __monospace__, type=str)
        self._editor_font = QtGui.QFont()
        self._editor_font.fromString(value)
        logger.info('font: %s' % (self._editor_font.toString()))

        value = self._settings.value('editor/opened_files', type=str)
        for v in value.split(';')[::-1]:
            filepath, _, zoom = v.rpartition(':')
            if not os.path.exists(filepath):
                continue
            index = self.open(os.path.abspath(filepath))
            self.widget(index).zoomTo(int(zoom) if zoom else 0)
            if self._single_instance:
                break
        if self.count() == 0:
            self.new('.rst')

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(self._timer_interval * 1000)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._onTimerTimeout)

    def closeEvent(self, event):
        self._settings.setValue('editor/font', self._editor_font.toString())
        opened = []
        for x in range(self.count()):
            editor = self.widget(x)
            opened.append('%s:%s' % (editor.getFileName(), editor.zoom()))
        self._settings.setValue('editor/opened_files', ';'.join(opened))
        self._settings.setValue('editor/wrap_line', self._wrap_line)
        self._settings.setValue('editor/show_ws_eol', self._show_ws_eol)
        self._settings.setValue('editor/single_instance', self._single_instance)

        self.do_close_all()
        if self.count() > 0:
            event.ignore()

    def _onStatusChanged(self, status):
        widget = self.sender()
        index = self.indexOf(widget)
        if index < 0:
            return
        self.statusChanged.emit(index, status)

    def _onTimerTimeout(self):
        """
        lastest input time > interval time
        """
        widget = self.currentWidget()
        index = self.currentIndex()
        if not widget._preedit_show:
            self.previewRequest.emit(index, 'input')
        else:
            self._timer.start()

    def _onInputPreview(self):
        widget = self.sender()
        index = self.indexOf(widget)
        if index < 0:
            return
        # delay preview
        self._timer.start()

    def _onModificationChanged(self, value):
        widget = self.sender()
        index = self.indexOf(widget)
        if index < 0:
            return
        widget.do_modification_changed(value)
        self.updateTitle(index)
        self.modificationChanged.emit(index, value)

    def _onCopyAvailable(self, value):
        widget = self.currentWidget()
        widget and widget.do_copy_available(value)

    def _onSelectionChanged(self):
        widget = self.currentWidget()
        widget and widget.do_selection_changed()

    def _onFilesDropped(self, value):
        for fname in value.split(';'):
            self.loadFile(fname)

    def _onVerticalScrollBarChanged(self, value):
        index = self.currentIndex()
        if index < 0:
            return
        self.verticalScrollBarChanged.emit(index, value)

    def _onConvertEol(self, value):
        widget = self.currentWidget()
        widget and widget.do_convert_eol(value)

    def _onTabClicked(self, index):
        self.do_switch_editor(index)

    def _onTabCloseRequest(self, index):
        self.do_close_editor(index)
        if self.count() == 0:
            self.new('.rst')
        else:
            cur_index = self.currentIndex()
            self.do_switch_editor(cur_index)

    def _onOpen(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, self.tr('Open a file'),
            os.getcwd(),
            ''.join(FILTER),
        )
        if filename:
            self.loadFile(filename)

    def _onSave(self):
        index = self.currentIndex()
        self.widget(index).do_save()
        self.previewRequest.emit(index, 'save')
        self.showMessageRequest.emit('save to "%s"' % self.filepath(index))

    def _onSaveAs(self):
        self.do_save_as()

    def _onSaveAll(self):
        self.do_save_all()

    def _onCloseAll(self):
        self.do_close_all()
        self.new('.rst')

    def _onDefaultFont(self):
        dlg = QtWidgets.QFontDialog(self)
        dlg.setMinimumSize(640, 480)
        dlg.setCurrentFont(self._editor_font)
        ret = dlg.exec_()
        if ret > 0:
            self._editor_font = dlg.selectedFont()
            self.do_set_font(self._editor_font)

    def _onOneEditor(self, value):
        self._single_instance = value

    def _newEditor(self):
        editor = Editor(self._settings, self._find_dialog, self)
        editor.setFont(self._editor_font)
        editor.statusChanged.connect(self._onStatusChanged)
        editor.verticalScrollBar().valueChanged.connect(self._onVerticalScrollBarChanged)
        editor.inputPreviewRequest.connect(self._onInputPreview)

        editor.modificationChanged.connect(self._onModificationChanged)
        editor.copyAvailable.connect(self._onCopyAvailable)
        editor.selectionChanged.connect(self._onSelectionChanged)

        editor.filesDropped.connect(self._onFilesDropped)
        editor.saveRequest.connect(self.do_save_as)
        editor.saveAllRequest.connect(self.do_save_all)
        editor.loadRequest.connect(self.loadFile)
        editor.closeRequest.connect(partial(self.do_close_editor, -1))
        editor.closeAppRequest.connect(self.do_close_app)

        editor.enableLexer(self._enable_lexer)

        editor.setVimEmulator(self._vim_emulator)
        editor.setEnabledEditAction(self._vim_emulator is None)

        editor.do_action('wrap_line', self._wrap_line)
        editor.do_action('show_ws_eol', self._show_ws_eol)
        return editor

    def action(self, act_id):
        g_action = GlobalAction()
        return g_action.get('' + act_id)

    def new(self, ext):
        if self._single_instance:
            self.do_close_all()
        editor = self._newEditor()
        editor.newFile(ext)
        title = ('*' if editor.isModified() else '') + os.path.basename(editor.getFileName())
        index = self.insertTab(0, editor, title)
        self.setCurrentIndex(index)
        self.fileLoaded.emit(index)
        self.statusChanged.emit(index, self.widget(index).status())
        self.previewRequest.emit(index, 'new')
        self.showMessageRequest.emit(self.tr('new "%s"' % self.filepath(index)))
        return index

    def open(self, filepath):
        if self._single_instance:
            self.do_close_all()
        editor = self._newEditor()
        if editor.read(filepath):
            title = ('*' if editor.isModified() else '') + os.path.basename(editor.getFileName())
            index = self.insertTab(0, editor, title)
            self.setCurrentIndex(index)
            self.fileLoaded.emit(index)
            self.showMessageRequest.emit(self.tr('load "%s"' % self.filepath(index)))
            self.statusChanged.emit(index, self.widget(index).status())
            self.previewRequest.emit(index, 'open')
            return index

    def text(self, index):
        if index is None:
            editor = self.currentWidget()
        else:
            editor = self.widget(index)
        if not editor:
            return
        return editor.text()

    def filepath(self, index=None):
        if index is None:
            editor = self.currentWidget()
        else:
            editor = self.widget(index)
        if not editor:
            return
        return editor.getFileName()

    def status(self, index):
        if index is None:
            editor = self.currentWidget()
        else:
            editor = self.widget(index)
        if not editor:
            return
        return editor.status()

    def openedFiles(self):
        opened = []
        for x in range(self.count()):
            opened.append(self.filepath(x))
        return opened

    def title(self, index=None, full=False):
        if index is None:
            editor = self.currentWidget()
        else:
            editor = self.widget(index)
        if full:
            title = ('* ' if editor.isModified() else '') + editor.getFileName()
        else:
            title = ('* ' if editor.isModified() else '') + os.path.basename(editor.getFileName())
        return title

    def updateTitle(self, index):
        self.setTabText(index, self.title(index))

    def enableLexer(self, enable):
        self._enable_lexer = enable
        for x in range(self.count()):
            self.widget(x).enableLexer(enable)

    def loadFile(self, path):
        """ load by function call """
        if not path:
            index = self.new('.rst')
            return index
        path = os.path.abspath(path)
        if not Editor.canOpened(path):
            return
        for index in range(self.count()):
            if path == self.filepath(index):
                self.setCurrentIndex(index)
                self.fileLoaded.emit(index)
                self.showMessageRequest.emit(self.tr('load "%s"' % self.filepath(index)))
                self.statusChanged.emit(index, self.widget(index).status())
                self.previewRequest.emit(index, 'open')
                return index
        if os.path.exists(path):
            logger.debug('Loading file: %s', path)
            index = self.open(path)
        else:
            logger.debug('Creating file: %s', path)
            index = self.new(path)
        return index

    def menuAboutToShow(self):
        widget = self.currentWidget()
        widget.menuAboutToShow()

    def menuEdit(self, menu):
        widget = self.currentWidget()
        widget.menuEdit(menu)

    def menuSetting(self, menu):
        menu.addAction(self.action('wrap_line'))
        menu.addAction(self.action('show_ws_eol'))
        menu.addAction(self.action('single_instance'))
        menu.addSeparator()
        menu.addAction(self.action('default_font'))

    def do_action(self, action, value):
        widget = self.currentWidget()
        if action == 'wrap_line':
            self._wrap_line = value
            for x in range(self.count()):
                self.widget(x).do_action('wrap_line', value)
        elif action == 'show_ws_eol':
            self._show_ws_eol = value
            for x in range(self.count()):
                self.widget(x).do_action('show_ws_eol', value)
        else:
            widget.do_action(action, value)

    def do_close_app(self):
        QtWidgets.qApp.closeAllWindows()

    def do_close_all(self):
        for x in list(range(self.count()))[::-1]:
            self.do_close_editor(x)

    def do_close_editor(self, index):
        if index < 0:
            index = self.currentIndex()
        if self.widget(index).do_close():
            # close
            widget = self.widget(index)
            self.removeTab(index)
            widget.close()
            del widget

    def do_save_all(self):
        for x in range(self.count()):
            self.widget(x).do_save()

    def do_save_as(self, new_fname=None):
        index = self.currentIndex()
        if not new_fname and new_fname is not None:
            # new_fname == ''
            fnames = self.widget(index).do_save()
        else:
            fnames = self.widget(index).do_save_as(new_fname)
            self.showMessageRequest.emit(self.tr('save as to "%s"' % self.filepath(index)))

        self.updateTitle(index)
        self.previewRequest.emit(index, 'save')
        if fnames:
            self.filenameChanged.emit(fnames[0], fnames[1])

    def do_switch_editor(self, index):
        widget = self.widget(index)
        if not widget:
            return
        if index != self.currentIndex():
            self.setCurrentIndex(index)
        widget.setFocus(QtCore.Qt.TabFocusReason)
        self.fileLoaded.emit(index)
        self.showMessageRequest.emit(self.tr('switch to "%s"' % self.filepath(index)))
        self.statusChanged.emit(index, widget.status())
        self.previewRequest.emit(index, 'open')

    def do_set_font(self, font):
        for x in range(self.count()):
            self.widget(x).setFont(font)
            self.widget(x).setLexerFont(font)

    def rename(self, old, new):
        """update editor filename after has changed name in OS """
        for x in range(self.count()):
            editor = self.widget(x)
            if old == editor.getFileName():
                editor.setFileName(new)
                self.updateTitle(x)
                self.fileLoaded.emit(x)
                self.showMessageRequest.emit(self.tr('rename "%s" => "%s"' % (old, new)))
                return

    def setVimEmulator(self, vim):
        self._vim_emulator = vim
        for x in range(self.count()):
            self.widget(x).setVimEmulator(self._vim_emulator)
            self.widget(x).setEnabledEditAction(self._vim_emulator is None)
            # invalid
            # QtGui.qt_set_sequence_auto_mnemonic(self._vim_emulator is None)
