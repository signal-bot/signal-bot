from signalbot.plugins import PluginChat, chat_entry_point


class PingPongChat(PluginChat):

    @chat_entry_point
    def triagemessage(self, message):
        if message.text != 'ping':
            return

        self.reply('pong')


__plugin_chat__ = PingPongChat
