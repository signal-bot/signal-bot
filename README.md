[![Build Status](https://travis-ci.org/signal-bot/signal-bot.svg?branch=master)](https://travis-ci.org/signal-bot/signal-bot)

# signal-bot

https://signal-bot.github.io

This project is in its infancy!

## The idea

* signal-bot provides headless chat/bot/monitoring services for the [Signal][signal] messenger.
* Services are made available via plugins.
* Writing new plugins to extend functionality is easy and modular since signal-bot smoothly wraps around [signal-cli][signal-cli] in order to provide a convenient Python framework.

## To do

* finish mocker to support "message protocol" testing, i.e. testing whether certain messages are responded to as expected by signalbot; also allow for easy definition of such test cases/conversations
* lay out the core signal-bot message triager and the plugin interface
* setup.py that also deals with python-gi, which is not smoothly installable via pip; for travis one way may be to symlink the dist-packages
* currently we test python 2.7 and 3.4; if we feel the urge we can make travis testing with python 3.5 and 3.6 work (glib needs to be compiled)

## Mocker (work in progress)

The idea behind `Mocker` is to enable for testing and debugging of signal-bot and its plugins.
It offers a dbus service that (partially) mimicks the dbus service of signal-cli (if needed, it should eventually mimick the [signal-cli dbus service interface][signal-dbus] exactly).

```python
from pydbus import SessionBus
from signalclidbusmock import Mocker
from threading import Thread
import time

# start dummy dbus service
mocker = Mocker()
mocker.start()


# a minimalistic signal-bot
def message(t, s, g, m, a):
    t = Thread(args=['Hello {}, this is Signalbot :-)'.format(s), None, [s]],
               daemon=True,
               target=signal.sendMessage)
    t.start()


bus = SessionBus()
signal = bus.get('org.signalbot.signalclidbusmock')
signal.onMessageReceived = message

# simulate sending messages to signal-bot
mocker.messageSignalbot('+123', None, 'Hi signal-bot!', [])
mocker.messageSignalbot('+000', None, 'Who are you?', [])

# wait for signal-bot to respond
time.sleep(1)

# the messages we sent to signal-bot
print(mocker.tosignalbot)

# the messages signal-bot sent in response
print(mocker.fromsignalbot)
```



[signal]: https://signal.org/
[signal-cli]: https://github.com/AsamK/signal-cli
[signal-dbus]: https://github.com/AsamK/signal-cli/blob/master/src/main/java/org/asamk/Signal.java
