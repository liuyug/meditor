import os
import fnmatch
import urllib.request
import zipfile

from PyQt5.QtWidgets import QProgressDialog


def toUtf8(text):
    if isinstance(text, bytes):
        return text.decode(encoding='utf-8')
    return text


def toBytes(text):
    if isinstance(text, str):
        return text.encode(encoding='utf-8')
    return text


def myglob(root_path, patterns, rel_path=None):
    """
    pattern: ['*.c', '*.cpp', '*.css', ...]
    """
    matches = []
    for root, dirnames, filenames in os.walk(root_path):
        for pattern in patterns:
            for filename in fnmatch.filter(filenames, pattern):
                abs_path = os.path.join(root, filename)
                if rel_path:
                    matches.append(os.path.relpath(abs_path, rel_path))
                else:
                    matches.append(abs_path)
    return matches


def get_include_files(src, patterns, dest):
    """
    return: [(src_file, dest_file), ...]
    """
    files = []
    for filename in myglob(src, patterns, src):
        files.append([
            os.path.join(src, filename),
            os.path.join(dest, filename)
        ])
    return files


def download(src, dest, parent=None, text=None, block=8192):
    def _download(response, dest_file, dest_size):
        dlg = QProgressDialog(text, 'Cancel', 0, dest_size, parent)
        dlg.setWindowTitle('Markup Editor')
        dlg.setModal(True)
        count = 0
        while True:
            data = response.read(block)
            if not data:
                break
            count += len(data)
            dlg.setValue(count)
            if dlg.wasCanceled():
                dlg.close()
                return False
            dest_file.write(data)
        dlg.close()
        return True

    with open(dest, 'wb') as dest_file:
        with urllib.request.urlopen(src) as response:
            s_size = response.getheader('Content-Length')
            if not s_size:
                return False
            dest_size = int(response.getheader('Content-Length'))
            return _download(response, dest_file, dest_size)


def unzip(src, dest=None, parent=None, text=None):
    zip_file = zipfile.ZipFile(src)
    total = sum(f.file_size for f in zip_file.infolist())
    count = 0

    dlg = QProgressDialog(text, 'Cancel', 0, total, parent)
    dlg.setWindowTitle('Markup Editor')
    dlg.setModal(True)
    for f in zip_file.infolist():
        count += f.file_size
        dlg.setValue(count)
        if dlg.wasCanceled():
            dlg.close()
            break
        zip_file.extract(f, dest)
    dlg.close()
