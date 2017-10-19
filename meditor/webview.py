
import os.path
from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets

from . import util
from . import __data_path__


class WebView(QtWebEngineWidgets.QWebEngineView):
    _case_sensitive = False
    _whole_word = False
    _enable_mathjax = False
    _mathjax = None

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
        # mathjax single
        # https://github.com/pkra/MathJax-single-file
        mathjax_min_path = os.path.join(__data_path__, 'math', 'MathJax.min.js')
        with open(mathjax_min_path, encoding='UTF-8') as f:
            self._mathjax = f.read()

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            self.popupMenu.popup(event.globalPos())

    def onLoadFinished(self, ok):
        if self._enable_mathjax:
            self.page().runJavaScript(self._mathjax)

    def setHtml(self, html, url=None):
        if not url:
            url = ''
        ext = os.path.splitext(url)
        self._enable_mathjax = ext[1].lower() == '.md'
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
