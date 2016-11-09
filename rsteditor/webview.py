
from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets

from rsteditor import util


class WebView(QtWebEngineWidgets.QWebEngineView):
    _case_sensitive = False
    _whole_word = False

    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        settings = self.settings()
        settings.setAttribute(settings.PluginsEnabled, False)
        self.setHtml('')
        self.loadFinished.connect(self.onLoadFinished)
        # popup menu
        self.popupMenu = QtWidgets.QMenu(self)
        action = self.pageAction(self.page().Copy)
        action.setShortcut(QtGui.QKeySequence('Ctrl+C'))
        self.popupMenu.addAction(action)
        self.popupMenu.addSeparator()
        action = self.pageAction(self.page().SelectAll)
        action.setShortcut(QtGui.QKeySequence('Ctrl+A'))
        self.popupMenu.addAction(action)

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
