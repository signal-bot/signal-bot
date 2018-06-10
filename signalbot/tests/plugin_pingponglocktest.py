from signalbot.plugins.plugin import Plugin
from time import sleep


class PingPongLockTest(Plugin):

    def triagemessage(self, message):

        if message.text in ['backup_A', 'backup_B']:
            if message.text == 'backup_B':
                sleep(1)
            self.reply("{}: Attempting to acquire exclusive lock...".format(
                message.text))
            try:
                with self.chat_lock:
                    self.reply("{}: Locked - sleeping 1 sec ...".format(
                        message.text))
                    sleep(1)
                    self.reply("{}: ... done sleeping / locking".format(
                        message.text))
            except Exception as e:
                if str(e) == 'Exclusive lock could not be acquired.':
                    self.error('{}: Blocking exclusive thread since there '
                               'is already another blocking thread running.'
                               ''.format(message.text))
                else:
                    raise e
            return

        elif message.text == 'backup':
            self.reply("Acquiring lock...")
            with self.chat_lock:
                self.reply("Locked - sleeping 1 sec ...")
                sleep(1)
                self.reply("... done sleeping / locking")
            return

        self.reply('start pong')
        sleep(1)
        self.reply('pong')


__plugin__ = PingPongLockTest
