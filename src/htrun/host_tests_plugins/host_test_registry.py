#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Registry of available host test plugins."""


class HostTestRegistry:
    """Register and store host test plugins for further usage."""

    # Here we actually store all the plugins
    PLUGINS = {}  # 'Plugin Name' : Plugin Object

    def print_error(self, text):
        """Print an error message to the console.

        Args:
            text: Error message reason.
        """
        print("Plugin load failed. Reason: %s" % text)

    def register_plugin(self, plugin):
        """Store a plugin in the registry.

        This method also calls the plugin's setup() method to configure the plugin.

        Args:
            plugin: Plugin instance.

        Returns:
            True if plugin setup was successful and plugin can be registered, else
            False.
        """
        # TODO:
        # - check for unique caps for specified type
        if plugin.name not in self.PLUGINS:
            if plugin.setup():  # Setup plugin can be completed without errors
                self.PLUGINS[plugin.name] = plugin
                return True
            else:
                self.print_error("%s setup failed" % plugin.name)
        else:
            self.print_error("%s already loaded" % plugin.name)
        return False

    def call_plugin(self, type, capability, *args, **kwargs):
        """Execute the first plugin found with a particular 'type' and 'capability'.

        Args:
            type: Plugin type.
            capability: Plugin capability name.
            args: Additional plugin parameters.
            kwargs: Additional plugin parameters.

        Returns:
            True if a plugin was found and execution succeeded, otherwise False.
        """
        for plugin_name in self.PLUGINS:
            plugin = self.PLUGINS[plugin_name]
            if plugin.type == type and capability in plugin.capabilities:
                return plugin.execute(capability, *args, **kwargs)
        return False

    def get_plugin_caps(self, type):
        """List all capabilities for plugins with the specified type.

        Args:
            type: Plugin type.

        Returns:
            List of capabilities found. If there are no capabilities an empty
            list is returned.
        """
        result = []
        for plugin_name in self.PLUGINS:
            plugin = self.PLUGINS[plugin_name]
            if plugin.type == type:
                result.extend(plugin.capabilities)
        return sorted(result)

    def load_plugin(self, name):
        """Import a plugin module.

        Args:
            name: Name of the module to import.

        Returns:
            Imported module.

        Raises:
            ImportError: The module with the given name was not found.
        """
        mod = __import__("module_%s" % name)
        return mod

    def get_string(self):
        """User friendly printing method to show hooked plugins.

        Returns:
            PrettyTable formatted string describing the contents of the plugin
            registry.
        """
        from prettytable import PrettyTable, HEADER

        column_names = [
            "name",
            "type",
            "capabilities",
            "stable",
            "os_support",
            "required_parameters",
        ]
        pt = PrettyTable(column_names, junction_char="|", hrules=HEADER)
        for column in column_names:
            pt.align[column] = "l"
        for plugin_name in sorted(self.PLUGINS.keys()):
            name = self.PLUGINS[plugin_name].name
            type = self.PLUGINS[plugin_name].type
            stable = self.PLUGINS[plugin_name].stable
            capabilities = ", ".join(self.PLUGINS[plugin_name].capabilities)
            is_os_supported = self.PLUGINS[plugin_name].is_os_supported()
            required_parameters = ", ".join(
                self.PLUGINS[plugin_name].required_parameters
            )
            row = [
                name,
                type,
                capabilities,
                stable,
                is_os_supported,
                required_parameters,
            ]
            pt.add_row(row)
        return pt.get_string()

    def get_dict(self):
        """Return a dictionary of registered plugins."""
        result = {}
        for plugin_name in sorted(self.PLUGINS.keys()):
            name = self.PLUGINS[plugin_name].name
            type = self.PLUGINS[plugin_name].type
            stable = self.PLUGINS[plugin_name].stable
            capabilities = self.PLUGINS[plugin_name].capabilities
            is_os_supported = self.PLUGINS[plugin_name].is_os_supported()
            required_parameters = self.PLUGINS[plugin_name].required_parameters
            result[plugin_name] = {
                "name": name,
                "type": type,
                "stable": stable,
                "capabilities": capabilities,
                "os_support": is_os_supported,
                "required_parameters": required_parameters,
            }
        return result

    def __str__(self):
        """Return str representation of object."""
        return self.get_string()
