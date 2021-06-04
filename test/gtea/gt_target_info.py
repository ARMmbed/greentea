#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import shutil
import tempfile
import unittest

from six import StringIO

from mock import patch
from greentea.gtea import target_info


class GreenteaTargetInfo(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_platform_property_from_targets_no_json(self):
        with patch("greentea.gtea.target_info._find_targets_json") as _find:
            _find.return_value = iter([])
            result = target_info._get_platform_property_from_targets(
                "not_a_platform", "not_a_property"
            )
            self.assertIsNone(result)

    def test_get_platform_property_from_targets_no_file(self):
        with patch("greentea.gtea.target_info._find_targets_json") as _find, patch(
            "greentea.gtea.target_info.open"
        ) as _open:
            _find.return_value = iter(["foo"])
            _open.side_effect = IOError
            result = target_info._get_platform_property_from_targets(
                "not_a_platform", "not_a_property"
            )
            self.assertIsNone(result)

    def test_get_platform_property_from_targets_invalid_json(self):
        with patch("greentea.gtea.target_info._find_targets_json") as _find, patch(
            "greentea.gtea.target_info.open"
        ) as _open:
            _find.return_value = iter(["foo"])
            _open.return_value.__enter__.return_value = StringIO("{")
            result = target_info._get_platform_property_from_targets(
                "not_a_platform", "not_a_property"
            )
            self.assertIsNone(result)

    def test_get_platform_property_from_targets_empty_json(self):
        with patch("greentea.gtea.target_info._find_targets_json") as _find, patch(
            "greentea.gtea.target_info.open"
        ) as _open:
            _find.return_value = iter(["foo"])
            _open.return_value.__enter__.return_value = StringIO("{}")
            result = target_info._get_platform_property_from_targets(
                "not_a_platform", "not_a_property"
            )
            self.assertIsNone(result)

    def test_get_platform_property_from_targets_no_value(self):
        with patch("greentea.gtea.target_info._find_targets_json") as _find, patch(
            "greentea.gtea.target_info.open"
        ) as _open:
            _find.return_value = iter(["foo"])
            _open.return_value.__enter__.return_value = StringIO('{"K64F": {}}')
            result = target_info._get_platform_property_from_targets(
                "K64F", "not_a_property"
            )
            self.assertEqual(result, None)

    def test_get_platform_property_from_targets_in_json(self):
        with patch("greentea.gtea.target_info._find_targets_json") as _find, patch(
            "greentea.gtea.target_info.open"
        ) as _open:
            _find.return_value = iter(["foo"])
            _open.return_value.__enter__.return_value = StringIO(
                '{"K64F": {"copy_method": "cp"}}'
            )
            result = target_info._get_platform_property_from_targets(
                "K64F", "copy_method"
            )
            self.assertEqual("cp", result)

    def test_find_targets_json(self):
        with patch("greentea.gtea.target_info.os.walk") as _walk:
            _walk.return_value = iter(
                [("", ["foo"], []), ("foo", [], ["targets.json"])]
            )
            result = list(target_info._find_targets_json("bogus_path"))
            self.assertEqual(result, [os.path.join("foo", "targets.json")])

    def test_find_targets_json_ignored(self):
        with patch("greentea.gtea.target_info.os.walk") as _walk:
            walk_result = [("", [".build"], [])]
            _walk.return_value = iter(walk_result)
            result = list(target_info._find_targets_json("bogus_path"))
            self.assertEqual(result, [])
            self.assertEqual(walk_result, [("", [], [])])

    def test_platform_property_from_targets_json_empty(self):
        result = target_info._platform_property_from_targets_json(
            {}, "not_a_target", "not_a_property"
        )
        self.assertIsNone(result)

    def test_platform_property_from_targets_json_base_target(self):
        result = target_info._platform_property_from_targets_json(
            {"K64F": {"copy_method": "cp"}}, "K64F", "copy_method"
        )
        self.assertEqual(result, "cp")

    def test_platform_property_from_targets_json_inherits(self):
        result = target_info._platform_property_from_targets_json(
            {"K64F": {"inherits": ["Target"]}, "Target": {"copy_method": "cp"}},
            "K64F",
            "copy_method",
        )
        self.assertEqual(result, "cp")

    def test_platform_property_from_default_missing(self):
        result = target_info._get_platform_property_from_default("not_a_property")
        self.assertIsNone(result)

    def test_platform_property_from_default(self):
        result = target_info._get_platform_property_from_default("copy_method")
        self.assertEqual(result, "default")

    def test_platform_property(self):
        """Test that platform_property picks the property value preserving
        the following priority relationship:
        targets.json > default
        """
        with patch(
            "greentea.gtea.target_info._get_platform_property_from_targets"
        ) as _targets, patch(
            "greentea.gtea.target_info._get_platform_property_from_default"
        ) as _default:
            # 1
            _targets.return_value = "targets"
            _default.return_value = "default"
            self.assertEqual(
                target_info.get_platform_property("K64F", "copy_method"), "targets"
            )
            # 2
            _targets.return_value = None
            self.assertEqual(
                target_info.get_platform_property("K64F", "copy_method"), "default"
            )
            # 3
            _default.return_value = None
            self.assertEqual(
                target_info.get_platform_property("K64F", "copy_method"), None
            )
            # 4
            _targets.return_value = "targets"
            self.assertEqual(
                target_info.get_platform_property("K64F", "copy_method"), "targets"
            )


if __name__ == "__main__":
    unittest.main()
