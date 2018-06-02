from pydbus.generic import signal
import time


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
        self._sentmessages = []
        self._groups = {(0, 1, 2): 'test group'}

    def sendMessage(self, message, attachmentfiles, recipients):
        if len(recipients) > 1 and all([len(k) == 1 for k in recipients]):
            raise TypeError('conform with signal-cli 0.6.0 and wrap single '
                            'recipient into list like so [\'+123\']')
        self._sentmessages.append([time.time(),
                                   message, attachmentfiles, recipients])

    def sendGroupMessage(self, message, attachmentfiles, group_id):
        self._sentmessages.append([time.time(),
                                   message, attachmentfiles, group_id])

    def getGroupName(self, group_id):
        return self._groups.get(tuple(group_id), '')

    MessageReceived = signal()
