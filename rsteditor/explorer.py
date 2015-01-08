
import os
import os.path
import sys
import shutil
import logging
from functools import partial

from PyQt4 import QtGui
from PyQt4 import QtCore

from rsteditor.util import toUtf8


class Explorer(QtGui.QTreeWidget):
    fileLoaded = QtCore.pyqtSignal('QString')
    pathLoaded = QtCore.pyqtSignal('QString')
    fileDeleted = QtCore.pyqtSignal('QString')
    fileRenamed = QtCore.pyqtSignal('QString', 'QString')
    fileNew = QtCore.pyqtSignal()

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
        # popup menu
        newAction = QtGui.QAction(self.tr('&New'), self)
        newAction.triggered.connect(self.onNewFile)
        newdirectoryAction = QtGui.QAction(self.tr('New &directory'), self)
        newdirectoryAction.triggered.connect(self.onNewDirectory)
        self.renameAction = QtGui.QAction(self.tr('&Rename...'), self)
        self.renameAction.triggered.connect(self.onRename)
        self.deleteAction = QtGui.QAction(self.tr('Delete'), self)
        self.deleteAction.triggered.connect(self.onDelete)
        refreshAction = QtGui.QAction(self.tr('Refresh'), self)
        refreshAction.triggered.connect(self.onRefresh)
        drivers_path = self.getDrivesPath()
        self.driveGroup = QtGui.QActionGroup(self)
        for drive_path in drivers_path:
            act = QtGui.QAction(drive_path,
                                self,
                                checkable=True)
            act.triggered.connect(partial(self.onDriveChanged, drive_path))
            self.driveGroup.addAction(act)
        self.popupMenu = QtGui.QMenu(self)
        self.popupMenu.addAction(newAction)
        self.popupMenu.addAction(newdirectoryAction)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(self.renameAction)
        self.popupMenu.addAction(self.deleteAction)
        self.popupMenu.addSeparator()
        self.popupMenu.addAction(refreshAction)
        self.popupMenu.addSeparator()
        for act in self.driveGroup.actions():
            self.popupMenu.addAction(act)

    def resizeEvent(self, event):
        if self.root_item:
            self.root_item.setText(0, self.getDisplayName(self.root_path))
            self.setColumnWidth(0, -1)
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

    def onNewFile(self):
        self.fileNew.emit()

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
            item.setText(0, newname)

    def onDelete(self):
        item = self.currentItem()
        if not item or item == self.root_item:
            return
        filename = toUtf8(item.text(0))
        if self.deletePath(filename):
            self.removeItemWidget(item, 0)

    def onRefresh(self):
        self.setRootPath(self.root_path, True)

    def onDriveChanged(self, drive, checked):
        self.setRootPath(drive)

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

    def setRootPath(self, path, refresh=False):
        """ set exporer root path """
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
        self.root_path = path
        os.chdir(path)
        self.root_item = self.addRoot(self.getDisplayName(self.root_path))
        dirs = sorted(os.listdir(self.root_path))
        for d in dirs:
            if d.startswith('.'):
                continue
            self.appendItem(self.root_item, d)
        self.expandItem(self.root_item)

    def getDisplayName(self, name):
        """ directory display name """
        client_width = self.width() - 32
        char_width = self.fontMetrics().width(' ')
        disp_char_num = client_width / char_width - 1
        if (len(name) - 3) > disp_char_num:
            display_name = '<<<%s' % name[-disp_char_num + 3:]
        else:
            display_name = name
        return display_name

    def getRootPath(self):
        return self.root_path

    def loadFile(self, filename):
        """
        set root directory and sent signal to request load file.
        """
        if filename:
            if os.path.exists(filename):
                logging.debug('Loading file: %s', filename)
                self.setRootPath(os.path.dirname(filename))
                self.fileLoaded.emit(filename)
        return

    def deletePath(self, filename):
        path = os.path.join(self.root_path, filename)
        if not os.path.exists(path):
            return False
        ret = QtGui.QMessageBox.question(self,
                                         self.tr('Delete'),
                                         self.tr('Do you want to delete "%1"?').arg(filename),
                                         QtGui.QMessageBox.Yes,
                                         QtGui.QMessageBox.No)
        if ret == QtGui.QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                    self.fileDeleted.emit(path)
                return True
            except OSError as err:
                QtGui.QMessageBox.critical(self,
                                           self.tr('Error'),
                                           err)
        return False

    def newDirectory(self):
        text, ok = QtGui.QInputDialog.getText(self,
                                              self.tr('New directory'),
                                              self.tr('Please input name:'))
        if ok:
            filename = toUtf8(text)
            path = os.path.join(self.root_path, filename)
            if os.path.exists(path):
                QtGui.QMessageBox.warning(self,
                                          self.tr('File exists'),
                                          self.tr('File "%1" has existed!').arg(filename)
                                          )
            else:
                os.mkdir(path)
                return filename
        return

    def renamePath(self, filename):
        path = os.path.join(self.root_path, filename)
        if not os.path.exists(path):
            return False
        text, ok = QtGui.QInputDialog.getText(self,
                                              self.tr('Rename'),
                                              self.tr('Please input new name:'),
                                              QtGui.QLineEdit.Normal,
                                              filename)
        if ok:
            newname = toUtf8(text)
            newpath = os.path.join(self.root_path, newname)
            if os.path.exists(newpath):
                QtGui.QMessageBox.warning(self,
                                          self.tr('File exists'),
                                          self.tr('File "%1" has existed!').arg(newname)
                                          )
            else:
                os.rename(path, newpath)
                if os.path.isfile(newpath):
                    self.fileRenamed.emit(path, newpath)
                return newname
        return

    def getDrivesPath(self):
        if sys.platform != 'win32':
            return []
        drivers = []
        for drive in toUtf8('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            path = '%s:\\' % drive
            if os.path.exists(path):
                drivers.append(path)
        return drivers
