
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets

from .util import toUtf8


class WebView(QtWebEngineWidgets.QWebEngineView):
    exportHtml = QtCore.pyqtSignal()
    _actions = None
    _settings = None
    _find_dialog = None

    def __init__(self, settings, find_dialog, parent=None):
        super(WebView, self).__init__(parent)
        self._settings = settings
        self._find_dialog = find_dialog
        self.settings().setAttribute(self.settings().PluginsEnabled, False)
        self.setAcceptDrops(False)

        self.page().view().setFocusPolicy(QtCore.Qt.NoFocus)
        self.page().setHtml('')
        self.page().loadFinished.connect(self.onLoadFinished)
        self.page().pdfPrintingFinished.connect(self.onPdfPrintingFinished)

        self._actions = {}
        action = self.pageAction(self.page().Copy)
        self._actions['copy'] = action

        action = self.pageAction(self.page().SelectAll)
        self._actions['select_all'] = action

        action = QtWidgets.QAction(self.tr('Export to PDF'), self)
        action.triggered.connect(partial(self._onAction, 'export_pdf'))
        self._actions['export_pdf'] = action

        action = QtWidgets.QAction(self.tr('Export to HTML'), self)
        action.triggered.connect(partial(self._onAction, 'export_html'))
        self._actions['export_html'] = action

        action = QtWidgets.QAction(self.tr('Find'), self)
        action.triggered.connect(partial(self._onAction, 'find'))
        self._actions['find'] = action

        action = QtWidgets.QAction(self.tr('Find Next'), self)
        action.triggered.connect(partial(self._onAction, 'findnext'))
        self._actions['find_next'] = action

        action = QtWidgets.QAction(self.tr('Find Previous'), self)
        action.triggered.connect(partial(self._onAction, 'findprev'))
        self._actions['find_prev'] = action

        action = QtWidgets.QAction(self.tr('Zoom In'), self)
        action.triggered.connect(partial(self._onAction, 'zoom_in'))
        self._actions['zoom_in'] = action

        action = QtWidgets.QAction(self.tr('Zoom Original'), self)
        action.triggered.connect(partial(self._onAction, 'zoom_original'))
        self._actions['zoom_original'] = action

        action = QtWidgets.QAction(self.tr('Zoom Out'), self)
        action.triggered.connect(partial(self._onAction, 'zoom_out'))
        self._actions['zoom_out'] = action

        # popup menu
        self.popupMenu = QtWidgets.QMenu(self)
        self.menuEdit(self.popupMenu)
        self.popupMenu.addSeparator()
        self.menuExport(self.popupMenu)

        # zoom
        scale = self._settings.value('webview/scale', 1.0, type=float)
        self.setZoomFactor(scale)

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

    def action(self, action):
        return self._actions.get(action)

    def menuAboutToShow(self):
        self.action('export_pdf').setEnabled(self.isVisible())
        self.action('export_html').setEnabled(self.isVisible())
        # page widget will set enabled

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
