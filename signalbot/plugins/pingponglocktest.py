from .plugin import Plugin


class PingPongLockTest(Plugin):

    def receive(self, message):

        from time import sleep

        if message.text == 'backup2':
            sleep(1)
            message.reply("Acquiring lock...")
            with self.get_chat_lock(message.get_chat_id()):
                message.reply("Locked - sleeping 2 sec ...")
                sleep(1)
                message.reply("... done sleeping / locking")
            return

        if message.text == 'backup':
            message.reply("Acquiring lock...")
            with self.get_chat_lock(message.get_chat_id()):
                message.reply("Locked - sleeping 2 sec ...")
                sleep(1)
                message.reply("... done sleeping / locking")
            return

        message.reply('start pong')
        sleep(1)
        message.reply('pong')


__plugin__ = PingPongLockTest
