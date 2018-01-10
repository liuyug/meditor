
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
        self.setAcceptDrops(False)

        self.page().view().setFocusPolicy(QtCore.Qt.NoFocus)
        self.page().setHtml('')
        self.page().loadFinished.connect(self.onLoadFinished)
        self.page().pdfPrintingFinished.connect(self.onPdfPrintingFinished)

        self._actions = {}
        action = self.pageAction(self.page().Copy)
        action.setShortcut(QtGui.QKeySequence.Copy)
        self._actions['copy'] = action

        action = self.pageAction(self.page().SelectAll)
        action.setShortcut(QtGui.QKeySequence.SelectAll)
        self._actions['select_all'] = action

        action = QtWidgets.QAction(self.tr('Export to PDF'), self)
        action.triggered.connect(partial(self._onAction, 'export_pdf'))
        self._actions['export_pdf'] = action

        action = QtWidgets.QAction(self.tr('Export to HTML'), self)
        action.triggered.connect(partial(self._onAction, 'export_html'))
        self._actions['export_html'] = action

        action = QtWidgets.QAction(self.tr('Find'), self)
        action.setShortcut(QtGui.QKeySequence.Find)
        action.triggered.connect(partial(self._onAction, 'find'))
        self._actions['find'] = action

        action = QtWidgets.QAction(self.tr('Find Next'), self)
        action.setShortcut(QtGui.QKeySequence.FindNext)
        action.triggered.connect(partial(self._onAction, 'findnext'))
        self._actions['find_next'] = action

        action = QtWidgets.QAction(self.tr('Find Previous'), self)
        action.setShortcut(QtGui.QKeySequence.FindPrevious)
        action.triggered.connect(partial(self._onAction, 'findprev'))
        self._actions['find_prev'] = action

        # popup menu
        self.popupMenu = QtWidgets.QMenu(self)
        self.menuEdit(self.popupMenu)
        self.popupMenu.addSeparator()
        self.menuExport(self.popupMenu)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            self.menuAboutToShow()
            self.popupMenu.popup(event.globalPos())

    def _onAction(self, action):
        if action == 'find':
            self.find(self._find_dialog)
        elif action == 'findnext':
            self.findNext(self._find_dialog.getFindText())
        elif action == 'findprev':
            self.findPrevious(self._find_dialog.getFindText())
        elif action == 'export_pdf':
            self.do_export_pdf()
        elif action == 'export_html':
            self.exportHtml.emit()

    def onLoadFinished(self, ok):
        pass

    def onPdfPrintingFinished(self, filePath, success):
        pass

    def action(self, action):
        return self._actions.get(action)

    def menuAboutToShow(self):
        self.action('export_pdf').setEnabled(self.isVisible())
        self.action('export_html').setEnabled(self.isVisible())

    def menuEdit(self, menu):
        menu.addAction(self.action('copy'))

        menu.addSeparator()
        menu.addAction(self.action('select_all'))

        menu.addSeparator()
        menu.addAction(self.action('find'))
        menu.addAction(self.action('find_next'))
        menu.addAction(self.action('find_prev'))
        # page widget will set enabled

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
        self._case_sensitive = finddialog.isCaseSensitive()
        self._whole_word = finddialog.isWholeWord()

    def findNext(self, text):
        self.page().findText(text, self.page().FindFlags())

    def findPrevious(self, text):
        self.page().findText(text, self.page().FindBackward)

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
