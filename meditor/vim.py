
from functools import partial

from PyQt5 import QtCore, QtWidgets
from PyQt5.Qsci import QsciScintilla


VIM_MODE = {
    0: 'normal',
    1: 'insert',
    2: 'command',
    3: 'visual',
    4: 'v-block',  # visual block
    'normal': 0,
    'insert': 1,
    'command': 2,
    'visual': 3,
    'v-block': 4,
}

QsciScintilla

KEY_SCINTILLA = {
    'j': QsciScintilla.SCI_LINEDOWN,
    # 'i': QsciScintilla.SCI_LINESCROLLDOWN,
    'k': QsciScintilla.SCI_LINEUP,
    # 'i': QsciScintilla.SCI_LINESCROLLUP,
    # 'i': QsciScintilla.SCI_PARADOWN,
    # 'i': QsciScintilla.SCI_PARAUP,
    'h': QsciScintilla.SCI_CHARLEFT,
    'l': QsciScintilla.SCI_CHARRIGHT,
    'b': QsciScintilla.SCI_WORDLEFT,       # begin of previous word
    'B': QsciScintilla.SCI_WORDLEFTEND,    # end of previous word
    'e': QsciScintilla.SCI_WORDRIGHT,      # begin of next word
    'E': QsciScintilla.SCI_WORDRIGHTEND,   # end of next word
    'W': QsciScintilla.SCI_WORDPARTLEFT,   # previous word part
    'w': QsciScintilla.SCI_WORDPARTRIGHT,  # next word part
    '0': QsciScintilla.SCI_HOME,
    # 'i': QsciScintilla.SCI_HOMEDISPLAY,
    # 'i': QsciScintilla.SCI_HOMEWRAP,
    '^': QsciScintilla.SCI_VCHOME,
    # 'i': QsciScintilla.SCI_VCHOMEWRAP,
    # 'i': QsciScintilla.SCI_VCHOMEDISPLAY,
    '$': QsciScintilla.SCI_LINEEND,
    # 'i': QsciScintilla.SCI_LINEENDDISPLAY,
    # 'i': QsciScintilla.SCI_LINEENDWRAP,
    'gg': QsciScintilla.SCI_DOCUMENTSTART,
    'G': QsciScintilla.SCI_DOCUMENTEND,
    '\x02': QsciScintilla.SCI_PAGEUP,  # ctrl + b
    '\x06': QsciScintilla.SCI_PAGEDOWN,  # ctrl + f
    # 'i': QsciScintilla.SCI_STUTTEREDPAGEUP,
    # 'i': QsciScintilla.SCI_STUTTEREDPAGEDOWN,
    'X': QsciScintilla.SCI_DELETEBACK,
    # 'd': QsciScintilla.SCI_DELETEBACKNOTLINE,
    'db': QsciScintilla.SCI_DELWORDLEFT,
    'dw': QsciScintilla.SCI_DELWORDRIGHT,
    # 'dw': QsciScintilla.SCI_DELWORDRIGHTEND,
    # 'i': QsciScintilla.SCI_DELLINELEFT,
    'D': QsciScintilla.SCI_DELLINERIGHT,
    # 'd': QsciScintilla.SCI_LINEDELETE,
    'dd': QsciScintilla.SCI_LINECUT,
    'yy': QsciScintilla.SCI_LINECOPY,
    # 'i': QsciScintilla.SCI_LINETRANSPOSE,
    # 'i': QsciScintilla.SCI_LINEREVERSE,
    # 'i': QsciScintilla.SCI_LINEDUPLICATE,
    'gu': QsciScintilla.SCI_LOWERCASE,
    'gU': QsciScintilla.SCI_UPPERCASE,
    # 'i': QsciScintilla.SCI_CANCEL,
    # 'i': QsciScintilla.SCI_EDITTOGGLEOVERTYPE,
    'o': QsciScintilla.SCI_NEWLINE,
    # 'o': QsciScintilla.SCI_FORMFEED,
    # 'i': QsciScintilla.SCI_TAB,
    # 'i': QsciScintilla.SCI_BACKTAB,
    # 'i': QsciScintilla.SCI_SELECTIONDUPLICATE,
    # 'i': QsciScintilla.SCI_VERTICALCENTRECARET,
    # 'i': QsciScintilla.SCI_MOVESELECTEDLINESUP,
    # 'i': QsciScintilla.SCI_MOVESELECTEDLINESDOWN,
    # 'i': QsciScintilla.SCI_SCROLLTOSTART,
    # 'i': QsciScintilla.SCI_SCROLLTOEND,
    # other message
    'u': QsciScintilla.SCI_UNDO,
    '.': QsciScintilla.SCI_REDO,
    'y': QsciScintilla.SCI_COPY,
    'x': QsciScintilla.SCI_CUT,
    'd': QsciScintilla.SCI_CUT,
    'P': QsciScintilla.SCI_PASTE,
}

KEY_VISUAL_SCINTILLA = {
    'j': QsciScintilla.SCI_LINEDOWNEXTEND,
    'k': QsciScintilla.SCI_LINEUPEXTEND,
    # 'i': QsciScintilla.SCI_PARADOWNEXTEND,
    # 'i': QsciScintilla.SCI_PARAUPEXTEND,
    'h': QsciScintilla.SCI_CHARLEFTEXTEND,
    'l': QsciScintilla.SCI_CHARRIGHTEXTEND,
    'b': QsciScintilla.SCI_WORDLEFTEXTEND,
    'e': QsciScintilla.SCI_WORDRIGHTEXTEND,
    'B': QsciScintilla.SCI_WORDLEFTENDEXTEND,
    'E': QsciScintilla.SCI_WORDRIGHTENDEXTEND,
    'W': QsciScintilla.SCI_WORDPARTLEFTEXTEND,
    'w': QsciScintilla.SCI_WORDPARTRIGHTEXTEND,
    '0': QsciScintilla.SCI_HOMEEXTEND,
    # 'i': QsciScintilla.SCI_HOMEDISPLAYEXTEND,
    # 'i': QsciScintilla.SCI_HOMEWRAPEXTEND,
    '^': QsciScintilla.SCI_VCHOMEEXTEND,
    # 'i': QsciScintilla.SCI_VCHOMEWRAPEXTEND,
    # 'i': QsciScintilla.SCI_VCHOMEDISPLAYEXTEND,
    '$': QsciScintilla.SCI_LINEENDEXTEND,
    # 'i': QsciScintilla.SCI_LINEENDDISPLAYEXTEND,
    # 'i': QsciScintilla.SCI_LINEENDWRAPEXTEND,
    'gg': QsciScintilla.SCI_DOCUMENTSTARTEXTEND,
    'G': QsciScintilla.SCI_DOCUMENTENDEXTEND,
    '\x02': QsciScintilla.SCI_PAGEUPEXTEND,  # ctrl + b
    '\x06': QsciScintilla.SCI_PAGEDOWNEXTEND,  # ctrl + f
    # 'i': QsciScintilla.SCI_STUTTEREDPAGEUPEXTEND,
    # 'i': QsciScintilla.SCI_STUTTEREDPAGEDOWNEXTEND,
}

KEY_VBLOCK_SCINTILLA = {
    'j': QsciScintilla.SCI_LINEDOWNRECTEXTEND,
    'k': QsciScintilla.SCI_LINEUPRECTEXTEND,
    'h': QsciScintilla.SCI_CHARLEFTRECTEXTEND,
    'l': QsciScintilla.SCI_CHARRIGHTRECTEXTEND,
    '0': QsciScintilla.SCI_HOMERECTEXTEND,
    '^': QsciScintilla.SCI_VCHOMERECTEXTEND,
    '$': QsciScintilla.SCI_LINEENDRECTEXTEND,
    '\x02': QsciScintilla.SCI_PAGEUPRECTEXTEND,  # ctrl + b
    '\x06': QsciScintilla.SCI_PAGEDOWNRECTEXTEND,  # ctrl + f
}


class VimCommand(QtWidgets.QLineEdit):
    escapePressed = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.clear()
            self.escapePressed.emit()
        else:
            super(VimCommand, self).keyPressEvent(event)


class VimEmulator(QtWidgets.QWidget):
    _mode_label = None
    _command_edit = None
    _mode = 0
    _editor = None
    _leader_char = ''
    _vertical_edit = None

    def __init__(self, parent):
        super(VimEmulator, self).__init__(parent)
        self._mode_label = QtWidgets.QLabel(self)
        font = self._mode_label.font()
        font.setBold(True)
        self._mode_label.setFont(font)

        self._command_edit = VimCommand(self)

        h_layout = QtWidgets.QHBoxLayout(self)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(self._mode_label)
        h_layout.addWidget(self._command_edit)

        self._mode_label.setBuddy(self._command_edit)

        self._command_edit.returnPressed.connect(
            partial(self.handleCommandMode, 'return'))
        self._command_edit.escapePressed.connect(
            partial(self.handleCommandMode, 'escape'))

        self.setMode('normal')
        self._vertical_edit = {}

    def handle(self, key, text, editor):
        print('debug key', hex(key), repr(text))
        if key == QtCore.Qt.Key_Escape:
            if self._vertical_edit:
                line, index = editor.getCursorPosition()
                if line == self._vertical_edit['from']  \
                        and index > self._vertical_edit['index']:
                    editor.setSelection(
                        self._vertical_edit['from'], self._vertical_edit['index'],
                        line, index,
                    )
                    text = editor.selectedText()
                    editor.selectAll(False)
                    editor.setCursorPosition(
                        self._vertical_edit['from'], self._vertical_edit['index'])
                    for x in range(
                            self._vertical_edit['from'] + 1,
                            self._vertical_edit['to'] + 1):
                        if len(editor.text(x)) > self._vertical_edit['index']:
                            editor.insertAt(text, x, self._vertical_edit['index'])
                self._vertical_edit = {}
            self.setMode('normal')
            self._command_edit.clear()
            editor.setFocus()
            editor.selectAll(False)
            self._leader_char = ''
            return True
        if self._mode == VIM_MODE['normal']:
            return self.handleNormalMode(key, text, editor)
        elif self._mode == VIM_MODE['insert']:
            return self.handleInsertMode(key, text, editor)
        elif self._mode == VIM_MODE['visual']:
            return self.handleVisualMode(key, text, editor)
        elif self._mode == VIM_MODE['v-block']:
            return self.handleVisualBlockMode(key, text, editor)
        return False

    def handleNormalMode(self, key, text, editor):
        print('normal', hex(key), repr(text))
        if not text:
            return False
        if self._leader_char:
            key = self._leader_char + text
            if key in ['gu', 'gU']:
                if editor.hasSelectedText():
                    if key in KEY_SCINTILLA:
                        editor.SendScintilla(KEY_SCINTILLA[key])
                    self._leader_char = ''
                    editor.selectAll(False)
                else:
                    self._leader_char = key
            elif self._leader_char in ['gu', 'gU']:
                if text in KEY_VISUAL_SCINTILLA:
                    editor.SendScintilla(KEY_VISUAL_SCINTILLA[text])
                    editor.SendScintilla(KEY_SCINTILLA[self._leader_char])
                    editor.selectAll(False)
                self._leader_char = ''
            elif self._leader_char == '/':
                self._leader_char = ''
                if text == '\r':
                    editor.findNext()
                elif text.isprintable():
                    self.setMode('command')
                    self._command_edit.setText(':' + key)
                    self._command_edit.setFocus()
                    self._editor = editor
            else:
                if key in KEY_SCINTILLA:
                    editor.SendScintilla(KEY_SCINTILLA[key])
                self._leader_char = ''
        elif text == ':':
            self.setMode('command')
            self._command_edit.setText(':')
            self._command_edit.setFocus()
            self._editor = editor
        elif text == 'i':
            self.setMode('insert')
        elif text == 'v':
            self.setMode('visual')
        elif text == '\x16':  # ctrl + v
            self.setMode('v-block')
        elif text == 'y':
            if editor.hasSelectedText():
                editor.SendScintilla(KEY_SCINTILLA['y'])
            else:
                self._leader_char = text
        elif text == 'd':
            if editor.hasSelectedText():
                editor.SendScintilla(KEY_SCINTILLA['d'])
            else:
                self._leader_char = text
        elif text == 'g':
            self._leader_char = text
        elif text == '/':
            self._leader_char = text
        elif text == '~':
            text = editor.selectedText()
            if not text:
                editor.SendScintilla(KEY_VISUAL_SCINTILLA['l'])
                text = editor.selectedText()
            if text.islower():
                editor.SendScintilla(KEY_SCINTILLA['gU'])
            else:
                editor.SendScintilla(KEY_SCINTILLA['gu'])
            editor.selectAll(False)
        elif text == 'x':
            if editor.hasSelectedText():
                editor.SendScintilla(KEY_SCINTILLA['x'])
            else:
                editor.delete(1)
        elif text == 'a':
            editor.SendScintilla(KEY_SCINTILLA['l'])
            self.setMode('insert')
        elif text == 'A':
            editor.SendScintilla(KEY_SCINTILLA['$'])
            self.setMode('insert')
        elif text == 'o':
            editor.SendScintilla(KEY_SCINTILLA['$'])
            editor.SendScintilla(KEY_SCINTILLA['o'])
            self.setMode('insert')
        elif text == 'O':
            editor.SendScintilla(KEY_SCINTILLA['k'])
            editor.SendScintilla(KEY_SCINTILLA['$'])
            editor.SendScintilla(KEY_SCINTILLA['o'])
            self.setMode('insert')
        elif text == 'p':
            editor.SendScintilla(KEY_SCINTILLA['l'])
            editor.SendScintilla(KEY_SCINTILLA['P'])
        elif text == '<':
            editor.indentLines(False)
        elif text == '>':
            editor.indentLines(True)
        elif text == 'J':
            editor.linesJoin()
        elif text in KEY_SCINTILLA:
            editor.SendScintilla(KEY_SCINTILLA[text])
        return True

    def handleInsertMode(self, key, text, editor):
        return False

    def handleVisualMode(self, key, text, editor):
        print('visual', hex(key), repr(text))
        if not text:
            return False
        if text in KEY_VISUAL_SCINTILLA:
            editor.SendScintilla(KEY_VISUAL_SCINTILLA[text])
        elif text == '<':
            editor.indentLines(False)
        elif text == '>':
            editor.indentLines(True)
        elif text == 'J':
            editor.linesJoin()
        elif text == ':':
            self.setMode('command')
            self._command_edit.setText(":'<,'>")
            self._command_edit.setFocus()
            self._editor = editor
        else:
            if text in KEY_SCINTILLA:
                editor.SendScintilla(KEY_SCINTILLA[text])
            self.setMode('normal')
            editor.selectAll(False)
        return True

    def handleVisualBlockMode(self, key, text, editor):
        print('visual block', hex(key), repr(text))
        if not text:
            return False
        if text in KEY_VBLOCK_SCINTILLA:
            editor.SendScintilla(KEY_VBLOCK_SCINTILLA[text])
        elif text == '<':
            editor.indentLines(False)
        elif text == '>':
            editor.indentLines(True)
        elif text == 'J':
            editor.linesJoin()
        elif text == ':':
            self.setMode('command')
            self._command_edit.setText(":'<,'>")
            self._command_edit.setFocus()
            self._editor = editor
        elif text == 'I':
            line_from, index_from, line_to, index_to = editor.getSelection()
            editor.setCursorPosition(line_from, index_from)
            self.setMode('insert')
            editor.selectAll(False)
            self._vertical_edit = {
                'from': line_from,
                'to': line_to,
                'index': index_from,
                'text': '',
            }
        else:
            if text in KEY_SCINTILLA:
                editor.SendScintilla(KEY_SCINTILLA[text])
            self.setMode('normal')
            editor.selectAll(False)
        return True

    def handleCommandMode(self, key):
        """VIM Command"""
        text = self._command_edit.text()
        self._command_edit.clear()
        print(key, text)
        if not self._editor:
            return
        if key == 'return':
            self.setMode('normal')
            text = text.lstrip(':')
            if text.startswith("'<,'>"):
                text = text.lstrip("'<,'>")
                in_selection = True
            else:
                in_selection = False
            if text.startswith('/'):
                search = text.split('/')
                find_text = search[1]
                print('find text', find_text, search)
                if in_selection and self._editor.hasSelectedText():
                    is_find = self._editor.findFirstInSelection(
                        find_text,
                        True,   # re
                        False,  # cs
                        False,  # wo
                        posix=True,
                    )
                else:
                    is_find = self._editor.findFirst(
                        find_text,
                        True,   # re
                        False,  # cs
                        False,  # wo
                        True,   # wrap
                        posix=True,
                    )
            elif text.startswith('s/'):
                search = text.split('/')
                if len(search) > 2:
                    find_text = search[1]
                    replace_text = search[2]
                    print('find text', find_text, replace_text)
                    if len(search) > 3:
                        op = search[3]
                    else:
                        op = ''
                    if in_selection and self._editor.hasSelectedText():
                        is_find = self._editor.findFirstInSelection(
                            find_text,
                            True,   # re
                            True if 'i' in op else False,  # cs
                            False,  # wo
                            posix=True,
                        )
                    else:
                        is_find = self._editor.findFirst(
                            find_text,
                            True,   # re
                            True if 'i' in op else False,  # cs
                            False,  # wo
                            True,   # wrap
                            posix=True,
                        )
                    if is_find:
                        self._editor.replace(replace_text)
                    while is_find:
                        is_find = self._editor.findNext()
                        if is_find:
                            self._editor.replace(replace_text)
            else:
                cmd = text.split(' ')
                if len(cmd) > 1:
                    parameter = cmd[1]
                else:
                    parameter = ''
                if 'a' in cmd[0]:
                    parameter = '__ALL'
                if 'r' in cmd[0]:
                    pass
                if 'n' in cmd[0]:
                    self._editor.loadRequest.emit(parameter)
                if 'w' in cmd[0]:
                    if in_selection:
                        pass
                    else:
                        self._editor.saveRequest.emit(parameter)
                if 'q' in cmd[0]:
                    self._editor.closeRequest.emit(parameter)
            self._editor.setFocus()
        elif key == 'escape':
            self.setMode('normal')
            self._editor.setFocus()

    def setMode(self, mode):
        if isinstance(mode, int):
            self._mode = mode
        else:
            self._mode = VIM_MODE[mode]
        label = '{0:>7}'.format(VIM_MODE[self._mode].upper())
        self._mode_label.setText(label)

    def mode(self):
        return self._mode
