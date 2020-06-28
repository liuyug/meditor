

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction

from .util import singleton


@singleton
class GlobalAction():
    _commands = None

    def __init__(self):
        self._commands = {}

    def register(self, act_id, action, group=None):
        if act_id not in self._commands:
            cmd = QAction()
            cmd.setShortcutContext(Qt.ApplicationShortcut)
            cmd.triggered.connect(partial(self.do_action, act_id))
            self._commands[act_id] = {
                'cmd': cmd,
                'actions': [],
                'group': group,
            }
        self._commands[act_id]['actions'].append(action)
        return self._commands[act_id]['cmd']

    def unregister(self, action):
        for act_id in self._commands:
            actions = self._commands[act_id]['actions']
            if action in actions:
                actions.remove(action)
                break

    def unregister_by_widget(self, widget):
        for act_id in self._commands:
            actions = self._commands[act_id]['actions']
            for action in actions:
                if action.parentWidget() == widget:
                    actions.remove(action)

    def do_action(self, act_id):
        if act_id not in self._commands:
            return
        actions = self._commands[act_id]['actions']
        if len(actions) == 1:
            action = actions[0]
            action.trigger()
        else:
            for action in actions:
                parent = action.parentWidget()
                if parent and parent.hasFocus():
                    action.trigger()
                    break

    def get(self, act_id):
        if act_id in self._commands:
            return self._commands[act_id]['cmd']

    def enableGroup(self, group, value):
        for cmd in self._commands.values():
            if cmd['group'] == group:
                cmd['cmd'].setEnabled(value)
