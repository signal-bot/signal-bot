from .plugin import Plugin


class PingPong(Plugin):
    def receive(self, message):
        if message.text != 'ping':
            return

        message.reply('pong')


__plugin__ = PingPong
