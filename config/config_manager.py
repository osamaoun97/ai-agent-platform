"""
config/config_manager.py

A simple configuration manager that reads key-value pairs from a .env file.

The ConfigManager class provides an interface to access configuration values stored
in a .env file using either method-style (get()) or dictionary-style access.

Example:
    config = ConfigManager()
    db_host = config.get('DB_HOST', 'localhost')  # with default value
    api_key = config['API_KEY']  # raises KeyError if not found

File Format:
    The .env file should contain key-value pairs in the format:
    KEY=value

    Lines starting with # are treated as comments
    Empty lines are ignored
    Values can contain = characters

Classes:
    ConfigManager: Manages configuration values from a .env file
"""

import os


class ConfigManager:
    """
    Manages configuration values loaded from a .env file.

    The configuration file is expected to be at 'config/.env'
    and contain key=value pairs.

    Attributes:
        filepath (str): Path to the configuration file
        config (dict): Dictionary storing the configuration key-value pairs

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
    """

    def __init__(self, filepath=None):
        self.filepath = filepath or "config/.env"
        self.config = {}
        self._load()

    def _load(self):
        """
        Load key=value pairs from the file into a dictionary.

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Config file '{self.filepath}' not found.")

        with open(self.filepath, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                self.config[key.strip()] = value.strip()

    def get(self, key, default=None):
        """
        Get a configuration value with an optional default.

        Args:
            key (str): The configuration key to lookup
            default: Value to return if key is not found

        Returns:
            The value associated with the key, or the default if not found
        """
        return self.config.get(key, default)

    def __getitem__(self, key):
        """
        Allow dictionary-style access to configuration values.

        Args:
            key (str): The configuration key to lookup

        Returns:
            The value associated with the key

        Raises:
            KeyError: If the key is not found
        """
        return self.config[key]

    def __contains__(self, key):
        """
        Check if a configuration key exists.

        Args:
            key (str): The configuration key to check

        Returns:
            bool: True if the key exists, False otherwise
        """
        return key in self.config
