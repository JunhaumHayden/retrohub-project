# tests/db_test.py
import unittest
import os
from datetime import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your database manager
from app.database.factories.database_manager import DatabaseManager
from app.database.database_config import Base


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        db_url = os.getenv('PG_DATABASE_URL_TEST')
        DatabaseManager.init_db(db_type='postgresql_test')
        cls.session = DatabaseManager.get_session()

    @classmethod
    def tearDownClass(cls):
        """Tear down test database connection."""
        cls.session.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)