#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Classes performing test selection, test execution and reporting of test results."""

from sys import stdout
from .target_base import TargetBase
from . import __version__


class HostTestResults(object):
    """Test results set by host tests."""

    def enum(self, **enums):
        """Return a new base type.

        Args:
            enums: Dictionary of namespaces for the type.
        """
        return type("Enum", (), enums)

    def __init__(self):
        """Initialise the test result type."""
        self.TestResults = self.enum(
            RESULT_SUCCESS="success",
            RESULT_FAILURE="failure",
            RESULT_ERROR="error",
            RESULT_END="end",
            RESULT_UNDEF="undefined",
            RESULT_TIMEOUT="timeout",
            RESULT_IOERR_COPY="ioerr_copy",
            RESULT_IOERR_DISK="ioerr_disk",
            RESULT_IO_SERIAL="ioerr_serial",
            RESULT_NO_IMAGE="no_image",
            RESULT_NOT_DETECTED="not_detected",
            RESULT_MBED_ASSERT="mbed_assert",
            RESULT_PASSIVE="passive",
            RESULT_BUILD_FAILED="build_failed",
            RESULT_SYNC_FAILED="sync_failed",
        )

        # Magically creates attributes in this class corresponding
        # to RESULT_ elements in self.TestResults enum
        for attr in self.TestResults.__dict__:
            if attr.startswith("RESULT_"):
                setattr(self, attr, self.TestResults.__dict__[attr])

        # Indexes of this list define string->int mapping between
        # actual strings with results
        self.TestResultsList = [
            self.TestResults.RESULT_SUCCESS,
            self.TestResults.RESULT_FAILURE,
            self.TestResults.RESULT_ERROR,
            self.TestResults.RESULT_END,
            self.TestResults.RESULT_UNDEF,
            self.TestResults.RESULT_TIMEOUT,
            self.TestResults.RESULT_IOERR_COPY,
            self.TestResults.RESULT_IOERR_DISK,
            self.TestResults.RESULT_IO_SERIAL,
            self.TestResults.RESULT_NO_IMAGE,
            self.TestResults.RESULT_NOT_DETECTED,
            self.TestResults.RESULT_MBED_ASSERT,
            self.TestResults.RESULT_PASSIVE,
            self.TestResults.RESULT_BUILD_FAILED,
            self.TestResults.RESULT_SYNC_FAILED,
        ]

    def get_test_result_int(self, test_result_str):
        """Map test result string to unique integer.

        Args:
            test_result_str: Test results as a string.
        """
        if test_result_str in self.TestResultsList:
            return self.TestResultsList.index(test_result_str)
        return -1

    def __getitem__(self, test_result_str):
        """Return integer test result code.

        Args:
            test_result_str: Test results as a string.
        """
        return self.get_test_result_int(test_result_str)


class Test(HostTestResults):
    """Base class for host test's test runner."""

    def __init__(self, options):
        """Initialise the test runner.

        Args:
            options: Options instance describing the target.
        """
        HostTestResults.__init__(self)
        self.target = TargetBase(options)

    def run(self):
        """Run a host test."""
        pass

    def setup(self):
        """Set up and check if configuration for test is correct."""
        pass

    def notify(self, msg):
        """Write a message to stdout.

        Flush immediately so the buffered data is immediately written to stdout.

        Args:
            msg: Text to write to stdout.
        """
        stdout.write(msg)
        stdout.flush()

    def print_result(self, result):
        """Print test results in "KV" format packets.

        Args:
            result: A member of HostTestResults.RESULT_* enums.
        """
        self.notify("{{%s}}\n" % result)
        self.notify("{{%s}}\n" % self.RESULT_END)

    def finish(self):
        """Finishes tasks and closes resources."""
        pass

    def get_hello_string(self):
        """Hello string used as first print."""
        return "host test executor ver. " + __version__


class DefaultTestSelectorBase(Test):
    """Test class with serial port initialization.

    This is a base for other test selectors.
    """

    def __init__(self, options):
        """Initialise test selector.

        Args:
            options: Options instance describing the target.
        """
        Test.__init__(self, options=options)
