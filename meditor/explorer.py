
import os
import os.path
import sys
import subprocess
import shutil
import logging
from unicodedata import east_asian_width
from functools import partial

from PyQt5 import QtCore, QtWidgets

from .util import toUtf8

logger = logging.getLogger(__name__)


class Explorer(QtWidgets.QTreeWidget):
    fileLoaded = QtCore.pyqtSignal('QString')
    pathLoaded = QtCore.pyqtSignal('QString')
    fileDeleted = QtCore.pyqtSignal('QString')
    fileRenamed = QtCore.pyqtSignal('QString', 'QString')
    fileNew = QtCore.pyqtSignal('QString')

    def __init__(self, parent, style=None):
        super(Explorer, self).__init__(parent)
        self.header().close()
        self.root_path = None
        self.root_item = None
        self.padding_right = 32
        # QStyle, such as QtWidgets.QStyleFactory.create('windows')
        self.qstyle = style
        # QT BUG, must keep reference or crash
        self.iconProvider = QtWidgets.QFileIconProvider()

        self.setRootIsDecorated(False)
        self.setItemsExpandable(False)
        self.itemActivated.connect(self.onItemActivated)
        self.pathLoaded.connect(self.onPathLoaded)
        # popup menu
        newRstAction = QtWidgets.QAction(self.tr('reStructedText'), self)
        newRstAction.triggered.connect(partial(self.onNewFile, 'rst'))
        newMdAction = QtWidgets.QAction(self.tr('Markdown'), self)
        newMdAction.triggered.connect(partial(self.onNewFile, 'md'))

        newdirectoryAction = QtWidgets.QAction(self.tr('New &directory'), self)
        newdirectoryAction.triggered.connect(self.onNewDirectory)
        self.renameAction = QtWidgets.QAction(self.tr('&Rename...'), self)
        self.renameAction.triggered.connect(self.onRename)
        self.deleteAction = QtWidgets.QAction(self.tr('Delete'), self)
        self.deleteAction.triggered.connect(self.onDelete)
        refreshAction = QtWidgets.QAction(self.tr('Refresh'), self)
        refreshAction.triggered.connect(self.onRefresh)
        explorerAction = QtWidgets.QAction(self.tr('Windows Explorer'), self)
        explorerAction.triggered.connect(self.onWindowsExplorer)
        drivers_path = self.getDrivesPath()
        self.driveGroup = QtWidgets.QActionGroup(self)
        for drive_path in drivers_path:
            act = QtWidgets.QAction(drive_path,
                                self,
                                checkable=True)
            act.triggered.connect(partial(self.onDriveChanged, drive_path))
            self.driveGroup.addAction(act)
        self.popupMenu = QtWidgets.QMenu(self)
        submenu = QtWidgets.QMenu(self.tr('New'), self.popupMenu)
        submenu.addAction(newRstAction)
        submenu.addAction(newMdAction)
        self.popupMenu.addMenu(submenu)

        self.popupMenu.addAction(newdirectoryAction)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(self.renameAction)
        self.popupMenu.addAction(self.deleteAction)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(refreshAction)
        self.popupMenu.addAction(explorerAction)
        self.popupMenu.addSeparator()
        for act in self.driveGroup.actions():
            self.popupMenu.addAction(act)
        # drag & drop
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def resizeEvent(self, event):
        if self.root_item:
            self.root_item.setText(0, self.getDisplayName(self.root_path))
            self.setColumnWidth(0, self.width() - self.padding_right)
        return

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            pos = event.globalPos()
            item = self.itemAt(event.pos())
        else:
            pos = None
            item = self.currentItem()
            self.scrollToItem(item)
        if item is None:
            item = self.root_item
            self.scrollToItem(item)
        if pos is None:
            rect = self.visualItemRect(item)
            pos = self.mapToGlobal(rect.center())
        self.renameAction.setEnabled(item != self.root_item)
        self.deleteAction.setEnabled(item != self.root_item)
        self.popupMenu.popup(pos)

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

    def onNewFile(self, label):
        self.fileNew.emit(label)

    def onNewDirectory(self):
        newpath = self.newDirectory()
        if newpath:
            self.appendItem(self.root_item, newpath)

    def onRename(self):
        item = self.currentItem()
        if not item or item == self.root_item:
            return
        filename = toUtf8(item.text(0))
        newname = self.renamePath(filename)
        if newname:
            if os.path.dirname(newname) == self.root_path:
                item.setText(0, os.path.basename(newname))
            else:
                self.root_item.removeChild(item)

    def onDelete(self):
        item = self.currentItem()
        if not item or item == self.root_item:
            return
        filename = toUtf8(item.text(0))
        if self.deletePath(filename):
            self.root_item.removeChild(item)

    def onRefresh(self):
        self.setRootPath(self.root_path, True)

    def onWindowsExplorer(self):
        subprocess.Popen('explorer "%s"' % self.root_path, shell=True)

    def onDriveChanged(self, drive, checked):
        self.setRootPath(drive)

    def dragMoveEvent(self, event):
        super(Explorer, self).dragMoveEvent(event)
        if (event.source() == self and
                self.dragDropMode() == QtWidgets.QAbstractItemView.InternalMove):
            item = self.itemAt(event.pos())
            if item is None:
                event.ignore()
            elif item.flags() & QtCore.Qt.ItemIsDropEnabled:
                event.accept()
            else:
                event.ignore()

    def dropEvent(self, event):
        # InternalMove mode will ignore function dropMimeData
        if (event.source() == self and
                (event.dropAction == QtCore.Qt.MoveAction or
                 self.dragDropMode() == QtWidgets.QAbstractItemView.InternalMove)):
            drop_item = self.itemAt(event.pos())
            if drop_item is None:
                return
            if drop_item == self.root_item:
                dest_dir = os.path.dirname(self.root_path)
            else:
                dest_dir = os.path.join(self.root_path, toUtf8(drop_item.text(0)))
            mimeData = event.mimeData()
            if mimeData.hasFormat('application/x-qabstractitemmodeldatalist'):
                bytearray = mimeData.data('application/x-qabstractitemmodeldatalist')
                for drag_item in self.decodeMimeData(bytearray):
                    name = toUtf8(drag_item.text(0))
                    oldpath = os.path.join(self.root_path, name)
                    newpath = os.path.join(dest_dir, name)
                    if self.movePath(oldpath, newpath):
                        self.root_item.removeChild(drag_item)
        else:
            return super(Explorer, self).dropEvent(event)

    def decodeMimeData(self, bytearray):
        data = []
        ds = QtCore.QDataStream(bytearray)
        root_index = self.indexFromItem(self.root_item)
        while not ds.atEnd():
            row = ds.readInt32()
            column = ds.readInt32()
            index = root_index.child(row, column)
            map_items = ds.readInt32()
            for i in range(map_items):
                ds.readInt32()    # QtCore.Qt.ItemDataRole(key)
                value = QtCore.QVariant()
                ds >> value
            item = self.itemFromIndex(index)
            data.append(item)
        return data

    def addRoot(self, name):
        root = QtWidgets.QTreeWidgetItem(self)
        root.setText(0, self.getDisplayName(name))
        root.setIcon(0, self.getFileIcon('/'))
        return root

    def appendItem(self, rootitem, name):
        if not rootitem:
            raise Exception('Add root item firstly!')
        child = QtWidgets.QTreeWidgetItem(rootitem)
        child.setText(0, name)
        child.setIcon(0, self.getFileIcon(name))
        path = os.path.join(self.root_path, name)
        if os.path.isfile(path):
            child.setFlags(child.flags() & ~QtCore.Qt.ItemIsDropEnabled)
        return child

    def setRootPath(self, path, refresh=False):
        """ set exporer root path """
        def pathkey(path):
            if os.path.isdir(os.path.join(self.root_path, path)):
                prefix = '0_'
            else:
                prefix = '1_'
            path = prefix + path
            return path.lower()

        if not os.path.exists(path):
            return
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        if not refresh and path == self.root_path:
            return
        for act in self.driveGroup.actions():
            drive = toUtf8(act.text())
            if drive[:2] == path[:2]:
                act.setChecked(True)
        self.clear()
        self.root_path = os.path.realpath(path)
        os.chdir(path)
        self.root_item = self.addRoot(self.root_path)
        dirs = sorted(os.listdir(self.root_path), key=pathkey)
        for d in dirs:
            if d.startswith('.'):
                continue
            self.appendItem(self.root_item, d)
        self.expandItem(self.root_item)

    def getDisplayName(self, name):
        """ directory display name """
        client_width = self.width() - self.padding_right
        char_width = self.fontMetrics().width(' ')
        disp_char_num = int(client_width / char_width) - 1
        full_char = 'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        w = sum(east_asian_width(x) == 'W' or x in full_char for x in name)
        char_length = len(name) + w
        if (char_length - 3) > disp_char_num:
            display_name = '<<<%s' % name[-disp_char_num + 4:]
        else:
            display_name = name
        return display_name

    def getRootPath(self):
        return self.root_path

    def getFileIcon(self, name, style=None):
        if name == '/':
            if self.qstyle:
                icon = self.qstyle.standardIcon(QtWidgets.QStyle.SP_DirOpenIcon)
            else:
                icon = self.iconProvider.icon(self.iconProvider.Folder)
        else:
            path = os.path.join(self.root_path, name)
            if os.path.isdir(path):
                if self.qstyle:
                    icon = self.qstyle.standardIcon(QtWidgets.QStyle.SP_DirIcon)
                else:
                    icon = self.iconProvider.icon(self.iconProvider.Folder)
            else:
                icon = self.iconProvider.icon(QtCore.QFileInfo(path))
        return icon

    def loadFile(self, filename):
        """
        set root directory and sent signal to request load file.
        """
        if filename:
            if os.path.exists(filename):
                logger.debug('Loading file: %s', filename)
                self.setRootPath(os.path.dirname(filename))
                self.fileLoaded.emit(filename)
        return

    def deletePath(self, filename):
        path = os.path.join(self.root_path, filename)
        if not os.path.exists(path):
            return False
        ret = QtWidgets.QMessageBox.question(self,
                                             self.tr('Delete'),
                                             self.tr('Do you want to delete "%s"?') % (filename),
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                    self.fileDeleted.emit(path)
                return True
            except OSError as err:
                QtWidgets.QMessageBox.critical(self,
                                           self.tr('Error'),
                                           err)
        return False

    def newDirectory(self):
        text, ok = QtWidgets.QInputDialog.getText(self,
                                                  self.tr('New directory'),
                                                  self.tr('Please input name:'))
        if ok:
            filename = toUtf8(text)
            path = os.path.join(self.root_path, filename)
            if os.path.exists(path):
                QtWidgets.QMessageBox.warning(self,
                                              self.tr('File exists'),
                                              self.tr('File "%s" has existed!') % (filename)
                                              )
            else:
                os.mkdir(path)
                return filename
        return

    def renamePath(self, filename):
        path = os.path.join(self.root_path, filename)
        if not os.path.exists(path):
            return
        text, ok = QtWidgets.QInputDialog.getText(self,
                                                  self.tr('Rename'),
                                                  self.tr('Please input new name:'),
                                                  QtWidgets.QLineEdit.Normal,
                                                  filename)
        if ok:
            newname = toUtf8(text)
            newpath = os.path.abspath(os.path.join(self.root_path, newname))
            return self.movePath(path, newpath)
        return

    def movePath(self, src, dest):
        if os.path.exists(dest):
            QtWidgets.QMessageBox.warning(
                self,
                self.tr('File exists'),
                self.tr('File "%s" has existed!') % (os.path.basename(dest)),
            )
            return
        try:
            os.rename(src, dest)
        except OSError as err:
            QtWidgets.QMessageBox.critical(
                self,
                self.tr('Error'),
                err,
            )
            return
        if os.path.isfile(dest):
            self.fileRenamed.emit(src, dest)
        return dest

    def getDrivesPath(self):
        if sys.platform != 'win32':
            return []
        drivers = []
        for drive in toUtf8('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            path = '%s:\\' % drive
            if os.path.exists(path):
                drivers.append(path)
        return drivers


class Workspace(QtWidgets.QTreeWidget):
    type_root = QtWidgets.QTreeWidgetItem.UserType
    type_folder = type_root + 1
    type_file = type_root + 2
    role_path = QtCore.Qt.UserRole

    fileLoaded = QtCore.pyqtSignal('QString')
    fileDeleted = QtCore.pyqtSignal('QString')
    fileRenamed = QtCore.pyqtSignal('QString', 'QString')
    fileNew = QtCore.pyqtSignal('QString')

    def __init__(self, parent, style=None):
        super(Workspace, self).__init__(parent)
        self.header().close()
        self.padding_right = 32
        # QStyle, such as QtWidgets.QStyleFactory.create('windows')
        self.qstyle = style
        # QT BUG, must keep reference or crash
        self.iconProvider = QtWidgets.QFileIconProvider()

        # self.setRootIsDecorated(False)
        self.setExpandsOnDoubleClick(True)

        self.itemActivated.connect(self.onItemActivated)
        # self.pathLoaded.connect(self.onPathLoaded)
        # popup menu
        newRstAction = QtWidgets.QAction(self.tr('reStructedText'), self)
        newRstAction.triggered.connect(partial(self.onNewFile, 'rst'))
        newMdAction = QtWidgets.QAction(self.tr('Markdown'), self)
        newMdAction.triggered.connect(partial(self.onNewFile, 'md'))

        newdirectoryAction = QtWidgets.QAction(self.tr('New &directory'), self)
        newdirectoryAction.triggered.connect(self.onNewDirectory)
        self.renameAction = QtWidgets.QAction(self.tr('&Rename...'), self)
        self.renameAction.triggered.connect(self.onRename)
        self.deleteAction = QtWidgets.QAction(self.tr('Delete'), self)
        self.deleteAction.triggered.connect(self.onDelete)
        refreshAction = QtWidgets.QAction(self.tr('Refresh'), self)
        refreshAction.triggered.connect(self.onRefresh)
        explorerAction = QtWidgets.QAction(self.tr('Windows Explorer'), self)
        explorerAction.triggered.connect(self.onWindowsExplorer)

        self.popupMenu = QtWidgets.QMenu(self)
        submenu = QtWidgets.QMenu(self.tr('New'), self.popupMenu)
        submenu.addAction(newRstAction)
        submenu.addAction(newMdAction)
        self.popupMenu.addMenu(submenu)

        self.popupMenu.addAction(newdirectoryAction)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(self.renameAction)
        self.popupMenu.addAction(self.deleteAction)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(refreshAction)
        self.popupMenu.addAction(explorerAction)
        self.popupMenu.addSeparator()
        # drag & drop
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def contextMenuEvent(self, event):
        if event.reason() == event.Mouse:
            pos = event.globalPos()
            item = self.itemAt(event.pos())
        else:
            pos = None
            item = self.currentItem()
            self.scrollToItem(item)
        # if item is None:
        #     item = self.root_item
        #     self.scrollToItem(item)
        if pos is None:
            rect = self.visualItemRect(item)
            pos = self.mapToGlobal(rect.center())
        item = self.currentItem()
        self.renameAction.setEnabled(bool(item) and item.type() != self.type_root)
        self.deleteAction.setEnabled(bool(item))
        self.popupMenu.popup(pos)

    def onItemActivated(self, item, col):
        if col > 0:
            return
        if item.type() == self.type_root:
            if item.childCount() == 0:
                self.expandDir(item)
        elif item.type() == self.type_folder:
            if item.childCount() == 0:
                self.expandDir(item)
        else:
            path = os.path.join(item.data(0, self.role_path), item.text(0))
            self.fileLoaded.emit(path)

    def onNewFile(self, label):
        self.fileNew.emit(label)

    def onNewDirectory(self):
        path = self.getCurrentPath()
        sub_path = self.doNewDirectory(path)
        if sub_path:
            item = self.currentItem()
            if item.type() == self.type_file:
                item = item.parent()
            item.addChild(self.createNode(path, sub_path))

    def onRename(self):
        item = self.currentItem()
        if item.type() == self.type_root:
            return
        path = os.path.join(item.data(0, self.role_path), item.text(0))
        newpath = self.doRenamePath(path)
        if newpath:
            if os.path.dirname(newpath) == os.path.dirname(path):
                item.setText(0, os.path.basename(newpath))
            elif newpath.startswith(os.path.dirname(path)):
                parent = item.parent()
                parent.takeChildren()
                self.expandDir(parent)
            else:
                parent = item.parent()
                parent.removeChild(item)
                del item

    def onDelete(self):
        item = self.currentItem()
        if item.type() == self.type_root:
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)
            del item
            return
        path = os.path.join(item.data(0, self.role_path), item.text(0))
        if self.doDeletePath(path):
            parent = item.parent()
            parent.removeChild(item)
            del item

    def onRefresh(self):
        item = self.currentItem()
        if item.type() == self.type_file:
            item = item.parent()
        item.takeChildren()
        self.expandDir(item)

    def onWindowsExplorer(self):
        path = self.getCurrentPath()
        subprocess.Popen('explorer "%s"' % path, shell=True)

    def dragMoveEvent(self, event):
        super(Workspace, self).dragMoveEvent(event)
        if (event.source() == self and
                self.dragDropMode() == QtWidgets.QAbstractItemView.InternalMove):
            item = self.itemAt(event.pos())
            if item is None:
                event.ignore()
            elif item.flags() & QtCore.Qt.ItemIsDropEnabled:
                event.accept()
            else:
                event.ignore()

    def dropEvent(self, event):
        # InternalMove mode will ignore function dropMimeData
        if (event.source() == self and
                (event.dropAction == QtCore.Qt.MoveAction or
                 self.dragDropMode() == QtWidgets.QAbstractItemView.InternalMove)):
            drop_item = self.itemAt(event.pos())
            if drop_item is None:
                return
            if drop_item.type() == self.type_file:
                drop_item = drop_item.parent()
            if drop_item.type() == self.type_folder:
                drop_path = os.path.join(
                    drop_item.data(0, self.role_path), drop_item.text(0))
            else:
                drop_path = drop_item.data(0, self.role_path)
            mimeData = event.mimeData()
            if mimeData.hasFormat('application/x-qabstractitemmodeldatalist'):
                bytearray = mimeData.data('application/x-qabstractitemmodeldatalist')
                for drag_item in self._decodeMimeData(bytearray):
                    oldpath = os.path.join(
                        drag_item.data(0, self.role_path), drag_item.text(0))
                    newpath = os.path.join(drop_path, drag_item.text(0))
                    if self.doMovePath(oldpath, newpath):
                        parent = drag_item.parent()
                        parent.removeChild(drag_item)
                        drag_item.setData(0, self.role_path, drop_path)
                        drop_item.addChild(drag_item)
        else:
            return super(Workspace, self).dropEvent(event)

    def _decodeMimeData(self, bytearray):
        data = []
        ds = QtCore.QDataStream(bytearray)
        while not ds.atEnd():
            ds.readInt32()  # row
            ds.readInt32()  # column
            map_items = ds.readInt32()
            data_item = {}
            for i in range(map_items):
                key = ds.readInt32()
                value = QtCore.QVariant()
                ds >> value
                data_item[QtCore.Qt.ItemDataRole(key)] = value
            items = self.findItems(
                data_item[QtCore.Qt.DisplayRole].value(),
                QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
            for item in items:
                if item.data(0, self.role_path) == data_item[self.role_path]:
                    data.append(item)
                    break
        return data

    def dropMimeData(self, parent, index, data, action):
        # don't call?
        print(parent, index, data, action)
        return False

    def createRoot(self, path, name):
        root = QtWidgets.QTreeWidgetItem(self.type_root)
        root.setFlags(root.flags() & ~QtCore.Qt.ItemIsDragEnabled)
        root.setText(0, name)
        root.setIcon(0, self.getFileIcon(path))
        root.setData(0, self.role_path, path)
        return root

    def createNode(self, path, name):
        if os.path.isdir(os.path.join(path, name)):
            child = QtWidgets.QTreeWidgetItem(self.type_folder)
        else:
            child = QtWidgets.QTreeWidgetItem(self.type_file)
        child.setText(0, name)
        child.setIcon(0, self.getFileIcon(os.path.join(path, name)))
        child.setData(0, self.role_path, path)
        return child

    def expandDir(self, parent):
        def pathkey(key):
            if os.path.isdir(os.path.join(path, key)):
                prefix = '0_'
            else:
                prefix = '1_'
            key = prefix + key
            return key.lower()

        if parent.type() == self.type_root:
            path = parent.data(0, self.role_path)
        elif parent.type() == self.type_folder:
            path = os.path.join(parent.data(0, self.role_path), parent.text(0))
        dirs = sorted(os.listdir(path), key=pathkey)
        children = []
        for d in dirs:
            if d.startswith('.'):
                continue
            children.append(self.createNode(path, d))
        parent.addChildren(children)

    def appendRootPath(self, path):
        if not os.path.exists(path):
            return
        if os.path.isfile(path):
            path = os.path.dirname(path)

        root_path = os.path.abspath(path)
        root_name = os.path.basename(root_path)
        root_item = self.createRoot(root_path, root_name)

        self.expandDir(root_item)
        self.addTopLevelItem(root_item)

    def getFileIcon(self, path, style=None):
        if path == '/':
            if self.qstyle:
                icon = self.qstyle.standardIcon(QtWidgets.QStyle.SP_DirOpenIcon)
            else:
                icon = self.iconProvider.icon(self.iconProvider.Folder)
        else:
            if os.path.isdir(path):
                if self.qstyle:
                    icon = self.qstyle.standardIcon(QtWidgets.QStyle.SP_DirIcon)
                else:
                    icon = self.iconProvider.icon(self.iconProvider.Folder)
            else:
                icon = self.iconProvider.icon(QtCore.QFileInfo(path))
        return icon

    def doDeletePath(self, path):
        if not os.path.exists(path):
            return False
        ret = QtWidgets.QMessageBox.question(
            self,
            self.tr('Delete'),
            self.tr('Do you want to delete "%s"?') % (os.path.basename(path)),
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No)
        if ret == QtWidgets.QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                    self.fileDeleted.emit(path)
                return True
            except OSError as err:
                QtWidgets.QMessageBox.critical(
                    self, self.tr('Error'), err)
        return False

    def doNewDirectory(self, root):
        value, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr('New directory'),
            self.tr('Please input name:'))
        if ok:
            value = toUtf8(value)
            path = os.path.join(root, value)
            if os.path.exists(path):
                QtWidgets.QMessageBox.warning(
                    self,
                    self.tr('File exists'),
                    self.tr('File "%s" has existed!') % (value))
            else:
                os.mkdir(path)
                return value

    def doRenamePath(self, path):
        if not os.path.exists(path):
            return
        value, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr('Rename'),
            self.tr('Please input new name:'),
            QtWidgets.QLineEdit.Normal,
            path)
        if ok:
            value = os.path.abspath(toUtf8(value))
            return self.doMovePath(path, value)

    def doMovePath(self, src, dest):
        if os.path.exists(dest):
            QtWidgets.QMessageBox.warning(
                self,
                self.tr('File exists'),
                self.tr('File "%s" has existed!') % (os.path.basename(dest)),
            )
            return
        try:
            os.rename(src, dest)
        except OSError as err:
            QtWidgets.QMessageBox.critical(
                self,
                self.tr('Error'),
                err,
            )
            return
        if os.path.isfile(dest):
            self.fileRenamed.emit(src, dest)
        return dest

    def getRootPaths(self):
        root_paths = []
        for index in range(self.topLevelItemCount()):
            root = self.topLevelItem(index)
            path = root.data(0, self.role_path)
            root_paths.append(path)
        return root_paths

    def getCurrentPath(self):
        item = self.currentItem()
        path = item.data(0, self.role_path)
        if item.type() == self.type_folder:
            path = os.path.join(path, item.text(0))
        return path

    def refreshPath(self, path):
        self.onRefresh()
