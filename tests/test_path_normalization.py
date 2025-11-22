import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import normalize_path
from dispatcher import dispatch

# Mock function for testing dispatch
def mock_function(path):
    return f"Path received: {path}"

class TestPathNormalization(unittest.TestCase):
    def test_normalize_path(self):
        # Test cases
        self.assertEqual(normalize_path(".//data//file.txt"), "data/file.txt")
        self.assertEqual(normalize_path("./folder/"), "folder/")
        self.assertEqual(normalize_path("dir\\file"), "dir/file")
        self.assertEqual(normalize_path("path//to//file"), "path/to/file")
        self.assertEqual(normalize_path("  spaces/file  "), "spaces/file")

    def test_dispatch_normalization(self):
        # Mock registry to return our mock function
        import registry
        original_get = registry.get_function
        
        registry._function_registry["test_func"] = {
            "function": mock_function,
            "argument_types": {"path": "str"},
            "description": "Test function"
        }
        
        # Test dispatch with dirty path
        result = dispatch("test_func", {"path": ".//dirty//path"})
        self.assertIn("Path received: dirty/path", result)
        
        # Restore registry
        if "test_func" in registry._function_registry:
            del registry._function_registry["test_func"]

if __name__ == '__main__':
    unittest.main()
