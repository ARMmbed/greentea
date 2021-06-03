#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import tempfile
import unittest

from greentea.gtea import greentea_dlm


home_dir = tempfile.mkdtemp()
greentea_dlm.HOME_DIR = home_dir
greentea_dlm.GREENTEA_HOME_DIR = ".mbed-greentea"
greentea_dlm.GREENTEA_GLOBAL_LOCK = "glock.lock"
greentea_dlm.GREENTEA_KETTLE = "kettle.json"  # active Greentea instances
greentea_dlm.GREENTEA_KETTLE_PATH = os.path.join(
    greentea_dlm.HOME_DIR,
    greentea_dlm.GREENTEA_HOME_DIR,
    greentea_dlm.GREENTEA_KETTLE,
)


class GreenteaDlmFunctionality(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_greentea_home_dir_init(self):
        greentea_dlm.greentea_home_dir_init()

        path = os.path.join(greentea_dlm.HOME_DIR, greentea_dlm.GREENTEA_HOME_DIR)
        self.assertTrue(os.path.exists(path))

    def test_greentea_get_app_sem(self):
        sem, name, uuid = greentea_dlm.greentea_get_app_sem()
        self.assertIsNotNone(sem)
        self.assertIsNotNone(name)
        self.assertIsNotNone(uuid)

    def test_greentea_get_target_lock(self):
        lock = greentea_dlm.greentea_get_target_lock("target-id-2")
        path = os.path.join(
            greentea_dlm.HOME_DIR,
            greentea_dlm.GREENTEA_HOME_DIR,
            "target-id-2",
        )
        self.assertIsNotNone(lock)
        self.assertEqual(path, lock.path)

    def test_greentea_get_global_lock(self):
        lock = greentea_dlm.greentea_get_global_lock()
        path = os.path.join(
            greentea_dlm.HOME_DIR,
            greentea_dlm.GREENTEA_HOME_DIR,
            "glock.lock",
        )
        self.assertIsNotNone(lock)
        self.assertEqual(path, lock.path)

    def test_get_json_data_from_file_invalid_file(self):
        result = greentea_dlm.get_json_data_from_file("null_file")
        self.assertIsNone(result)

    def test_get_json_data_from_file_invalid_json(self):
        path = os.path.join(greentea_dlm.HOME_DIR, "test")

        with open(path, "w") as f:
            f.write("invalid json")

        result = greentea_dlm.get_json_data_from_file(path)
        self.assertEqual(result, None)

        os.remove(path)

    def test_get_json_data_from_file_valid_file(self):
        path = os.path.join(greentea_dlm.HOME_DIR, "test")

        with open(path, "w") as f:
            f.write("{}")

        result = greentea_dlm.get_json_data_from_file(path)
        self.assertEqual(result, {})

        os.remove(path)

    def test_greentea_update_kettle(self):
        uuid = "001"
        greentea_dlm.greentea_update_kettle(uuid)

        data = greentea_dlm.get_json_data_from_file(greentea_dlm.GREENTEA_KETTLE_PATH)
        self.assertIsNotNone(data)
        self.assertIn("start_time", data[uuid])
        self.assertIn("cwd", data[uuid])
        self.assertIn("locks", data[uuid])

        self.assertEqual(data[uuid]["cwd"], os.getcwd())
        self.assertEqual(data[uuid]["locks"], [])

        # Check greentea_kettle_info()
        output = greentea_dlm.greentea_kettle_info().splitlines()
        line = output[3]
        self.assertIn(os.getcwd(), line)
        self.assertIn(uuid, line)

        # Test greentea_acquire_target_id
        target_id = "999"
        greentea_dlm.greentea_acquire_target_id(target_id, uuid)
        data = greentea_dlm.get_json_data_from_file(greentea_dlm.GREENTEA_KETTLE_PATH)
        self.assertIn(uuid, data)
        self.assertIn("locks", data[uuid])
        self.assertIn(target_id, data[uuid]["locks"])

        # Test greentea_release_target_id
        greentea_dlm.greentea_release_target_id(target_id, uuid)
        data = greentea_dlm.get_json_data_from_file(greentea_dlm.GREENTEA_KETTLE_PATH)
        self.assertIn(uuid, data)
        self.assertIn("locks", data[uuid])
        self.assertNotIn(target_id, data[uuid]["locks"])

        # Test greentea_acquire_target_id_from_list
        target_id = "999"
        result = greentea_dlm.greentea_acquire_target_id_from_list([target_id], uuid)
        data = greentea_dlm.get_json_data_from_file(greentea_dlm.GREENTEA_KETTLE_PATH)
        self.assertEqual(result, target_id)
        self.assertIn(uuid, data)
        self.assertIn("locks", data[uuid])
        self.assertIn(target_id, data[uuid]["locks"])

        # Check greentea_clean_kettle()
        greentea_dlm.greentea_clean_kettle(uuid)
        data = greentea_dlm.get_json_data_from_file(greentea_dlm.GREENTEA_KETTLE_PATH)
        self.assertEqual(data, {})
