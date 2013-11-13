
from PyQt4 import QtCore

def toUtf8(str):
    if isinstance(str, QtCore.QString):
        return unicode(str.toUtf8(), encoding='utf-8')
    if not isinstance(str, unicode):
        return str.decode('utf-8', 'ignore')
    return
