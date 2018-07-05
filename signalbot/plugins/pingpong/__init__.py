from ..plugin import PluginChat


class PingPongChat(PluginChat):

    def triagemessage(self, message):
        if message.text != 'ping':
            return

        self.reply('pong')


__plugin_chat__ = PingPongChat
