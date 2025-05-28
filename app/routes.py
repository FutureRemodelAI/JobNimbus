from flask import Blueprint
from flask import jsonify
from flask import render_template_string
from flask import request

from app.config import CONTACTS_ENDPOINT
from app.database import db
from app.models import Contact
from app.utils import jobnimbus_request

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template_string(
        """
    <h1>Welcome to the JobNimbus Contacts API!</h1>
    <ul>
        <li>GET /contacts - Get All Contacts</li>
        <li>POST /contacts - Create Contact</li>
        <li>GET /contacts/&lt;jnid&gt; - Get Contact by ID</li>
        <li>PUT /contacts/&lt;jnid&gt; - Update Contact</li>
        <li>DELETE /contacts/&lt;jnid&gt; - Delete Contact (Soft)</li>
    </ul>
    """
    )


@main.route("/contacts", methods=["GET"])
def get_all_contacts():
    data, status = jobnimbus_request("GET", CONTACTS_ENDPOINT)
    return jsonify(data), status


@main.route("/contacts", methods=["POST"])
def create_contact():
    contact_data = request.get_json()
    if not contact_data:
        return jsonify({"error": "Missing JSON body"}), 400

    data, status = jobnimbus_request("POST", CONTACTS_ENDPOINT, json=contact_data)

    if status == 200:
        contact = Contact(
            jnid=data.get("jnid"),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            display_name=data.get("display_name", ""),
            company=data.get("company", ""),
            status=data.get("status"),
            status_name=data.get("status_name"),
            record_type=data.get("record_type"),
            record_type_name=data.get("record_type_name"),
            address_line1=data.get("address_line1", ""),
            address_line2=data.get("address_line2", ""),
            city=data.get("city", ""),
            state_text=data.get("state_text", ""),
            zip=data.get("zip", ""),
            country_name=data.get("country_name", ""),
            created_by_name=data.get("created_by_name", ""),
            email=data.get("email", ""),
            home_phone=data.get("home_phone", ""),
            mobile_phone=data.get("mobile_phone", ""),
            work_phone=data.get("work_phone", ""),
            fax_number=data.get("fax_number", ""),
            website=data.get("website", ""),
        )
        db.session.add(contact)
        db.session.commit()

    return jsonify(data), status


@main.route("/contacts/<string:jnid>", methods=["GET"])
def get_contact(jnid):
    contact = db.session.get(Contact, jnid)
    # return jsonify(contact.to_dict()), 200 if contact else ({"error": "Contact not found"}, 404)
    if contact:
        return jsonify(contact.to_dict()), 200
    else:
        return jsonify({"error": "Contact not found"}), 404


@main.route("/contacts/<string:jnid>", methods=["PUT"])
def update_contact(jnid):
    data = request.get_json()
    contact = db.session.get(Contact, jnid)

    if not contact:
        return jsonify({"error": "Contact not found"}), 404

    for key, value in data.items():
        if hasattr(contact, key):
            setattr(contact, key, value)
    db.session.commit()

    jn_data, jn_status = jobnimbus_request("PUT", f"{CONTACTS_ENDPOINT}/{jnid}", json=data)
    return jsonify(jn_data), jn_status


@main.route("/contacts/<string:jnid>", methods=["DELETE"])
def delete_contact(jnid):
    contact = db.session.get(Contact, jnid)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    is_active = data.get("is_active")
    is_archived = data.get("is_archived", not is_active)

    contact.is_active = is_active
    contact.is_archived = is_archived
    db.session.commit()

    jn_data, jn_status = jobnimbus_request(
        "PUT",
        f"{CONTACTS_ENDPOINT}/{jnid}",
        json={"is_active": is_active, "is_archived": is_archived},
    )

    return jsonify(jn_data), jn_status
