
from PyQt4 import QtCore


def toUtf8(text):
    if text is None:
        return b''
    if isinstance(text, QtCore.QString):
        return unicode(text.toUtf8(), encoding='utf-8')
    if not isinstance(text, unicode):
        return text.decode('utf-8', 'ignore')
    return text


def logDebug(*args):
    print('[DEBUG]', args)
