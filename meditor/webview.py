
from functools import partial

from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets

from .util import toUtf8


class WebView(QtWebEngineWidgets.QWebEngineView):
    exportHtml = QtCore.pyqtSignal()
    _case_sensitive = False
    _whole_word = False
    _actions = None
    _find_dialog = None

    def __init__(self, find_dialog, parent=None):
        super(WebView, self).__init__(parent)
        self._find_dialog = find_dialog
        self.settings().setAttribute(self.settings().PluginsEnabled, False)
        self.page().setHtml('')
        self.page().loadFinished.connect(self.onLoadFinished)
        self.page().pdfPrintingFinished.connect(self.onPdfPrintingFinished)

        self._actions = {}
        action = self.pageAction(self.page().Copy)
        action.setShortcut(QtGui.QKeySequence('Ctrl+C'))
        self._actions['copy'] = action

        action = self.pageAction(self.page().SelectAll)
        action.setShortcut(QtGui.QKeySequence('Ctrl+A'))
        self._actions['select_all'] = action

        action = QtWidgets.QAction(self.tr('Export to PDF'), self)
        action.triggered.connect(self.onExportToPdf)
        self._actions['export_pdf'] = action

        action = QtWidgets.QAction(self.tr('Export to HTML'), self)
        action.triggered.connect(self.onExportToHtml)
        self._actions['export_html'] = action

        action = QtWidgets.QAction(self.tr('Find'), self)
        action.setShortcut('Ctrl+F')
        action.triggered.connect(partial(self._onEditAction, 'find'))
        self._actions['find'] = action

        action = QtWidgets.QAction(self.tr('Find Next'), self)
        action.setShortcut('F3')
        action.triggered.connect(partial(self._onEditAction, 'findnext'))
        self._actions['find_next'] = action

        action = QtWidgets.QAction(self.tr('Find Previous'), self)
        action.setShortcut('Shift+F3')
        action.triggered.connect(partial(self._onEditAction, 'findprev'))
        self._actions['find_prev'] = action

        # popup menu
        self.popupMenu = QtWidgets.QMenu(self)
        self.popupMenu.addAction(self.action('copy'))
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(self.action('select_all'))
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(self.action('export_pdf'))
        self.popupMenu.addAction(self.action('export_html'))

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            self.popupMenu.popup(event.globalPos())

    def _onEditAction(self, action):
        if action == 'find':
            self.find(self._find_dialog)
        elif action == 'findnext':
            self.findNext(self._find_dialog.getFindText())
        elif action == 'findprev':
            self.findPrevious(self._find_dialog.getFindText())

    def onLoadFinished(self, ok):
        pass

    def onPdfPrintingFinished(self, filePath, success):
        pass

    def onExportToPdf(self):
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

    def onExportToHtml(self):
        self.exportHtml.emit()

    def action(self, action):
        return self._actions.get(action)

    def editMenu(self, menu):
        menu.addAction(self.action('copy'))
        menu.addSeparator()
        menu.addAction(self.action('select_all'))
        menu.addSeparator()
        menu.addAction(self.action('find'))
        menu.addAction(self.action('find_next'))
        menu.addAction(self.action('find_prev'))
        # page widget will set enabled

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
        self._case_sensitive = finddialog.isCaseSensitive()
        self._whole_word = finddialog.isWholeWord()

    def findNext(self, text):
        self.page().findText(text, self.page().FindFlags())

    def findPrevious(self, text):
        self.page().findText(text, self.page().FindBackward)
