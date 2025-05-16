import uuid

from flask import Blueprint
from flask import jsonify
from flask import render_template_string
from flask import request

from app.database import db
from app.models import Contact
from app.models import db

main = Blueprint("main", __name__)


@main.route("/")
def home():
    html_content = """
    <h1>Welcome to the JobNimbus Contacts API!</h1>
    <ul>
        <li>GET / - Home</li>
        <li>GET /contacts - Get All Contacts</li>
        <li>POST /contacts - Create Contact</li>
        <li>GET /contacts/&lt;jnid&gt; - Get Contact by ID</li>
        <li>PUT /contacts/&lt;jnid&gt; - Update Contact</li>
        <li>DELETE /contacts/&lt;jnid&gt; - Delete Contact</li>
    </ul>
    """
    return render_template_string(html_content)


# Create a new contact
@main.route("/contacts", methods=["POST"])
def create_contact():
    data = request.get_json()

    # Validation: At least one among the required fields
    required_fields = ["first_name", "last_name", "display_name", "company"]
    if not any(data.get(field) for field in required_fields):
        return (
            jsonify(
                {
                    "error": "At least one of 'first_name', 'last_name', 'display_name', or 'company' is required."
                }
            ),
            400,
        )

    # Ensure 'record_type_name' and 'status_name' are present
    if not data.get("record_type_name"):
        return jsonify({"error": "'record_type_name' is required."}), 400

    if not data.get("status_name"):
        return jsonify({"error": "'status_name' is required."}), 400

    # Validate 'record_type_name' and 'status_name' values
    valid_record_types = ["Lead", "Subcontractor"]
    valid_statuses = ["New", "Active", "Inactive"]

    record_type_name = data.get("record_type_name")
    status_name = data.get("status_name")

    if record_type_name not in valid_record_types:
        return (
            jsonify(
                {
                    "error": f"Invalid 'record_type_name'. Must be one of: {', '.join(valid_record_types)}"
                }
            ),
            400,
        )

    if status_name not in valid_statuses:
        return (
            jsonify(
                {"error": f"Invalid 'status_name'. Must be one of: {', '.join(valid_statuses)}"}
            ),
            400,
        )

    # Validate 'source_name' if it is provided (optional)
    allowed_sources = [
        "Web Search",
        "Referral",
        "Yard Sign",
        "Canvassing",
        "Trade Show",
        "Vehicle Wrap",
        "Self Generated",
        "Angi",
        "Facebook",
        "HomeAdvisor",
        "Yelp",
    ]
    source_name = data.get("source_name")
    if source_name and source_name not in allowed_sources:
        return (
            jsonify(
                {"error": f"Invalid 'source_name'. Must be one of: {', '.join(allowed_sources)}"}
            ),
            400,
        )

    # When creating a new Contact:
    max_recid = db.session.query(db.func.max(Contact.recid)).scalar()
    new_recid = (max_recid or 0) + 1

    # Create a new contact with the provided data, using default None for missing fields
    new_contact = Contact(
        jnid=str(uuid.uuid4()).replace("-", "")[:12],  # Generate a 12-character unique ID
        recid=new_recid,
        first_name=data.get("first_name", None),
        last_name=data.get("last_name", None),
        display_name=data.get("display_name", None),
        company=data.get("company", None),
        record_type=data.get("record_type", None),
        record_type_name=record_type_name,  # Mandatory field
        status=data.get("status", None),
        status_name=status_name,  # Mandatory field
        source_name=source_name if source_name else None,  # Optional field, omitted if not provided
        customer=data.get("customer", None),
        type=data.get("type", None),
        external_id=data.get("external_id", None),
        class_id=data.get("class_id", None),
        class_name=data.get("class_name", None),
        number=data.get("number", None),
        created_by=data.get("created_by", None),
        created_by_name=data.get("created_by_name", None),
        date_created=data.get("date_created", None),
        date_updated=data.get("date_updated", None),
        location=data.get("location", None),
        is_active=data.get("is_active", None),
        rules=data.get("rules", None),
        is_archived=data.get("is_archived", None),
        owners=data.get("owners", None),
        subcontractors=data.get("subcontractors", None),
        color=data.get("color", None),
        date_start=data.get("date_start", None),
        date_end=data.get("date_end", None),
        tags=data.get("tags", None),
        related=data.get("related", None),
        sales_rep=data.get("sales_rep", None),
        sales_rep_name=data.get("sales_rep_name", None),
        date_status_change=data.get("date_status_change", None),
        description=data.get("description", None),
        address_line1=data.get("address_line1", None),
        address_line2=data.get("address_line2", None),
        city=data.get("city", None),
        state_text=data.get("state_text", None),
        zip=data.get("zip", None),
        country_name=data.get("country_name", None),
        source=data.get("source", None),
        geo=data.get("geo", None),
        image_id=data.get("image_id", None),
        estimated_time=data.get("estimated_time", None),
        actual_time=data.get("actual_time", None),
        task_count=data.get("task_count", None),
        last_estimate=data.get("last_estimate", None),
        last_invoice=data.get("last_invoice", None),
        last_budget_gross_margin=data.get("last_budget_gross_margin", None),
        last_budget_gross_profit=data.get("last_budget_gross_profit", None),
        last_budget_revenue=data.get("last_budget_revenue", None),
        is_lead=data.get("is_lead", None),
        is_closed=data.get("is_closed", None),
        is_sub_contractor=data.get("is_sub_contractor", None),
        email=data.get("email", None),
        home_phone=data.get("home_phone", None),
        mobile_phone=data.get("mobile_phone", None),
        work_phone=data.get("work_phone", None),
        fax_number=data.get("fax_number", None),
        website=data.get("website", None),
    )

    try:
        # Attempt to add the new contact to the database
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "Contact created successfully", "jnid": new_contact.jnid}), 201
    except Exception as e:
        db.session.rollback()  # Ensure rollback in case of error
        return jsonify({"error": str(e)}), 500


# Get all contacts
@main.route("/contacts", methods=["GET"])
def get_all_contacts():
    try:
        contacts = Contact.query.all()
        contact_list = [contact.to_dict() for contact in contacts]
        return jsonify(contact_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get a single contact by jnid
@main.route("/contacts/<string:jnid>", methods=["GET"])
def get_contact(jnid):
    # contact = Contact.query.get(jnid)
    contact = db.session.get(Contact, jnid)
    if contact:
        return jsonify(contact.to_dict()), 200
    return jsonify({"error": "Contact not found"}), 404


# Update contact by jnid
@main.route("/contacts/<string:jnid>", methods=["PUT"])
def update_contact(jnid):
    # contact = Contact.query.get(jnid)
    contact = db.session.get(Contact, jnid)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404

    data = request.get_json()
    try:
        for key, value in data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        db.session.commit()
        return jsonify({"message": "Contact updated", "jnid": contact.jnid})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# Delete contact by jnid
@main.route("/contacts/<string:jnid>", methods=["DELETE"])
def delete_contact(jnid):
    # contact = Contact.query.get(jnid)
    contact = db.session.get(Contact, jnid)
    if not contact:
        return jsonify({"error": "Contact not found"}), 404
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "Contact deleted", "jnid": jnid})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
