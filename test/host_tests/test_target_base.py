#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import shutil
import mock
import os
import unittest
from tempfile import mkdtemp

from htrun.host_tests_runner.target_base import TargetBase


class TemporaryDirectory(object):
    def __init__(self):
        self.fname = "tempdir"

    def __enter__(self):
        self.fname = mkdtemp()
        return self.fname

    def __exit__(self, *args, **kwargs):
        shutil.rmtree(self.fname)


@mock.patch("htrun.host_tests_runner.target_base.ht_plugins")
@mock.patch("htrun.host_tests_runner.target_base.create")
class TestTargetBase(unittest.TestCase):
    def test_skips_discover_mbed_if_non_mbed_copy_method_used(
        self, mock_create, mock_ht_plugins
    ):
        with TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "test.elf")
            with open(image_path, "w") as f:
                f.write("1234")

            options = mock.Mock(
                copy_method="pyocd",
                image_path=image_path,
                disk=None,
                port="port",
                micro="mcu",
                target_id="BK99",
                polling_timeout=5,
                program_cycle_s=None,
                json_test_configuration=None,
                format="blah",
            )

            mbed = TargetBase(options)
            mbed.copy_image()

            mock_create().list_mbeds.assert_not_called()
            mock_ht_plugins.call_plugin.assert_called_once_with(
                "CopyMethod",
                options.copy_method,
                image_path=options.image_path,
                mcu=options.micro,
                serial=options.port,
                destination_disk=options.disk,
                target_id=options.target_id,
                pooling_timeout=options.polling_timeout,
                format=options.format,
            )

    def test_discovers_mbed_if_mbed_copy_method_used(
        self, mock_create, mock_ht_plugins
    ):
        with TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "test.elf")
            with open(image_path, "w") as f:
                f.write("1234")
            options = mock.Mock(
                copy_method="shell",
                image_path=image_path,
                disk=None,
                port="port",
                micro="mcu",
                target_id="BK99",
                polling_timeout=5,
                program_cycle_s=None,
                json_test_configuration=None,
                format="blah",
            )

            mbed = TargetBase(options)
            mbed.copy_image()

            mock_create().list_mbeds.assert_called()
            mock_ht_plugins.call_plugin.assert_called_once_with(
                "CopyMethod",
                options.copy_method,
                image_path=options.image_path,
                mcu=options.micro,
                serial=options.port,
                destination_disk=options.disk,
                target_id=options.target_id,
                pooling_timeout=options.polling_timeout,
                format=options.format,
            )


if __name__ == "__main__":
    unittest.main()
