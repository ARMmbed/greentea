#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import inspect
import six
from time import time
from inspect import isfunction, ismethod


class BaseHostTestAbstract(object):
    """Base class for host-test test cases.

    Defines an interface of setup, test and teardown methods subclasses should
    implement.

    This class also performs common 'housekeeping' tasks such as pushing/popping
    messages on the event_queue and handling test config.
    """

    name = ""  # name of the host test (used for local registration)
    __event_queue = None  # To main even loop
    __dut_event_queue = None  # To DUT
    script_location = None  # Path to source file used to load host test
    __config = {}

    def __notify_prn(self, text):
        if self.__event_queue:
            self.__event_queue.put(("__notify_prn", text, time()))

    def __notify_conn_lost(self, text):
        if self.__event_queue:
            self.__event_queue.put(("__notify_conn_lost", text, time()))

    def __notify_sync_failed(self, text):
        if self.__event_queue:
            self.__event_queue.put(("__notify_sync_failed", text, time()))

    def __notify_dut(self, key, value):
        """Send data over serial to DUT."""
        if self.__dut_event_queue:
            self.__dut_event_queue.put((key, value, time()))

    def notify_complete(self, result=None):
        """Notify the main event loop that a host test is complete.

        Args:
            result: True for success, False failure.
        """
        if self.__event_queue:
            self.__event_queue.put(("__notify_complete", result, time()))

    def reset_dut(self, value):
        """Reset the device under test.

        Args:
            value: Value to send with the reset message.
        """
        if self.__event_queue:
            self.__event_queue.put(("__reset_dut", value, time()))

    def reset(self):
        """Reset the device under test and continue running the host test."""
        if self.__event_queue:
            self.__event_queue.put(("__reset", "0", time()))

    def notify_conn_lost(self, text):
        """Notify main event loop of a DUT-host connection error.

        Args:
            text: Additional text to send with the notification.
        """
        self.__notify_conn_lost(text)

    def log(self, text):
        """Send log message to main event loop.

        Args:
            text: Additional text to send with the notification.
        """
        self.__notify_prn(text)

    def send_kv(self, key, value):
        """Send Key-Value pair to the DUT.

        Args:
            key: Key part of KV pair.
            value: Value part of KV pair.
        """
        self.__notify_dut(key, value)

    def setup_communication(self, event_queue, dut_event_queue, config={}):
        """Setup queues used for comms between DUT and host.

        Args:
            event_queue: List of KV messages sent toward the host.
            dut_event_queue: List of KV messages sent toward the DUT.
            config: Test config.
        """
        self.__event_queue = event_queue  # To main even loop
        self.__dut_event_queue = dut_event_queue  # To DUT
        self.__config = config

    def get_config_item(self, name):
        """Get an item from the config by name.

        Args:
            name: Name of config parameter to get.

        Returns:
            Value of the config parameter with the given name. None if not found.
        """
        return self.__config.get(name, None)

    def setup(self):
        """Setup tests and callbacks."""
        raise NotImplementedError

    def result(self):
        """Return host test result (True, False or None)."""
        raise NotImplementedError

    def teardown(self):
        """Test teardown."""
        raise NotImplementedError


def event_callback(key):
    """Decorator for defining a event callback method.

    Adds an "event_key" attribute to the decorated function, which is set to the passed
    key.
    """

    def decorator(func):
        func.event_key = key
        return func

    return decorator


class HostTestCallbackBase(BaseHostTestAbstract):
    def __init__(self):
        BaseHostTestAbstract.__init__(self)
        self.__callbacks = {}
        self.__restricted_callbacks = [
            "__coverage_start",
            "__testcase_start",
            "__testcase_finish",
            "__testcase_summary",
            "__exit",
            "__exit_event_queue",
        ]

        self.__consume_by_default = [
            "__coverage_start",
            "__testcase_start",
            "__testcase_finish",
            "__testcase_count",
            "__testcase_name",
            "__testcase_summary",
            "__rxd_line",
        ]

        self.__assign_default_callbacks()
        self.__assign_decorated_callbacks()

    def __callback_default(self, key, value, timestamp):
        """Default callback."""
        # self.log("CALLBACK: key=%s, value=%s, timestamp=%f"% (key, value, timestamp))
        pass

    def __default_end_callback(self, key, value, timestamp):
        """Default handler for event 'end' that gives test result from target.

        This callback is not decorated as we don't know in what order this
        callback will be registered. We want to let users override this callback.
        Hence it should be registered before registering user defined callbacks.
        """
        self.notify_complete(value == "success")

    def __assign_default_callbacks(self):
        """Assign default callback handlers."""
        for key in self.__consume_by_default:
            self.__callbacks[key] = self.__callback_default
        # Register default handler for event 'end' before assigning user defined
        # callbacks to let users over write it.
        self.register_callback("end", self.__default_end_callback)

    def __assign_decorated_callbacks(self):
        """Look for any callback methods decorated with @event_callback

        Example:
            Define a method with @event_callback decorator like:

            @event_callback('<event key>')
            def event_handler(self, key, value, timestamp):
               do something..
        """
        for name, method in inspect.getmembers(self, inspect.ismethod):
            key = getattr(method, "event_key", None)
            if key:
                self.register_callback(key, method)

    def register_callback(self, key, callback, force=False):
        """Register callback for a specific event (key: event name).

        Args:
            key: Name of the event.
            callback: Callable which will be registered for event "key".
            force: God mode.
        """

        # Non-string keys are not allowed
        if type(key) is not str:
            raise TypeError("event non-string keys are not allowed")

        # And finally callback should be callable
        if not callable(callback):
            raise TypeError("event callback should be callable")

        # Check if callback has all three required parameters (key, value, timestamp)
        # When callback is class method should have 4 arguments (self, key, value,
        # timestamp)
        if ismethod(callback):
            arg_count = six.get_function_code(callback).co_argcount
            if arg_count != 4:
                err_msg = "callback 'self.%s('%s', ...)' defined with %d arguments" % (
                    callback.__name__,
                    key,
                    arg_count,
                )
                err_msg += (
                    ", should have 4 arguments: self.%s(self, key, value, timestamp)"
                    % callback.__name__
                )
                raise TypeError(err_msg)

        # When callback is just a function should have 3 arguments func(key, value,
        # timestamp)
        if isfunction(callback):
            arg_count = six.get_function_code(callback).co_argcount
            if arg_count != 3:
                err_msg = "callback '%s('%s', ...)' defined with %d arguments" % (
                    callback.__name__,
                    key,
                    arg_count,
                )
                err_msg += (
                    ", should have 3 arguments: %s(key, value, timestamp)"
                    % callback.__name__
                )
                raise TypeError(err_msg)

        if not force:
            # Event starting with '__' are reserved
            if key.startswith("__"):
                raise ValueError("event key starting with '__' are reserved")

            # We predefined few callbacks you can't use
            if key in self.__restricted_callbacks:
                raise ValueError(
                    "we predefined few callbacks you can't use e.g. '%s'" % key
                )

        self.__callbacks[key] = callback

    def get_callbacks(self):
        return self.__callbacks

    def setup(self):
        pass

    def result(self):
        pass

    def teardown(self):
        pass


class BaseHostTest(HostTestCallbackBase):

    __BaseHostTest_Called = False

    def base_host_test_inited(self):
        """Check if BaseHostTest ctor was called.

        Call to BaseHostTest is required in order to force required
        interfaces implementation.

        Returns:
            True if ctor was called.
        """
        return self.__BaseHostTest_Called

    def __init__(self):
        HostTestCallbackBase.__init__(self)
        self.__BaseHostTest_Called = True
