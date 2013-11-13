
from PyQt4 import QtCore
from PyQt4 import QtWebKit

from rsteditor import util

class WebView(QtWebKit.QWebView):
    """ """
    def __init__(self, *args, **kwargs):
        super(WebView, self).__init__(*args, **kwargs)
        self.dx = 0
        self.dy = 0
        self.wait = False
        self.setHtml('')
        self.loadFinished.connect(self.onLoadFinished)

    def contextMenuEvent(self, event):
        return

    def onLoadFinished(self, ok):
        if ok and self.wait:
            self.wait = False
            self.scroll(self.dx, self.dy)
        return

    def setHtml(self, html, url=None):
        if not url:
            url = ''
        super(WebView, self).setHtml(util.toUtf8(html), QtCore.QUrl(url))

    def getVScrollMaximum(self):
        return self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical)

    def setScrollBarValue(self, dx, dy, wait=False):
        if wait:
            self.dx = dx
            self.dy = dy
            self.wait = wait
        else:
            self.scroll(dx, dy)
        return

    def scroll(self, dx, dy):
        self.page().mainFrame().setScrollBarValue(QtCore.Qt.Horizontal, dx)
        self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, dy)

