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
        self._thread = Thread(target=self._loop.run, daemon=True)
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
                <arg type="as" direction="in" name="recipients" />
            </method>
            <method name="sendGroupMessage">
                <arg type="s" direction="in" name="message" />
                <arg type="as" direction="in" name="attachmentfiles" />
                <arg type="ay" direction="in" name="group_id" />
            </method>
            <method name="getGroupName">
                <arg type="ay" direction="in" name="group_id" />
                <arg type="s" direction="out" />
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
        self._groups = {(0, 1, 2): 'test group'}

    def sendMessage(self, message, attachmentfiles, recipients):
        if len(recipients) > 1 and all([len(k) == 1 for k in recipients]):
            raise TypeError('conform with signal-cli 0.6.0 and wrap single '
                            'recipient into list like so [\'+123\']')
        self._incoming.append([time.time(),
                               message, attachmentfiles, recipients])

    def sendGroupMessage(self, message, attachmentfiles, group_id):
        self._incoming.append([time.time(),
                               message, attachmentfiles, group_id])

    def getGroupName(self, group_id):
        return self._groups.get(tuple(group_id), '')

    MessageReceived = signal()
