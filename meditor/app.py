#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os
import os.path
import sys
import subprocess
import logging
import logging.handlers
import argparse
import threading
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets, QtPrintSupport
from pygments.formatters import get_formatter_by_name

from . import __app_name__, __app_version__, __app_path__, \
    __data_path__, __home_data_path__, __mathjax_full_path__, \
    pygments_styles
from .editor import Editor, CodeViewer
from .tab_editor import TabEditor
from .scilib import EXTENSION_LEXER
from . import webview
from . import explorer
from . import output
from . import globalvars
from .util import toUtf8, toBytes, download, unzip
from .findreplace import FindReplaceDialog


requestPreview = threading.Event()

# for logger
logger = None


def previewWorker(self):
    while True:
        requestPreview.wait()
        if self.previewQuit:
            logger.debug('Preview exit')
            break
        requestPreview.clear()
        logger.debug('Preview %s' % self.previewPath)
        ext = os.path.splitext(self.previewPath)[1].lower()
        if not self.previewText:
            self.previewHtml = ''
        elif ext in ['.rst', '.rest']:
            self.previewHtml = output.rst2htmlcode(self.previewText,
                                                   theme=self.rst_theme)
        elif ext in ['.md', '.markdown']:
            self.previewHtml = output.md2htmlcode(self.previewText,
                                                  theme=self.md_theme)
        elif ext in EXTENSION_LEXER:
            self.previewHtml = output.htmlcode(self.previewText, self.previewPath)
        else:
            self.previewPath = \
                '<html><body><h1>Error</h1><p>Unknown extension: %s</p></body></html>' \
                % ext
        self.previewSignal.emit()
    return


class MainWindow(QtWidgets.QMainWindow):
    rst_theme = 'default'
    md_theme = 'default'
    previewText = ''
    previewHtml = ''
    previewPath = None
    previewQuit = False
    previewSignal = QtCore.pyqtSignal()

    def __init__(self, settings):
        super(MainWindow, self).__init__()
        self.settings = settings
        self._app_exec = os.path.realpath(sys.argv[0])
        if sys.platform == 'win32':
            ext = os.path.splitext(self._app_exec)[1]
            if ext not in ['.py', '.exe']:
                self._app_exec += '.exe'
        logger.info('app name: %s' % self._app_exec)
        self._icon_path = os.path.join(__data_path__, 'meditor-text-editor.ico')

        if sys.platform != 'linux':
            from . import qrc_icon_theme
            QtGui.QIcon.setThemeName('embed_qrc')

        self.setWindowIcon(
            QtGui.QIcon.fromTheme(
                'accessories-text-editor',
                QtGui.QIcon(self._icon_path)
            ))
        self.setAcceptDrops(True)
        # main window
        self.findDialog = FindReplaceDialog(self)

        self.tab_editor = TabEditor(self.settings, self.findDialog, self)
        self.setCentralWidget(self.tab_editor)

        # left dock window
        self.dock_explorer = QtWidgets.QDockWidget(self.tr('Workspace'), self)
        self.dock_explorer.setObjectName('dock_explorer')
        self.explorer = explorer.Workspace(self.settings, self.dock_explorer)
        self.dock_explorer.setWidget(self.explorer)
        self.dock_explorer.visibilityChanged.connect(
            partial(self.onDockVisibility, 'explorer'))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_explorer)
        # right dock window
        self.dock_webview = QtWidgets.QDockWidget(self.tr('Web Preview'), self)
        self.dock_webview.setObjectName('dock_webview')
        self.webview = webview.WebView(
            self.settings, self.findDialog, self.dock_webview)
        self.dock_webview.setWidget(self.webview)
        self.dock_webview.visibilityChanged.connect(
            partial(self.onDockVisibility, 'webview'))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_webview)

        self.dock_codeview = QtWidgets.QDockWidget(self.tr('Code Preview'), self)
        self.dock_codeview.setObjectName('dock_codeview')
        self.codeview = CodeViewer(self.findDialog, self.dock_codeview)
        self.dock_codeview.setWidget(self.codeview)
        self.dock_codeview.visibilityChanged.connect(
            partial(self.onDockVisibility, 'codeview'))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_codeview)

        value = settings.value('view/explorer', True, type=bool)
        settings.setValue('view/explorer', value)
        self.dock_explorer.setVisible(value)

        value = settings.value('view/webview', True, type=bool)
        settings.setValue('view/webview', value)
        self.dock_webview.setVisible(value)

        value = settings.value('view/codeview', True, type=bool)
        settings.setValue('view/codeview', value)
        self.dock_codeview.setVisible(value)
        # event
        self.tab_editor.statusChanged.connect(self.onEditorStatusChange)
        self.tab_editor.verticalScrollBarChanged.connect(self.onEditorVScrollBarChanged)
        self.tab_editor.previewRequest.connect(self.onEditorPreviewRequest)
        self.tab_editor.modificationChanged.connect(self.onEditorModified)
        self.tab_editor.filenameChanged.connect(self.onFileRenamed)
        self.tab_editor.fileLoaded.connect(self.onEditorFileLoaded)

        self.webview.exportHtml.connect(partial(self.onMenuExport, 'html'))

        self.explorer.fileLoaded.connect(self.onExplorerFileLoaded)
        self.explorer.fileNew.connect(self.onExplorerNew)
        self.explorer.fileDeleted.connect(self.onExplorerFileDeleted)
        self.explorer.fileRenamed.connect(self.onFileRenamed)

        # setup main frame
        self.setupMenu()
        self.setupToolbar()
        self.setupStatusBar()

        # restore window state
        self.restoreGeometry(settings.value('geometry', type=QtCore.QByteArray))
        self.restoreState(settings.value('windowState', type=QtCore.QByteArray))

        self.previewSignal.connect(self.onUpdatePreviewView)
        self.previewWorker = threading.Thread(target=previewWorker, args=(self,))
        logger.debug(' Preview worker start '.center(80, '-'))
        self.previewWorker.start()
        self.tab_editor.loadFile(self.tab_editor.filepath())
        self.previewCurrentText(force=True)

    def setupMenu(self):
        settings = self.settings
        # action
        # file
        newwindowAction = QtWidgets.QAction(self.tr('New &window'), self)
        newwindowAction.triggered.connect(self.onMenuNewWindow)
        newwindowAction.setIcon(QtGui.QIcon.fromTheme('window-new'))

        printAction = QtWidgets.QAction(self.tr('&Print'), self)
        printAction.setShortcut(QtGui.QKeySequence.Print)
        printAction.triggered.connect(self.onMenuPrint)
        printAction.setIcon(QtGui.QIcon.fromTheme('document-print'))

        printPreviewAction = QtWidgets.QAction(self.tr('Print Preview'), self)
        printPreviewAction.triggered.connect(self.onMenuPrintPreview)
        printPreviewAction.setIcon(QtGui.QIcon.fromTheme('document-print-preview'))

        fileAssociationAction = QtWidgets.QAction(self.tr('File associate'), self)
        fileAssociationAction.triggered.connect(self.onMenuFileAssociation)
        fileAssociationAction.setEnabled(sys.platform == 'win32')

        exitAction = QtWidgets.QAction(self.tr('&Exit'), self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setShortcut(QtGui.QKeySequence.Quit)
        exitAction.setIcon(QtGui.QIcon.fromTheme('application-exit'))
        exitAction.triggered.connect(self.close)
        # edit
        # view
        # preview
        self.previewAction = QtWidgets.QAction(self.tr('Preview'), self, checkable=True)
        self.previewAction.triggered.connect(partial(self.onMenuPreview, 'preview'))
        self.previewAction.setChecked(
            settings.value('view/webview', True, type=bool) or
            settings.value('view/codeview', True, type=bool))

        previewsaveAction = QtWidgets.QAction(
            self.tr('Preview on save'), self, checkable=True)
        previewsaveAction.triggered.connect(
            partial(self.onMenuPreview, 'previewonsave'))
        value = settings.value('preview/onsave', True, type=bool)
        settings.setValue('preview/onsave', value)
        previewsaveAction.setChecked(value)

        previewinputAction = QtWidgets.QAction(
            self.tr('Preview on input'), self, checkable=True)
        previewinputAction.triggered.connect(
            partial(self.onMenuPreview, 'previewoninput'))
        value = settings.value('preview/oninput', True, type=bool)
        settings.setValue('preview/oninput', value)
        previewinputAction.setChecked(value)

        previewsyncAction = QtWidgets.QAction(
            self.tr('Scroll synchronize'), self, checkable=True)
        previewsyncAction.triggered.connect(
            partial(self.onMenuPreview, 'previewsync'))
        value = settings.value('preview/sync', True, type=bool)
        settings.setValue('preview/sync', value)
        previewsyncAction.setChecked(value)
        # theme
        # docutils theme
        default_cssAction = QtWidgets.QAction(
            'Default theme', self, checkable=True)
        default_cssAction.triggered.connect(
            partial(self.onMenuRstThemeChanged, 'default'))

        rstThemeGroup = QtWidgets.QActionGroup(self)
        rstThemeGroup.setExclusive(True)
        rstThemeGroup.addAction(default_cssAction)
        for theme in output.get_rst_themes().keys():
            act = QtWidgets.QAction('%s theme' % theme, self, checkable=True)
            act.triggered.connect(partial(self.onMenuRstThemeChanged, theme))
            rstThemeGroup.addAction(act)

        value = settings.value('rst_theme', 'default', type=str)
        settings.setValue('rst_theme', value)
        self.rst_theme = value

        default_cssAction.setChecked(True)
        theme_name = '%s theme' % value
        for act in rstThemeGroup.actions():
            theme = act.text()
            if theme_name == theme:
                act.setChecked(True)
                break
        # markdown theme
        default_cssAction = QtWidgets.QAction(
            'Default theme', self, checkable=True)
        default_cssAction.triggered.connect(
            partial(self.onMenuMdThemeChanged, 'default'))

        mdThemeGroup = QtWidgets.QActionGroup(self)
        mdThemeGroup.setExclusive(True)
        mdThemeGroup.addAction(default_cssAction)
        for theme in output.get_md_themes().keys():
            act = QtWidgets.QAction('%s theme' % theme, self, checkable=True)
            act.triggered.connect(partial(self.onMenuMdThemeChanged, theme))
            mdThemeGroup.addAction(act)

        value = settings.value('md_theme', 'default', type=str)
        settings.setValue('md_theme', value)
        self.md_theme = value

        default_cssAction.setChecked(True)
        theme_name = '%s theme' % toUtf8(value)
        for act in mdThemeGroup.actions():
            theme = act.text()
            if theme_name == theme:
                act.setChecked(True)
                break
        # code style
        self.codeStyleGroup = QtWidgets.QActionGroup(self)
        self.codeStyleGroup.setExclusive(True)
        for k, v in pygments_styles.items():
                act = QtWidgets.QAction(v, self, checkable=True)
                act.triggered.connect(partial(self.onMenuCodeStyleChanged, k))
                self.codeStyleGroup.addAction(act)

        value = settings.value('pygments', 'null', type=str)
        settings.setValue('pygments', value)
        for act in self.codeStyleGroup.actions():
            pygments_desc = toUtf8(act.text())
            if pygments_desc == pygments_styles.get(value, ''):
                act.setChecked(True)
                break

        self.mathjaxAction = QtWidgets.QAction(self.tr('Install MathJax'), self)
        self.mathjaxAction.triggered.connect(partial(self.onMenuMathJax, 'install'))
        self.mathjaxAction.setEnabled(not os.path.exists(__mathjax_full_path__))

        # settings
        self.highDpiAction = QtWidgets.QAction(
            self.tr('&High DPI support'), self, checkable=True)
        self.highDpiAction.triggered.connect(
            partial(self.onMenuSettings, 'high_dpi'))
        value = settings.value('highdpi', type=bool)
        self.highDpiAction.setChecked(value)

        # help
        helpAction = QtWidgets.QAction(self.tr('&Help Documents'), self)
        helpAction.setShortcut(QtGui.QKeySequence.HelpContents)
        helpAction.setIcon(QtGui.QIcon.fromTheme('help-contents'))
        helpAction.triggered.connect(self.onMenuHelp)

        aboutAction = QtWidgets.QAction(self.tr('&About'), self)
        aboutAction.setIcon(QtGui.QIcon.fromTheme('help-about'))
        aboutAction.triggered.connect(self.onMenuAbout)

        aboutqtAction = QtWidgets.QAction(self.tr('About &Qt'), self)
        aboutqtAction.triggered.connect(QtWidgets.qApp.aboutQt)

        # menu
        menubar = self.menuBar()
        menu = menubar.addMenu(self.tr('&File'))
        submenu = menu.addMenu(self.tr('&New'))
        submenu.addAction(self.explorer.action('new_rst'))
        submenu.addAction(self.explorer.action('new_md'))
        menu.addMenu(submenu)
        menu.addAction(newwindowAction)
        menu.addAction(self.tab_editor.action('open'))
        menu.addAction(self.explorer.action('open_workspace'))

        menu.addSeparator()
        menu.addAction(self.tab_editor.action('save'))
        menu.addAction(self.tab_editor.action('save_as'))
        menu.addAction(self.tab_editor.action('close_all'))

        menu.addSeparator()
        self.webview.menuExport(menu)
        menu.aboutToShow.connect(self.webview.menuAboutToShow)

        menu.addSeparator()
        menu.addAction(printPreviewAction)
        menu.addAction(printAction)

        menu.addSeparator()
        menu.addAction(exitAction)

        menu = menubar.addMenu(self.tr('&Edit'))
        self.tab_editor.menuEdit(menu)
        menu.aboutToShow.connect(self.tab_editor.menuAboutToShow)

        menu = menubar.addMenu(self.tr('&View'))
        menu.addAction(self.dock_explorer.toggleViewAction())
        menu.addAction(self.dock_webview.toggleViewAction())
        menu.addAction(self.dock_codeview.toggleViewAction())

        menu = menubar.addMenu(self.tr('&Theme'))
        submenu = QtWidgets.QMenu(self.tr('reStructuredText'), menu)
        for act in rstThemeGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)

        submenu = QtWidgets.QMenu(self.tr('Markdown'), menu)
        for act in mdThemeGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)

        menu.addSeparator()
        submenu = QtWidgets.QMenu(self.tr('Pygments'), menu)
        for act in self.codeStyleGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)

        menu.addSeparator()
        menu.addAction(self.mathjaxAction)

        menu = menubar.addMenu(self.tr('&Settings'))
        menu.addAction(self.highDpiAction)

        menu.addSeparator()
        menu.addAction(previewsaveAction)
        menu.addAction(previewinputAction)
        menu.addAction(previewsyncAction)

        menu.addSeparator()
        self.tab_editor.menuSetting(menu)

        menu.addSeparator()
        menu.addAction(fileAssociationAction)

        menu = menubar.addMenu(self.tr('&Help'))
        menu.addAction(helpAction)

        menu.addSeparator()
        menu.addAction(aboutAction)
        menu.addAction(aboutqtAction)

    def setupToolbar(self):
        tb_normal = QtWidgets.QToolBar('normal')
        tb_normal.setObjectName('normal')

        newButton = QtWidgets.QToolButton(self)
        menu = QtWidgets.QMenu(self.tr('New'), self)
        menu.addAction(self.explorer.action('new_rst'))
        menu.addAction(self.explorer.action('new_md'))
        newButton.setMenu(menu)
        newButton.setPopupMode(newButton.MenuButtonPopup)
        newButton.setDefaultAction(self.explorer.action('new_rst'))
        tb_normal.addWidget(newButton)

        tb_normal.addAction(self.tab_editor.action('open'))
        tb_normal.addAction(self.explorer.action('open_workspace'))
        tb_normal.addAction(self.tab_editor.action('save'))
        tb_normal.addSeparator()
        tb_normal.addAction(self.tab_editor.action('undo'))
        tb_normal.addAction(self.tab_editor.action('redo'))
        tb_normal.addSeparator()
        tb_normal.addAction(self.tab_editor.action('cut'))
        tb_normal.addAction(self.tab_editor.action('copy'))
        tb_normal.addAction(self.tab_editor.action('paste'))
        tb_normal.addSeparator()
        tb_normal.addAction(self.tab_editor.action('find'))
        tb_normal.addAction(self.tab_editor.action('format_table'))
        tb_normal.addSeparator()
        tb_normal.addAction(self.tab_editor.action('zoom_in'))
        tb_normal.addAction(self.tab_editor.action('zoom_out'))
        tb_normal.addAction(self.tab_editor.action('zoom_original'))
        tb_normal.addSeparator()
        tb_normal.addAction(self.previewAction)
        self.addToolBar(tb_normal)

    def setupStatusBar(self):
        # status bar
        self.statusCursor = QtWidgets.QLabel('Cursor', self)
        self.statusBar().addPermanentWidget(self.statusCursor)

        self.statusEncoding = QtWidgets.QLabel('ASCII', self)
        self.statusBar().addPermanentWidget(self.statusEncoding)

        self.statusEol = QtWidgets.QLabel('EOL', self)
        self.statusBar().addPermanentWidget(self.statusEol)

        self.statusLexer = QtWidgets.QLabel('Lexer', self)
        self.statusBar().addPermanentWidget(self.statusLexer)

        self.showMessage(self.tr('Ready'))

    def showMessage(self, message):
        self.statusBar().showMessage(message, 5000)

    def closeEvent(self, event):
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        self.settings.setValue('view/explorer', self.dock_explorer.isVisible())
        self.settings.setValue('view/webview', self.dock_webview.isVisible())
        self.settings.setValue('view/codeview', self.dock_codeview.isVisible())

        if not self.tab_editor.close():
            event.ignore()
            return
        self.explorer.close()
        self.webview.close()
        self.codeview.close()
        self.findDialog.done(0)

        self.settings.sync()

        self.previewQuit = True
        requestPreview.set()
        self.previewWorker.join()
        logger.info(' rsteditor end '.center(80, '='))
        event.accept()

    def dragEnterEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            for url in mimedata.urls():
                if not url.isLocalFile():
                    return
                if not Editor.canOpened(os.path.abspath(url.toLocalFile())):
                    return
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasUrls():
            for url in mimedata.urls():
                if not url.isLocalFile():
                    return
                if not Editor.canOpened(os.path.abspath(url.toLocalFile())):
                    return
            event.acceptProposedAction()

    def dropEvent(self, event):
        mimedata = event.mimeData()
        for url in mimedata.urls():
            self.tab_editor.loadFile(os.path.abspath(url.toLocalFile()))

    def onEditorStatusChange(self, index, status):
        for item in status.split(';'):
            key, value = item.split(':')
            length = max(len(value) + 2, 8)
            if key == 'lexer':
                self.statusLexer.setText(value.center(length, ' '))
            elif key == 'encoding':
                self.statusEncoding.setText(value.center(length, ' '))
            elif key == 'eol':
                self.statusEol.setText(value.center(length, ' '))
            elif key == 'cursor':
                self.statusCursor.setText(value.center(length, ' '))

    def onMenuNewWindow(self):
        if sys.platform == 'win32' and self._app_exec.endswith('.py'):
            subprocess.Popen(['python', self._app_exec])
        else:
            subprocess.Popen([self._app_exec])
        return

    def onMenuExport(self, label):
        if label == 'html':
            in_filepath = self.tab_editor.filepath()
            in_basename, in_ext = os.path.splitext(os.path.basename(in_filepath))
            out_file = in_basename + '.html'
            out_html = QtWidgets.QFileDialog.getSaveFileName(
                self, self.tr('export HTML as ...'),
                os.path.join(self.explorer.getCurrentPath(), out_file),
                "HTML files (*.html *.htm)",
            )
            if isinstance(out_html, tuple):
                out_html = out_html[0]
            if out_html:
                out_html = out_html
                basename, out_ext = os.path.splitext(out_html)
                if out_ext.lower() not in ['.html', '.htm']:
                    out_html += '.html'
                if in_ext.lower() in ['.rst', '.rest']:
                    output.rst2html(in_filepath,
                                    out_html,
                                    theme=self.rst_theme)
                elif in_ext.lower() in ['.md', '.markdown']:
                    output.md2html(in_filepath,
                                out_html,
                                theme=self.md_theme)

    def onMenuPrintPreview(self):
        if self.codeview.hasFocus():
            printer = self.codeview.getPrinter(
                QtPrintSupport.QPrinter.ScreenResolution)
            widget = self.codeview
        elif self.webview.hasFocus():
            printer = QtPrintSupport.QPrinter(
                QtPrintSupport.QPrinter.ScreenResolution)
            widget = self.webview
        else:
            widget = self.tab_editor.currentWidget()
            printer = widget.getPrinter(
                QtPrintSupport.QPrinter.ScreenResolution)
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        printer.setPageOrientation(QtGui.QPageLayout.Portrait)
        printer.setPageMargins(15, 15, 15, 15, QtPrintSupport.QPrinter.Millimeter)
        preview = QtPrintSupport.QPrintPreviewDialog(printer, widget)
        preview.paintRequested.connect(widget.print_)
        preview.exec_()

    def onMenuPrint(self):
        if self.codeview.hasFocus():
            printer = self.codeview.getPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.codeview
        elif self.webview.hasFocus():
            printer = QtPrintSupport.QPrinter(
                QtPrintSupport.QPrinter.HighResolution)
            widget = self.webview
        else:
            widget = self.tab_editor.currentWidget()
            printer = widget.getPrinter(
                QtPrintSupport.QPrinter.HighResolution)
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        printer.setPageMargins(15, 15, 15, 15, QtPrintSupport.QPrinter.Millimeter)
        printDialog = QtPrintSupport.QPrintDialog(printer, widget)
        if printDialog.exec_() == QtWidgets.QDialog.Accepted:
            widget.print_(printer)

    def onMenuFileAssociation(self):
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
                self._icon_path)
            settings.setValue(
                '/%s/shell/open/command/.' % file_type,
                '"%s" "%%1"' % self._app_exec)
        settings.sync()
        # Notify system that change a file association.
        from ctypes import windll
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0
        windll.shell32.SHChangeNotify(
            SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)

    def onDockVisibility(self, dock, value):
        if value and dock == 'webview':
            self.webview.setFocus(QtCore.Qt.TabFocusReason)
        elif value and dock == 'codeview':
            self.codeview.setFocus(QtCore.Qt.TabFocusReason)
        if value:
            self.previewCurrentText()

    def onMenuPreview(self, label, checked):
        if label == 'preview':
            if checked:
                self.dock_webview.setVisible(True)
            else:
                self.dock_webview.setVisible(False)
                self.dock_codeview.setVisible(False)
        elif label == 'previewonsave':
            self.settings.setValue('preview/onsave', checked)
        elif label == 'previewoninput':
            self.settings.setValue('preview/oninput', checked)
        elif label == 'previewsync':
            self.settings.setValue('preview/sync', checked)

    def onMenuRstThemeChanged(self, label, checked):
        self.rst_theme = label
        self.settings.setValue('rst_theme', self.rst_theme)
        self.showMessage(self.tr('reStructuredText theme: %s' % label))
        self.previewCurrentText()

    def onMenuMdThemeChanged(self, label, checked):
        self.md_theme = label
        self.settings.setValue('md_theme', self.md_theme)
        self.showMessage(self.tr('Markdown theme: %s' % label))
        self.previewCurrentText()

    def onMenuCodeStyleChanged(self, label, checked):
        if not label:
            return
        self.settings.setValue('pygments', label)
        pygments_rst_path = os.path.join(
            __home_data_path__, 'themes', 'reStructuredText',
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
        self.showMessage(
            self.tr('pygments change: %s' % label))

    def onMenuMathJax(self, label):
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
                self.mathjaxAction.setEnabled(False)
                os.remove(dest_file)

    def onMenuSettings(self, action, value):
        if action == 'high_dpi':
            self.settings.setValue('highdpi', value)
            msgBox = QtWidgets.QMessageBox(self)
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setWindowTitle(self.tr('High DPI'))
            if value:
                message = self.tr('High DPI has been enabled.')
            else:
                message = self.tr('High DPI has been disabled.')
            msgBox.setText(message)
            msgBox.setInformativeText(self.tr('Restart it now?'))
            msgBox.setStandardButtons(
                QtWidgets.QMessageBox.Ok |
                QtWidgets.QMessageBox.Cancel
            )
            msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            ret = msgBox.exec_()
            if ret == QtWidgets.QMessageBox.Ok:
                self.close()

    def onMenuHelp(self):
        help_paths = [
            os.path.join(__home_data_path__, 'help', 'demo.rst'),
            os.path.join(__data_path__, 'help', 'demo.rst'),
        ]
        for help_path in help_paths:
            if os.path.exists(help_path):
                break
        self.explorer.appendRootPath(help_path, expand=True)
        self.tab_editor.loadFile(help_path)

    def onMenuAbout(self):
        title = self.tr('About %s') % (__app_name__)
        text = self.tr("%s %s\n\nThe editor for Markup Text\n\n"
                       ) % (__app_name__, __app_version__)
        text += self.tr('Platform: %s\n') % (sys.platform)
        text += self.tr('Home data path: %s\n') % (__home_data_path__)
        text += self.tr('Application data path: %s\n') % (__data_path__)
        widget = self.tab_editor.currentWidget()
        if widget.lexer():
            text += self.tr('Editor lexer: %s\n') % widget.lexer().__module__
        text += self.tr('\n')
        text += self.tr('QScintilla: %s\n') % widget.getScintillaVersion()
        QtWidgets.QMessageBox.about(self, title, text)

    def onExplorerNew(self, ext):
        index = self.tab_editor.new(ext)
        self.showMessage(self.tr('new "%s"' % self.tab_editor.filepath(index)))

    def onExplorerFileLoaded(self, path):
        if not os.path.exists(path):
            return
        index = self.tab_editor.loadFile(path)
        if index is None:
            self.showMessage(self.tr('load "%s"' % path))
            subprocess.Popen(path, shell=True)

    def onExplorerFileDeleted(self, path):
        for x in range(self.tab_editor.count()):
            editor = self.tab_editor.widget(x)
            if path == editor.getFileName():
                self.showMessage(self.tr('delete "%s"' % path))
                self.tab_editor.removeTab(x)
                del editor
                break
        if self.tab_editor.count() == 0:
            self.tab_editor.new('.rst')

    def onEditorFileLoaded(self, index):
        self.updateWindowTitle(index)
        self.showMessage(self.tr('load "%s"' % self.tab_editor.filepath(index)))

    def onEditorVScrollBarChanged(self, value):
        if self.settings.value('preview/sync', type=bool):
            widget = self.tab_editor.currentWidget()
            dy = widget.getVScrollValue()
            editor_vmax = widget.getVScrollMaximum()
            if editor_vmax:
                self.webview.scrollRatioPage(dy, editor_vmax)

    def onEditorModified(self, index, value):
        self.updateWindowTitle(index)
        self.showMessage(self.tr('modified "%s"' % self.tab_editor.filepath(index)))

    def onEditorPreviewRequest(self, index, source):
        if source == 'input' and not self.settings.value('preview/oninput', type=bool):
            return
        if source == 'save' and not self.settings.value('preview/onsave', type=bool):
            return
        self.do_preview(index)

    def onFileRenamed(self, old_name, new_name):
        self.showMessage(
            self.tr('rename "%s" => "%s"' % (old_name, new_name)))
        if self.sender() == self.explorer:
            self.tab_editor.rename(old_name, new_name)
        elif self.sender() == self.tab_editor:
            self.explorer.refreshPath(old_name)
            self.explorer.refreshPath(new_name)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def do_preview(self, index, force=False):
        if requestPreview.is_set():
            logger.debug('Preview is working..., ignore')
        elif force or self.dock_codeview.isVisible() or self.dock_webview.isVisible():
            widget = self.tab_editor.widget(index)
            self.previewPath = widget.getFileName()
            self.previewText = widget.text()
            requestPreview.set()

    def previewCurrentText(self, force=False):
        self.do_preview(self.tab_editor.currentIndex(), force=force)

    def onUpdatePreviewView(self):
        if self.dock_webview.isVisible():
            self.webview.setHtml(self.previewHtml, self.previewPath)
        if self.dock_codeview.isVisible():
            self.codeview.setValue(self.previewHtml)
            self.codeview.setFileName(self.previewPath + '.html')
        widget = self.tab_editor.currentWidget()
        dy = widget.getVScrollValue()
        editor_vmax = widget.getVScrollMaximum()
        if editor_vmax:
            self.webview.scrollRatioPage(dy, editor_vmax)
        widget.setFocus()

    def updateWindowTitle(self, index):
        title = __app_name__ + ' - ' + self.tab_editor.title(index, full=True)
        self.setWindowTitle(title)


def main():
    globalvars.init()
    parser = argparse.ArgumentParser()
    parser.add_argument('--style', choices=list(QtWidgets.QStyleFactory.keys()))
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % __app_version__)
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=0)
    parser.add_argument('--log-file', help='output to log file')
    parser.add_argument('rstfile', nargs='?', help='rest file')
    args = parser.parse_args()

    globalvars.logging_level = logging.WARNING - (args.verbose * 10)
    if globalvars.logging_level <= logging.DEBUG:
        globalvars.logging_level = logging.DEBUG
        formatter = logging.Formatter('[%(module)s %(lineno)d] %(message)s')
    else:
        formatter = logging.Formatter('%(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(globalvars.logging_level)

    app_logger = logging.getLogger(__name__.partition('.')[0])
    app_logger.setLevel(logging.DEBUG)
    app_logger.addHandler(console_handler)

    if args.log_file:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=args.log_file,
            when='D',
            interval=1,
            backupCount=7,
            utc=False,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(globalvars.logging_level)
        app_logger.addHandler(file_handler)

    global logger
    logger = logging.getLogger(__name__)

    logger.info('=== %s v%s begin ===' % (__app_name__, __app_version__))
    logger.debug(args)
    logger.info('app  data path: ' + __data_path__)
    logger.info('home data path: ' + __home_data_path__)

    qt_path = os.path.join(os.path.dirname(QtCore.__file__))
    QtWidgets.QApplication.addLibraryPath(qt_path)
    # for pyinstaller
    QtWidgets.QApplication.addLibraryPath(os.path.join(qt_path, 'PyQt5'))

    settings = QtCore.QSettings(__app_path__, 'config')
    value = settings.value('highdpi', False, type=bool)
    settings.setValue('highdpi', value)
    if value:
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setStyle(args.style)
    app = QtWidgets.QApplication(sys.argv)
    logger.info('app scale factor: %s' % app.devicePixelRatio())
    logger.debug('qt plugin path: ' + ', '.join(app.libraryPaths()))
    win = MainWindow(settings)
    if args.rstfile:
        win.tab_editor.loadFile(os.path.abspath(args.rstfile))
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
