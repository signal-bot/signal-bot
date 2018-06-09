from .plugin import Plugin


class PingPong(Plugin):

    def triagemessage(self, message):
        if message.text != 'ping':
            return

        message.reply('pong')


__plugin__ = PingPong
