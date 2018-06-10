from .plugin import Plugin


class PingPong(Plugin):

    def triagemessage(self, message):
        if message.text != 'ping':
            return

        self.reply('pong')


__plugin__ = PingPong
