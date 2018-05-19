from gi.repository import GLib
from pydbus import SessionBus
from pydbus.generic import signal
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
        self._thread = Thread(target=self._loop.run)
        self._thread.daemon = True
        self._thread.start()
        self.outgoing = []

    def messageSignalbot(self, sender, group_id, message, attachmentfiles):
        self._mock.MessageReceived(int(time.time()),
                                   sender, group_id, message, attachmentfiles)
        self.outgoing.append([int(time.time()),
                              sender, group_id, message, attachmentfiles])

    @property
    def incoming(self):
        return self._mock._incoming

    def close(self):
        self._loop.quit()
        self._thread.join()
        self._service.unpublish()


class SignalCLIDBusMock(object):
    """
    <node name="/org/signalbot/signalclidbusmock">
        <interface name="org.signalbot.signalclidbusmock">
            <method name="sendMessage">
                <arg type="s" direction="in" name="message" />
                <arg type="as" direction="in" name="attachmentfiles" />
                <arg type="s" direction="in" name="recipient" />
            </method>
            <method name="sendGroupMessage">
                <arg type="s" direction="in" name="message" />
                <arg type="as" direction="in" name="attachmentfiles" />
                <arg type="ay" direction="in" name="group_id" />
            </method>
            <signal name="MessageReceived">
                <arg type="x" direction="out" />
                <arg type="s" direction="out" />
                <arg type="ay" direction="out" />
                <arg type="s" direction="out" />
                <arg type="as" direction="out" />
            </signal>
        </interface>
        </node>
    """

    def __init__(self):
        self._incoming = []

    def sendMessage(self, message, attachmentfiles, recipient):
        self._incoming.append([time.time(),
                               message, attachmentfiles, recipient])

    def sendGroupMessage(self, message, attachmentfiles, group_id):
        self._incoming.append([time.time(),
                               message, attachmentfiles, group_id])

    MessageReceived = signal()
