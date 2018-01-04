
import os.path
import logging

from PyQt5 import QtCore, QtWidgets

from .editor import Editor
from . import __default_basename__


logger = logging.getLogger(__name__)


FILTER = [
    'All support files (*.rst *.md *.txt);;',
    'reStructuredText files (*.rst *.rest);;',
    'Markdown files (*.md *.markdown);;',
    'Text files (*.txt)',
]


class TabEditor(QtWidgets.QTabWidget):
    statusChanged = QtCore.pyqtSignal(int, 'QString')
    previewRequest = QtCore.pyqtSignal(int, 'QString')
    modificationChanged = QtCore.pyqtSignal(int, bool)
    verticalScrollBarChanged = QtCore.pyqtSignal(int, int)
    filenameChanged = QtCore.pyqtSignal('QString', 'QString')
    _actions = None
    _enable_lexer = True
    _find_dialog = None
    _settings = None

    def __init__(self, settings, find_dialog, parent=None):
        super(TabEditor, self).__init__(parent)
        self._settings = settings
        self._find_dialog = find_dialog
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self._onTabCloseRequested)

        self._actions = {}
        action = QtWidgets.QAction(self.tr('&Open'), self)
        action.setShortcut('Ctrl+O')
        action.triggered.connect(self._onOpen)
        self._actions['open'] = action

        action = QtWidgets.QAction(self.tr('&Save'), self)
        action.setShortcut('Ctrl+S')
        action.triggered.connect(self._onSave)
        self._actions['save'] = action

        action = QtWidgets.QAction(self.tr('Save as...'), self)
        action.triggered.connect(self._onSaveAs)
        self._actions['save_as'] = action

        action = QtWidgets.QAction(self.tr('Close all'), self)
        action.triggered.connect(self._onCloseAll)
        self._actions['close_all'] = action

        self._actions.update(Editor.createAction(self, self._onEditAction))

    def closeEvent(self, event):
        for x in range(self.count()):
            if not self._saveAndContinue(x):
                event.ignore()
                return
        self._settings.setValue('editor/opened_files', ';'.join(self.openedFiles()))

    def _onStatusChanged(self, status):
        widget = self.sender()
        index = self.indexOf(widget)
        if index < 0:
            return
        self.statusChanged.emit(index, status)

    def _onInputPreview(self):
        widget = self.sender()
        index = self.indexOf(widget)
        if index < 0:
            return
        self.previewRequest.emit(index, 'input')

    def _onModificationChanged(self, value):
        widget = self.sender()
        index = self.indexOf(widget)
        if index < 0:
            return
        self.updateTitle(index)
        self.modificationChanged.emit(index, value)

    def _onVerticalScrollBarChanged(self, value):
        index = self.currentIndex()
        if index < 0:
            return
        self.verticalScrollBarChanged.emit(index, value)

    def _onTabCloseRequested(self, index):
        if self._saveAndContinue(index):
            widget = self.widget(index)
            self.removeTab(index)
            del widget
        if self.count() == 0:
            self.new('.rst')
        self.currentWidget().setFocus(QtCore.Qt.TabFocusReason)

    def _onOpen(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, self.tr('Open a file'),
            os.getcwd(),
            ''.join(FILTER),
        )
        if filename:
            self.loadFile(os.path.abspath(filename))

    def _onSave(self, index):
        if not index:
            index = self.currentIndex()

        filepath = self.filepath(index)
        dir_name = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        basename, _ = os.path.splitext(filename)
        if not dir_name and basename == __default_basename__:
            self.onSaveAs(index)
        else:
            self.widget(index).writeFile()
            self.updateTitle(index)
            self.previewRequest.emit(index, 'save')

    def _onSaveAs(self, index):
        if not index:
            index = self.currentIndex()

        filepath = self.filepath(index)
        dir_name = os.path.dirname(filepath)
        if not dir_name:
            dir_name = os.getcwd()

        filename = os.path.basename(filepath)
        new_filepath, selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr('Save file as ...'),
            os.path.join(dir_name, filename),
            ''.join(FILTER),
        )
        if new_filepath:
            new_filepath = os.path.abspath(new_filepath)
            _, ext = os.path.splitext(new_filepath)
            if not ext:
                ext = selected_filter.split('(')[1][1:4].strip()
                new_filepath = new_filepath + ext
            self.widget(index).writeFile(new_filepath)
            self.updateTitle(index)
            self.previewRequest.emit(index, 'save')
            self.filenameChanged.emit(filepath, new_filepath)

    def _saveAndContinue(self, index):
        if self.widget(index).isModified():
            filepath = self.filepath(index)
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText(self.tr('The document has been modified.'))
            msgBox.setInformativeText(
                self.tr('Do you want to save your changes?\n%s' % filepath)
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
                self._onSave(index)
        return True

    def _onCloseAll(self):
        x = self.currentIndex()
        while x > -1:
            if not self._saveAndContinue(x):
                return
            widget = self.widget(x)
            self.removeTab(x)
            del widget
            x = self.currentIndex()
        self.new('.rst')

    def _newEditor(self):
        editor = Editor(self._find_dialog, self)
        editor.statusChanged.connect(self._onStatusChanged)
        editor.verticalScrollBar().valueChanged.connect(self._onVerticalScrollBarChanged)
        editor.inputPreviewRequest.connect(self._onInputPreview)
        editor.modificationChanged.connect(self._onModificationChanged)
        editor.enableLexer(self._enable_lexer)
        return editor

    def action(self, action):
        return self._actions.get(action)

    def new(self, ext):
        editor = self._newEditor()
        editor.newFile(ext)
        title = ('*' if editor.isModified() else '') + os.path.basename(editor.getFileName())
        index = self.insertTab(0, editor, title)
        return index

    def open(self, filepath):
        editor = self._newEditor()
        editor.readFile(filepath)
        title = ('*' if editor.isModified() else '') + os.path.basename(editor.getFileName())
        index = self.insertTab(0, editor, title)
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
        return [self.filepath(x) for x in range(self.count())]

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
        if not path:
            index = self.new('.rst')
        else:
            if not Editor.isCanOpened(path):
                logger.warn('Not load file: %s' % path)
                return
            index = None
            for x in range(self.count()):
                if path == self.filepath(x):
                    index = x
                    break
            if index is None:
                if os.path.exists(path):
                    logger.debug('Loading file: %s', path)
                    index = self.open(path)
                else:
                    logger.debug('Creating file: %s', path)
                    index = self.new(path)
        self.setCurrentIndex(index)
        self.statusChanged.emit(index, self.widget(index).status())
        self.previewRequest.emit(index, 'loadfile')
        return path

    def editMenu(self, menu):
        widget = self.currentWidget()
        widget.editMenu(menu, self)

    def _onEditAction(self, action):
        widget = self.currentWidget()
        widget.do_action(action)
