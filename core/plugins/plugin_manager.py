"""
Plugin Manager for ORION

Central orchestration system for plugin discovery, loading, and lifecycle management.
Handles dynamic plugin loading from multiple directories and integrates with ORION's core.
"""

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type
from logger import logger
from core.plugins.plugin_base import PluginBase


class PluginManager:
    """
    Manages the lifecycle of all ORION plugins.

    Responsibilities:
    - Discover plugins from configured directories
    - Load and initialize plugins dynamically
    - Manage plugin lifecycle (enable, disable, reload)
    - Track plugin status and handle errors gracefully

    Attributes:
        plugin_dirs: List of directories to search for plugins
        plugins: Dictionary of loaded plugin instances
    """

    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        """
        Initialize the plugin manager.

        Args:
            plugin_dirs: List of directories to search for plugins.
                        If None, uses default directories.
        """
        self.plugins: Dict[str, PluginBase] = {}

        if plugin_dirs is None:
            # Default plugin directories
            base_dir = Path(__file__).parent
            user_dir = Path.home() / '.orion' / 'plugins'
            self.plugin_dirs = [
                str(base_dir),  # core/plugins/
                str(user_dir)   # ~/.orion/plugins/
            ]
        else:
            self.plugin_dirs = plugin_dirs

        logger.info("PluginManager initialized with directories: %s", self.plugin_dirs)

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in configured directories.

        Searches for Python packages (directories with __init__.py) that
        contain a plugin.py file with a PluginBase subclass.

        Returns:
            List of discovered plugin names
        """
        discovered = []

        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                logger.debug("Plugin directory does not exist: %s", plugin_dir)
                continue

            # Scan for subdirectories (potential plugins)
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)

                # Skip if not a directory
                if not os.path.isdir(item_path):
                    continue

                # Skip special directories
                if item.startswith('_') or item.startswith('.'):
                    continue

                # Check if it's a valid plugin package
                plugin_file = os.path.join(item_path, 'plugin.py')
                init_file = os.path.join(item_path, '__init__.py')

                if os.path.exists(plugin_file) and os.path.exists(init_file):
                    discovered.append(item)
                    logger.debug("Discovered plugin: %s at %s", item, item_path)

        logger.info("Discovered %d plugins: %s", len(discovered), discovered)
        return discovered

    def load_plugin(self, plugin_name: str) -> bool:  # pylint: disable=too-many-return-statements
        """
        Load and initialize a plugin by name.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            True if plugin loaded successfully, False otherwise
        """
        if plugin_name in self.plugins:
            logger.warning("Plugin '%s' is already loaded", plugin_name)
            return True

        try:
            # Find the plugin directory
            plugin_path = self._find_plugin_path(plugin_name)
            if not plugin_path:
                logger.error("Plugin '%s' not found in any plugin directory", plugin_name)
                return False

            # Import the plugin module
            plugin_module = self._import_plugin_module(plugin_name, plugin_path)
            if not plugin_module:
                return False

            # Find the PluginBase subclass
            plugin_class = self._find_plugin_class(plugin_module, plugin_name)
            if not plugin_class:
                return False

            # Instantiate the plugin
            plugin_instance = plugin_class()

            # Initialize the plugin
            if not plugin_instance.initialize():
                logger.error("Plugin '%s' initialization failed", plugin_name)
                plugin_instance.error_state = "Initialization failed"
                return False

            # Mark as loaded and store
            plugin_instance.loaded = True
            plugin_instance.enabled = True
            self.plugins[plugin_name] = plugin_instance

            # Register plugin functions
            plugin_instance.register_functions()
            plugin_instance.on_enable()

            logger.info("Plugin '%s' v%s loaded successfully",
                       plugin_instance.name, plugin_instance.version)
            return True

        except ImportError as e:
            logger.error("Failed to import plugin '%s': %s", plugin_name, e)
            return False
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error loading plugin '%s': %s", plugin_name, e, exc_info=True)
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin and clean up its resources.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if plugin unloaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            logger.warning("Plugin '%s' is not loaded", plugin_name)
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Disable and shutdown
            if plugin.enabled:
                plugin.on_disable()
                plugin.enabled = False

            plugin.shutdown()
            plugin.loaded = False

            # Remove from registry
            del self.plugins[plugin_name]

            logger.info("Plugin '%s' unloaded successfully", plugin_name)
            return True

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error unloading plugin '%s': %s", plugin_name, e, exc_info=True)
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (useful for development).

        Args:
            plugin_name: Name of the plugin to reload

        Returns:
            True if plugin reloaded successfully, False otherwise
        """
        logger.info("Reloading plugin '%s'", plugin_name)

        # Unload if currently loaded
        if plugin_name in self.plugins:
            if not self.unload_plugin(plugin_name):
                return False

        # Reload the module
        return self.load_plugin(plugin_name)

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Get a loaded plugin instance by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_name)

    def list_plugins(self) -> Dict[str, Dict]:
        """
        Get status information for all loaded plugins.

        Returns:
            Dictionary mapping plugin names to their status info
        """
        return {
            name: plugin.get_status()
            for name, plugin in self.plugins.items()
        }

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a loaded plugin.

        Args:
            plugin_name: Name of the plugin to enable

        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.error("Plugin '%s' not found", plugin_name)
            return False

        if plugin.enabled:
            logger.info("Plugin '%s' is already enabled", plugin_name)
            return True

        plugin.enabled = True
        plugin.on_enable()
        logger.info("Plugin '%s' enabled", plugin_name)
        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a loaded plugin.

        Args:
            plugin_name: Name of the plugin to disable

        Returns:
            True if successful, False otherwise
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            logger.error("Plugin '%s' not found", plugin_name)
            return False

        if not plugin.enabled:
            logger.info("Plugin '%s' is already disabled", plugin_name)
            return True

        plugin.on_disable()
        plugin.enabled = False
        logger.info("Plugin '%s' disabled", plugin_name)
        return True

    def load_all_plugins(self) -> int:
        """
        Discover and load all available plugins.

        Returns:
            Number of successfully loaded plugins
        """
        discovered = self.discover_plugins()
        loaded_count = 0

        for plugin_name in discovered:
            if self.load_plugin(plugin_name):
                loaded_count += 1

        logger.info("Loaded %d/%d plugins", loaded_count, len(discovered))
        return loaded_count

    def _find_plugin_path(self, plugin_name: str) -> Optional[str]:
        """
        Find the filesystem path for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Absolute path to plugin directory or None if not found
        """
        for plugin_dir in self.plugin_dirs:
            plugin_path = os.path.join(plugin_dir, plugin_name)
            if os.path.exists(plugin_path):
                return plugin_path
        return None

    def _import_plugin_module(self, plugin_name: str, plugin_path: str):
        """
        Dynamically import a plugin module.

        Args:
            plugin_name: Name of the plugin
            plugin_path: Path to the plugin directory

        Returns:
            Imported module or None on failure
        """
        try:
            # Construct module path
            module_file = os.path.join(plugin_path, 'plugin.py')
            module_name = f"core.plugins.{plugin_name}.plugin"

            # Add plugin directory to sys.path if not already there
            if plugin_path not in sys.path:
                sys.path.insert(0, os.path.dirname(plugin_path))

            # Import using importlib
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                return module

            logger.error("Failed to create module spec for '%s'", plugin_name)
            return None

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error importing plugin module '%s': %s", plugin_name, e)
            return None

    def _find_plugin_class(self, module, plugin_name: str) -> Optional[Type[PluginBase]]:
        """
        Find the PluginBase subclass in a module.

        Args:
            module: Imported plugin module
            plugin_name: Name of the plugin (for logging)

        Returns:
            Plugin class or None if not found
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # Check if it's a class and subclass of PluginBase (but not PluginBase itself)
            if (isinstance(attr, type) and
                issubclass(attr, PluginBase) and
                attr is not PluginBase):
                return attr

        logger.error("No PluginBase subclass found in plugin '%s'", plugin_name)
        return None
