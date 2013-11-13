
import os
import os.path

from PyQt4 import QtGui
from PyQt4 import QtCore

from rsteditor.util import toUtf8


class Explorer(QtGui.QTreeWidget):
    fileLoaded = QtCore.pyqtSignal('QString')
    pathLoaded = QtCore.pyqtSignal('QString')

    def __init__(self, *args, **kwargs):
        super(Explorer, self).__init__(*args, **kwargs)
        self.header().close()
        self.root_path = None
        self.root_item = None
        self.qstyle = QtGui.QStyleFactory.create('cleanlooks')
        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.itemActivated.connect(self.onItemActivated)
        self.pathLoaded.connect(self.onPathLoaded)

    def resizeEvent(self, event):
        if self.root_item:
            self.root_item.setText(0, self.getDisplayName(self.root_path))
            self.setColumnWidth(0, -1)
        return

    def onItemActivated(self, item, col):
        if col > 0:
            return
        if item == self.root_item:
            new_path = os.path.dirname(self.root_path)
            self.setRootPath(new_path)
        else:
            child_name = toUtf8(item.text(0))
            new_path = os.path.join(self.root_path, child_name)
            if os.path.isdir(new_path):
                self.setRootPath(new_path)
            else:
                self.loadFile(new_path)
        return

    def onPathLoaded(self, path):
        self.setRootPath(path)

    def addRoot(self, name):
        root = QtGui.QTreeWidgetItem(self)
        root.setText(0, self.getDisplayName(name))
        root.setIcon(0, self.qstyle.standardIcon(QtGui.QStyle.SP_DirOpenIcon))
        return root

    def appendItem(self, rootitem, name):
        if not rootitem:
            raise Exception('Add root item firstly!')
        child = QtGui.QTreeWidgetItem(rootitem)
        child.setText(0, name)
        path = os.path.join(self.root_path, name)
        if os.path.isdir(path):
            child.setIcon(0, self.qstyle.standardIcon(QtGui.QStyle.SP_DirIcon))
        else:
            child.setIcon(0, self.qstyle.standardIcon(QtGui.QStyle.SP_FileIcon))
        return child

    def setRootPath(self, path=None, refresh=False):
        """ set exporer root path """
        if not path:
            path = os.path.expanduser('~')
        if not os.path.exists(path):
            return
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if not refresh and path == self.root_path:
            return
        self.clear()
        self.root_path = path
        os.chdir(path)
        self.root_item = self.addRoot(self.getDisplayName(self.root_path))
        dirs = sorted(os.listdir(self.root_path))
        for dir in dirs:
            if dir.startswith('.'):
                continue
            self.appendItem(self.root_item, dir)
        self.expandItem(self.root_item)

    def getDisplayName(self, name):
        """ directory display name """
        client_width = self.width() - 32
        char_width = self.fontMetrics().width(' ')
        disp_char_num = client_width / char_width - 1
        if (len(name) - 3) > disp_char_num:
            display_name = '<<<%s'% name[-disp_char_num + 3:]
        else:
            display_name = name
        return display_name

    def getRootPath(self):
        return self.root_path

    def loadFile(self, filename):
        if filename and os.path.exists(filename):
            self.setRootPath(os.path.dirname(filename))
            self.fileLoaded.emit(filename)
        return

