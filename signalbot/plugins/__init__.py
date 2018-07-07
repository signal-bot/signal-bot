from abc import ABC, abstractmethod
from pathlib import Path
from threading import Condition, Lock, Thread


class ChatThreadcounter(object):

    def __init__(self, isolated_lock):
        self._isolated_lock = isolated_lock
        self.entry_lock = Lock()
        self._count = 0

        # Condition to protect _count
        self._condition = Condition()

    def __enter__(self):
        # Do not allow starting new isolated threads during entry to the
        # ChatThreadcount lock. This is to prevent a new isolated thread
        # to obtain the IsolationLock between the
        #   self._chat_lock.wait_until_unblocked()
        # and the
        #   self._count += 1
        # which would mean the new isolated thread would start despite our
        # new thread running!
        with self.entry_lock:

            # Check if there is an isolated thread running and wait for it to
            # finish if needed.
            # This needs to be done before increasing the thread count. Else,
            # an isolated thread might wait forever for all threads to finish
            # in wait_until_only_one()
            self._isolated_lock.wait_until_unblocked()

            # Increase thread count
            with self._condition:
                self._count += 1

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._condition:
            # Decrease thread count
            self._count -= 1

            # Notify for wait_until_only_one()
            # No need for notify_all() since there can only be one
            # isolated thread anyway.
            self._condition.notify()

    def wait_until_only_one(self):
        with self._condition:
            while self._count > 1:
                self._condition.wait()


class IsolationException(Exception):
    pass


class IsolationLock(object):

    def __init__(self):
        self._lock = Lock()
        self._entry_lock = Lock()
        self.threadcounter = ChatThreadcounter(self)

    def _fail_exception(self):
        # For now, we force the plugin to properly deal with denied isolated
        # threads (as well as allow plugins to clean up and send an error
        # message to the chat) by throwing an exception; there ought to be a
        # nicer way that does not require plugin developers to do the
        # try-with-except...probably to be implemented in the Plugin class
        raise IsolationException('Isolation lock could not be acquired.')

    def __enter__(self):

        # Ensure no threads can accumulate waiting to try and get the isolated
        # lock. This is possible since we do not allow waiting for the isolated
        # chat lock, so we can just immediately fail here.
        #
        # This is important since otherwise the following deadlock is possible:
        # Thread 1:
        # - holds self._lock
        # - does self.threadcounter.wait_until_only_one()
        # Thread 2:
        # - has entered the threadcounter
        # - waits below at "with self.threadcounter.entry_lock"
        # Thread 3:
        # - is in self.threadcounter.__enter__
        # - holds self.threadcounter.entry_lock
        # - does wait_until_unblocked()
        #
        # Note that this Deadlock can also be prevented by moving the
        #   self.threadcounter.wait_until_only_one()
        # below into the
        #   with self.threadcounter.entry_lock:
        # However, then there could be the following deadlock:
        # Thread 1:
        # - is at self.threadcounter.entry_lock below
        # Thread 2:
        # - is in Threadcounter.__enter__ at wait_until_unblocked()
        if not self._entry_lock.acquire(False):
            self._fail_exception()

        try:

            # Sometimes obtaining an IsolationLock is disallowed by
            # ChatThreadcount to prevent race conditions.
            with self.threadcounter.entry_lock:

                # Ensure no messages start processing for the same chat. Also
                # ensure there is only one isolated thread running at all times
                if not self._lock.acquire(False):
                    self._fail_exception()

            # Ensure all other threads have finished processing.
            self.threadcounter.wait_until_only_one()

        finally:
            # Release entry lock
            self._entry_lock.release()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def wait_until_unblocked(self):
        with self._lock:
            pass


def chat_entry_point(func):
    """
    Starts func in the context of a PluginChat instance.
    This will start a separate thread in which the actual processing is done
    and return that thread.
    """
    def start_func(*args):
        return args[0]._start(target=func, args=args)
    start_func.is_entry_point = True
    return start_func


class PluginChat(ABC):

    def __init__(self, chat, data_dir):

        self._data_dir_checked = False
        self._data_dir = data_dir

        self.chat = chat
        # Init locks; needs to be done in the main thread to avoid race
        # conditions
        self.isolated_thread = IsolationLock()
        self.resource_lock = Lock()

        # Ensure triagemessage is a chat_entry_point
        try:
            self.triagemessage.is_entry_point
        except AttributeError:
            raise Exception("PluginChat.triagemessage must be decorated with"
                            "@chat_entry_point")

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def data_dir(self):
        if not self._data_dir_checked:
            Path.mkdir(self._data_dir, exist_ok=True, parents=True)
            self._data_dir_checked = True
        return self._data_dir

    def reply(self, text, attachments=[]):
        self.chat.reply(text, attachments)

    def error(self, text, attachments=[]):
        self.chat.error(text, attachments)

    def success(self, text, attachments=[]):
        self.chat.success(text, attachments)

    def _start(self, args, target):
        """
        Start a new thread in which `target` is called with `args` as
        arguments. In the created thread, isolated_thread can be used to
        ensure exclusive access to per-chat resources.
        This method is used for incoming messages and is planned to be used
        for scheduled events as well.
        """
        t = Thread(
            args=[args, target],
            daemon=True,
            target=self._thread_start)
        t.start()
        return t

    def _thread_start(self, args, target):
        # Enter threadcounter context to make isolated_thread work correctly
        with self.isolated_thread.threadcounter:
            # Do actual stuff
            try:
                target(*args)
            except IsolationException as e:
                self.error('{}'.format(e))

    @abstractmethod
    @chat_entry_point
    def triagemessage(self, message):
        """
        To be implemented by the respective plugin chat class
        """
        pass


class PluginRouter(object):

    def __init__(self, data_dir, chat_class):
        self._data_dir_checked = False
        self._data_dir = data_dir

        self._chat_class = chat_class
        if not issubclass(self._chat_class, PluginChat):
            raise Exception("chat_class must be a a subclass of PluginChat")

        self._chats = {}
        self._started = False

    def start(self):
        for chat in self._chats.values():
            chat.start()
        self._started = True

    def stop(self):
        self._started = False
        for chat in self._chats.values():
            chat.stop()

    @property
    def data_dir(self):
        if not self._data_dir_checked:
            Path.mkdir(self._data_dir, exist_ok=True)
            self._data_dir_checked = True
        return self._data_dir

    def enable(self, chat):
        if chat.id not in self._chats:
            chat_dir = Path.joinpath(self._data_dir, 'chats', str(chat))
            self._chats[chat.id] = self._chat_class(chat, chat_dir)
            if self._started:
                self._chats[chat.id].start()

    def disable(self, chat):
        if chat.id in self._chats:
            self._chats[chat.id].stop()
            del self._chats[chat.id]

    def triagemessage(self, message):
        chat_id = message.chat.id
        if chat_id in self._chats:
            self._chats[chat_id].triagemessage(message)
