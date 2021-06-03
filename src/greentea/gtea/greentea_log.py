#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Greentea logging implementation."""
from threading import Lock

try:
    import colorama

    COLORAMA = True
except ImportError:
    COLORAMA = False


class GreenTeaSimpleLockLogger(object):
    """Simple locking printing mechanism."""

    # Colors used by color(ama) terminal component
    DIM = str()
    BRIGHT = str()
    GREEN = str()
    RED = str()
    BLUE = str()
    YELLOW = str()
    RESET = str()

    def __init__(self, color_enable=True):
        """Initialise the colors for formatting if in use."""
        self.colorful(color_enable)

        # Mutext used to protect logger prints
        # Usage:
        # GREENTEA_LOG_MUTEX.acquire(1)
        # GREENTEA_LOG_MUTEX.release()
        self.GREENTEA_LOG_MUTEX = Lock()

        if self.color_enable:
            if not COLORAMA:
                self.gt_log("Colorful console output is disabled")
            else:
                colorama.init()

    def colorful(self, enable=True):
        """Enable/Disable colourful printing."""
        self.color_enable = enable
        if self.color_enable:
            self.__set_colors()
        else:
            self.__clear_colors()

    def __set_colors(self):
        """Set colours to use for formatting."""
        if COLORAMA and self.color_enable:
            self.DIM = colorama.Style.DIM
            self.BRIGHT = colorama.Style.BRIGHT
            self.GREEN = colorama.Fore.GREEN
            self.RED = colorama.Fore.RED
            self.BLUE = colorama.Fore.BLUE
            self.YELLOW = colorama.Fore.YELLOW
            self.RESET = colorama.Style.RESET_ALL

    def __clear_colors(self):
        """Zero colours used for formatting."""
        self.DIM = str()
        self.BRIGHT = str()
        self.GREEN = str()
        self.RED = str()
        self.BLUE = str()
        self.YELLOW = str()
        self.RESET = str()

    def __print(self, text):
        """Mutex protected print."""
        self.GREENTEA_LOG_MUTEX.acquire(1)
        print(text)
        self.GREENTEA_LOG_MUTEX.release()

    def gt_log(self, text, print_text=True):
        """Print standard log message, in colour if colorama is installed and enabled.

        Args:
            text: String to be logged.
            print_text: Force log to be printed on screen.
        Returns:
            String with message.
        """
        result = self.GREEN + self.BRIGHT + "gt: " + self.RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_log_tab(self, text, tab_count=1, print_text=True):
        """Print standard log message with tab margin on the left.

        Args:
            text: String to be logged.
            tab_count: How many tabs should be added (indent level).
            print_text: Force log to be printed on screen.

        Returns:
            String with message.
        """
        result = "\t" * tab_count + text
        if print_text:
            self.__print(result)
        return result

    def gt_log_err(self, text, print_text=True):
        """Print error log message, in color if colorama is installed and enabled.

        Args:
            text: String to be logged.
            print_text: Force log to be printed on screen.

        Returns:
            String with message.
        """
        result = self.RED + self.BRIGHT + "gt: " + self.RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_log_warn(self, text, print_text=True):
        """Print warning log message, in color if colorama is installed and enabled.

        Args:
            text: String to be logged.
            print_text: Force log to be printed on screen.

        Returns:
            String with message.
        """
        result = self.YELLOW + "gt: " + self.RESET + text
        if print_text:
            self.__print(result)
        return result

    def gt_bright(self, text):
        """Create bright text using colorama.

        Args:
            text: String to make bright.

        Returns:
            String with additional BRIGHT color codes.
        """
        if not text:
            text = ""
        return self.BLUE + self.BRIGHT + text + self.RESET


gt_logger = GreenTeaSimpleLockLogger()
