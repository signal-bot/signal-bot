from signalbot.plugins.plugin import Plugin
from time import sleep


class PingPongLockTest(Plugin):

    def triagemessage(self, message):

        if message.text == 'backup2':
            sleep(1)
            message.reply("Acquiring lock...")
            with self.chat_lock:
                message.reply("Locked - sleeping 2 sec ...")
                sleep(1)
                message.reply("... done sleeping / locking")
            return

        if message.text == 'backup':
            message.reply("Acquiring lock...")
            with self.chat_lock:
                message.reply("Locked - sleeping 2 sec ...")
                sleep(1)
                message.reply("... done sleeping / locking")
            return

        message.reply('start pong')
        sleep(1)
        message.reply('pong')


__plugin__ = PingPongLockTest
