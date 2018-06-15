from .plugin import Plugin, PluginChat


class PingPongChat(PluginChat):

    def triagemessage(self, message):
        if message.text != 'ping':
            return

        self.reply('pong')


class PingPong(Plugin):
    def chat_class(self):
        return PingPongChat


__plugin__ = PingPong
