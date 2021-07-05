#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from htrun.host_tests.base_host_test import BaseHostTest, event_callback


class TestEvenCallbackDecorator(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_event_callback_decorator(self):
        class Ht(BaseHostTest):
            @event_callback("Hi")
            def hi(self, key, value, timestamp):
                print("hi")

            @event_callback("Hello")
            def hello(self, key, value, timestamp):
                print("hello")

        h = Ht()
        h.setup()
        callbacks = h.get_callbacks()
        self.assertIn("Hi", callbacks)
        self.assertIn("Hello", callbacks)
