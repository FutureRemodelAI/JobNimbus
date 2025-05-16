import pytest
from app import create_app, db
from app.models import Contact

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:Vissu@localhost:5432/contacts_test_db",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()

def test_jnid_auto_generation(session):
    contact = Contact(
        first_name="Test",
        last_name="User",
        record_type_name="Lead",
        status_name="Active"
    )
    session.add(contact)
    session.commit()

    assert contact.jnid is not None
    assert len(contact.jnid) == 12

def test_insert_and_query_contact(session):
    contact = Contact(
        first_name="Alice",
        last_name="Smith",
        record_type_name="Subcontractor",
        status_name="Inactive"
    )
    session.add(contact)
    session.commit()

    queried = session.query(Contact).filter_by(first_name="Alice").first()
    assert queried is not None
    assert queried.last_name == "Smith"
