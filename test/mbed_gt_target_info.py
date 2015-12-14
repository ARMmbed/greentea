#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from mbed_greentea import mbed_target_info

class GreenteaTargetInfo(unittest.TestCase):

    def setUp(self):
        self.YOTTA_SEARCH_SSL_ISSUE = """/Library/Python/2.7/site-packages/requests/packages/urllib3/util/ssl_.py:90: InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
  InsecurePlatformWarning
frdm-k64f-gcc 0.0.24: Official mbed build target for the mbed frdm-k64f development board.
frdm-k64f-armcc 0.0.16: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.
/Library/Python/2.7/site-packages/requests/packages/urllib3/util/ssl_.py:90: InsecurePlatformWarning: A true SSLContext object is not available. This prevents urllib3 from configuring SSL appropriately and may cause certain SSL connections to fail. For more information, see https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning.
  InsecurePlatformWarning
"""

    def tearDown(self):
        pass

    def test_parse_yotta_target_cmd_output_mixed_chars(self):
        self.assertIn("m", mbed_target_info.parse_yotta_target_cmd_output("m 0.0.0"))
        self.assertIn("m", mbed_target_info.parse_yotta_target_cmd_output(" m 0.0.0"))
        self.assertIn("aaaaaaaaaaaaa", mbed_target_info.parse_yotta_target_cmd_output("aaaaaaaaaaaaa 0.0.0"))
        self.assertIn("aaaa-bbbb-cccc", mbed_target_info.parse_yotta_target_cmd_output("aaaa-bbbb-cccc 0.0.0"))
        self.assertIn("aBc-DEF_hijkkk", mbed_target_info.parse_yotta_target_cmd_output("aBc-DEF_hijkkk 0.0.0"))

    def test_parse_yotta_target_cmd_output_mixed_version(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.0"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 1.1.1"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 1.1.12"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 1.1.123"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 11.22.33"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.1"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.10.12"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.20.123"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.2.123"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 10.20.123"))
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 110.200.123"))

    def test_parse_yotta_target_cmd_output(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24"))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-armcc 1.12.3"))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14"))
        self.assertIn("stm32f429i-disco-gcc", mbed_target_info.parse_yotta_target_cmd_output("stm32f429i-disco-gcc 0.0.14"))

    def test_parse_yotta_target_cmd_output_mixed_whitechars(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24 "))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-armcc 1.12.3 "))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14 "))
        self.assertIn("stm32f429i-disco-gcc", mbed_target_info.parse_yotta_target_cmd_output("stm32f429i-disco-gcc 0.0.14 "))

    def test_parse_yotta_target_cmd_output_mixed_nl(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24\n"))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-armcc 1.12.3\n"))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14\n"))
        self.assertIn("stm32f429i-disco-gcc", mbed_target_info.parse_yotta_target_cmd_output("stm32f429i-disco-gcc 0.0.14\n"))

    def test_parse_yotta_target_cmd_output_mixed_rcnl(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24\r\n"))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-armcc 1.12.3\r\n"))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14\r\n"))
        self.assertIn("stm32f429i-disco-gcc", mbed_target_info.parse_yotta_target_cmd_output("stm32f429i-disco-gcc 11.222.333\r\n"))

    def test_parse_yotta_target_cmd_output_mixed_nl_whitechars(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24 \n"))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-armcc 1.12.3 \n"))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14 \n"))
        self.assertIn("stm32f429i-disco-gcc", mbed_target_info.parse_yotta_target_cmd_output("stm32f429i-disco-gcc 0.0.14 \n"))

    def test_parse_yotta_target_cmd_output_mixed_rcnl_whitechars(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-gcc 0.0.24 \r\n"))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_target_cmd_output("frdm-k64f-armcc 1.12.3 \r\n"))
        self.assertIn("mbed-gcc", mbed_target_info.parse_yotta_target_cmd_output("mbed-gcc 0.0.14 \r\n"))
        self.assertIn("stm32f429i-disco-gcc", mbed_target_info.parse_yotta_target_cmd_output("stm32f429i-disco-gcc 0.0.14 \r\n"))

    def test_parse_yotta_search_cmd_output(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_search_cmd_output("frdm-k64f-gcc 0.0.24: Official mbed build target for the mbed frdm-k64f development board."))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_search_cmd_output("frdm-k64f-armcc 0.0.16: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain."))
        self.assertEqual(None, mbed_target_info.parse_yotta_search_cmd_output(""))
        self.assertEqual(None, mbed_target_info.parse_yotta_search_cmd_output("additional results from https://yotta-private.herokuapp.com:"))

    def test_parse_yotta_search_cmd_output_text(self):
        # Old style with new switch --short : 'yotta search ... --short'
        text = """frdm-k64f-gcc 0.1.4: Official mbed build target for the mbed frdm-k64f development board.
frdm-k64f-armcc 0.1.3: Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.

additional results from https://yotta-private.herokuapp.com:
"""
        targets = []
        for line in text.splitlines():
            yotta_target_name = mbed_target_info.parse_yotta_search_cmd_output(line)
            if yotta_target_name:
                targets.append(yotta_target_name)
        self.assertIn("frdm-k64f-gcc", targets)
        self.assertIn("frdm-k64f-armcc", targets)
        self.assertEqual(2, len(targets))

    def test_parse_yotta_search_cmd_output_new_style(self):
        self.assertIn("frdm-k64f-gcc", mbed_target_info.parse_yotta_search_cmd_output("frdm-k64f-gcc 0.1.4"))
        self.assertIn("frdm-k64f-armcc", mbed_target_info.parse_yotta_search_cmd_output("frdm-k64f-armcc 0.1.4"))
        pass

    def test_parse_yotta_search_cmd_output_new_style_text(self):
        # New style of 'yotta search ...'
        text = """frdm-k64f-gcc 0.1.4
    Official mbed build target for the mbed frdm-k64f development board.
    mbed-target:k64f, mbed-official, k64f, frdm-k64f, gcc
frdm-k64f-armcc 0.1.4
    Official mbed build target for the mbed frdm-k64f development board, using the armcc toolchain.
    mbed-target:k64f, mbed-official, k64f, frdm-k64f, armcc

additional results from https://yotta-private.herokuapp.com:"""
        targets = []
        for line in text.splitlines():
            yotta_target_name = mbed_target_info.parse_yotta_search_cmd_output(line)
            if yotta_target_name:
                targets.append(yotta_target_name)
        self.assertIn("frdm-k64f-gcc", targets)
        self.assertIn("frdm-k64f-armcc", targets)
        self.assertEqual(2, len(targets))

    def test_parse_yotta_search_cmd_output_new_style_text_2(self):
        # New style of 'yotta search ...'
        text = """nrf51dk-gcc 0.0.3:
    Official mbed build target for the nRF51-DK 32KB platform.
    mbed-official, mbed-target:nrf51_dk, gcc

additional results from https://yotta-private.herokuapp.com:
  nrf51dk-gcc 0.0.3:
      Official mbed build target for the nRF51-DK 32KB platform.
      mbed-official, mbed-target:nrf51_dk, gcc
  nrf51dk-armcc 0.0.3:
      Official mbed build target for the nRF51-DK 32KB platform.
      mbed-official, mbed-target:nrf51_dk, armcc
"""
        targets = []
        for line in text.splitlines():
            yotta_target_name = mbed_target_info.parse_yotta_search_cmd_output(line)
            if yotta_target_name and yotta_target_name not in targets:
                targets.append(yotta_target_name)

        self.assertIn("nrf51dk-gcc", targets)
        self.assertIn("nrf51dk-armcc", targets)
        self.assertEqual(2, len(targets))

    def test_parse_yotta_search_cmd_output_with_ssl_errors(self):
        result = []
        for line in self.YOTTA_SEARCH_SSL_ISSUE.splitlines():
            yotta_target_name = mbed_target_info.parse_yotta_search_cmd_output(line)
            if yotta_target_name:
                result.append(yotta_target_name)
        self.assertIn("frdm-k64f-gcc", result)
        self.assertIn("frdm-k64f-armcc", result)
        self.assertEqual(2, len(result))

    def test_parse_mbed_target_from_target_json(self):
        target_json_data = {
          "name": "frdm-k64f-armcc",
          "version": "0.1.4",
          "keywords": [
            "mbed-target:k64f",
            "mbed-official",
            "k64f",
            "frdm-k64f",
            "armcc"
          ],
        }

        # Positive tests
        self.assertEqual('frdm-k64f-armcc', mbed_target_info.parse_mbed_target_from_target_json('k64f', target_json_data))
        self.assertEqual('frdm-k64f-armcc', mbed_target_info.parse_mbed_target_from_target_json('K64F', target_json_data))

        # Except cases
        self.assertNotEqual('frdm-k64f-gcc', mbed_target_info.parse_mbed_target_from_target_json('k64f', target_json_data))
        self.assertNotEqual('frdm-k64f-gcc', mbed_target_info.parse_mbed_target_from_target_json('K64F', target_json_data))
        self.assertEqual(None, mbed_target_info.parse_mbed_target_from_target_json('_k64f_', target_json_data))
        self.assertEqual(None, mbed_target_info.parse_mbed_target_from_target_json('', target_json_data))
        self.assertEqual(None, mbed_target_info.parse_mbed_target_from_target_json('Some board name', target_json_data))

    def test_parse_mbed_target_from_target_json_multiple(self):
        target_json_data = {
          "name": "frdm-k64f-armcc",
          "version": "0.1.4",
          "keywords": [
            "mbed-target:k64f",
            "mbed-target:frdm-k64f",
            "mbed-official",
            "k64f",
            "frdm-k64f",
            "armcc"
          ],
        }

        # Positive tests
        self.assertEqual('frdm-k64f-armcc', mbed_target_info.parse_mbed_target_from_target_json('k64f', target_json_data))
        self.assertEqual('frdm-k64f-armcc', mbed_target_info.parse_mbed_target_from_target_json('frdm-k64f', target_json_data))
        self.assertEqual('frdm-k64f-armcc', mbed_target_info.parse_mbed_target_from_target_json('K64F', target_json_data))
        self.assertEqual('frdm-k64f-armcc', mbed_target_info.parse_mbed_target_from_target_json('FRDM-K64F', target_json_data))

        # Except cases
        self.assertNotEqual('frdm-k64f-gcc', mbed_target_info.parse_mbed_target_from_target_json('k64f', target_json_data))
        self.assertNotEqual('frdm-k64f-gcc', mbed_target_info.parse_mbed_target_from_target_json('frdm-k64f', target_json_data))
        self.assertNotEqual('frdm-k64f-gcc', mbed_target_info.parse_mbed_target_from_target_json('K64F', target_json_data))
        self.assertNotEqual('frdm-k64f-gcc', mbed_target_info.parse_mbed_target_from_target_json('FRDM-K64F', target_json_data))

if __name__ == '__main__':
    unittest.main()
