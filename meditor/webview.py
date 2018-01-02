
from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets

from .util import toUtf8


class WebView(QtWebEngineWidgets.QWebEngineView):
    exportHtml = QtCore.pyqtSignal()
    _case_sensitive = False
    _whole_word = False

    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        settings = self.settings()
        settings.setAttribute(settings.PluginsEnabled, False)
        self.page().setHtml('')
        self.page().loadFinished.connect(self.onLoadFinished)
        self.page().pdfPrintingFinished.connect(self.onPdfPrintingFinished)
        # popup menu
        self.popupMenu = QtWidgets.QMenu(self)
        self.copyAction = self.pageAction(self.page().Copy)
        self.copyAction.setShortcut(QtGui.QKeySequence('Ctrl+C'))
        self.popupMenu.addAction(self.copyAction)
        self.popupMenu.addSeparator()
        self.selectAllAction = self.pageAction(self.page().SelectAll)
        self.selectAllAction.setShortcut(QtGui.QKeySequence('Ctrl+A'))
        self.popupMenu.addAction(self.selectAllAction)
        self.popupMenu.addSeparator()
        self.exportPdfAction = QtWidgets.QAction(self.tr('Export to PDF'), self)
        self.exportPdfAction.triggered.connect(self.onExportToPdf)
        self.popupMenu.addAction(self.exportPdfAction)
        self.exportHtmlAction = QtWidgets.QAction(self.tr('Export to HTML'), self)
        self.exportHtmlAction.triggered.connect(self.onExportToHtml)
        self.popupMenu.addAction(self.exportHtmlAction)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            self.popupMenu.popup(event.globalPos())

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
