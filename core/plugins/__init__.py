"""
ORION Plugin System

Provides extensibility through a modular plugin architecture.
Plugins can register new functions, add capabilities, and extend ORION's functionality.
"""

from core.plugins.plugin_base import PluginBase
from core.plugins.plugin_manager import PluginManager

__all__ = ['PluginBase', 'PluginManager']
