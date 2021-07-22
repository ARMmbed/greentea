#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Logger."""

import sys
import logging
from functools import partial


class HtrunLogger(object):
    """Yet another logger flavour."""

    def __init__(self, name):
        """Initialise logger to stdout."""
        logging.basicConfig(
            stream=sys.stdout,
            format="[%(created).2f][%(name)s]%(message)s",
            level=logging.DEBUG,
        )
        self.logger = logging.getLogger(name)
        self.format_str = "[%(logger_level)s] %(message)s"

        def __prn_log(self, logger_level, text, timestamp=None):
            self.logger.debug(
                self.format_str
                % {
                    "logger_level": logger_level,
                    "message": text,
                }
            )

        self.prn_dbg = partial(__prn_log, self, "DBG")
        self.prn_wrn = partial(__prn_log, self, "WRN")
        self.prn_err = partial(__prn_log, self, "ERR")
        self.prn_inf = partial(__prn_log, self, "INF")
        self.prn_txt = partial(__prn_log, self, "TXT")
        self.prn_txd = partial(__prn_log, self, "TXD")
        self.prn_rxd = partial(__prn_log, self, "RXD")
