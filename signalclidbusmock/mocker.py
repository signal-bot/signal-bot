from .signalclidbusmock import SignalCLIDBusMock
from gi.repository import GLib
from pydbus import SessionBus
from threading import Thread
import time


class Mocker(object):

    def __init__(self):
        self._bus = SessionBus()
        self._mock = SignalCLIDBusMock()
        self._service = self._bus.publish(
            "org.signalbot.signalclidbusmock",
            self._mock)
        self._loop = GLib.MainLoop()
        self._thread = Thread(target=self._loop.run, daemon=True)
        self._thread.start()
        self.tosignalbot = []

    def messageSignalbot(self, sender, group_id, message, attachmentfiles):
        self._mock.MessageReceived(int(time.time()),
                                   sender, group_id, message, attachmentfiles)
        self.tosignalbot.append([int(time.time()),
                                 sender, group_id, message, attachmentfiles])

    @property
    def fromsignalbot(self):
        return self._mock._sentmessages

    def close(self):
        self._loop.quit()
        self._thread.join()
        self._service.unpublish()
