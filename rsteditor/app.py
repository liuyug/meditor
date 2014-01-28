#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
import subprocess
import shutil
import logging
import argparse
import threading
from functools import partial

from PyQt4 import QtGui, QtCore

from rsteditor import __app_name__
from rsteditor import __app_version__
from rsteditor import __default_filename__
from rsteditor import __data_path__
from rsteditor import __home_data_path__
from rsteditor import editor
from rsteditor import webview
from rsteditor import explorer
from rsteditor import output
from rsteditor.util import toUtf8
from rsteditor import globalvars

ALLOWED_LOADS = ['.rst', '.rest',
                 '.html', '.htm',
                 '.txt',
                 '.c', '.cpp', '.h',
                 '.sh',
                 '.py'
                 ]

requestPreview = threading.Event()


def previewWorker(self):
    while True:
        requestPreview.wait()
        if self.previewQuit:
            logging.debug('Preview exit')
            break
        logging.debug('Preview %s', self.previewPath)
        ext = os.path.splitext(self.previewPath)[1].lower()
        self.previewHtml = ''
        if ext in ['.rst', '.rest', '.txt']:
            self.previewHtml = output.rst2html(self.previewText)
        elif ext in ['.htm', '.html', '.php', '.asp']:
            self.previewHtml = toUtf8(self.previewText)
        else:
            self.previewPath = None
        self.previewSignal.emit()
        requestPreview.clear()
    return


class MainWindow(QtGui.QMainWindow):
    previewText = ''
    previewHtml = ''
    previewPath = None
    previewQuit = False
    previewSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.app_exec = os.path.realpath(sys.argv[0])
        self.settings = settings = QtCore.QSettings(
            __app_name__.lower(),
            'config'
        )
        # status bar
        self.statusBar().showMessage(self.tr('Ready'))
        # action
        ## file
        newAction = QtGui.QAction(self.tr('&New'), self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.onNew)
        newwindowAction = QtGui.QAction(self.tr('New &window'), self)
        newwindowAction.setShortcut('Ctrl+W')
        newwindowAction.triggered.connect(self.onNewWindow)
        openAction = QtGui.QAction(self.tr('&Open'), self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.onOpen)
        saveAction = QtGui.QAction(self.tr('&Save'), self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.onSave)
        saveAsAction = QtGui.QAction(self.tr('Save as...'), self)
        saveAsAction.triggered.connect(self.onSaveAs)
        exitAction = QtGui.QAction(self.tr('&Exit'), self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        ## edit
        self.undoAction = QtGui.QAction(self.tr('&Undo'), self)
        self.undoAction.setShortcut('Ctrl+Z')
        self.undoAction.triggered.connect(partial(self.onEdit, 'undo'))
        self.redoAction = QtGui.QAction(self.tr('&Redo'), self)
        self.redoAction.setShortcut('Shift+Ctrl+Z')
        self.redoAction.triggered.connect(partial(self.onEdit, 'redo'))
        self.cutAction = QtGui.QAction(self.tr('Cu&t'), self)
        self.cutAction.setShortcut('Ctrl+X')
        self.cutAction.triggered.connect(partial(self.onEdit, 'cut'))
        self.copyAction = QtGui.QAction(self.tr('&Copy'), self)
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.triggered.connect(partial(self.onEdit, 'copy'))
        self.pasteAction = QtGui.QAction(self.tr('&Paste'), self)
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.triggered.connect(partial(self.onEdit, 'paste'))
        self.deleteAction = QtGui.QAction(self.tr('&Delete'), self)
        self.deleteAction.triggered.connect(partial(self.onEdit, 'delete'))
        self.selectallAction = QtGui.QAction(self.tr('Select &All'), self)
        self.selectallAction.setShortcut('Ctrl+A')
        self.selectallAction.triggered.connect(partial(self.onEdit,
                                                       'selectall'))
        self.findAction = QtGui.QAction(self.tr('&Find'), self)
        self.findAction.setShortcut('Ctrl+F')
        self.findAction.triggered.connect(partial(self.onEdit, 'find'))
        self.findnextAction = QtGui.QAction(self.tr('Find next'), self)
        self.findnextAction.setShortcut('F3')
        self.findnextAction.triggered.connect(partial(self.onEdit, 'findnext'))
        self.findprevAction = QtGui.QAction(self.tr('Find previous'), self)
        self.findprevAction.setShortcut('Shift+F3')
        self.findprevAction.triggered.connect(partial(self.onEdit, 'findprev'))
        ## view
        self.explorerAction = QtGui.QAction(self.tr('File explorer'),
                                            self,
                                            checkable=True)
        self.explorerAction.triggered.connect(partial(self.onView, 'explorer'))
        value = settings.value('view/explorer', True).toBool()
        settings.setValue('view/explorer', value)
        self.explorerAction.setChecked(value)
        self.webviewAction = QtGui.QAction(self.tr('Web Viewer'),
                                           self,
                                           checkable=True)
        self.webviewAction.triggered.connect(partial(self.onView, 'webview'))
        value = settings.value('view/webview', True).toBool()
        settings.setValue('view/webview', value)
        self.webviewAction.setChecked(value)
        self.codeviewAction = QtGui.QAction(self.tr('Code Viewer'),
                                            self,
                                            checkable=True)
        self.codeviewAction.triggered.connect(partial(self.onView, 'codeview'))
        value = settings.value('view/codeview', True).toBool()
        settings.setValue('view/codeview', value)
        self.codeviewAction.setChecked(value)
        ## preview
        previewAction = QtGui.QAction(self.tr('&Preview'), self)
        previewAction.setShortcut('Ctrl+P')
        previewAction.triggered.connect(partial(self.onPreview, 'preview'))
        previewsaveAction = QtGui.QAction(self.tr('Preview on save'),
                                          self,
                                          checkable=True)
        previewsaveAction.triggered.connect(partial(self.onPreview,
                                                    'previewonsave'))
        value = settings.value('preview/onsave', True).toBool()
        settings.setValue('preview/onsave', value)
        previewsaveAction.setChecked(value)
        previewinputAction = QtGui.QAction(self.tr('Preview on input'),
                                           self,
                                           checkable=True)
        previewinputAction.triggered.connect(partial(self.onPreview,
                                                     'previewoninput'))
        value = settings.value('preview/oninput', True).toBool()
        settings.setValue('preview/oninput', value)
        previewinputAction.setChecked(value)
        previewsyncAction = QtGui.QAction(self.tr('Scroll synchronize'),
                                          self,
                                          checkable=True)
        previewsyncAction.triggered.connect(partial(self.onPreview,
                                                    'previewsync'))
        value = settings.value('preview/sync', True).toBool()
        settings.setValue('preview/sync', value)
        previewsyncAction.setChecked(value)
        ## help
        helpAction = QtGui.QAction(self.tr('&Help'), self)
        helpAction.triggered.connect(self.onHelp)
        aboutAction = QtGui.QAction(self.tr('&About'), self)
        aboutAction.triggered.connect(self.onAbout)
        aboutqtAction = QtGui.QAction(self.tr('About &Qt'), self)
        aboutqtAction.triggered.connect(QtGui.QApplication.aboutQt)
        # menu
        menubar = self.menuBar()
        menu = menubar.addMenu(self.tr('&File'))
        menu.addAction(newAction)
        menu.addAction(newwindowAction)
        menu.addAction(openAction)
        menu.addSeparator()
        menu.addAction(saveAction)
        menu.addAction(saveAsAction)
        menu.addSeparator()
        menu.addAction(exitAction)
        menu = menubar.addMenu(self.tr('&Edit'))
        menu.addAction(self.undoAction)
        menu.addAction(self.redoAction)
        menu.addSeparator()
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addAction(self.deleteAction)
        menu.addSeparator()
        menu.addAction(self.selectallAction)
        menu.addSeparator()
        menu.addAction(self.findAction)
        menu.addAction(self.findnextAction)
        menu.addAction(self.findprevAction)
        menu.aboutToShow.connect(self.onEditMenuShow)
        menu = menubar.addMenu(self.tr('&View'))
        menu.addAction(self.explorerAction)
        menu.addAction(self.webviewAction)
        menu.addAction(self.codeviewAction)
        menu.aboutToShow.connect(self.onViewMenuShow)
        menu = menubar.addMenu(self.tr('&Preview'))
        menu.addAction(previewAction)
        menu.addSeparator()
        menu.addAction(previewsaveAction)
        menu.addAction(previewinputAction)
        menu.addAction(previewsyncAction)
        menu = menubar.addMenu(self.tr('&Help'))
        menu.addAction(helpAction)
        menu.addSeparator()
        menu.addAction(aboutAction)
        menu.addAction(aboutqtAction)
        # toolbar
        #self.tb_normal = QtGui.QToolBar('normal')
        #self.tb_normal.setObjectName('normal')
        #self.tb_normal.addAction(newAction)
        #self.tb_normal.addAction(openAction)
        #self.tb_normal.addAction(saveAction)
        #self.tb_normal.addAction(exitAction)
        #self.addToolBar(self.tb_normal)
        # main window
        self.editor = editor.Editor(self)
        self.editor.setObjectName('editor')
        self.setCentralWidget(self.editor)
        # left dock window
        self.dock_explorer = QtGui.QDockWidget(self.tr('Explorer'), self)
        self.dock_explorer.setObjectName('dock_explorer')
        self.explorer = explorer.Explorer(self.dock_explorer)
        self.dock_explorer.setWidget(self.explorer)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_explorer)
        # right dock window
        self.dock_webview = QtGui.QDockWidget(self.tr('Web Previewer'), self)
        self.dock_webview.setObjectName('dock_webview')
        self.webview = webview.WebView(self.dock_webview)
        self.dock_webview.setWidget(self.webview)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_webview)
        self.dock_codeview = QtGui.QDockWidget(self.tr('Code viewer'), self)
        self.dock_codeview.setObjectName('dock_codeview')
        self.codeview = editor.CodeViewer(self.dock_codeview)
        self.dock_codeview.setWidget(self.codeview)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_codeview)
        # event
        self.explorer.fileLoaded.connect(self.onFileLoaded)
        self.explorer.fileNew.connect(self.onNew)
        self.explorer.fileRenamed.connect(self.onFileRenamed)
        self.explorer.fileDeleted.connect(self.onFileDeleted)
        self.editor.verticalScrollBar().valueChanged.connect(
            self.onValueChanged)
        self.editor.lineInputed.connect(self.onInputPreview)
        # window state
        self.restoreGeometry(settings.value('geometry').toByteArray())
        self.restoreState(settings.value('windowState').toByteArray())
        path = toUtf8(settings.value('explorer/rootPath').toString())
        if not os.path.exists(path):
            path = os.path.expanduser('~')
        self.explorer.setRootPath(path)
        self.setFont(QtGui.QFont('Monospace', 12))
        self.editor.emptyFile()
        value = settings.value('editor/enableLexer', True).toBool()
        settings.setValue('editor/enableLexer', value)
        self.editor.enableLexer(value)
        self.previewWorker = threading.Thread(target=previewWorker, args=(self,))
        self.previewSignal.connect(self.previewDisplay)
        logging.debug('Preview worker start')
        self.previewWorker.start()

    def closeEvent(self, event):
        if self.saveAndContinue():
            event.accept()
        else:
            event.ignore()
        settings = self.settings
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        settings.setValue('explorer/rootPath', self.explorer.getRootPath())
        settings.sync()
        self.previewQuit = True
        requestPreview.set()
        self.previewWorker.join()

    def onNew(self):
        if not self.saveAndContinue():
            return
        filename = __default_filename__
        self.setWindowTitle('%s - %s' % (__app_name__, filename))
        ext = os.path.splitext(filename)[1].lower()
        text = ''
        skeleton = os.path.join(__home_data_path__,
                                'template',
                                'skeleton%s' % ext)
        if os.path.exists(skeleton):
            with open(skeleton, 'r') as f:
                text = f.read()
        self.editor.setValue(text)
        self.editor.setFileName(filename)
        self.editor.setFocus()
        self.preview(text, filename)

    def onNewWindow(self):
        if sys.platform == 'win32' and self.app_exec.endswith('.py'):
            subprocess.Popen(['python', self.app_exec])
        else:
            subprocess.Popen([self.app_exec])
        return

    def onOpen(self):
        if not self.saveAndContinue():
            return
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     self.tr('Open a file'))
        if filename:
            filename = toUtf8(filename)
            self.setWindowTitle('%s - %s' % (__app_name__, filename))
            self.loadFile(filename)
        return

    def onSave(self):
        filename = self.editor.getFileName()
        if filename == __default_filename__:
            self.onSaveAs()
        else:
            self.editor.writeFile()
            if self.settings.value('preview/onsave').toBool():
                text = toUtf8(self.editor.getValue())
                self.preview(text, filename)
        return

    def onSaveAs(self):
        filename = QtGui.QFileDialog.getSaveFileName(
            self,
            self.tr('Save file as ...')
        )
        if filename:
            filename = toUtf8(filename)
            self.editor.writeFile(filename)
            self.setWindowTitle('%s - %s' % (__app_name__, filename))
            if self.settings.value('preview/onsave').toBool():
                text = toUtf8(self.editor.getValue())
                self.preview(text, filename)
            self.explorer.setRootPath(os.path.dirname(filename), True)
        return

    def onEditMenuShow(self):
        widget = self.focusWidget()
        if isinstance(widget, editor.CodeViewer):
            self.undoAction.setEnabled(False)
            self.redoAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            self.copyAction.setEnabled(widget.isCopyAvailable())
            self.pasteAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.selectallAction.setEnabled(True)
            self.findAction.setEnabled(True)
            self.findnextAction.setEnabled(True)
            self.findprevAction.setEnabled(True)
        elif isinstance(widget, editor.Editor):
            self.undoAction.setEnabled(widget.isUndoAvailable())
            self.redoAction.setEnabled(widget.isRedoAvailable())
            self.cutAction.setEnabled(widget.isCopyAvailable())
            self.copyAction.setEnabled(widget.isCopyAvailable())
            self.pasteAction.setEnabled(widget.isPasteAvailable())
            self.deleteAction.setEnabled(widget.isCopyAvailable())
            self.selectallAction.setEnabled(True)
            self.findAction.setEnabled(True)
            self.findnextAction.setEnabled(True)
            self.findprevAction.setEnabled(True)
        elif isinstance(widget, webview.WebView):
            self.undoAction.setEnabled(False)
            self.redoAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            action = widget.pageAction(widget.page().Copy)
            self.copyAction.setEnabled(action.isEnabled())
            self.pasteAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.selectallAction.setEnabled(True)
            self.findAction.setEnabled(False)
            self.findnextAction.setEnabled(False)
            self.findprevAction.setEnabled(False)

    def onEdit(self, label):
        widget = self.focusWidget()
        if isinstance(widget, editor.CodeViewer):
            if label == 'copy':
                widget.copy()
            elif label == 'selectall':
                widget.selectAll()
            elif label == 'find':
                widget.find()
            elif label == 'findnext':
                widget.findNext()
            elif label == 'findprev':
                widget.findPrevious()
        elif isinstance(widget, editor.Editor):
            if label == 'undo':
                widget.undo()
            elif label == 'redo':
                widget.redo()
            elif label == 'cut':
                widget.cut()
            elif label == 'copy':
                widget.copy()
            elif label == 'paste':
                widget.paste()
            elif label == 'delete':
                widget.delete()
            elif label == 'selectall':
                widget.selectAll()
            elif label == 'find':
                widget.find()
            elif label == 'findnext':
                widget.findNext()
            elif label == 'findprev':
                widget.findPrevious()
        elif isinstance(widget, webview.WebView):
            if label == 'copy':
                widget.triggerPageAction(widget.page().Copy)
            elif label == 'selectall':
                widget.triggerPageAction(widget.page().SelectAll)
        return

    def onViewMenuShow(self):
        self.explorerAction.setChecked(self.dock_explorer.isVisible())
        self.webviewAction.setChecked(self.dock_webview.isVisible())
        self.codeviewAction.setChecked(self.dock_codeview.isVisible())

    def onView(self, label, checked):
        if label == 'explorer':
            self.dock_explorer.setVisible(checked)
            self.settings.setValue('view/explorer', checked)
        elif label == 'webview':
            self.dock_webview.setVisible(checked)
            self.settings.setValue('view/webview', checked)
        elif label == 'codeview':
            self.dock_codeview.setVisible(checked)
            self.settings.setValue('view/codeview', checked)
        return

    def onPreview(self, label, checked):
        if label == 'preview':
            text = toUtf8(self.editor.getValue())
            self.preview(text, self.editor.getFileName())
        elif label == 'previewonsave':
            self.settings.setValue('preview/onsave', checked)
        elif label == 'previewoninput':
            self.settings.setValue('preview/oninput', checked)
        elif label == 'previewsync':
            self.settings.setValue('preview/sync', checked)
        return

    def onHelp(self):
        help_path = os.path.join(__data_path__, 'docs', 'demo.rst')
        if sys.platform == 'win32' and self.app_exec.endswith('.py'):
            subprocess.Popen(['python', self.app_exec, help_path])
        else:
            subprocess.Popen([self.app_exec, help_path])
        return

    def onAbout(self):
        title = toUtf8(self.tr('About %s')) % __app_name__
        text = toUtf8(self.tr(
            "%s %s\n\n"
            "The editor for ReStructedText."
        )) % (__app_name__, __app_version__)
        QtGui.QMessageBox.about(self, title, text)

    def onFileLoaded(self, path):
        if not self.saveAndContinue():
            return
        path = toUtf8(path)
        if not os.path.exists(path):
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in ALLOWED_LOADS:
            text = None
            if self.editor.readFile(path):
                self.editor.setFocus()
                self.setWindowTitle('%s - %s' % (__app_name__, path))
                text = toUtf8(self.editor.getValue())
                self.preview(text, path)
        return

    def onValueChanged(self, value):
        if self.settings.value('preview/sync').toBool():
            dx = self.editor.getHScrollValue()
            dy = self.editor.getVScrollValue()
            editor_vmax = self.editor.getVScrollMaximum()
            webview_vmax = self.webview.getVScrollMaximum()
            if editor_vmax:
                self.webview.setScrollBarValue(
                    dx,
                    dy * webview_vmax / editor_vmax
                )
        return

    def onInputPreview(self):
        if self.settings.value('preview/oninput').toBool():
            text = toUtf8(self.editor.getValue())
            self.preview(text, self.editor.getFileName())
        return

    def onFileRenamed(self, old_name, new_name):
        filename = self.editor.getFileName()
        if toUtf8(old_name) == filename:
            self.editor.setFileName(toUtf8(new_name))
            self.setWindowTitle('%s - %s' % (__app_name__, toUtf8(new_name)))

    def onFileDeleted(self, name):
        filename = self.editor.getFileName()
        if toUtf8(name) == filename:
            self.editor.emptyFile()
            self.setWindowTitle('%s - %s' % (
                __app_name__,
                __default_filename__)
            )
            self.preview('', __default_filename__)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def preview(self, text, path):
        if not requestPreview.is_set():
            self.previewText = text
            self.previewPath = path
            requestPreview.set()
        else:
            logging.debug('Preview is working...')
        return

    def previewDisplay(self):
        self.webview.setHtml(self.previewHtml, self.previewPath)
        self.codeview.setValue(self.previewHtml)
        dx = self.editor.getHScrollValue()
        dy = self.editor.getVScrollValue()
        editor_vmax = self.editor.getVScrollMaximum()
        webview_vmax = self.webview.getVScrollMaximum()
        if editor_vmax:
            self.webview.setScrollBarValue(dx, dy * webview_vmax / editor_vmax)

    def saveAndContinue(self):
        if self.editor.isModified():
            msgBox = QtGui.QMessageBox(self)
            msgBox.setIcon(QtGui.QMessageBox.Question)
            msgBox.setText(self.tr('The document has been modified.'))
            msgBox.setInformativeText(
                self.tr('Do you want to save your changes?')
            )
            msgBox.setStandardButtons(
                QtGui.QMessageBox.Save |
                QtGui.QMessageBox.Discard |
                QtGui.QMessageBox.Cancel
            )
            msgBox.setDefaultButton(QtGui.QMessageBox.Save)
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox.Cancel:
                return False
            if ret == QtGui.QMessageBox.Save:
                self.onSave()
        return True

    def loadFile(self, path):
        """ widget load file from command line """
        if not path:
            self.preview('', __default_filename__)
            return
        self.explorer.loadFile(path)


def main():
    globalvars.init()
    parser = argparse.ArgumentParser()
    parser.add_argument('--style', choices=QtGui.QStyleFactory.keys())
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % __app_version__)
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=0)
    parser.add_argument('rstfile', nargs='?', help='rest file')
    args = parser.parse_args()
    rstfile = os.path.realpath(args.rstfile) if args.rstfile else None
    globalvars.logging_level = logging.WARNING - (args.verbose * 10)
    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=globalvars.logging_level)
    logging.debug(args)
    if not os.path.exists(__home_data_path__):
        shutil.copytree(__data_path__, __home_data_path__)
    QtGui.QApplication.setStyle(args.style)
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.loadFile(rstfile)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
