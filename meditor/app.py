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
import platform
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets, QtPrintSupport
from pygments.formatters import get_formatter_by_name

from . import __app_name__, __app_version__, __app_path__, \
    __data_path__, __home_data_path__, \
    __mathjax_full_path__, __mathjax_min_path__, \
    pygments_styles
from .editor import Editor, CodeViewer
from .tab_editor import TabEditor
from .vim import VimEmulator
from .scilib import EXTENSION_LEXER
from . import webview
from . import workspace
from . import output
from . import globalvars
from .util import toUtf8, toBytes, download, unzip
from .findreplace import FindReplaceDialog
from .gaction import GlobalAction
from . import qrc_icon_theme


previewEvent = threading.Event()

# for logger
logger = None


def previewWorker(self):
    while True:
        previewEvent.wait()
        if self.previewQuit:
            logger.debug('Preview exit')
            break
        previewEvent.clear()
        previewText = self.previewData['text']
        previewPath = self.previewData['path']
        logger.debug('Preview %s' % previewPath)
        ext = os.path.splitext(previewPath)[1].lower()
        settings = {}
        if not previewText:
            self.previewHtml = ''
        elif ext in ['.rst', '.rest']:
            if self.previewData['mathjax']:
                if os.path.exists(__mathjax_full_path__):
                    settings['mathjax'] = __mathjax_full_path__
            self.previewHtml = output.rst2htmlcode(previewText,
                                                   theme=self.rst_theme,
                                                   settings=settings)
        elif ext in ['.md', '.markdown']:
            if self.previewData['mathjax']:
                if os.path.exists(__mathjax_full_path__):
                    mathjax_path = __mathjax_full_path__ + '?config=TeX-MML-AM_CHTML'
                else:
                    mathjax_path = __mathjax_min_path__
                mathjax = """<script type="text/javascript" src="file:///%s"></script>""" % mathjax_path
                settings['mathjax'] = mathjax
            self.previewHtml = output.md2htmlcode(previewText,
                                                  theme=self.md_theme,
                                                  settings=settings)
        elif ext in ['.htm', '.html', '.php', '.asp']:
            self.previewHtml = previewText
        elif ext in EXTENSION_LEXER:
            self.previewHtml = output.htmlcode(previewText, previewPath)
        else:
            previewPath = \
                '<html><body><h1>Error</h1><p>Unknown extension: %s</p></body></html>' \
                % ext
        self.updatePreviewViewRequest.emit()
    return


class MainWindow(QtWidgets.QMainWindow):
    rst_theme = 'default'
    md_theme = 'default'
    icon_theme = None
    previewData = None
    previewHtml = ''
    previewQuit = False
    updatePreviewViewRequest = QtCore.pyqtSignal()
    previewViewVisibleNotify = QtCore.pyqtSignal(bool)
    _toolbar = None

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

        if sys.platform == 'linux':
            value = settings.value('embed_icon', False, type=bool)
        else:
            value = settings.value('embed_icon', True, type=bool)
        settings.setValue('embed_icon', value)
        # Reference: QIcon::themeSearchPaths()
        # The default value will depend on the platform:
        # On X11, the search path will use the XDG_DATA_DIRS environment variable if available.
        # By default all platforms will have the resource directory :\icons as a fallback.
        if value:
            qrc_icon_theme.qInitResources()
            icon_index = QtCore.QSettings(':/icons/embed_qrc/index.theme', QtCore.QSettings.IniFormat)
            icon_theme = icon_index.value('Icon Theme/Name', 'default', type=str)
            del icon_index
            QtGui.QIcon.setThemeName('embed_qrc')
            self.icon_theme = 'Embed[%s]' % icon_theme
        else:
            self.icon_theme = 'System'
        logger.info('Icon theme name: %s' % self.icon_theme)

        self.setWindowIcon(
            QtGui.QIcon.fromTheme(
                'accessories-text-editor',
                QtGui.QIcon(self._icon_path)
            ))
        self.setAcceptDrops(True)
        self.previewData = {
            'text': '',
            'path': '',
            'mathjax': False,
        }
        # main window
        self.findDialog = FindReplaceDialog(self)

        widget = QtWidgets.QWidget(self)

        self.vim = VimEmulator(widget)
        self.tab_editor = TabEditor(self.settings, self.findDialog, widget)
        value = settings.value('vim_mode', False, type=bool)
        self.tab_editor.setVimEmulator(self.vim if value else None)
        self.vim.setVisible(value)

        v_layout = QtWidgets.QVBoxLayout(widget)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(self.tab_editor)
        v_layout.addWidget(self.vim)
        self.setCentralWidget(widget)

        # left dock window
        self.dock_workspace = QtWidgets.QDockWidget(self.tr('Workspace'), self)
        self.dock_workspace.setObjectName('dock_workspace')
        self.workspace = workspace.Workspace(self.settings, self.dock_workspace)
        self.dock_workspace.setWidget(self.workspace)
        self.dock_workspace.visibilityChanged.connect(
            partial(self.onDockVisibility, 'workspace'))
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dock_workspace)
        # right dock window
        self.dock_webview = QtWidgets.QDockWidget(self.tr('Preview'), self)
        self.dock_webview.setObjectName('dock_webview')
        self.webview = webview.WebView(
            self.settings, self.findDialog, self.dock_webview)
        self.dock_webview.setWidget(self.webview)
        self.dock_webview.visibilityChanged.connect(
            partial(self.onDockVisibility, 'webview'))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_webview)

        self.dock_codeview = QtWidgets.QDockWidget(self.tr('HTML Code'), self)
        self.dock_codeview.setObjectName('dock_codeview')
        self.codeview = CodeViewer(self.settings, self.findDialog, self.dock_codeview)
        self.dock_codeview.setWidget(self.codeview)
        self.dock_codeview.visibilityChanged.connect(
            partial(self.onDockVisibility, 'codeview'))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_codeview)

        value = settings.value('view/workspace', True, type=bool)
        settings.setValue('view/workspace', value)
        self.dock_workspace.setVisible(value)

        value = settings.value('view/webview', True, type=bool)
        settings.setValue('view/webview', value)
        self.dock_webview.setVisible(value)

        value = settings.value('view/codeview', True, type=bool)
        settings.setValue('view/codeview', value)
        self.dock_codeview.setVisible(value)
        # event
        self.tab_editor.statusChanged.connect(self.onEditorStatusChange)
        self.tab_editor.showMessageRequest.connect(self.showMessage)
        self.tab_editor.verticalScrollBarChanged.connect(self.onEditorVScrollBarChanged)
        self.tab_editor.previewRequest.connect(self.onEditorPreviewRequest)
        self.tab_editor.modificationChanged.connect(self.onEditorModified)
        self.tab_editor.filenameChanged.connect(self.onFileRenamed)
        self.tab_editor.fileLoaded.connect(self.onEditorFileLoaded)

        self.webview.exportHtml.connect(partial(self.onMenuExport, 'html'))

        self.workspace.showMessageRequest.connect(self.showMessage)
        self.workspace.fileLoaded.connect(self.onWorkspaceFileLoaded)
        self.workspace.fileNew.connect(self.onWorkspaceNew)
        self.workspace.fileDeleted.connect(self.onWorkspaceFileDeleted)
        self.workspace.fileRenamed.connect(self.onFileRenamed)

        # setup main frame
        self._toolbar = QtWidgets.QToolBar('ToolBar')
        self._toolbar.setObjectName('ToolBar')

        self.setupMenu()
        self.setupToolbar(self._toolbar)
        self.setupStatusBar()

        # restore window state
        self.restoreGeometry(settings.value('geometry', type=QtCore.QByteArray))
        self.restoreState(settings.value('windowState', type=QtCore.QByteArray))

        self.updatePreviewViewRequest.connect(self.onUpdatePreviewView)
        self.previewWorker = threading.Thread(target=previewWorker, args=(self,))
        logger.debug(' Preview worker start '.center(80, '-'))
        self.previewWorker.start()
        self.tab_editor.do_switch_editor(0)
        self.previewCurrentText(force=True)

    def setupMenu(self):
        settings = self.settings
        # action
        g_action = GlobalAction()
        # file
        action = QtWidgets.QAction(self.tr('New &window'), self)
        action.triggered.connect(self.onMenuNewWindow)
        cmd = g_action.register('mainwindow.new_window', action)
        cmd.setText(action.text())
        cmd.setIcon(QtGui.QIcon.fromTheme('window-new'))

        action = QtWidgets.QAction(self.tr('&Print'), self)
        action.triggered.connect(self.onMenuPrint)
        cmd = g_action.register('mainwindow.print', action)
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.Print)
        cmd.setIcon(QtGui.QIcon.fromTheme('document-print'))

        action = QtWidgets.QAction(self.tr('Print Preview'), self)
        action.triggered.connect(self.onMenuPrintPreview)
        cmd = g_action.register('mainwindow.print_preview', action)
        cmd.setText(action.text())
        cmd.setIcon(QtGui.QIcon.fromTheme('document-print-preview'))

        action = QtWidgets.QAction(self.tr('File associate'), self)
        action.triggered.connect(self.onMenuFileAssociation)
        cmd = g_action.register('mainwindow.file_associate', action)
        cmd.setText(action.text())
        cmd.setEnabled(sys.platform == 'win32')

        action = QtWidgets.QAction(self.tr('&Quit'), self)
        action.triggered.connect(self.close)
        cmd = g_action.register('mainwindow.quit', action)
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.Quit)
        cmd.setIcon(QtGui.QIcon.fromTheme('application-exit'))
        # edit
        # view
        # preview
        action = QtWidgets.QAction(
            self.tr('Preview on save'), self, checkable=True)
        action.triggered.connect(
            partial(self.onMenuPreview, 'preview_onsave'))
        value = settings.value('preview/onsave', True, type=bool)
        settings.setValue('preview/onsave', value)
        cmd = g_action.register('mainwindow.preview_onsave', action)
        cmd.setText(action.text())
        cmd.setCheckable(True)
        action.setChecked(value)
        cmd.setChecked(value)

        action = QtWidgets.QAction(
            self.tr('Preview on input'), self, checkable=True)
        action.triggered.connect(
            partial(self.onMenuPreview, 'preview_oninput'))
        value = settings.value('preview/oninput', True, type=bool)
        settings.setValue('preview/oninput', value)
        cmd = g_action.register('mainwindow.preview_oninput', action)
        cmd.setText(action.text())
        cmd.setCheckable(True)
        action.setChecked(value)
        cmd.setChecked(value)

        action = QtWidgets.QAction(
            self.tr('Scroll synchronize'), self, checkable=True)
        action.triggered.connect(
            partial(self.onMenuPreview, 'preview_sync'))
        value = settings.value('preview/sync', True, type=bool)
        settings.setValue('preview/sync', value)
        cmd = g_action.register('mainwindow.preview_sync', action)
        cmd.setText(action.text())
        cmd.setCheckable(True)
        action.setChecked(value)
        cmd.setChecked(value)

        action = QtWidgets.QAction(
            self.tr('Preview with MathJax'), self, checkable=True)
        action.triggered.connect(
            partial(self.onMenuPreview, 'preview_mathjax'))
        value = settings.value('preview/mathjax', False, type=bool)
        settings.setValue('preview/mathjax', value)
        cmd = g_action.register('mainwindow.preview_mathjax', action)
        cmd.setText(action.text())
        cmd.setCheckable(True)
        action.setChecked(value)
        cmd.setChecked(value)
        self.previewData['mathjax'] = value
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

        action = QtWidgets.QAction(self.tr('Install MathJax'), self)
        action.triggered.connect(partial(self.onMenuMathJax, 'install'))
        cmd = g_action.register('mainwindow.install_mathjax', action)
        cmd.setText(action.text())
        cmd.setEnabled(not os.path.exists(__mathjax_full_path__))
        # settings
        # # application style
        value = settings.value('app_style', 'Windows', type=str)
        settings.setValue('app_style', value)
        self.appStyleGroup = QtWidgets.QActionGroup(self)
        self.appStyleGroup.setExclusive(True)
        for k in list(QtWidgets.QStyleFactory.keys()):
            act = QtWidgets.QAction(k, self, checkable=True)
            act.triggered.connect(partial(self.onMenuAppStyleChanged, k))
            self.appStyleGroup.addAction(act)
            if value == k:
                act.setChecked(True)

        action = QtWidgets.QAction(self.tr('VIM Mode'), self, checkable=True)
        action.triggered.connect(partial(self.onMenuSettings, 'vim_mode'))
        value = settings.value('vim_mode', False, type=bool)
        cmd = g_action.register('mainwindow.vim_mode', action)
        cmd.setText(action.text())
        cmd.setIcon(QtGui.QIcon.fromTheme('gvim'))
        cmd.setCheckable(True)
        cmd.setChecked(value)

        action = QtWidgets.QAction(
            self.tr('&High DPI support'), self, checkable=True)
        action.triggered.connect(
            partial(self.onMenuSettings, 'high_dpi'))
        value = settings.value('highdpi', type=bool)
        cmd = g_action.register('mainwindow.high_dpi', action)
        cmd.setText(action.text())
        cmd.setCheckable(True)
        cmd.setChecked(value)

        # help
        action = QtWidgets.QAction(self.tr('&Help Documents'), self)
        action.triggered.connect(self.onMenuHelp)
        cmd = g_action.register('mainwindow.help', action)
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.HelpContents)
        cmd.setIcon(QtGui.QIcon.fromTheme('help-contents'))

        action = QtWidgets.QAction(self.tr('&About'), self)
        action.triggered.connect(self.onMenuAbout)
        cmd = g_action.register('mainwindow.about', action)
        cmd.setText(action.text())
        cmd.setIcon(QtGui.QIcon.fromTheme('help-about'))

        action = QtWidgets.QAction(self.tr('About &Qt'), self)
        action.triggered.connect(QtWidgets.qApp.aboutQt)
        cmd = g_action.register('mainwindow.about_qt', action)
        cmd.setText(action.text())

        # menu
        menubar = self.menuBar()
        menu = menubar.addMenu(self.tr('&File'))

        submenu = menu.addMenu(QtGui.QIcon.fromTheme('document-new'), self.tr('&New'))
        submenu.addAction(self.workspace.action('new_rst'))
        submenu.addAction(self.workspace.action('new_md'))
        menu.addMenu(submenu)
        menu.addAction(self.action('new_window'))
        menu.addAction(self.tab_editor.action('open'))
        menu.addAction(self.workspace.action('open_workspace'))

        menu.addSeparator()
        menu.addAction(self.tab_editor.action('save'))
        menu.addAction(self.tab_editor.action('save_as'))
        menu.addAction(self.tab_editor.action('save_all'))
        menu.addAction(self.tab_editor.action('close_all'))

        menu.addSeparator()
        submenu = menu.addMenu(self.tr('Line Endings'))
        submenu.addAction(self.tab_editor.action('eol_windows'))
        submenu.addAction(self.tab_editor.action('eol_unix'))
        submenu.addAction(self.tab_editor.action('eol_mac'))

        menu.addSeparator()
        self.webview.menuExport(menu)
        menu.aboutToShow.connect(self.webview.menuAboutToShow)

        menu.addSeparator()
        menu.addAction(self.action('print_preview'))
        menu.addAction(self.action('print'))

        menu.addSeparator()
        menu.addAction(self.action('quit'))

        menu = menubar.addMenu(self.tr('&Edit'))
        self.tab_editor.menuEdit(menu)
        menu.aboutToShow.connect(partial(self.onMenuAboutToShow, 'edit'))

        menu = menubar.addMenu(self.tr('&View'))
        menu.addAction(self.dock_workspace.toggleViewAction())
        menu.addAction(self.dock_webview.toggleViewAction())
        menu.addAction(self.dock_codeview.toggleViewAction())
        menu.addSeparator()
        menu.addAction(self._toolbar.toggleViewAction())

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
        menu.addAction(self.action('install_mathjax'))

        menu = menubar.addMenu(self.tr('&Settings'))

        submenu = QtWidgets.QMenu(self.tr('Application Style'), menu)
        for act in self.appStyleGroup.actions():
            submenu.addAction(act)
        menu.addMenu(submenu)
        menu.addSeparator()

        menu.addAction(self.action('vim_mode'))
        menu.addAction(self.action('high_dpi'))

        menu.addSeparator()
        menu.addAction(self.action('preview_onsave'))
        menu.addAction(self.action('preview_oninput'))
        menu.addAction(self.action('preview_sync'))
        menu.addAction(self.action('preview_mathjax'))

        menu.addSeparator()
        self.tab_editor.menuSetting(menu)

        menu.addSeparator()
        menu.addAction(self.action('file_associate'))

        menu = menubar.addMenu(self.tr('&Help'))
        menu.addAction(self.action('help'))

        menu.addSeparator()
        menu.addAction(self.action('about'))
        menu.addAction(self.action('about_qt'))

    def action(self, act_id):
        g_action = GlobalAction()
        return g_action.get('mainwindow.' + act_id)

    def setupToolbar(self, toolbar):
        newButton = QtWidgets.QToolButton(self)
        menu = QtWidgets.QMenu('', self)
        menu.addAction(self.workspace.action('new_rst'))
        menu.addAction(self.workspace.action('new_md'))
        newButton.setMenu(menu)
        newButton.setPopupMode(newButton.MenuButtonPopup)
        newButton.setDefaultAction(self.workspace.action('new_rst'))
        toolbar.addWidget(newButton)

        toolbar.addAction(self.tab_editor.action('open'))
        toolbar.addAction(self.workspace.action('open_workspace'))
        toolbar.addAction(self.tab_editor.action('save'))
        toolbar.addSeparator()
        toolbar.addAction(self.tab_editor.action('undo'))
        toolbar.addAction(self.tab_editor.action('redo'))
        toolbar.addSeparator()
        toolbar.addAction(self.tab_editor.action('cut'))

        cpButton = QtWidgets.QToolButton(self)
        menu = QtWidgets.QMenu('', self)
        menu.addAction(self.tab_editor.action('copy'))
        menu.addAction(self.tab_editor.action('copy_table'))
        cpButton.setMenu(menu)
        cpButton.setPopupMode(cpButton.MenuButtonPopup)
        cpButton.setDefaultAction(self.tab_editor.action('copy'))
        toolbar.addWidget(cpButton)

        toolbar.addAction(self.tab_editor.action('paste'))
        toolbar.addSeparator()
        toolbar.addAction(self.tab_editor.action('find'))

        ftButton = QtWidgets.QToolButton(self)
        menu = QtWidgets.QMenu('', self)
        menu.addAction(self.tab_editor.action('format_table_vline'))
        menu.addAction(self.tab_editor.action('format_table_comma'))
        menu.addAction(self.tab_editor.action('format_table_tab'))
        menu.addAction(self.tab_editor.action('format_table_space'))
        ftButton.setMenu(menu)
        ftButton.setPopupMode(ftButton.MenuButtonPopup)
        ftButton.setDefaultAction(self.tab_editor.action('format_table'))
        toolbar.addWidget(ftButton)

        toolbar.addAction(self.action('vim_mode'))
        toolbar.addSeparator()
        toolbar.addAction(self.tab_editor.action('zoom_in'))
        toolbar.addAction(self.tab_editor.action('zoom_out'))
        toolbar.addAction(self.tab_editor.action('zoom_original'))
        toolbar.addSeparator()
        toolbar.addAction(self.dock_workspace.toggleViewAction())
        toolbar.addAction(self.dock_webview.toggleViewAction())
        self.addToolBar(toolbar)

    def setupStatusBar(self):
        # status bar
        self.statusCursor = QtWidgets.QLabel('Cursor', self)
        self.statusBar().addPermanentWidget(self.statusCursor)

        self.statusLength = QtWidgets.QLabel('Length', self)
        self.statusBar().addPermanentWidget(self.statusLength)

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
        self.settings.setValue('view/workspace', self.dock_workspace.isVisible())
        self.settings.setValue('view/webview', self.dock_webview.isVisible())
        self.settings.setValue('view/codeview', self.dock_codeview.isVisible())
        self.settings.setValue('vim_mode', self.action('vim_mode').isChecked())

        if not self.tab_editor.close():
            event.ignore()
            return
        self.webview.close()
        self.workspace.close()
        self.codeview.close()
        self.findDialog.done(0)

        self.settings.sync()

        self.previewQuit = True
        previewEvent.set()
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
            elif key == 'length':
                self.statusLength.setText(value.center(length, ' '))

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
                os.path.join(os.getcwd(), out_file),
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
        if value:
            if dock == 'webview':
                self.webview.setFocus(QtCore.Qt.TabFocusReason)
            elif dock == 'codeview':
                self.codeview.setFocus(QtCore.Qt.TabFocusReason)
            self.previewCurrentText()
        if dock == 'webview' or dock == 'codeview':
            self.previewViewVisibleNotify.emit(value)

    def onMenuPreview(self, label, checked):
        if label == 'preview_onsave':
            self.settings.setValue('preview/onsave', checked)
        elif label == 'preview_oninput':
            self.settings.setValue('preview/oninput', checked)
        elif label == 'preview_sync':
            self.settings.setValue('preview/sync', checked)
        elif label == 'preview_mathjax':
            self.settings.setValue('preview/mathjax', checked)
            self.previewData['mathjax'] = checked
            self.previewCurrentText()

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

    def onMenuAppStyleChanged(self, label, checked):
        self.settings.setValue('app_style', label)
        QtWidgets.qApp.setStyle(label)

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
        elif action == 'vim_mode':
            self.tab_editor.setVimEmulator(self.vim if value else None)
            self.vim.setVisible(value)

    def onMenuHelp(self):
        help_paths = [
            os.path.join(__home_data_path__, 'help', 'demo.rst'),
            os.path.join(__data_path__, 'help', 'demo.rst'),
        ]
        for help_path in help_paths:
            if os.path.exists(help_path):
                break
        self.workspace.appendRootPath(help_path, expand=True)
        self.tab_editor.loadFile(help_path)

    def onMenuAbout(self):
        title = self.tr('About %s') % (__app_name__)
        text = self.tr("%s %s\n\nThe editor for Markup Text\n\n"
                       ) % (__app_name__, __app_version__)
        text += self.tr('Platform: %s\n') % (platform.platform())
        text += self.tr('Icon Theme: %s\n') % (self.icon_theme)
        text += self.tr('Home data path: %s\n') % (__home_data_path__)
        text += self.tr('Application data path: %s\n') % (__data_path__)
        widget = self.tab_editor.currentWidget()
        if widget.lexer():
            text += self.tr('Editor lexer: %s\n') % widget.lexer().__module__
        text += self.tr('\n')
        text += self.tr('Python: %s\n') % platform.python_version()
        text += self.tr('PyQt5: %s\n') % QtCore.PYQT_VERSION_STR
        text += self.tr('QScintilla: %s\n') % widget.getScintillaVersion()
        QtWidgets.QMessageBox.about(self, title, text)

    def onMenuAboutToShow(self, menu_id):
        if self.codeview.hasFocus():
            self.codeview.menuAboutToShow()
        elif self.webview.hasFocus():
            self.webview.menuAboutToShow()
        else:
            self.tab_editor.menuAboutToShow()

    def onWorkspaceNew(self, ext):
        self.tab_editor.new(ext)

    def onWorkspaceFileLoaded(self, path):
        if not os.path.exists(path):
            return
        index = self.tab_editor.loadFile(path)
        if index is None:
            self.showMessage(self.tr('Shell run "%s"' % path))
            subprocess.Popen(path, shell=True)

    def onWorkspaceFileDeleted(self, path):
        for x in range(self.tab_editor.count()):
            editor = self.tab_editor.widget(x)
            if path == editor.getFileName():
                self.tab_editor.removeTab(x)
                del editor
                break
        if self.tab_editor.count() == 0:
            self.tab_editor.new('.rst')

    def onEditorFileLoaded(self, index):
        self.updateWindowTitle(index)

    def onEditorVScrollBarChanged(self, value):
        if self.settings.value('preview/sync', type=bool):
            widget = self.tab_editor.currentWidget()
            dy = widget.getVScrollValue()
            editor_vmax = widget.getVScrollMaximum()
            if editor_vmax:
                self.webview.scrollRatioPage(dy, editor_vmax)

    def onEditorModified(self, index, value):
        self.updateWindowTitle(index)

    def onEditorPreviewRequest(self, index, source):
        if source == 'input' and not self.settings.value('preview/oninput', type=bool):
            return
        if source == 'save' and not self.settings.value('preview/onsave', type=bool):
            return
        self.do_preview(index)

    def onFileRenamed(self, old_name, new_name):
        if self.sender() == self.workspace:
            self.tab_editor.rename(old_name, new_name)
        elif self.sender() == self.tab_editor:
            self.workspace.refreshPath(old_name)
            self.workspace.refreshPath(new_name)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def do_preview(self, index, force=False):
        if previewEvent.is_set():
            logger.debug('Preview is working..., ignore')
        elif force or self.dock_codeview.isVisible() or self.dock_webview.isVisible():
            widget = self.tab_editor.widget(index)
            self.previewData['text'] = widget.text()
            self.previewData['path'] = widget.getFileName()
            previewEvent.set()

    def previewCurrentText(self, force=False):
        self.do_preview(self.tab_editor.currentIndex(), force=force)

    def onUpdatePreviewView(self):
        if self.dock_webview.isVisible():
            self.webview.setHtml(self.previewHtml, self.previewData.get('path'))
        if self.dock_codeview.isVisible():
            self.codeview.setValue(self.previewHtml)
            self.codeview.setFileName(self.previewData.get('path') + '.html')
        widget = self.tab_editor.currentWidget()
        if not widget:
            return
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
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % __app_version__)
    parser.add_argument('-v', '--verbose', help='verbose help',
                        action='count', default=0)
    parser.add_argument('--no-sandbox', action='store_true', help='disable qtwebengine sandbox')
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

    app = QtWidgets.QApplication(sys.argv)
    logger.info('app scale factor: %s' % app.devicePixelRatio())
    logger.debug('qt plugin path: ' + ', '.join(app.libraryPaths()))
    win = MainWindow(settings)
    if args.rstfile:
        win.tab_editor.loadFile(os.path.abspath(args.rstfile))

    # application style
    value = settings.value('app_style', 'Windows', type=str)
    app.setStyle(value)

    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
