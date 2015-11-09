

def toUtf8(text):
    if isinstance(text, bytes):
        return text.decode(encoding='utf-8')
    return text


def toBytes(text):
    if isinstance(text, str):
        return text.encode(encoding='utf-8')
    return text
