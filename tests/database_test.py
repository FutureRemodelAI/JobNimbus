import unittest
from flask import Flask
from app.database import db
from app.config import TestingConfig
from app.models import Contact  # Adjust import based on your model location

class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        # Create Flask app with testing config
        self.app = Flask(__name__)
        self.app.config.from_object(TestingConfig)

        # Initialize SQLAlchemy with the app
        db.init_app(self.app)

        # Create app context and push it for using DB
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all tables fresh before each test
        db.create_all()

    def tearDown(self):
        # Drop all tables after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_contact(self):
        # Create a new Contact instance
        contact = Contact(
            first_name="John",
            last_name="Doe",
            display_name="John Doe",
            company="Example Inc",
            record_type_name="Subcontractor",
            status_name="Active",
            source_name="Refferal"
        )
        db.session.add(contact)
        db.session.commit()

        # Query the contact back
        result = Contact.query.filter_by(first_name="John").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.last_name, "Doe")
        self.assertEqual(result.company, "Example Inc")

if __name__ == "__main__":
    unittest.main()
