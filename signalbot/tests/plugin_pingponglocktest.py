from signalbot.plugins.plugin import Plugin, ExclusivityException
from time import sleep


class PingPongLockTest(Plugin):

    def triagemessage(self, message):

        if message.text in ['backup_A', 'backup_B', 'backup_C']:
            if message.text != 'backup_A':
                sleep(1)
            self.reply("{}: Attempting to acquire exclusive lock...".format(
                message.text))
            if message.text in ['backup_A', 'backup_B']:
                with self.isolated_thread:
                    self.reply("{}: Locked - sleeping 1 sec ...".format(
                        message.text))
                    sleep(1)
                    self.reply("{}: ... done sleeping / locking".format(
                        message.text))
            elif message.text == 'backup_C':
                try:
                    with self.isolated_thread:
                        self.reply("{}: Locked - sleeping 1 sec ...".format(
                            message.text))
                        sleep(1)
                        self.reply("{}: ... done sleeping / locking".format(
                            message.text))
                except ExclusivityException:
                    self.error('We want to do our own handling if we cannot '
                               'get the exclusive lock.')
            return

        elif message.text == 'backup':
            self.reply("Acquiring lock...")
            with self.isolated_thread:
                self.reply("Locked - sleeping 1 sec ...")
                sleep(1)
                self.reply("... done sleeping / locking")
            return

        self.reply('start pong')
        sleep(1)
        self.reply('pong')


__plugin__ = PingPongLockTest
