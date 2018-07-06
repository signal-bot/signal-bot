from pathlib import Path
from signalclidbusmock import Mocker
from subprocess import Popen
from tempfile import TemporaryDirectory
import unittest
import yaml


class HelloWorldTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = TemporaryDirectory()

        config = {
            'master': ['+123'],
            'plugins': ['pingpong'],
            'testing_plugins': ['pingponglocktest'],
            'startup_notification': True,
        }
        configfile = Path.joinpath(Path(self.tempdir.name), 'config.yaml')
        yaml.dump(config, configfile.open('w'))

        self.mocker = Mocker()
        self.mocker.start()

        self.bot_popen = Popen(
            ['signal-bot', '--data-dir', self.tempdir.name, '--mocker'])
        # Wait for startup notification
        self.mocker.wait_for_n_messages(n=1)

    def tearDown(self):
        self.bot_popen.terminate()
        self.mocker.stop()
        self.tempdir.cleanup()

    def _assert_expected_messages(self, expect_messages):
        self.assertEqual([['Always at your service! ✔', [], ['+123']]] +
                         expect_messages,
                         [have[1:] for have in self.mocker.fromsignalbot])

    def test_master(self):
        self.mocker.messageSignalbot('+000', None, '//enable pingpong', [])
        self.mocker.messageSignalbot('+000', None, 'ping', [])
        self.mocker.messageSignalbot('+123', None, '//enable pingpong', [])
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        self.mocker.messageSignalbot('+123', None, '//disable pingpong', [])
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        self.mocker.wait_for_n_messages(n=5)
        expect_messages = [
            ['You are not my master. ❌', [], ['+000']],
            ['Plugin pingpong enabled. ✔', [], ['+123']],
            ['pong', [], ['+123']],
            ['Plugin pingpong disabled. ✔', [], ['+123']]]
        self._assert_expected_messages(expect_messages)

    def test_locking_basic(self):
        self.mocker.messageSignalbot('+123', None, '//enable pingponglocktest',
                                     [])
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        self.mocker.messageSignalbot('+123', None, 'backup', [])
        self.mocker.wait_for_n_messages(n=5)
        self.mocker.messageSignalbot('+123', None, 'ping', [])
        self.mocker.wait_for_n_messages(n=3, timeout=10)
        expect_messages = [
            ['Plugin pingponglocktest enabled. ✔', [], ['+123']],
            ['start pong', [], ['+123']],
            ['Acquiring lock...', [], ['+123']],
            ['pong', [], ['+123']],
            ['Locked - sleeping 1 sec ...', [], ['+123']],
            ['... done sleeping / locking', [], ['+123']],
            ['start pong', [], ['+123']],
            ['pong', [], ['+123']]]
        self._assert_expected_messages(expect_messages)

    def test_locking_threeblocking(self):
        self.mocker.messageSignalbot('+123', None, '//enable pingponglocktest',
                                     [])
        self.mocker.messageSignalbot('+123', None, 'backup_A', [])
        self.mocker.messageSignalbot('+123', None, 'backup_B', [])
        self.mocker.messageSignalbot('+123', None, 'backup_C', [])
        self.mocker.wait_for_n_messages(n=8, timeout=10)
        expect_messages = [
            ['Plugin pingponglocktest enabled. ✔', [], ['+123']],
            ['backup_A: Attempting to acquire exclusive lock...',
             [], ['+123']],
            ['backup_B: Attempting to acquire exclusive lock...',
             [], ['+123']],
            ['Isolation lock could not be acquired. ❌', [], ['+123']],
            ['backup_C: Attempting to acquire exclusive lock...',
             [], ['+123']],
            ['We want to do our own handling if we cannot get the exclusive '
             'lock. ❌', [], ['+123']],
            ['backup_A: Locked - sleeping 1 sec ...', [], ['+123']],
            ['backup_A: ... done sleeping / locking', [], ['+123']],
        ]
        self._assert_expected_messages(expect_messages)
