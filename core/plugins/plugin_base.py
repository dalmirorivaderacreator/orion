"""
Plugin Base Class for ORION

Defines the abstract interface that all ORION plugins must implement.
Provides lifecycle hooks, metadata management, and integration with the function registry.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class PluginBase(ABC):
    """
    Abstract base class for all ORION plugins.

    Plugins extend ORION's functionality by registering new functions,
    adding capabilities, or integrating with external services.

    Attributes:
        name: Unique identifier for the plugin
        version: Semantic version string (e.g., "1.0.0")
        description: Human-readable description of plugin functionality
        author: Plugin author/maintainer
        dependencies: List of required Python packages
        enabled: Whether the plugin is currently active
        loaded: Whether the plugin has been successfully loaded
        error_state: Error message if plugin failed to load
    """

    def __init__(self):
        """Initialize plugin with default state."""
        self.enabled = False
        self.loaded = False
        self.error_state: Optional[str] = None
        self._config: Dict[str, Any] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique plugin name."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Return the plugin version (semantic versioning)."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a human-readable description of the plugin."""

    @property
    def author(self) -> str:
        """Return the plugin author. Override if needed."""
        return "Unknown"

    @property
    def dependencies(self) -> List[str]:
        """
        Return list of required Python packages.

        Returns:
            List of package names (e.g., ['requests', 'beautifulsoup4'])
        """
        return []

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Called once when the plugin is first loaded. Use this to:
        - Set up resources
        - Validate dependencies
        - Initialize connections
        - Load configuration

        Returns:
            True if initialization succeeded, False otherwise
        """

    @abstractmethod
    def shutdown(self) -> None:
        """
        Clean up plugin resources.

        Called when the plugin is being unloaded or ORION is shutting down.
        Use this to:
        - Close connections
        - Save state
        - Release resources
        """

    def on_enable(self) -> None:
        """
        Called when the plugin is enabled.

        Override to perform actions when plugin becomes active.
        Default implementation does nothing.
        """

    def on_disable(self) -> None:
        """
        Called when the plugin is disabled.

        Override to perform cleanup when plugin becomes inactive.
        Default implementation does nothing.
        """

    @abstractmethod
    def register_functions(self) -> None:
        """
        Register plugin functions with ORION's function registry.

        Use the @register_function decorator from registry.py to add
        new functions that become available to the LLM dispatcher.

        Example:
            from registry import register_function

            @register_function(
                name="my_function",
                description="Does something useful",
                argument_types={"arg1": "str"}
            )
            def my_function(arg1):
                return f"Result: {arg1}"
        """

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to store
        """
        self._config[key] = value

    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status information.

        Returns:
            Dictionary with plugin status details
        """
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
            'loaded': self.loaded,
            'error_state': self.error_state,
            'dependencies': self.dependencies
        }

    def __repr__(self) -> str:
        """Return string representation of plugin."""
        status = "enabled" if self.enabled else "disabled"
        return f"<{self.__class__.__name__} '{self.name}' v{self.version} ({status})>"
