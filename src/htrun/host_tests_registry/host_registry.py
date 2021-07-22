#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Registry of available host tests."""

try:
    from imp import load_source
except ImportError:
    import importlib
    import sys

    def load_source(module_name, file_path):
        """Dynamically import a plugin module.

        Args:
           module_name: Name of the module to load.
           file_path: Path to the module.
        """
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module


from inspect import getmembers, isclass
from os import listdir
from os.path import abspath, exists, isdir, isfile, join

from ..host_tests.base_host_test import BaseHostTest


class HostRegistry:
    """Class stores registry with host tests and objects representing them."""

    HOST_TESTS = {}  # Map between host_test_name -> host_test_object

    def register_host_test(self, ht_name, ht_object):
        """Register host test object by name.

        Args:
            ht_name: Host test unique name.
            ht_object: Host test class object.
        """
        if ht_name not in self.HOST_TESTS:
            self.HOST_TESTS[ht_name] = ht_object

    def unregister_host_test(self, ht_name):
        """Unregister host test object by name.

        Args:
            ht_name: Host test unique name.
        """
        if ht_name in self.HOST_TESTS:
            del self.HOST_TESTS[ht_name]

    def get_host_test(self, ht_name):
        """Fetch host test object by name.

        Args:
            ht_name: Host test unique name.

        Returns:
            Host test callable object or None if object is not found.
        """
        return self.HOST_TESTS[ht_name] if ht_name in self.HOST_TESTS else None

    def is_host_test(self, ht_name):
        """Check (by name) if host test object is registered already.

        Args:
            ht_name: Host test unique name.

        Returns:
            True if ht_name is registered (available), else False.
        """
        return ht_name in self.HOST_TESTS and self.HOST_TESTS[ht_name] is not None

    def table(self, verbose=False):
        """Print list of registered host test classes (by name).

        For dev & debug purposes.
        """
        from prettytable import PrettyTable, HEADER

        column_names = ["name", "class", "origin"]
        pt = PrettyTable(column_names, junction_char="|", hrules=HEADER)
        for column in column_names:
            pt.align[column] = "l"

        for name, host_test in sorted(self.HOST_TESTS.items()):
            cls_str = str(host_test.__class__)
            if host_test.script_location:
                src_path = host_test.script_location
            else:
                src_path = "htrun"
            pt.add_row([name, cls_str, src_path])
        return pt.get_string()

    def register_from_path(self, path, verbose=False):
        """Enumerate and register locally stored host tests.

        Host test are derived from htrun.BaseHostTest classes

        Args:
            path: Path to the host tests directory.
            verbose: Enable verbose logging.
        """
        if path:
            path = path.strip('"')
            if verbose:
                print("HOST: Inspecting '%s' for local host tests..." % path)
            if exists(path) and isdir(path):
                python_modules = [
                    f
                    for f in listdir(path)
                    if isfile(join(path, f)) and f.endswith(".py")
                ]
                for module_file in python_modules:
                    self._add_module_to_registry(path, module_file, verbose)

    def _add_module_to_registry(self, path, module_file, verbose):
        module_name = module_file[:-3]
        try:
            mod = load_source(module_name, abspath(join(path, module_file)))
        except Exception as e:
            print(
                "HOST: Error while loading local host test module '%s'"
                % join(path, module_file)
            )
            print("HOST: %s" % str(e))
            return
        if verbose:
            print("HOST: Loading module '%s': %s" % (module_file, str(mod)))

        for name, obj in getmembers(mod):
            if (
                isclass(obj)
                and issubclass(obj, BaseHostTest)
                and str(obj) != str(BaseHostTest)
            ):
                if obj.name:
                    host_test_name = obj.name
                else:
                    host_test_name = module_name
                host_test_cls = obj
                host_test_cls.script_location = join(path, module_file)
                if verbose:
                    print(
                        "HOST: Found host test implementation: %s -|> %s"
                        % (str(obj), str(BaseHostTest))
                    )
                    print(
                        "HOST: Registering '%s' as '%s'"
                        % (str(host_test_cls), host_test_name)
                    )
                self.register_host_test(host_test_name, host_test_cls())
