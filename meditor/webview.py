
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets

from .gaction import GlobalAction
from .util import toUtf8
from . import __app_name__, __app_version__

hello_html = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8" />
<title>Hello %s v%s</title>
</head>
<body>
<h1>Hello %s v%s!</h1>
</body>
</html>
""" % (__app_name__, __app_version__, __app_name__, __app_version__)


class WebView(QtWebEngineWidgets.QWebEngineView):
    exportHtml = QtCore.pyqtSignal()
    _settings = None
    _find_dialog = None

    def __init__(self, settings, find_dialog, parent=None):
        super(WebView, self).__init__(parent)
        self._settings = settings
        self._find_dialog = find_dialog
        self.settings().setAttribute(self.settings().PluginsEnabled, False)
        self.setAcceptDrops(False)

        # self.page().loadFinished.connect(self.onLoadFinished)
        # self.page().pdfPrintingFinished.connect(self.onPdfPrintingFinished)
        # self.page().renderProcessTerminated.connect(self.onRenderProcessTerminated)

        g_action = GlobalAction()

        action = self.pageAction(self.page().Copy)
        cmd = g_action.register('copy', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.Copy)

        action = self.pageAction(self.page().SelectAll)
        cmd = g_action.register('select_all', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.SelectAll)

        action = QtWidgets.QAction(self.tr('Export to PDF'), self)
        action.triggered.connect(partial(self._onAction, 'export_pdf'))
        cmd = g_action.register('export_pdf', action, 'webview.export')
        cmd.setText(action.text())

        action = QtWidgets.QAction(self.tr('Export to HTML'), self)
        action.triggered.connect(partial(self._onAction, 'export_html'))
        cmd = g_action.register('export_html', action, 'webview.export')
        cmd.setText(action.text())

        action = QtWidgets.QAction(self.tr('Find'), self)
        action.triggered.connect(partial(self._onAction, 'find'))
        cmd = g_action.register('find', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.Find)

        action = QtWidgets.QAction(self.tr('Find Next'), self)
        action.triggered.connect(partial(self._onAction, 'findnext'))
        cmd = g_action.register('find_next', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.FindNext)

        action = QtWidgets.QAction(self.tr('Find Previous'), self)
        action.triggered.connect(partial(self._onAction, 'findprev'))
        cmd = g_action.register('find_prev', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.FindPrevious)

        action = QtWidgets.QAction(self.tr('Zoom In'), self)
        action.triggered.connect(partial(self._onAction, 'zoom_in'))
        cmd = g_action.register('zoom_in', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.ZoomIn)

        action = QtWidgets.QAction(self.tr('Zoom Original'), self)
        action.triggered.connect(partial(self._onAction, 'zoom_original'))
        cmd = g_action.register('zoom_original', action, 'webview')
        cmd.setText(action.text())

        action = QtWidgets.QAction(self.tr('Zoom Out'), self)
        action.triggered.connect(partial(self._onAction, 'zoom_out'))
        cmd = g_action.register('zoom_out', action, 'webview')
        cmd.setText(action.text())
        cmd.setShortcut(QtGui.QKeySequence.ZoomOut)

        # popup menu
        self.popupMenu = QtWidgets.QMenu(self)
        self.menuEdit(self.popupMenu)
        self.popupMenu.addSeparator()
        self.menuExport(self.popupMenu)

        # zoom
        scale = self._settings.value('webview/scale', 1.0, type=float)
        self.setZoomFactor(scale)
        self.setHtml(hello_html)

    def closeEvent(self, event):
        self._settings.setValue('webview/scale', self.zoomFactor())

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            self.menuAboutToShow()
            self.popupMenu.popup(event.globalPos())

    def _onAction(self, action):
        if action == 'find':
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
        elif action == 'export_pdf':
            self.do_export_pdf()
        elif action == 'export_html':
            self.exportHtml.emit()
        elif action == 'zoom_in':
            factor = self.zoomFactor()
            self.setZoomFactor(factor + 0.1)
        elif action == 'zoom_original':
            self.setZoomFactor(1.0)
        elif action == 'zoom_out':
            factor = self.zoomFactor()
            self.setZoomFactor(factor - 0.1)

    def onLoadFinished(self, ok):
        pass

    def onPdfPrintingFinished(self, filePath, success):
        pass

    def onRenderProcessTerminated(self, status, exit_code):
        pass

    def action(self, act_id):
        g_action = GlobalAction()
        return g_action.get('' + act_id)

    def menuAboutToShow(self):
        self.action('undo').setEnabled(False)
        self.action('redo').setEnabled(False)
        action = self.pageAction(self.page().Copy)
        self.action('copy').setEnabled(action.isEnabled())
        self.action('copy_table').setEnabled(False)
        self.action('cut').setEnabled(False)
        self.action('paste').setEnabled(False)
        self.action('delete').setEnabled(False)
        self.action('replace_next').setEnabled(False)
        self.action('indent').setEnabled(False)
        self.action('unindent').setEnabled(False)
        self.action('format_table_vline').setEnabled(False)
        self.action('format_table_comma').setEnabled(False)
        self.action('format_table_space').setEnabled(False)
        self.action('format_table_tab').setEnabled(False)
        self.action('export_pdf').setEnabled(self.isVisible())
        self.action('export_html').setEnabled(True)

    def menuEdit(self, menu):
        menu.addAction(self.action('copy'))

        menu.addSeparator()
        menu.addAction(self.action('select_all'))

        menu.addSeparator()
        menu.addAction(self.action('find'))
        menu.addAction(self.action('find_next'))
        menu.addAction(self.action('find_prev'))

        menu.addSeparator()
        menu.addAction(self.action('zoom_in'))
        menu.addAction(self.action('zoom_original'))
        menu.addAction(self.action('zoom_out'))

    def menuExport(self, menu):
        menu.addAction(self.action('export_pdf'))
        menu.addAction(self.action('export_html'))

    def setHtml(self, html, url=None):
        url = url or ''
        self.page().setHtml(toUtf8(html), QtCore.QUrl.fromLocalFile(url))

    def scrollRatioPage(self, value, maximum):
        scrollJS = 'window.scrollTo(0, document.body.scrollHeight * %s / %s);'
        self.page().runJavaScript(scrollJS % (value, maximum))

    def print_(self, printer):
        """ QWebEngineView don't support print in Qt5.7 """
        # TODO: crash ???
        # self.page().print(printer, lambda x: x)
        painter = QtGui.QPainter()
        if painter.begin(printer):
            xscale = printer.pageRect().width() / float(self.width())
            yscale = printer.pageRect().height() / float(self.height())
            scale = min(xscale, yscale)
            painter.translate(
                printer.paperRect().x() + printer.pageRect().width() / 2,
                printer.paperRect().y() + printer.pageRect().height() / 2)
            painter.scale(scale, scale)
            painter.translate(-self.width() / 2, -self.height() / 2)
            self.render(painter)

    def find(self, finddialog, readonly=True):
        finddialog.setReadOnly(readonly)
        finddialog.find_next.connect(self.findNext)
        finddialog.find_previous.connect(self.findPrevious)
        finddialog.exec_()
        finddialog.find_next.disconnect(self.findNext)
        finddialog.find_previous.disconnect(self.findPrevious)

    def findNext(self, text, cs, wo):
        flags = self.page().FindFlags()
        if cs:
            flags |= self.page().FindCaseSensitively
        self.page().findText(text, flags)

    def findPrevious(self, text, cs, wo):
        flags = self.page().FindFlags()
        flags |= self.page().FindBackward
        if cs:
            flags |= self.page().FindCaseSensitively
        self.page().findText(text, flags)

    def do_export_pdf(self):
        pdf_file = '%s.pdf' % self.title()
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, self.tr('export PDF as ...'),
            pdf_file,
            'PDF files (*.pdf)',
        )
        if isinstance(filename, tuple):
            filename = filename[0]
        if filename:
            pageLayout = QtGui.QPageLayout(
                QtGui.QPageSize(QtGui.QPageSize.A4),
                QtGui.QPageLayout.Portrait,
                QtCore.QMarginsF(15, 15, 15, 15),
                QtGui.QPageLayout.Millimeter
            )
            self.page().printToPdf(filename, pageLayout)
