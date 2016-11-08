
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

from rsteditor import util

from .findreplace import FindReplaceDialog


class WebView(QtWebEngineWidgets.QWebEngineView):
    _case_sensitive = False
    _whole_word = False

    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        settings = self.settings()
        settings.setAttribute(settings.PluginsEnabled, False)
        self.setHtml('')
        self.loadFinished.connect(self.onLoadFinished)

        self.findDialog = FindReplaceDialog(self)
        self.findDialog.setReadOnly(True)
        self.findDialog.find_next.connect(self.findNext)
        self.findDialog.find_previous.connect(self.findPrevious)

        self.popupMenu = QtWidgets.QMenu(self)
        self.popupMenu.addAction(self.pageAction(self.page().Copy))
        self.popupMenu.addAction(self.pageAction(self.page().SelectAll))

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            self.popupMenu.popup(event.globalPos())

    def onLoadFinished(self, ok):
        return

    def setHtml(self, html, url=None):
        if not url:
            url = ''
        super(WebView, self).setHtml(
            util.toUtf8(html),
            QtCore.QUrl.fromLocalFile(url)
        )

    def scrollRatioPage(self, value, maximum):
        scrollJS = 'window.scrollTo(0, document.body.scrollHeight * %s / %s);'
        self.page().runJavaScript(scrollJS % (value, maximum))

    def print_(self, printer):
        """ QWebEngineView don't support print in Qt5.7 """
        widget = self.page().view()
        widget.render(printer)

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
