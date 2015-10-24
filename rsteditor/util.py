

def toUtf8(text):
    if isinstance(text, bytes):
        return text.decode(encoding='utf-8')
    return text
