import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:Vissu@localhost:5432/contacts"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False


# Local Development
class DevelopmentConfig(Config):
    DEBUG = True


# Deployment
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


JOBNIMBUS_API_KEY = os.getenv("JOBNIMBUS_API_KEY")
BASE_URL = "https://app.jobnimbus.com/api1"
CONTACTS_ENDPOINT = f"{BASE_URL}/contacts"
