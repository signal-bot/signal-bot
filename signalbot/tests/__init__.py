from pathlib import Path
from signalclidbusmock import Mocker
from subprocess import Popen
from tempfile import TemporaryDirectory
import time
import unittest
import yaml


class HelloWorldTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = TemporaryDirectory()

        config = {
            'master': '+123',
            'plugins': ['pingpong'],
            'testing_plugins': ['pingponglocktest'],
        }
        configfile = Path.joinpath(Path(self.tempdir.name), 'config.yaml')
        yaml.dump(config, configfile.open('w'))

        self.mocker = Mocker()
        self.mocker.start()

        self.bot_popen = Popen(
            ['signal-bot', '--data-dir', self.tempdir.name, '--mocker'])
        time.sleep(.3)

    def tearDown(self):
        self.bot_popen.kill()
        self.mocker.stop()
        self.tempdir.cleanup()

    def test_master(self):
        self.mocker.messageSignalbot('+000', None, '/enable pingpong', [])
        self.mocker.messageSignalbot('+000', None, 'ping', [])
        self.mocker.messageSignalbot('+123', None, '/enable pingpong', [])
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        self.mocker.messageSignalbot('+123', None, '/disable pingpong', [])
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        time.sleep(.1)
        self.assertCountEqual(self.mocker.fromsignalbot[0][1:],
                              ['You are not my master. ❌', [], ['+000']])
        self.assertCountEqual(self.mocker.fromsignalbot[1][1:],
                              ['Plugin pingpong enabled. ✔', [], ['+123']])
        self.assertCountEqual(self.mocker.fromsignalbot[2][1:],
                              ['pong', [], ['+123']])
        self.assertCountEqual(self.mocker.fromsignalbot[3][1:],
                              ['Plugin pingpong disabled. ✔', [], ['+123']])

    def test_locking_basic(self):
        self.mocker.messageSignalbot('+123', None, '/enable pingponglocktest',
                                     [])
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        self.mocker.messageSignalbot('+123', None, 'backup', [])
        time.sleep(.1)
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        time.sleep(5)
        expect_messages = [
            ['Plugin pingponglocktest enabled. ✔', [], ['+123']],
            ['start pong', [], ['+123']],
            ['Acquiring lock...', [], ['+123']],
            ['pong', [], ['+123']],
            ['Locked - sleeping 1 sec ...', [], ['+123']],
            ['... done sleeping / locking', [], ['+123']],
            ['start pong', [], ['+123']],
            ['pong', [], ['+123']]]
        self.assertEqual(len(expect_messages), len(self.mocker.fromsignalbot))
        for want, have in zip(expect_messages, self.mocker.fromsignalbot):
            self.assertCountEqual(want, have[1:])

    def test_locking_twoblocking(self):
        self.mocker.messageSignalbot('+123', None, '/enable pingponglocktest',
                                     [])
        self.mocker.messageSignalbot('+123', None, 'backup_A', [])
        self.mocker.messageSignalbot('+123', None, 'backup_B', [])
        time.sleep(5)
        expect_messages = [
            ['Plugin pingponglocktest enabled. ✔', [], ['+123']],
            ['backup_A: Attempting to acquire exclusive lock...',
             [], ['+123']],
            ['backup_B: Attempting to acquire exclusive lock...',
             [], ['+123']],
            ['backup_B: Blocking exclusive thread since there is already '
             'another blocking thread running. ❌', [], ['+123']],
            ['backup_A: Locked - sleeping 1 sec ...', [], ['+123']],
            ['backup_A: ... done sleeping / locking', [], ['+123']],
        ]
        self.assertCountEqual(expect_messages,
                              [have[1:]
                               for have in self.mocker.fromsignalbot])
