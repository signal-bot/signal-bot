from gi.repository import GLib
from pydbus import SessionBus
from threading import Thread


class Signalbot(object):

    def __init__(self, mocker=False):
        self._mocker = mocker

    def start(self):
        self._bus = SessionBus()
        if self._mocker:
            self._signal = self._bus.get('org.signalbot.signalclidbusmock')
        else:
            self._signal = self._bus.get('org.asamk.Signal')
        self._signal.onMessageReceived = self._receivemessage
        self._loop = GLib.MainLoop()
        self._thread = Thread(daemon=True,
                              target=self._loop.run)
        self._thread.start()

    def _receivemessage(self,
                        timestamp, sender, group_id, message, attachmentfiles):
        t = Thread(
            args=[timestamp, sender, group_id, message, attachmentfiles],
            daemon=True,
            target=self._triagemessage)
        t.start()

    def _triagemessage(self,
                       timestamp, sender, group_id, message, attachmentfiles):
        if not group_id:
            self._signal.sendMessage('Hello {}!'.format(sender),
                                     [],
                                     [sender])

    def stop(self):
        self._loop.quit()
        self._thread.join()
        self._signal.onMessageReceived = None
