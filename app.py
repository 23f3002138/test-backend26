import csv
import io
import os
from datetime import timezone, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from models import db, Event, Participant, SiteConfig

ADMIN_PASSKEY = "connaissance2026"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "connaissance.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()


# ── Event Routes ────────────────────────────────────────────────────────────


@app.route("/api/events", methods=["GET"])
def get_events():
    events = Event.query.order_by(Event.date).all()
    return jsonify([e.to_dict() for e in events])


@app.route("/api/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict())


@app.route("/api/events", methods=["POST"])
def create_event():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Event name is required"}), 400

    event = Event(
        name=data["name"],
        description=data.get("description", ""),
        date=data.get("date", "TBD"),
        rules=data.get("rules", ""),
        eligibility=data.get("eligibility", "Open to all"),
        image_url=data.get("image_url", ""),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json()

    event.name = data.get("name", event.name)
    event.description = data.get("description", event.description)
    event.date = data.get("date", event.date)
    event.rules = data.get("rules", event.rules)
    event.eligibility = data.get("eligibility", event.eligibility)
    event.image_url = data.get("image_url", event.image_url)

    db.session.commit()
    return jsonify(event.to_dict())


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    # Delete associated participants first
    Participant.query.filter_by(event_id=event_id).delete()
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted successfully"})


# ── Registration Routes ─────────────────────────────────────────────────────


@app.route("/api/register", methods=["POST"])
def register_participant():
    data = request.get_json()
    required = ["name", "email", "phone", "college", "event_id"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # Check event exists
    event = Event.query.get(data["event_id"])
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Check duplicate registration
    existing = Participant.query.filter_by(
        email=data["email"], event_id=data["event_id"]
    ).first()
    if existing:
        return jsonify({"error": "You have already registered for this event"}), 409

    participant = Participant(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        college=data["college"],
        event_id=data["event_id"],
    )
    db.session.add(participant)
    db.session.commit()
    return jsonify({"message": "Registration successful!", "participant": participant.to_dict()}), 201


# ── Admin: Participants ──────────────────────────────────────────────────────


@app.route("/api/participants", methods=["GET"])
def get_participants():
    event_id = request.args.get("event_id", type=int)
    query = Participant.query
    if event_id:
        query = query.filter_by(event_id=event_id)
    participants = query.order_by(Participant.registered_at.desc()).all()
    return jsonify([p.to_dict() for p in participants])


@app.route("/api/participants/download", methods=["GET"])
def download_participants():
    event_id = request.args.get("event_id", type=int)
    query = Participant.query
    if event_id:
        query = query.filter_by(event_id=event_id)
    participants = query.order_by(Participant.registered_at.desc()).all()

    IST = timezone(timedelta(hours=5, minutes=30))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "Phone", "College", "Event", "Registered At"])
    for p in participants:
        ist_time = p.registered_at.replace(tzinfo=timezone.utc).astimezone(IST)
        formatted_time = ist_time.strftime("%d/%m/%Y %I:%M:%S %p")
        writer.writerow([
            p.id, p.name, p.email, p.phone, p.college,
            p.event.name if p.event else "", formatted_time
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=participants.csv"},
    )


@app.route("/api/participants/<int:participant_id>", methods=["PUT"])
def update_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    data = request.get_json()

    participant.name = data.get("name", participant.name)
    participant.email = data.get("email", participant.email)
    participant.phone = data.get("phone", participant.phone)
    participant.college = data.get("college", participant.college)
    if data.get("event_id"):
        event = Event.query.get(data["event_id"])
        if event:
            participant.event_id = data["event_id"]

    db.session.commit()
    return jsonify(participant.to_dict())


@app.route("/api/participants/<int:participant_id>", methods=["DELETE"])
def delete_participant(participant_id):
    participant = Participant.query.get_or_404(participant_id)
    db.session.delete(participant)
    db.session.commit()
    return jsonify({"message": "Participant deleted successfully"})


# ── Stats ────────────────────────────────────────────────────────────────────


@app.route("/api/stats", methods=["GET"])
def get_stats():
    total_events = Event.query.count()
    total_participants = Participant.query.count()
    total_colleges = db.session.query(Participant.college).distinct().count()
    return jsonify({
        "total_events": total_events,
        "total_participants": total_participants,
        "total_colleges": total_colleges,
    })



# ── Admin Auth ───────────────────────────────────────────────────────────────


@app.route("/api/admin/verify", methods=["POST"])
def verify_admin():
    data = request.get_json()
    if data and data.get("passkey") == ADMIN_PASSKEY:
        return jsonify({"success": True, "message": "Access granted"})
    return jsonify({"success": False, "error": "Invalid passkey"}), 401

# ── Site Config ──────────────────────────────────────────────────────────────


DEFAULT_CONFIG = {
    "hero_video": "https://videos.pexels.com/video-files/3129671/3129671-hd_1920_1080_30fps.mp4",
    "about_bg": "https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?w=1400",
    "about_video": "",
    "events_bg": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1400",
    "events_video": "",
    "gallery_bg": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1400",
    "gallery_video": "",
    "contact_bg": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1400",
    "contact_video": "",
}


@app.route("/api/config", methods=["GET"])
def get_config():
    config = {}
    for key, default in DEFAULT_CONFIG.items():
        config[key] = SiteConfig.get(key, default)
    return jsonify(config)


@app.route("/api/config", methods=["PUT"])
def update_config():
    data = request.get_json()
    for key, value in data.items():
        if key in DEFAULT_CONFIG:
            SiteConfig.set(key, value)
    return jsonify({"message": "Settings updated"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
