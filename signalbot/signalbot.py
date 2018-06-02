from gi.repository import GLib
from pydbus import SessionBus, SystemBus, connect
from threading import Thread
from pathlib import Path
from importlib import import_module
import yaml


class Message(object):

    def __init__(self, bot,
                 timestamp, sender, group_id, text, attachmentfiles):
        self.bot = bot
        self.timestamp = timestamp
        self.sender = sender
        self.group_id = group_id
        self.text = text
        self.attachmentfiles = attachmentfiles

    def is_group(self):
        return self.group_id != []

    def get_chat_id(self):
        if self.is_group():
            return self.group_id
        else:
            return self.sender

    def reply(self, text, attachments=[]):
        if self.is_group():
            self.bot.send_group_message(text, attachments, self.group_id)
        else:
            self.bot.send_message(text, attachments, [self.sender])

    def error(self, text, attachments=[]):
        self.reply(text + ' ❌', attachments=attachments)

    def success(self, text, attachments=[]):
        self.reply(text + ' ✔', attachments=attachments)


class Signalbot(object):

    def __init__(self, data_dir=None, mocker=False):
        self._mocker = mocker

        if data_dir is None:
            self._data_dir = Path.joinpath(Path.home(), '.config', 'signalbot')
        elif type(data_dir) is str:
            self._data_dir = Path(data_dir)
        else:
            self._data_dir = data_dir

        self._configfile = Path.joinpath(self._data_dir, 'config.yaml')
        self.config = yaml.load(self._configfile.open('r'))
        if 'bus' not in self.config:
            self.config['bus'] = None
        if 'plugins' not in self.config:
            self.config['plugins'] = []
        if 'master' not in self.config:
            self.config['master'] = None
        if 'enabled' not in self.config:
            self.config['enabled'] = {}

    def _save_config(self):
        yaml.dump(self.config, self._configfile.open('w'))

    def start(self):
        if self.config['bus'] == 'session' or self.config['bus'] is None:
            self._bus = SessionBus()
        elif self.args.bus == 'system':
            self._bus = SystemBus()
        else:
            self._bus = connect(self.config['bus'])

        if self._mocker:
            self._signal = self._bus.get('org.signalbot.signalclidbusmock')
        else:
            self._signal = self._bus.get('org.asamk.Signal')
        self._signal.onMessageReceived = self._receivemessage

        self._plugins = {
            plugin: import_module('.plugins.' + plugin,
                                  package='signalbot').__plugin__(self)
            for plugin in self.config['plugins']}

        self._loop = GLib.MainLoop()
        self._thread = Thread(daemon=True, target=self._loop.run)
        self._thread.start()

    def start_and_wait(self):
        self.start()
        self._thread.join()

    def send_message(self, text, attachments, receivers):
        self._signal.sendMessage(text, attachments, receivers)

    def send_group_message(self, text, attachments, group_id):
        self. _signal.sendGroupMessage(text, attachments, group_id)

    def _receivemessage(self,
                        timestamp, sender, group_id, text, attachmentfiles):
        message = Message(self,
                          timestamp, sender, group_id, text, attachmentfiles)

        self._triagemessage(message)

    def _master_print_help(self, message):
        message.reply("""
            Available commands:
            /help
            /enable plugin [plugin ...]
            /disable plugin  [plugin ...]
            /list-enabled
            /list-available
            """)

    def _master_enable(self, message, params):
        for plugin in params:

            if plugin not in self.config['plugins']:
                message.error("Plugin {} not loaded".format(plugin))
                continue

            chat_id = message.get_chat_id()
            if chat_id not in self.config['enabled']:
                self.config['enabled'][chat_id] = []

            if plugin in self.config['enabled'][chat_id]:
                message.reply("Plugin {} is already enabled.".format(plugin))
                continue

            self.config['enabled'][chat_id].append(plugin)
            self._save_config()
            message.success("Plugin {} enabled.".format(plugin))

    def _master_disable(self, message, params):
        for plugin in params:
            chat_id = message.get_chat_id()

            if chat_id not in self.config['enabled'] or \
                    plugin not in self.config['enabled'][chat_id]:
                message.reply("Plugin {} is already disabled.".format(plugin))
                continue

            self.config['enabled'][chat_id].remove(plugin)
            if not len(self.config['enabled'][chat_id]):
                del self.config['enabled'][chat_id]
            self._save_config()
            message.success("Plugin {} disabled.".format(plugin))

    def _master_list_enabled(self, message):
        reply = "Enabled plugins:\n"
        chat_id = message.get_chat_id()
        if chat_id in self.config['enabled']:
            for plugin in self.config['enabled'][chat_id]:
                reply += "{}\n".format(plugin)
        message.reply(reply)

    def _master_list_available(self, message):
        reply = "Available plugins:\n"
        for plugin in self._plugins:
            reply += "{}\n".format(plugin)
        message.reply(reply)

    def _master_message(self, message):
        if message.sender != self.config['master']:
            message.error("You are not my master.")
            return

        params = message.text[1:].split(' ')
        command = params[0]
        params = params[1:]
        if command == "help":
            self._master_print_help(message)
        elif command == "enable":
            self._master_enable(message, params)
        elif command == "disable":
            self._master_disable(message, params)
        elif command == "list-enabled":
            self._master_list_enabled(message)
        elif command == "list-available":
            self._master_list_available(message)
        else:
            message.error("Invalid command.")

    def _triagemessage(self, message):

        # Master messages are handled internally
        if message.text.startswith('/'):
            self._master_message(message)
            return

        # Other messages are handled by plugins
        chat_id = message.get_chat_id()
        if chat_id not in self.config['enabled']:
            return
        for plugin in self.config['enabled'][chat_id]:
            if plugin not in self._plugins:
                continue
            self._plugins[plugin].receive(message)

    def stop(self):
        self._loop.quit()
        self._thread.join()
        self._signal.onMessageReceived = None
