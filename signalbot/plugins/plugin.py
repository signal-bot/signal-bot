from threading import Condition, Lock, Thread


class ChatThreadcount:

    def __init__(self, chat_lock):
        self._chat_lock = chat_lock
        self._count = 0

        # Condition to protect _count
        self._condition = Condition()

    def __enter__(self):
        # Don't allow starting new blocked threads during entry to the
        # ChatThreadcount lock. This is to prevent a new blocking thread
        # to enter the ChatLock between the
        #   self._chat_lock.wait_until_unblocked()
        # and the
        #   self._count += 1
        # which would mean the new blocking thread would start despite our
        # new thread running!
        with self._chat_lock.get_suspend_entry_lock():

            # Check if there is a blocking thread running and wait for it to
            # finish if needed.
            # This needs to be done before increasing the thread count. Else, a
            # blocking thread might wait forever for all threads to finish in
            # wait_until_only_one()
            self._chat_lock.wait_until_unblocked()

            # Increase thread count
            with self._condition:
                self._count += 1

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._condition:
            # Decrease thread count
            self._count -= 1

            # Notify for wait_until_only_blocking_candidates()
            # No need for notify_all() since there can only be one
            # blocking thread anyway.
            self._condition.notify()

    def wait_until_only_one(self):
        with self._condition:
            while self._count > 1:
                self._condition.wait()


class ChatLock:

    def __init__(self):
        self._lock = Lock()
        self._entry_lock = Lock()
        self._threadcount = ChatThreadcount(self)

    def get_threadcount_context(self):
        return self._threadcount

    def get_suspend_entry_lock(self):
        return self._entry_lock

    def __enter__(self):

        # Sometimes starting a ChatLock is disallowed by ChatThreadcount to
        # prevent race conditions
        with self._entry_lock:

            # Ensure no messages start processing for the same chat. Also
            # ensure there is only one blocking thread running at all times
            unblocked = self._lock.acquire(False)

        # Ensure all other threads have finished processing.
        # Needs to be done outside self._entry_lock. Otherwise there can be a
        # deadlock if one thread is at
        #    wait_until_only_one()
        # and another thread is at
        #    with self._entry_lock
        if unblocked:
            self._threadcount.wait_until_only_one()

        # For now, we force the plugin to properly deal with denied exclusive
        # threads (as well as allow plugins to clean up and send an error
        # message to the chat) by throwing an exception; there ought to be a
        # nicer way that does not require plugin developers to do the
        # try-with-except...probably to be implemented in the Plugin class
        if not unblocked:
            raise Exception('Exclusive lock could not be acquired.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def wait_until_unblocked(self):
        with self._lock:
            pass


class Plugin:

    def __init__(self, bot):
        self.bot = bot
        # Init chat lock, needs to be done in the main thread to avoid race
        # conditions
        self.chat_lock = ChatLock()

    def _thread_start(self, args, target):
        # Enter threadcount context to make get_chat_lock() work correctly
        with self.chat_lock.get_threadcount_context():
            # Do actual stuff
            target(*args)

    def _start(self, args, target):
        """
        Start a new thread in which `target` is called with `args` as
        arguments. In the created thread, chat_lock can be used to
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

    def triagemessage(self, message):
        """
        To be implemented by the respective plugin class
        """
        pass

    def start_processing(self, message):
        """
        Starts processing of a message.
        This will start a separate thread in which the actual processing is
        done and return that thread.
        """
        return self._start(args=[message],
                           target=self.triagemessage)
