import unittest
import os
import tempfile


class TestConfigManager(unittest.TestCase):
    def setUp(self):
        """Create a temporary .env file for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.env_path = os.path.join(self.test_dir, "config")
        os.makedirs(self.env_path)

        self.env_file = os.path.join(self.env_path, ".env")
        with open(self.env_file, "w") as f:
            f.write("DB_HOST=localhost\n")
            f.write("DB_PORT=5432\n")
            f.write("# This is a comment\n")
            f.write("API_KEY=secret123\n")
            f.write("\n")
            f.write("COMPLEX_VALUE=with=equals=signs\n")

    def tearDown(self):
        """Clean up temporary files"""
        # Clean up files using try-except blocks for each operation
        try:
            if os.path.exists(self.env_file):
                os.remove(self.env_file)
        except (OSError, FileNotFoundError):
            pass

        try:
            if os.path.exists(self.env_path):
                os.rmdir(self.env_path)
        except (OSError, FileNotFoundError):
            pass

        try:
            if os.path.exists(self.test_dir):
                os.rmdir(self.test_dir)
        except (OSError, FileNotFoundError):
            pass

    def test_load_config(self):
        """Test if configuration is loaded correctly"""
        from config.config_manager import ConfigManager

        config = config = ConfigManager(self.env_file)
        self.assertEqual(config.get("DB_HOST"), "localhost")
        self.assertEqual(config.get("DB_PORT"), "5432")
        self.assertEqual(config.get("API_KEY"), "secret123")
        self.assertEqual(config.get("COMPLEX_VALUE"), "with=equals=signs")

    def test_get_with_default(self):
        """Test get() method with default values"""
        from config.config_manager import ConfigManager

        config = config = ConfigManager(self.env_file)
        self.assertEqual(config.get("MISSING_KEY", "default"), "default")
        self.assertIsNone(config.get("MISSING_KEY"))

    def test_dictionary_access(self):
        """Test dictionary-style access"""
        from config.config_manager import ConfigManager

        config = config = ConfigManager(self.env_file)
        self.assertEqual(config["DB_HOST"], "localhost")
        with self.assertRaises(KeyError):
            _ = config["MISSING_KEY"]

    def test_contains(self):
        """Test key existence check"""
        from config.config_manager import ConfigManager

        config = config = ConfigManager(self.env_file)
        self.assertTrue("DB_HOST" in config)
        self.assertFalse("MISSING_KEY" in config)

    def test_missing_file(self):
        """Test behavior when .env file is missing"""
        from config.config_manager import ConfigManager

        os.remove(self.env_file)
        with self.assertRaises(FileNotFoundError):
            config = ConfigManager(self.env_file)

    def test_empty_file(self):
        """Test with empty .env file"""
        with open(self.env_file, "w") as f:
            f.write("")

        from config.config_manager import ConfigManager
        config = config = ConfigManager(self.env_file)
        self.assertEqual(len(config.config), 0)
