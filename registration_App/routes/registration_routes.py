import re

from flask import Blueprint, current_app, jsonify, request

from config.database import db
from config.ses import send_notification
from models.registration import Registration

registration_bp = Blueprint("registrations", __name__, url_prefix="/api/registrations")

# Required fields and their maximum lengths (matching the database columns).
FIELD_LIMITS = {"name": 100, "place": 100, "phone": 20}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def error(message, status):
    return jsonify({"error": message}), status


def parse_id(raw_id):
    """Return a positive integer ID, or None if the value is not valid."""
    if raw_id.isdigit() and int(raw_id) > 0:
        return int(raw_id)
    return None


def validate_payload(data, require_email=True):
    """Return (cleaned_data, error_message). Only one of them is not None."""
    if not isinstance(data, dict):
        return None, "Request body must be valid JSON"

    cleaned = {}
    for field, max_length in FIELD_LIMITS.items():
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            return None, f"{field} is required"
        value = value.strip()
        if len(value) > max_length:
            return None, f"{field} must be at most {max_length} characters"
        cleaned[field] = value

    if require_email:
        email = data.get("email")
        if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
            return None, "email must be a valid email address"
        cleaned["email"] = email.strip()
    return cleaned, None


def notify_safely(email, subject, body):
    try:
        send_notification(email, subject, body)
    except Exception:
        current_app.logger.exception("SES notification failed")


@registration_bp.route("", methods=["POST"])
def create_registration():
    cleaned, problem = validate_payload(request.get_json(silent=True))
    if problem:
        return error(problem, 400)

    registration = Registration(
        **{field: cleaned[field] for field in FIELD_LIMITS}
    )
    db.session.add(registration)
    db.session.commit()
    notify_safely(
        cleaned["email"],
        "Registration created",
        f"Your registration was created successfully. Registration ID: {registration.id}.",
    )
    return jsonify(registration.to_dict()), 201


@registration_bp.route("", methods=["GET"])
def get_registrations():
    registrations = Registration.query.order_by(Registration.id).all()
    return jsonify([r.to_dict() for r in registrations]), 200


@registration_bp.route("/<id>", methods=["GET"])
def get_registration(id):
    registration_id = parse_id(id)
    if registration_id is None:
        return error("Invalid ID", 400)

    registration = db.session.get(Registration, registration_id)
    if registration is None:
        return error("Registration not found", 404)
    return jsonify(registration.to_dict()), 200


@registration_bp.route("/<id>", methods=["PUT"])
def update_registration(id):
    registration_id = parse_id(id)
    if registration_id is None:
        return error("Invalid ID", 400)

    cleaned, problem = validate_payload(
        request.get_json(silent=True), require_email=False
    )
    if problem:
        return error(problem, 400)

    registration = db.session.get(Registration, registration_id)
    if registration is None:
        return error("Registration not found", 404)

    registration.name = cleaned["name"]
    registration.place = cleaned["place"]
    registration.phone = cleaned["phone"]
    db.session.commit()
    return jsonify(registration.to_dict()), 200


@registration_bp.route("/<id>", methods=["DELETE"])
def delete_registration(id):
    registration_id = parse_id(id)
    if registration_id is None:
        return error("Invalid ID", 400)

    registration = db.session.get(Registration, registration_id)
    if registration is None:
        return error("Registration not found", 404)

    db.session.delete(registration)
    db.session.commit()
    return jsonify({"message": "Registration deleted"}), 200
