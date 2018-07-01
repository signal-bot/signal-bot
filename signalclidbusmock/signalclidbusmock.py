from pydbus.generic import signal
import time
from threading import Condition


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
        self._cv = Condition()
        self._sentmessages = []
        self._groups = {(0, 1, 2): 'test group'}

    def wait_until_n_messages(self, n=1, timeout=1):
        with self._cv:
            time_start = time.time()
            while len(self._sentmessages) < n:
                self._cv.wait(timeout=timeout)
                if timeout is not None and time.time() - time_start > timeout:
                    return False
        return True

    def sendMessage(self, message, attachmentfiles, recipients):
        if len(recipients) > 1 and all([len(k) == 1 for k in recipients]):
            raise TypeError('conform with signal-cli 0.6.0 and wrap single '
                            'recipient into list like so [\'+123\']')
        with self._cv:
            self._sentmessages.append([time.time(),
                                       message, attachmentfiles, recipients])
            self._cv.notify_all()

    def sendGroupMessage(self, message, attachmentfiles, group_id):
        with self._cv:
            self._sentmessages.append([time.time(),
                                       message, attachmentfiles, group_id])
            self._cv.notify_all()

    def getGroupName(self, group_id):
        return self._groups.get(tuple(group_id), '')

    MessageReceived = signal()
