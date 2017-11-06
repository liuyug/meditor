#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import sys
import subprocess
import logging
import logging.handlers
import argparse
import threading
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets, QtPrintSupport
from pygments.formatters import get_formatter_by_name

from . import __app_name__
from . import __app_version__
from . import __default_basename__
from . import __data_path__
from . import __icon_path__
from . import __home_data_path__
from . import pygments_styles
from . import editor
from . import webview
from . import explorer
from . import output
from . import globalvars
from .util import toUtf8, toBytes, download, unzip
from .findreplace import FindReplaceDialog


ALLOWED_LOADS = ['.rst', '.rest',
                 '.md', '.markdown',
                 '.html', '.htm',
                 '.txt',
                 '.c', '.cpp', '.h',
                 '.sh',
                 '.py'
                 ]

FILTER = [
    'All support files (*.rst *.md *.txt);;',
    'reStructedText files (*.rst *.rest);;',
    'Markdown files (*.md *.markdown);;',
    'Text files (*.txt)',
]

requestPreview = threading.Event()

# for debug
LOG_FILENAME = os.path.join(__home_data_path__, 'rsteditor.log')

# for logger
logger = None


def previewWorker(self):
    while True:
        requestPreview.wait()
        if self.previewQuit:
            logger.debug('Preview exit')
            break
        logger.debug('Preview %s', self.previewPath)
        ext = os.path.splitext(self.previewPath)[1].lower()
        if not self.previewText:
            self.previewHtml = ''
        elif ext in ['.rst', '.rest', '.txt']:
            self.previewHtml = output.rst2htmlcode(self.previewText,
                                                   theme=self.rst_theme)
        elif ext in ['.md', '.markdown']:
            self.previewHtml = output.md2htmlcode(self.previewText,
                                                  theme=self.md_theme)
        elif ext in ['.html', '.htm']:
            self.previewHtml = self.previewText
        elif ext in ALLOWED_LOADS:
            self.previewHtml = '<html><strong>Do not support preview.</strong></html>'
        else:
            self.previewPath = 'error'
        self.previewSignal.emit()
        requestPreview.clear()
    return


class MainWindow(QtWidgets.QMainWindow):
    rst_theme = 'default'
    md_theme = 'default'
    previewText = ''
    previewHtml = ''
    previewPath = None
    previewQuit = False
    previewSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(MainWindow, self).__init__()
        self._app_exec = os.path.realpath(sys.argv[0])
        if sys.platform == 'win32':
            ext = os.path.splitext(self._app_exec)[1]
            if ext not in ['.py', '.exe']:
                self._app_exec += '.exe'
        logger.info('app name: %s' % self._app_exec)
        self.settings = settings = QtCore.QSettings(
            __app_name__.lower(),
            'config'
        )
        # No support fromTheme function in Qt4.6
        self._icon = os.path.join(__icon_path__, 'meditor-text-editor.ico')
        logger.info('icon path: %s' % __icon_path__)
        self.setWindowIcon(QtGui.QIcon(self._icon))
        self.setupMenu()
        self.setupToolbar()
        self.setupStatusBar()
        # main window
        self.findDialog = FindReplaceDialog(self)

        self.editor = editor.Editor(self)
        self.editor.setObjectName('editor')
        self.editor.encodingChange.connect(
            partial(self.onStatusChange, 'encoding'))
        self.editor.lexerChange.connect(
            partial(self.onStatusChange, 'lexer'))
        self.editor.eolChange.connect(
            partial(self.onStatusChange, 'eol'))

        self.setCentralWidget(self.editor)
        # left dock window
        self.dock_explorer = QtWidgets.QDockWidget(self.tr('Explorer'), self)
        self.dock_explorer.setObjectName('dock_explorer')
        self.explorer = explorer.Workspace(self.dock_explorer)
        self.dock_explorer.setWidget(self.explorer)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_explorer)
        # right dock window
        self.dock_webview = QtWidgets.QDockWidget(self.tr('Web Previewer'), self)
        self.dock_webview.setObjectName('dock_webview')
        self.webview = webview.WebView(self.dock_webview)
        self.dock_webview.setWidget(self.webview)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_webview)
        self.dock_codeview = QtWidgets.QDockWidget(self.tr('Code viewer'), self)
        self.dock_codeview.setObjectName('dock_codeview')
        self.codeview = editor.CodeViewer(self.dock_codeview)
        self.dock_codeview.setWidget(self.codeview)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_codeview)
        # event
        self.webview.exportHtml.connect(partial(self.onExport, 'html'))
        self.explorer.fileLoaded.connect(self.onFileLoaded)
        self.explorer.fileNew.connect(self.onNew)
        self.explorer.fileRenamed.connect(self.onFileRenamed)
        self.explorer.fileDeleted.connect(self.onFileDeleted)
        self.editor.verticalScrollBar().valueChanged.connect(
            self.onValueChanged)
        self.editor.lineInputed.connect(self.onInputPreview)
        # window state
        self.restoreGeometry(settings.value('geometry', type=QtCore.QByteArray))
        self.restoreState(settings.value('windowState', type=QtCore.QByteArray))
        value = toUtf8(settings.value('explorer/workspace', type=str))
        for path in value.split(';'):
            self.explorer.appendRootPath(path)

        self.setFont(QtGui.QFont('Monospace', 12))
        self.editor.emptyFile()

        value = settings.value('editor/enableLexer', True, type=bool)
        self.editor.enableLexer(value)
        self.previewWorker = threading.Thread(target=previewWorker,
                                              args=(self,))
        self.previewSignal.connect(self.previewDisplay)
        logger.debug('Preview worker start')
        self.previewWorker.start()

    def setupMenu(self):
        settings = self.settings
        # action
        # file
        newRstAction = QtWidgets.QAction(
            self.tr('reStructedText'), self)
        newRstAction.setShortcut('Ctrl+N')
        newRstAction.triggered.connect(partial(self.onNew, 'rst'))

        newMdAction = QtWidgets.QAction(self.tr('Markdown'), self)
        newMdAction.triggered.connect(partial(self.onNew, 'md'))

        newwindowAction = QtWidgets.QAction(self.tr('New &window'), self)
        newwindowAction.setShortcut('Ctrl+W')
        newwindowAction.triggered.connect(self.onNewWindow)
        openAction = QtWidgets.QAction(self.tr('&Open'), self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.onOpen)
        saveAction = QtWidgets.QAction(self.tr('&Save'), self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.onSave)
        saveAsAction = QtWidgets.QAction(self.tr('Save as...'), self)
        saveAsAction.triggered.connect(self.onSaveAs)
        exportPDFAction = QtWidgets.QAction(self.tr('Export to PDF'), self)
        exportPDFAction.triggered.connect(partial(self.onExport, 'pdf'))
        exportHTMLAction = QtWidgets.QAction(self.tr('Export to HTML'), self)
        exportHTMLAction.triggered.connect(partial(self.onExport, 'html'))
        printAction = QtWidgets.QAction(self.tr('&Print'), self)
        printAction.setShortcut('Ctrl+P')
        printAction.triggered.connect(self.onPrint)
        printPreviewAction = QtWidgets.QAction(self.tr('Print Pre&view'), self)
        printPreviewAction.triggered.connect(self.onPrintPreview)
        exitAction = QtWidgets.QAction(self.tr('&Exit'), self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        # edit
        self.undoAction = QtWidgets.QAction(self.tr('&Undo'), self)
        self.undoAction.setShortcut('Ctrl+Z')
        self.undoAction.triggered.connect(partial(self.onEdit, 'undo'))
        self.redoAction = QtWidgets.QAction(self.tr('&Redo'), self)
        self.redoAction.setShortcut('Shift+Ctrl+Z')
        self.redoAction.triggered.connect(partial(self.onEdit, 'redo'))
        self.cutAction = QtWidgets.QAction(self.tr('Cu&t'), self)
        self.cutAction.setShortcut('Ctrl+X')
        self.cutAction.triggered.connect(partial(self.onEdit, 'cut'))
        self.copyAction = QtWidgets.QAction(self.tr('&Copy'), self)
        self.copyAction.setShortcut('Ctrl+C')
        self.copyAction.triggered.connect(partial(self.onEdit, 'copy'))
        self.pasteAction = QtWidgets.QAction(self.tr('&Paste'), self)
        self.pasteAction.setShortcut('Ctrl+V')
        self.pasteAction.triggered.connect(partial(self.onEdit, 'paste'))
        self.deleteAction = QtWidgets.QAction(self.tr('&Delete'), self)
        self.deleteAction.triggered.connect(partial(self.onEdit, 'delete'))
        self.selectallAction = QtWidgets.QAction(self.tr('Select &All'), self)
        self.selectallAction.setShortcut('Ctrl+A')
        self.selectallAction.triggered.connect(partial(self.onEdit,
                                                       'selectall'))
        self.findAction = QtWidgets.QAction(self.tr('&Find or Replace'), self)
        self.findAction.setShortcut('Ctrl+F')
        self.findAction.triggered.connect(partial(self.onEdit, 'find'))
        self.findnextAction = QtWidgets.QAction(self.tr('Find Next'), self)
        self.findnextAction.setShortcut('F3')
        self.findnextAction.triggered.connect(partial(self.onEdit, 'findnext'))
        self.findprevAction = QtWidgets.QAction(self.tr('Find Previous'), self)
        self.findprevAction.setShortcut('Shift+F3')
        self.findprevAction.triggered.connect(partial(self.onEdit, 'findprev'))

        self.replacenextAction = QtWidgets.QAction(self.tr('Replace Next'), self)
        self.replacenextAction.setShortcut('F4')
        self.replacenextAction.triggered.connect(partial(self.onEdit, 'replacenext'))

        self.indentAction = QtWidgets.QAction(self.tr('Indent'), self)
        self.indentAction.setShortcut('TAB')
        self.indentAction.triggered.connect(partial(self.onEdit, 'indent'))
        self.unindentAction = QtWidgets.QAction(self.tr('Unindent'), self)
        self.unindentAction.setShortcut('Shift+TAB')
        self.unindentAction.triggered.connect(partial(self.onEdit, 'unindent'))

        enableLexerAction = QtWidgets.QAction(self.tr('Enable Lexer'),
                self, checkable=True)
        value = settings.value('editor/enableLexer', True, type=bool)
        settings.setValue('editor/enableLexer', value)
        enableLexerAction.setChecked(value)
        enableLexerAction.triggered.connect(
            partial(self.onPreview, 'enablelexer'))

        fileAssociationAction = QtWidgets.QAction(self.tr('File Associate'), self)
        fileAssociationAction.triggered.connect(self.onFileAssociation)
        # view
        self.explorerAction = QtWidgets.QAction(self.tr('File explorer'),
                                            self,
                                            checkable=True)
        self.explorerAction.triggered.connect(partial(self.onView, 'explorer'))
        value = settings.value('view/explorer', True, type=bool)
        settings.setValue('view/explorer', value)
        self.explorerAction.setChecked(value)
        self.webviewAction = QtWidgets.QAction(self.tr('Web Viewer'),
                                           self,
                                           checkable=True)
        self.webviewAction.triggered.connect(partial(self.onView, 'webview'))
        value = settings.value('view/webview', True, type=bool)
        settings.setValue('view/webview', value)
        self.webviewAction.setChecked(value)
        self.codeviewAction = QtWidgets.QAction(self.tr('Code Viewer'),
                                            self,
                                            checkable=True)
        self.codeviewAction.triggered.connect(partial(self.onView, 'codeview'))
        value = settings.value('view/codeview', True, type=bool)
        settings.setValue('view/codeview', value)
        self.codeviewAction.setChecked(value)
        # preview
        previewAction = QtWidgets.QAction(self.tr('&Preview'), self)
        previewAction.triggered.connect(partial(self.onPreview, 'preview'))
        previewsaveAction = QtWidgets.QAction(self.tr('Preview on save'),
                                          self,
                                          checkable=True)
        previewsaveAction.triggered.connect(partial(self.onPreview,
                                                    'previewonsave'))
        value = settings.value('preview/onsave', True, type=bool)
        settings.setValue('preview/onsave', value)
        previewsaveAction.setChecked(value)
        previewinputAction = QtWidgets.QAction(self.tr('Preview on input'),
                                           self,
                                           checkable=True)
        previewinputAction.triggered.connect(partial(self.onPreview,
                                                     'previewoninput'))
        value = settings.value('preview/oninput', True, type=bool)
        settings.setValue('preview/oninput', value)
        previewinputAction.setChecked(value)
        previewsyncAction = QtWidgets.QAction(self.tr('Scroll synchronize'),
                                          self,
                                          checkable=True)
        previewsyncAction.triggered.connect(partial(self.onPreview,
                                                    'previewsync'))
        value = settings.value('preview/sync', True, type=bool)
        settings.setValue('preview/sync', value)
        previewsyncAction.setChecked(value)
        # theme
        # docutils theme
        default_cssAction = QtWidgets.QAction('Default theme',
                                           self,
                                           checkable=True)
        default_cssAction.triggered.connect(
            partial(self.onRstThemeChanged, 'default'))
        rstThemeGroup = QtWidgets.QActionGroup(self)
        rstThemeGroup.setExclusive(True)
        rstThemeGroup.addAction(default_cssAction)
        for theme in output.get_rst_themes().keys():
            act = QtWidgets.QAction('%s theme' % theme,
                                self,
                                checkable=True)
            act.triggered.connect(partial(self.onRstThemeChanged, theme))
            rstThemeGroup.addAction(act)
        value = toUtf8(settings.value('rst_theme', 'default', type=str))
        settings.setValue('rst_theme', value)
        self.rst_theme = value
        default_cssAction.setChecked(True)
        theme_name = '%s theme' % toUtf8(value)
        for act in rstThemeGroup.actions():
            theme = toUtf8(act.text())
            if theme_name == theme:
                act.setChecked(True)
                break
        # markdown theme
        default_cssAction = QtWidgets.QAction('Default theme',
                                           self,
                                           checkable=True)
        default_cssAction.triggered.connect(
            partial(self.onMdThemeChanged, 'default'))
        mdThemeGroup = QtWidgets.QActionGroup(self)
        mdThemeGroup.setExclusive(True)
        mdThemeGroup.addAction(default_cssAction)
        for theme in output.get_md_themes().keys():
            act = QtWidgets.QAction('%s theme' % theme,
                                self,
                                checkable=True)
            act.triggered.connect(partial(self.onMdThemeChanged, theme))
            mdThemeGroup.addAction(act)
        value = toUtf8(settings.value('md_theme', 'default', type=str))
        settings.setValue('md_theme', value)
        self.md_theme = value
        default_cssAction.setChecked(True)
        theme_name = '%s theme' % toUtf8(value)
        for act in mdThemeGroup.actions():
            theme = toUtf8(act.text())
            if theme_name == theme:
                act.setChecked(True)
                break
        # code style
        self.codeStyleGroup = QtWidgets.QActionGroup(self)
        self.codeStyleGroup.setExclusive(True)
        for k, v in pygments_styles.items():
                act = QtWidgets.QAction(v,
                                    self,
                                    checkable=True)
                act.triggered.connect(partial(self.onCodeStyleChanged, k))
                self.codeStyleGroup.addAction(act)
        value = toUtf8(settings.value('pygments', 'null', type=str))
        settings.setValue('pygments', value)
        for act in self.codeStyleGroup.actions():
            pygments_desc = toUtf8(act.text())
            if pygments_desc == pygments_styles.get(value, ''):
                act.setChecked(True)
                break
        self.mathjaxAction = QtWidgets.QAction(
            self.tr('Install MathJax'), self)
        self.mathjaxAction.triggered.connect(
            partial(self.onMathJax, 'install'))
        self.mathjaxAction.setEnabled(not os.path.exists(os.path.join(
            __home_data_path__, 'MathJax-master', 'MathJax.js')))
        # help
        helpAction = QtWidgets.QAction(self.tr('&Help'), self)
        helpAction.triggered.connect(self.onHelp)
        aboutAction = QtWidgets.QAction(self.tr('&About'), self)
        aboutAction.triggered.connect(self.onAbout)
        aboutqtAction = QtWidgets.QAction(self.tr('About &Qt'), self)
        aboutqtAction.triggered.connect(QtWidgets.QApplication.aboutQt)
        # menu
        menubar = self.menuBar()
        menu = menubar.addMenu(self.tr('&File'))
        submenu = QtWidgets.QMenu(self.tr('&New'), menu)
        submenu.addAction(newRstAction)
        submenu.addAction(newMdAction)
        menu.addMenu(submenu)
        menu.addAction(newwindowAction)
        menu.addAction(openAction)
        menu.addSeparator()
        menu.addAction(saveAction)
        menu.addAction(saveAsAction)
        menu.addSeparator()
        menu.addAction(exportPDFAction)
        menu.addAction(exportHTMLAction)
        menu.addSeparator()
        menu.addAction(printPreviewAction)
        menu.addAction(printAction)
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
        menu.addAction(self.replacenextAction)
        menu.addSeparator()
        menu.addAction(self.indentAction)
        menu.addAction(self.unindentAction)
        menu.addSeparator()
        menu.addAction(fileAssociationAction)
        menu.addAction(enableLexerAction)
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

        menu = menubar.addMenu(self.tr('&Theme'))
        submenu = QtWidgets.QMenu(self.tr('&reStructedText'), menu)
        for act in rstThemeGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)
        submenu = QtWidgets.QMenu(self.tr('&Markdown'), menu)
        for act in mdThemeGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)
        menu.addSeparator()
        submenu = QtWidgets.QMenu(self.tr('&Pygments'), menu)
        for act in self.codeStyleGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)
        menu.addAction(self.mathjaxAction)

        menu = menubar.addMenu(self.tr('&Help'))
        menu.addAction(helpAction)
        menu.addSeparator()
        menu.addAction(aboutAction)
        menu.addAction(aboutqtAction)

    def setupToolbar(self):
        # toolbar
        # self.tb_normal = QtWidgets.QToolBar('normal')
        # self.tb_normal.setObjectName('normal')
        # self.tb_normal.addAction(newAction)
        # self.tb_normal.addAction(openAction)
        # self.tb_normal.addAction(saveAction)
        # self.tb_normal.addAction(exitAction)
        # self.addToolBar(self.tb_normal)
        pass

    def setupStatusBar(self):
        # status bar
        self.statusEncoding = QtWidgets.QLabel('ASCII', self)
        self.statusBar().addPermanentWidget(self.statusEncoding)

        self.statusEol = QtWidgets.QLabel('EOL', self)
        self.statusBar().addPermanentWidget(self.statusEol)

        self.statusLexer = QtWidgets.QLabel('Lexer', self)
        self.statusBar().addPermanentWidget(self.statusLexer)

        self.statusBar().showMessage(self.tr('Ready'))

    def closeEvent(self, event):
        if self.saveAndContinue():
            event.accept()
        else:
            event.ignore()
        settings = self.settings
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        settings.setValue('explorer/workspace', ';'.join(
            self.explorer.getRootPaths()))
        settings.sync()
        self.previewQuit = True
        requestPreview.set()
        self.previewWorker.join()
        logger.info('=== rsteditor end ===')

    def onStatusChange(self, status, value):
        if status == 'lexer':
            self.statusLexer.setText(value)
        elif status == 'encoding':
            self.statusEncoding.setText(value)
        elif status == 'eol':
            self.statusEol.setText(value)

    def onNew(self, ext, path=None):
        if not self.saveAndContinue():
            return
        if path:
            filename = path
        else:
            filename = '%s.%s' % (__default_basename__, ext)

        self.setWindowTitle('%s - %s' % (__app_name__, filename))
        ext = os.path.splitext(filename)[1].lower()
        text = ''
        skeletons = [
            os.path.join(__home_data_path__, 'template', 'skeleton%s' % ext),
            os.path.join(__data_path__, 'template', 'skeleton%s' % ext),
        ]
        for skeleton in skeletons:
            if os.path.exists(skeleton):
                with open(skeleton, 'r', encoding='utf-8') as f:
                    text = f.read()
                break
        self.editor.setValue(text)
        self.editor.setFileName(filename)
        self.editor.setFocus()
        self.preview(text, filename)

    def onNewWindow(self):
        if sys.platform == 'win32' and self._app_exec.endswith('.py'):
            subprocess.Popen(['python', self._app_exec])
        else:
            subprocess.Popen([self._app_exec])
        return

    def onOpen(self):
        if not self.saveAndContinue():
            return
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, self.tr('Open a file'),
            filter=''.join(FILTER),
        )
        # ???: return a tuple
        if isinstance(filename, tuple):
            filename = filename[0]
        if filename:
            filename = toUtf8(filename)
            self.loadFile(filename)
        return

    def onSave(self):
        filename = self.editor.getFileName()
        if isinstance(filename, tuple):
            filename = filename[0]
        basename, _ = os.path.splitext(filename)
        if basename == __default_basename__:
            self.onSaveAs()
        else:
            self.editor.writeFile()
            if self.settings.value('preview/onsave', type=bool):
                text = toUtf8(self.editor.getValue())
                self.preview(text, filename)
        return

    def onSaveAs(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr('Save file as ...'),
            self.explorer.getCurrentPath(),
            ''.join(FILTER),
        )
        if isinstance(filename, tuple):
            filename = filename[0]
        if filename:
            filename = toUtf8(filename)
            self.editor.writeFile(filename)
            self.setWindowTitle('%s - %s' % (__app_name__, filename))
            if self.settings.value('preview/onsave', type=bool):
                text = toUtf8(self.editor.getValue())
                self.preview(text, filename)
            # self.explorer.setRootPath(os.path.dirname(filename), True)
        return

    def onExport(self, label):
        if not self.saveAndContinue():
            return
        if label == 'html':
            in_basename, in_ext = os.path.splitext(
                os.path.basename(self.editor.getFileName()))
            out_file = in_basename + '.html'
            out_html = QtWidgets.QFileDialog.getSaveFileName(
                self, self.tr('export HTML as ...'),
                os.path.join(self.explorer.getCurrentPath(), out_file),
                "HTML files (*.html *.htm)",
            )
            if isinstance(out_html, tuple):
                out_html = out_html[0]
            if out_html:
                out_html = toUtf8(out_html)
                basename, out_ext = os.path.splitext(out_html)
                if out_ext.lower() not in ['.html', '.htm']:
                    out_html += '.html'
                if in_ext.lower() in ['.rst', '.rest']:
                    output.rst2html(self.editor.getFileName(),
                                    out_html,
                                    theme=self.rst_theme)
                elif in_ext.lower() in ['.md', '.markdown']:
                    output.md2html(self.editor.getFileName(),
                                out_html,
                                theme=self.md_theme)
        elif label == 'pdf':
            self.webview.onExportToPdf()

    def onPrintPreview(self):
        if self.editor.hasFocus():
            printer = self.editor.getPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.editor
        elif self.codeview.hasFocus():
            printer = self.editor.getPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.codeview
        elif self.webview.hasFocus():
            printer = QtPrintSupport.QPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.webview
        else:
            return
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        printer.setPageOrientation(QtGui.QPageLayout.Portrait)
        printer.setPageMargins(15, 15, 15, 15, QtPrintSupport.QPrinter.Millimeter)
        preview = QtPrintSupport.QPrintPreviewDialog(printer, widget)
        preview.paintRequested.connect(widget.print_)
        preview.exec_()

    def onPrint(self):
        if self.editor.hasFocus():
            printer = self.editor.getPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.editor
        elif self.codeview.hasFocus():
            printer = self.editor.getPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.codeview
        elif self.webview.hasFocus():
            printer = QtPrintSupport.QPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.webview
        else:
            return
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        printer.setPageMargins(15, 15, 15, 15, QtPrintSupport.QPrinter.Millimeter)
        printDialog = QtPrintSupport.QPrintDialog(printer, widget)
        if printDialog.exec_() == QtWidgets.QDialog.Accepted:
            widget.print_(printer)

    def onEditMenuShow(self):
        if self.codeview.hasFocus():
            self.undoAction.setEnabled(False)
            self.redoAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            self.copyAction.setEnabled(self.codeview.isCopyAvailable())
            self.pasteAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.selectallAction.setEnabled(True)
            self.findAction.setEnabled(True)
            self.findnextAction.setEnabled(True)
            self.findprevAction.setEnabled(True)
            self.replacenextAction.setEnabled(False)
        elif self.editor.hasFocus():
            self.undoAction.setEnabled(self.editor.isUndoAvailable())
            self.redoAction.setEnabled(self.editor.isRedoAvailable())
            self.cutAction.setEnabled(self.editor.isCopyAvailable())
            self.copyAction.setEnabled(self.editor.isCopyAvailable())
            self.pasteAction.setEnabled(self.editor.isPasteAvailable())
            self.deleteAction.setEnabled(self.editor.isCopyAvailable())
            self.selectallAction.setEnabled(True)
            self.findAction.setEnabled(True)
            self.findnextAction.setEnabled(True)
            self.findprevAction.setEnabled(True)
            self.replacenextAction.setEnabled(True)
            self.indentAction.setEnabled(self.editor.hasSelectedText())
            self.unindentAction.setEnabled(self.editor.hasSelectedText())
        elif self.webview.hasFocus():
            self.undoAction.setEnabled(False)
            self.redoAction.setEnabled(False)
            self.cutAction.setEnabled(False)
            action = self.webview.pageAction(self.webview.page().Copy)
            self.copyAction.setEnabled(action.isEnabled())
            self.pasteAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            self.selectallAction.setEnabled(True)
            self.findAction.setEnabled(False)
            self.findnextAction.setEnabled(False)
            self.findprevAction.setEnabled(False)

    def onEdit(self, label):
        if self.codeview.hasFocus():
            if label == 'copy':
                self.codeview.copy()
            elif label == 'selectall':
                self.codeview.selectAll()
            elif label == 'find':
                self.codeview.find(self.findDialog)
            elif label == 'findnext':
                self.codeview.findNext(self.findDialog.getFindText())
            elif label == 'findprev':
                self.codeview.findPrevious(self.findDialog.getFindText())
        elif self.editor.hasFocus():
            if label == 'undo':
                self.editor.undo()
            elif label == 'redo':
                self.editor.redo()
            elif label == 'cut':
                self.editor.cut()
            elif label == 'copy':
                self.editor.copy()
            elif label == 'paste':
                self.editor.paste()
            elif label == 'delete':
                self.editor.delete()
            elif label == 'selectall':
                self.editor.selectAll()
            elif label == 'find':
                self.editor.find(self.findDialog)
            elif label == 'findnext':
                self.editor.findNext(self.findDialog.getFindText())
            elif label == 'findprev':
                self.editor.findPrevious(self.findDialog.getFindText())
            elif label == 'replacenext':
                self.editor.replaceNext(
                    self.findDialog.getFindText(),
                    self.findDialog.getReplaceText())
            elif label == 'indent':
                self.editor.indentLines(True)
            elif label == 'unindent':
                self.editor.indentLines(False)
        elif self.webview.hasFocus():
            if label == 'copy':
                self.webview.triggerPageAction(self.webview.page().Copy)
            elif label == 'selectall':
                self.webview.triggerPageAction(self.webview.page().SelectAll)
            elif label == 'find':
                self.webview.find(self.findDialog)
            elif label == 'findnext':
                self.webview.findNext(self.findDialog.getFindText())
            elif label == 'findprev':
                self.webview.findPrevious(self.findDialog.getFindText())
        return

    def onFileAssociation(self):
        if sys.platform == 'win32':
            reg_base = 'HKEY_CURRENT_USER\Software\Classes'
            settings = QtCore.QSettings(reg_base, QtCore.QSettings.NativeFormat)

            for ext in ['.md', '.markdown', '.rst', '.rest']:
                file_type = 'MarkupEditor%s' % ext
                settings.setValue(
                    '/%s/.' % ext,
                    file_type)
                settings.setValue(
                    '/%s/OpenWithProgIds/%s' % (ext, file_type),
                    '')

                settings.setValue(
                    '/%s/.' % file_type,
                    'Markup Editor for %s' % ext[1:])
                settings.setValue(
                    '/%s/DefaultIcon/.' % file_type,
                    self._icon)
                settings.setValue(
                    '/%s/shell/open/command/.' % file_type,
                    '"%s" "%%1"' % self._app_exec)
            settings.sync()

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
            self.previewCurrentText()
        elif label == 'previewonsave':
            self.settings.setValue('preview/onsave', checked)
        elif label == 'previewoninput':
            self.settings.setValue('preview/oninput', checked)
        elif label == 'previewsync':
            self.settings.setValue('preview/sync', checked)
        elif label == 'enablelexer':
            self.settings.setValue('editor/enableLexer', checked)
            self.editor.enableLexer(checked)
        return

    def onRstThemeChanged(self, label, checked):
        self.rst_theme = label
        self.settings.setValue('rst_theme', self.rst_theme)
        self.previewCurrentText()

    def onMdThemeChanged(self, label, checked):
        self.md_theme = label
        self.settings.setValue('md_theme', self.md_theme)
        self.previewCurrentText()

    def onCodeStyleChanged(self, label, checked):
        if not label:
            return
        self.settings.setValue('pygments', label)
        pygments_rst_path = os.path.join(
            __home_data_path__, 'themes', 'reStructedText',
            'pygments.css')

        pygments_md_path = os.path.join(
            __home_data_path__, 'themes', 'Markdown',
            'pygments.css')
        comment = """
/*
 * +---------------+
 * | pygment style |
 * +---------------+
 */\n"""
        with open(pygments_rst_path, 'wb') as f:
            f.write(toBytes(comment))
            if label != 'null':
                formatter = get_formatter_by_name('html', style=label)
                f.write(toBytes(formatter.get_style_defs('pre.code')))
        with open(pygments_md_path, 'wb') as f:
            f.write(toBytes(comment))
            if label != 'null':
                formatter = get_formatter_by_name('html', style=label)
                f.write(toBytes(formatter.get_style_defs('.codehilite')))
        self.previewCurrentText()

    def onMathJax(self, label):
        if label == 'install':
            dlg = QtWidgets.QProgressDialog(self)
            dlg.setWindowModality(QtCore.Qt.WindowModal)
            dlg.forceShow()
            dlg.setWindowTitle('Wait')
            url = 'https://github.com/mathjax/MathJax/archive/master.zip'
            dest_file = os.path.join(__home_data_path__, 'MathJax.zip')
            dlg.setLabelText('Download MathJax...')
            success = download(url, dest_file, dlg)
            if success:
                dlg.setLabelText('Uncompress MathJax...')
                success = unzip(dest_file, __home_data_path__, dlg)
                self.mathjaxAction.setEnabled(success)

    def onHelp(self):
        help_paths = [
            os.path.join(__home_data_path__, 'docs', 'demo.rst'),
            os.path.join(__data_path__, 'docs', 'demo.rst'),
        ]
        for help_path in help_paths:
            if os.path.exists(help_path):
                break
        if self._app_exec.endswith('.py'):
            subprocess.Popen(['python', self._app_exec, help_path])
        else:
            subprocess.Popen([self._app_exec, help_path])
        return

    def onAbout(self):
        title = self.tr('About %s') % (__app_name__)
        text = self.tr("%s %s\n\nThe editor for Markup Text\n\n"
                       ) % (__app_name__, __app_version__)
        text += self.tr('Platform: %s\n') % (sys.platform)
        text += self.tr('Config path: %s\n') % (__home_data_path__)
        text += self.tr('Application path: %s\n') % (__data_path__)
        text += self.tr('Editor lexer: %s\n') % self.editor.cur_lexer.__module__
        QtWidgets.QMessageBox.about(self, title, text)

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
        else:
            subprocess.Popen(path, shell=True)
        return

    def onValueChanged(self, value):
        if self.settings.value('preview/sync', type=bool):
            dy = self.editor.getVScrollValue()
            editor_vmax = self.editor.getVScrollMaximum()
            if editor_vmax:
                self.webview.scrollRatioPage(dy, editor_vmax)
        return

    def onInputPreview(self):
        if self.settings.value('preview/oninput', type=bool):
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
            default_filename = '%s.rst' % __default_basename__
            self.editor.emptyFile()
            self.setWindowTitle('%s - %s' % (
                __app_name__,
                default_filename)
            )
            self.preview('', default_filename)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def preview(self, text, path):
        if not requestPreview.is_set():
            self.previewText = text
            self.previewPath = path
            requestPreview.set()
        else:
            logger.debug('Preview is working...')
        return

    def previewCurrentText(self):
        text = toUtf8(self.editor.getValue())
        self.preview(text, self.editor.getFileName())

    def previewDisplay(self):
        self.webview.setHtml(self.previewHtml, self.previewPath)
        self.codeview.setValue(self.previewHtml)
        self.codeview.setFileName(self.previewPath + '.html')
        dy = self.editor.getVScrollValue()
        editor_vmax = self.editor.getVScrollMaximum()
        if editor_vmax:
            self.webview.scrollRatioPage(dy, editor_vmax)
        self.editor.setFocus()

    def saveAndContinue(self):
        if self.editor.isModified():
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText(self.tr('The document has been modified.'))
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
                self.onSave()
        return True

    def loadFile(self, path):
        """
        widget load file from command line
        path:
            None, filename will be unknown.rst
            file exist, load file
            not exist, create new file
        """
        default_filename = '%s.rst' % __default_basename__
        if not path:
            path = default_filename
            text = ''
            # self.explorer.setRootPath(os.path.dirname(path))
        else:
            # self.explorer.setRootPath(os.path.dirname(path))
            self.explorer.appendRootPath(path)
            ext = os.path.splitext(path)[1].lower()
            if ext not in ALLOWED_LOADS:
                return
            if os.path.exists(path):
                logger.debug('Loading file: %s', path)
                if self.editor.readFile(path):
                    text = toUtf8(self.editor.getValue())
            else:
                logger.debug('Creating file: %s', path)
                skeleton = os.path.join(__home_data_path__,
                                        'template',
                                        'skeleton%s' % ext)
                if os.path.exists(skeleton):
                    with open(skeleton, 'r', encoding='utf-8') as f:
                        text = f.read()
                else:
                    text = ''
        self.editor.setValue(text)
        self.editor.setFileName(path)
        self.setWindowTitle('%s - %s' % (__app_name__, path))
        self.editor.setFocus()
        self.preview(text, path)


def main():
    globalvars.init()
    parser = argparse.ArgumentParser()
    parser.add_argument('--style', choices=QtWidgets.QStyleFactory.keys())
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % __app_version__)
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=0)
    parser.add_argument('rstfile', nargs='?', help='rest file')
    args = parser.parse_args()

    globalvars.logging_level = logging.WARNING - (args.verbose * 10)
    if globalvars.logging_level <= logging.DEBUG:
        globalvars.logging_level = logging.DEBUG
        formatter = logging.Formatter('[%(module)s %(lineno)d] %(message)s')
    else:
        formatter = logging.Formatter('%(message)s')

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=LOG_FILENAME,
        when='D',
        interval=1,
        backupCount=7,
        utc=False,
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(globalvars.logging_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(globalvars.logging_level)

    app_logger = logging.getLogger(__name__.partition('.')[0])
    app_logger.setLevel(logging.DEBUG)
    app_logger.addHandler(file_handler)
    app_logger.addHandler(console_handler)

    global logger
    logger = logging.getLogger(__name__)

    logger.info('=== rsteditor begin ===')
    logger.debug(args)
    logger.info('Log: %s' % LOG_FILENAME)
    logger.info('app  data path: ' + __data_path__)
    logger.info('home data path: ' + __home_data_path__)
    qt_path = os.path.join(os.path.dirname(QtCore.__file__))
    QtWidgets.QApplication.addLibraryPath(qt_path)
    # qt default
    QtWidgets.QApplication.addLibraryPath(os.path.join(qt_path, 'plugins'))
    # for pyinstaller
    QtWidgets.QApplication.addLibraryPath(os.path.join(qt_path, 'qt5_plugins'))
    QtWidgets.QApplication.addLibraryPath(os.path.join(qt_path, 'PyQt5', 'Qt', 'plugins'))
    rstfile = toUtf8(os.path.realpath(args.rstfile)) if args.rstfile else None
    QtWidgets.QApplication.setStyle(args.style)
    if sys.platform == 'win32':
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    logger.debug('qt plugin path: ' + ', '.join(app.libraryPaths()))
    win = MainWindow()
    win.loadFile(rstfile)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
