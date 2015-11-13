import os
import fnmatch


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
