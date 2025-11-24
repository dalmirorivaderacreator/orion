# ORION Plugin System - Developer Guide

## Overview

The ORION Plugin System provides a modular architecture for extending ORION's functionality without modifying core code. Plugins can register new functions, add capabilities, and integrate with external services.

## Architecture

### Core Components

- **`PluginBase`**: Abstract base class that all plugins must inherit from
- **`PluginManager`**: Central orchestration system for plugin lifecycle
- **Function Registry**: Integration point with ORION's existing function system

### Plugin Discovery

Plugins are automatically discovered from two locations:
1. `core/plugins/` - Built-in plugins shipped with ORION
2. `~/.orion/plugins/` - User-installed third-party plugins

## Creating a Plugin

### Step 1: Create Plugin Directory

```bash
mkdir -p core/plugins/my_plugin
cd core/plugins/my_plugin
```

### Step 2: Create Package Structure

Create `__init__.py`:
```python
"""
My Plugin for ORION
"""
from core.plugins.my_plugin.plugin import MyPlugin

__all__ = ['MyPlugin']
```

### Step 3: Implement Plugin Class

Create `plugin.py`:
```python
"""
My Plugin Implementation
"""
from core.plugins.plugin_base import PluginBase
from registry import register_function


class MyPlugin(PluginBase):
    """
    My custom plugin for ORION.
    """
    
    @property
    def name(self) -> str:
        return "my_plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Description of what my plugin does"
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    @property
    def dependencies(self) -> list:
        """List required Python packages"""
        return ["requests", "some-package"]
    
    def initialize(self) -> bool:
        """
        Initialize plugin resources.
        Return True if successful, False otherwise.
        """
        try:
            # Check dependencies
            import requests
            
            # Initialize resources
            self.set_config("api_key", "your-api-key")
            
            return True
        except ImportError:
            self.error_state = "Missing dependencies"
            return False
    
    def shutdown(self) -> None:
        """Clean up resources when plugin is unloaded."""
        # Close connections, save state, etc.
        pass
    
    def register_functions(self) -> None:
        """Register plugin functions with ORION."""
        
        @register_function(
            name="my_function",
            description="Does something useful",
            argument_types={
                "input_path": "str",
                "output_path": "str"
            }
        )
        def my_function(input_path: str, output_path: str) -> str:
            """
            Function implementation.
            
            Args:
                input_path: Input file path
                output_path: Output file path
                
            Returns:
                Status message
            """
            # Your implementation here
            return f"Processed {input_path} -> {output_path}"
```

### Step 4: Add Dependencies (Optional)

Create `requirements.txt`:
```
requests>=2.28.0
some-package>=1.0.0
```

## Plugin Lifecycle

### Lifecycle Hooks

1. **`initialize()`**: Called once when plugin is loaded
2. **`on_enable()`**: Called when plugin is enabled
3. **`on_disable()`**: Called when plugin is disabled
4. **`shutdown()`**: Called when plugin is unloaded

### Lifecycle Flow

```
Load Plugin → initialize() → register_functions() → on_enable()
                                                         ↓
                                                    [ACTIVE]
                                                         ↓
                                              on_disable() → shutdown()
```

## API Reference

### PluginBase Methods

#### Configuration
- `get_config(key, default=None)`: Get configuration value
- `set_config(key, value)`: Set configuration value

#### Status
- `get_status()`: Get plugin status dictionary
- `enabled`: Boolean property indicating if plugin is active
- `loaded`: Boolean property indicating if plugin is loaded
- `error_state`: String describing any error condition

### PluginManager Methods

#### Discovery & Loading
- `discover_plugins()`: Find available plugins
- `load_plugin(name)`: Load a specific plugin
- `load_all_plugins()`: Load all discovered plugins
- `unload_plugin(name)`: Unload a plugin
- `reload_plugin(name)`: Hot-reload a plugin

#### Management
- `get_plugin(name)`: Get plugin instance
- `list_plugins()`: Get status of all plugins
- `enable_plugin(name)`: Enable a plugin
- `disable_plugin(name)`: Disable a plugin

## Registering Functions

Functions registered by plugins become available to ORION's LLM dispatcher automatically.

### Function Registration Example

```python
from registry import register_function

@register_function(
    name="process_data",
    description="Procesa datos de entrada y genera salida",
    argument_types={
        "input_path": "str",
        "format": "str",
        "output_path": "str"
    }
)
def process_data(input_path: str, format: str, output_path: str) -> str:
    """Process data with specified format."""
    # Implementation
    return f"Data processed: {output_path}"
```

### Best Practices

1. **Clear Descriptions**: Use Spanish descriptions that clearly explain what the function does
2. **Type Hints**: Always specify argument types in `argument_types`
3. **Error Handling**: Return descriptive error messages, don't raise exceptions
4. **Return Values**: Return human-readable status messages
5. **Path Handling**: Use `os.path` for cross-platform compatibility

## Example Plugins

### file_processor
Batch file operations, duplicate detection, compression.

**Functions:**
- `batch_rename_files(directory, pattern, replacement)`
- `find_duplicates(directory)`
- `compress_files(directory, output_archive)`

### web_scraper
Web scraping and content extraction.

**Functions:**
- `scrape_webpage(url, selector)`
- `extract_links(url)`
- `download_images(url, output_dir)`

**Dependencies:** `beautifulsoup4`, `lxml`

### data_analyzer
Advanced data analysis and visualization.

**Functions:**
- `generate_chart(csv_path, chart_type, output_path)`
- `detect_outliers(csv_path, column)`
- `correlation_matrix(csv_path, output_path)`

**Dependencies:** `matplotlib`, `seaborn`

## Testing Your Plugin

Create a test file in `tests/test_my_plugin.py`:

```python
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.plugins import PluginManager
from registry import get_function


class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.manager = PluginManager()
        self.manager.load_plugin("my_plugin")
    
    def test_plugin_loaded(self):
        plugin = self.manager.get_plugin("my_plugin")
        self.assertIsNotNone(plugin)
        self.assertTrue(plugin.enabled)
    
    def test_function_registered(self):
        func = get_function("my_function")
        self.assertIsNotNone(func)
    
    def test_function_execution(self):
        func = get_function("my_function")
        result = func['function'](
            input_path="test.txt",
            output_path="output.txt"
        )
        self.assertIn("Processed", result)


if __name__ == '__main__':
    unittest.main()
```

## Debugging

### Enable Debug Logging

Check `logs/orion.log` for plugin-related messages:
- Plugin discovery
- Loading success/failure
- Function registration
- Errors and exceptions

### Common Issues

**Plugin not discovered:**
- Ensure `__init__.py` and `plugin.py` exist
- Check plugin directory is in search path

**Plugin fails to load:**
- Check `initialize()` returns `True`
- Verify dependencies are installed
- Check logs for error messages

**Functions not available:**
- Ensure `register_functions()` is called
- Check function names don't conflict
- Verify `@register_function` decorator is used correctly

## Distribution

### Packaging for Distribution

1. Create plugin directory with all files
2. Include `requirements.txt` for dependencies
3. Add `README.md` with usage instructions
4. Package as ZIP or distribute via Git

### Installation by Users

```bash
# Clone to user plugin directory
cd ~/.orion/plugins
git clone https://github.com/user/my-plugin.git

# Install dependencies
cd my-plugin
pip install -r requirements.txt

# Restart ORION
```

## Advanced Topics

### Plugin Configuration

Store persistent configuration:

```python
def initialize(self):
    # Load from config file
    config_path = os.path.expanduser("~/.orion/my_plugin_config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            for key, value in config.items():
                self.set_config(key, value)
    return True
```

### Inter-Plugin Communication

Access other plugins via PluginManager:

```python
def my_function(self):
    # Get plugin manager instance
    from core.plugins import PluginManager
    manager = PluginManager()
    
    # Access another plugin
    other_plugin = manager.get_plugin("other_plugin")
    if other_plugin and other_plugin.enabled:
        # Use other plugin's functionality
        pass
```

### Hot Reload During Development

```python
# In ORION console
>>> from core.plugins import PluginManager
>>> manager = PluginManager()
>>> manager.reload_plugin("my_plugin")
```

## Support

For questions or issues:
- Check the logs: `logs/orion.log`
- Review example plugins in `core/plugins/`
- Consult the test suite in `tests/test_plugin_system.py`
