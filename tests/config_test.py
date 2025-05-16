import unittest
from app.config import Config

class ConfigTest(unittest.TestCase):
    
    def test_config_has_database_url(self):
        self.assertTrue(hasattr(Config, 'SQLALCHEMY_DATABASE_URI'))

    def test_debug_default_false(self):
        self.assertFalse(getattr(Config, 'DEBUG', True))  
