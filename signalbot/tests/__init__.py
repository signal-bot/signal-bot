from signalbot import Signalbot
from signalclidbusmock import Mocker
import time
import unittest


class HelloWorldTest(unittest.TestCase):

    def setUp(self):
        self.mocker = Mocker()
        self.mocker.start()
        self.bot = Signalbot(mocker=True)
        self.bot.start()

    def test(self):
        self.mocker.messageSignalbot('World', None, 'Hi Signalbot!', [])
        time.sleep(.1)
        self.assertCountEqual(self.mocker.fromsignalbot[0][1:],
                              ['Hello World!', [], ['World']])
