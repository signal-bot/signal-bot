[![Build Status](https://travis-ci.org/signal-bot/signal-bot.svg?branch=master)](https://travis-ci.org/signal-bot/signal-bot)

# signal-bot

https://signal-bot.github.io

This project is in its infancy!

**Contents**

* [The idea](#the-idea)
* [Plugins](#plugins)
* [Developing a new plugin](#developing-a-new-plugin)
* [Mocker](#mocker)

## The idea

* signal-bot provides headless chat/bot/monitoring services for the [Signal][signal] messenger.
* Services are made available via plugins.
* Writing new plugins to extend functionality is easy and modular since signal-bot smoothly wraps around [signal-cli][signal-cli] in order to provide a convenient Python framework.

## Plugins

Ideas/plans for plugins include
* lunch menu plugin
* photo memories plugin
* splitbot
* automatically replying with the pdf of an author's manuscript which the author is entitled to distribute upon request
* ...

## Developing a new plugin

### Overview over the plugin structure and locks

### A minimal hello world example

### Contributing your plugin

Please refer to CONTRIBUTING.md.

## Mocker

The idea behind `Mocker` is to enable for testing and debugging of signal-bot and its plugins.
It offers a dbus service that (partially) mimicks the dbus service of signal-cli (if needed, it should eventually mimick the [signal-cli dbus service interface][signal-dbus] exactly).

Below we show a minimal example that uses the mocker and a toy bot.
In the future we will provide an example how the mocker can be used during development and for testing.

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
