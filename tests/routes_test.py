import json
import pytest
from app import create_app, db
from app.models import Contact

@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:Vissu@localhost:5432/contacts_test_db",  # your test DB URI
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_home_route(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"JobNimbus Contacts API" in response.data

def test_create_contact_valid(test_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "record_type_name": "Lead",
        "status_name": "New"
    }
    response = test_client.post('/contacts', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 201
    resp_json = response.get_json()
    assert "jnid" in resp_json
    assert resp_json["message"] == "Contact created successfully"

def test_create_contact_missing_required_fields(test_client):
    # No first_name, last_name, display_name, or company
    data = {
        "record_type_name": "Lead",
        "status_name": "New"
    }
    response = test_client.post('/contacts', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_get_all_contacts(test_client):
    response = test_client.get('/contacts')
    assert response.status_code == 200
    contacts = response.get_json()
    assert isinstance(contacts, list)

def test_get_contact_by_jnid(test_client):
    # First create a contact to retrieve
    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "record_type_name": "Lead",
        "status_name": "Active"
    }
    post_resp = test_client.post('/contacts', data=json.dumps(data), content_type='application/json')
    jnid = post_resp.get_json()["jnid"]

    get_resp = test_client.get(f'/contacts/{jnid}')
    assert get_resp.status_code == 200
    contact = get_resp.get_json()
    assert contact["jnid"] == jnid
    assert contact["first_name"] == "Jane"

def test_update_contact(test_client):
    data = {
        "first_name": "Will",
        "last_name": "Turner",
        "record_type_name": "Lead",
        "status_name": "New"
    }
    post_resp = test_client.post('/contacts', data=json.dumps(data), content_type='application/json')
    jnid = post_resp.get_json()["jnid"]

    update_data = {"status_name": "Active"}
    put_resp = test_client.put(f'/contacts/{jnid}', data=json.dumps(update_data), content_type='application/json')
    assert put_resp.status_code == 200
    resp_json = put_resp.get_json()
    assert resp_json["message"] == "Contact updated"

    # Confirm update
    get_resp = test_client.get(f'/contacts/{jnid}')
    assert get_resp.status_code == 200
    contact = get_resp.get_json()
    assert contact["status_name"] == "Active"

def test_delete_contact(test_client):
    data = {
        "first_name": "Mark",
        "last_name": "Twain",
        "record_type_name": "Lead",
        "status_name": "New"
    }
    post_resp = test_client.post('/contacts', data=json.dumps(data), content_type='application/json')
    jnid = post_resp.get_json()["jnid"]

    del_resp = test_client.delete(f'/contacts/{jnid}')
    assert del_resp.status_code == 200
    assert del_resp.get_json()["message"] == "Contact deleted"

    # Confirm deletion
    get_resp = test_client.get(f'/contacts/{jnid}')
    assert get_resp.status_code == 404

def test_update_non_existent_contact(client):
    response = client.put("/contacts/999999", json={
        "first_name": "UpdatedName"
    })
    assert response.status_code == 404
    assert response.json["error"] == "Contact not found"

def test_update_with_invalid_field(client):
    # First create a contact
    contact_data = {
        "first_name": "Amy",
        "last_name": "Brown",
        "display_name": "AB",
        "company_name": "AeroWorks",
        "record_type_name": "Lead",
        "status_name": "Active",
        "source_name": "Trade Show"
    }
    create_resp = client.post("/contacts", json=contact_data)
    
    # Assert creation success
    assert create_resp.status_code == 201, f"Contact creation failed: {create_resp.status_code}, {create_resp.json}"
    assert "jnid" in create_resp.json, f"Expected 'jnid' in response, got: {create_resp.json}"
    
    jnid = create_resp.json["jnid"]

    # Try to update with an invalid field
    update_resp = client.put(f"/contacts/{jnid}", json={"non_existing_field": "value"})
    
    # Allow either 400 (validation failed) or 200 (ignored invalid field) depending on app behavior
    assert update_resp.status_code in [200, 400], f"Unexpected update status: {update_resp.status_code}, {update_resp.json}"

    # Optional: Add deeper check
    if update_resp.status_code == 200:
        assert update_resp.json.get("message") == "Contact updated"
    else:
        assert "error" in update_resp.json

def test_delete_and_fetch(client):
    # Create
    contact_data = {
        "first_name": "Bob",
        "last_name": "Testman",
        "display_name": "BT",
        "company_name": "TestCo",
        "record_type_name": "Lead",
        "status_name": "Active",
        "source_name": "Facebook"
    }

    create_resp = client.post("/contacts", json=contact_data)
    assert create_resp.status_code == 201, f"Contact creation failed: {create_resp.status_code}, {create_resp.json}"
    jnid = create_resp.json["jnid"]

    # Delete
    delete_resp = client.delete(f"/contacts/{jnid}")
    assert delete_resp.status_code == 200
    assert delete_resp.json["message"] == "Contact deleted"

    # Try fetching deleted contact (if route exists)
    get_resp = client.get(f"/contacts/{jnid}")
    assert get_resp.status_code == 404 or get_resp.status_code == 400

def test_create_with_empty_json(client):
    response = client.post("/contacts", json={})
    assert response.status_code == 400
    assert "error" in response.json

def test_contact_lifecycle(client):
    contact_data = {
        "first_name": "Rick",
        "last_name": "Jones",
        "display_name": "RJ",
        "company_name": "LabTech",
        "record_type_name": "Subcontractor",
        "status_name": "Active",
        "source_name": "Yard Sign"
    }
    # Create
    create_resp = client.post("/contacts", json=contact_data)
    jnid = create_resp.json["jnid"]
    assert create_resp.status_code == 201, f"Contact creation failed: {create_resp.status_code}, {create_resp.json}"

    # Update
    update_resp = client.put(f"/contacts/{jnid}", json={"first_name": "Richard"})
    assert update_resp.status_code == 200

    # Delete
    delete_resp = client.delete(f"/contacts/{jnid}")
    assert delete_resp.status_code == 200

def test_update_multiple_fields(client):
    contact_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "display_name": "JD",
        "company_name": "XCorp",
        "record_type_name": "Subcontractor",
        "status_name": "Inactive",
        "source_name": "Trade Show"
    }
    create_resp = client.post("/contacts", json=contact_data)
    jnid = create_resp.json["jnid"]

    update_data = {
        "first_name": "Janet",
        "last_name": "Dane"
    }

    update_resp = client.put(f"/contacts/{jnid}", json=update_data)
    assert update_resp.status_code == 200
    assert update_resp.json["message"] == "Contact updated"
