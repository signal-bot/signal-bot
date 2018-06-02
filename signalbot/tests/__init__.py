from signalclidbusmock import Mocker
import time
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
import yaml
from subprocess import Popen


class HelloWorldTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = TemporaryDirectory()

        config = {
            'plugins': ['pingpong'],
            'master': '+123'}
        configfile = Path.joinpath(Path(self.tempdir.name), 'config.yaml')
        yaml.dump(config, configfile.open('w'))

        self.mocker = Mocker()
        self.mocker.start()

        runfile = Path.joinpath(Path(__file__).parent, '..', '..', 'run.py')
        self.bot_popen = Popen(
            [str(runfile), '--data-dir', self.tempdir.name, '--mocker'])
        time.sleep(.3)

    def tearDown(self):
        self.bot_popen.kill()
        self.mocker.stop()
        self.tempdir.cleanup()

    def test(self):
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
