"""
Test Suite for ORION Plugin System

Tests plugin discovery, loading, lifecycle management, and integration
with the function registry.
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# pylint: disable=wrong-import-position
from core.plugins import PluginBase, PluginManager
from registry import get_function


class MockPlugin(PluginBase):
    """Mock plugin for testing purposes."""

    @property
    def name(self) -> str:
        return "mock_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "A mock plugin for testing"

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def register_functions(self) -> None:
        from registry import register_function  # pylint: disable=import-outside-toplevel

        @register_function(
            name="mock_function",
            description="A mock function",
            argument_types={"arg": "str"}
        )
        def mock_function(arg: str) -> str:
            return f"Mock: {arg}"


class TestPluginBase(unittest.TestCase):
    """Test the PluginBase abstract class."""

    def test_plugin_instantiation(self):
        """Test that a plugin can be instantiated."""
        plugin = MockPlugin()
        self.assertEqual(plugin.name, "mock_plugin")
        self.assertEqual(plugin.version, "1.0.0")
        self.assertFalse(plugin.enabled)
        self.assertFalse(plugin.loaded)

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = MockPlugin()
        result = plugin.initialize()
        self.assertTrue(result)

    def test_plugin_config(self):
        """Test plugin configuration management."""
        plugin = MockPlugin()
        plugin.set_config("test_key", "test_value")
        self.assertEqual(plugin.get_config("test_key"), "test_value")
        self.assertIsNone(plugin.get_config("nonexistent"))
        self.assertEqual(plugin.get_config("nonexistent", "default"), "default")

    def test_plugin_status(self):
        """Test plugin status reporting."""
        plugin = MockPlugin()
        status = plugin.get_status()
        self.assertEqual(status['name'], "mock_plugin")
        self.assertEqual(status['version'], "1.0.0")
        self.assertFalse(status['enabled'])
        self.assertFalse(status['loaded'])


class TestPluginManager(unittest.TestCase):
    """Test the PluginManager class."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary plugin directory
        self.temp_dir = tempfile.mkdtemp()
        self.plugin_manager = PluginManager(plugin_dirs=[self.temp_dir])

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_plugin_manager_initialization(self):
        """Test plugin manager initialization."""
        self.assertIsNotNone(self.plugin_manager)
        self.assertEqual(len(self.plugin_manager.plugins), 0)

    def test_discover_plugins_empty(self):
        """Test plugin discovery with no plugins."""
        discovered = self.plugin_manager.discover_plugins()
        self.assertEqual(len(discovered), 0)

    def test_discover_plugins_with_valid_plugin(self):
        """Test plugin discovery with a valid plugin."""
        # Create a mock plugin directory
        plugin_dir = os.path.join(self.temp_dir, "test_plugin")
        os.makedirs(plugin_dir)

        # Create __init__.py
        with open(os.path.join(plugin_dir, "__init__.py"), "w", encoding="utf-8") as f:
            f.write("")

        # Create plugin.py
        with open(os.path.join(plugin_dir, "plugin.py"), "w", encoding="utf-8") as f:
            f.write("""
from core.plugins import PluginBase

class TestPlugin(PluginBase):
    @property
    def name(self):
        return "test_plugin"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "Test plugin"

    def initialize(self):
        return True

    def shutdown(self):
        pass

    def register_functions(self):
        pass
""")

        discovered = self.plugin_manager.discover_plugins()
        self.assertEqual(len(discovered), 1)
        self.assertIn("test_plugin", discovered)

    def test_list_plugins_empty(self):
        """Test listing plugins when none are loaded."""
        plugins = self.plugin_manager.list_plugins()
        self.assertEqual(len(plugins), 0)

    def test_get_plugin_not_found(self):
        """Test getting a plugin that doesn't exist."""
        plugin = self.plugin_manager.get_plugin("nonexistent")
        self.assertIsNone(plugin)


class TestPluginIntegration(unittest.TestCase):
    """Test plugin integration with ORION core."""

    def test_plugin_function_registration(self):
        """Test that plugin functions are registered correctly."""
        plugin = MockPlugin()
        plugin.initialize()
        plugin.register_functions()

        # Check if function was registered
        func_info = get_function("mock_function")
        self.assertIsNotNone(func_info)
        self.assertEqual(func_info['description'], "A mock function")

        # Test function execution
        result = func_info['function'](arg="test")
        self.assertEqual(result, "Mock: test")


class TestExamplePlugins(unittest.TestCase):
    """Test that example plugins can be loaded."""

    def setUp(self):
        """Set up plugin manager with default directories."""
        # Use actual plugin directories
        base_dir = Path(__file__).parent.parent / "core" / "plugins"
        self.plugin_manager = PluginManager(plugin_dirs=[str(base_dir)])

    def test_discover_example_plugins(self):
        """Test that example plugins are discovered."""
        discovered = self.plugin_manager.discover_plugins()

        # Should find at least the three example plugins
        expected_plugins = ["file_processor", "web_scraper", "data_analyzer"]
        for plugin_name in expected_plugins:
            self.assertIn(plugin_name, discovered,
                         f"Plugin '{plugin_name}' not discovered")

    def test_load_file_processor(self):
        """Test loading the file_processor plugin."""
        result = self.plugin_manager.load_plugin("file_processor")
        self.assertTrue(result, "Failed to load file_processor plugin")

        plugin = self.plugin_manager.get_plugin("file_processor")
        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.name, "file_processor")
        self.assertTrue(plugin.enabled)
        self.assertTrue(plugin.loaded)

        # Check registered functions
        self.assertIsNotNone(get_function("batch_rename_files"))
        self.assertIsNotNone(get_function("find_duplicates"))
        self.assertIsNotNone(get_function("compress_files"))

    def test_load_web_scraper(self):
        """Test loading the web_scraper plugin."""
        result = self.plugin_manager.load_plugin("web_scraper")
        # May fail if dependencies not installed, that's OK
        if result:
            plugin = self.plugin_manager.get_plugin("web_scraper")
            self.assertIsNotNone(plugin)
            self.assertEqual(plugin.name, "web_scraper")

    def test_load_data_analyzer(self):
        """Test loading the data_analyzer plugin."""
        result = self.plugin_manager.load_plugin("data_analyzer")
        # May fail if dependencies not installed, that's OK
        if result:
            plugin = self.plugin_manager.get_plugin("data_analyzer")
            self.assertIsNotNone(plugin)
            self.assertEqual(plugin.name, "data_analyzer")


if __name__ == '__main__':
    unittest.main()
