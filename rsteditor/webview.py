
from PyQt5 import QtGui, QtCore, QtWidgets, QtNetwork, QtWebEngineWidgets

from rsteditor import util


class WebView(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        settings = self.settings()
        settings.setAttribute(settings.PluginsEnabled, False)
        self.setHtml('')
        self.loadFinished.connect(self.onLoadFinished)
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
        widget = self.page().view()
        widget.render(printer)
