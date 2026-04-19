"""
ACEest Fitness & Gym Management System
Version: 1.0.0
Author: DevOps Assignment 2
"""

from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)
APP_VERSION = "1.0.0"

# ---------- In-Memory Data Store ----------
members = {}
trainers = {}
classes = {}
memberships = {}

member_id_counter = 1
trainer_id_counter = 1
class_id_counter = 1

# ---------- Health & Info ----------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "app": "ACEest Fitness & Gym Management System",
        "version": APP_VERSION,
        "status": "running",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "version": APP_VERSION}), 200

# ---------- Member Management ----------

@app.route("/members", methods=["GET"])
def get_members():
    return jsonify({"members": list(members.values()), "total": len(members)}), 200

@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = members.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member), 200

@app.route("/members", methods=["POST"])
def add_member():
    global member_id_counter
    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Name and email are required"}), 400

    # Check duplicate email
    for m in members.values():
        if m["email"] == data["email"]:
            return jsonify({"error": "Email already registered"}), 409

    member = {
        "id": member_id_counter,
        "name": data["name"],
        "email": data["email"],
        "phone": data.get("phone", ""),
        "membership_type": data.get("membership_type", "basic"),
        "joined_on": datetime.date.today().isoformat(),
        "active": True
    }
    members[member_id_counter] = member
    member_id_counter += 1
    return jsonify(member), 201

@app.route("/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = members.get(member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    data = request.get_json()
    member.update({k: v for k, v in data.items() if k in ["name", "phone", "membership_type", "active"]})
    return jsonify(member), 200

@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    if member_id not in members:
        return jsonify({"error": "Member not found"}), 404
    del members[member_id]
    return jsonify({"message": f"Member {member_id} deleted"}), 200

# ---------- Trainer Management ----------

@app.route("/trainers", methods=["GET"])
def get_trainers():
    return jsonify({"trainers": list(trainers.values()), "total": len(trainers)}), 200

@app.route("/trainers", methods=["POST"])
def add_trainer():
    global trainer_id_counter
    data = request.get_json()
    if not data or "name" not in data or "specialization" not in data:
        return jsonify({"error": "Name and specialization are required"}), 400

    trainer = {
        "id": trainer_id_counter,
        "name": data["name"],
        "specialization": data["specialization"],
        "experience_years": data.get("experience_years", 0),
        "available": data.get("available", True)
    }
    trainers[trainer_id_counter] = trainer
    trainer_id_counter += 1
    return jsonify(trainer), 201

# ---------- Class Schedule Management ----------

@app.route("/classes", methods=["GET"])
def get_classes():
    return jsonify({"classes": list(classes.values()), "total": len(classes)}), 200

@app.route("/classes", methods=["POST"])
def add_class():
    global class_id_counter
    data = request.get_json()
    if not data or "name" not in data or "trainer_id" not in data:
        return jsonify({"error": "Class name and trainer_id are required"}), 400

    if data["trainer_id"] not in trainers:
        return jsonify({"error": "Trainer not found"}), 404

    gym_class = {
        "id": class_id_counter,
        "name": data["name"],
        "trainer_id": data["trainer_id"],
        "schedule": data.get("schedule", "TBD"),
        "capacity": data.get("capacity", 20),
        "enrolled": 0
    }
    classes[class_id_counter] = gym_class
    class_id_counter += 1
    return jsonify(gym_class), 201

@app.route("/classes/<int:class_id>/enroll", methods=["POST"])
def enroll_member(class_id):
    gym_class = classes.get(class_id)
    if not gym_class:
        return jsonify({"error": "Class not found"}), 404
    if gym_class["enrolled"] >= gym_class["capacity"]:
        return jsonify({"error": "Class is full"}), 400
    gym_class["enrolled"] += 1
    return jsonify({"message": "Enrolled successfully", "class": gym_class}), 200

# ---------- Membership Plans ----------

MEMBERSHIP_PLANS = {
    "basic":    {"name": "Basic",    "price": 999,  "duration_days": 30,  "features": ["gym_access"]},
    "standard": {"name": "Standard", "price": 1999, "duration_days": 30,  "features": ["gym_access", "group_classes"]},
    "premium":  {"name": "Premium",  "price": 3999, "duration_days": 30,  "features": ["gym_access", "group_classes", "personal_trainer", "spa"]},
}

@app.route("/plans", methods=["GET"])
def get_plans():
    return jsonify({"plans": MEMBERSHIP_PLANS}), 200

@app.route("/plans/<plan_name>", methods=["GET"])
def get_plan(plan_name):
    plan = MEMBERSHIP_PLANS.get(plan_name.lower())
    if not plan:
        return jsonify({"error": "Plan not found"}), 404
    return jsonify(plan), 200

# ---------- BMI Calculator ----------

@app.route("/bmi", methods=["POST"])
def calculate_bmi():
    data = request.get_json()
    if not data or "weight_kg" not in data or "height_cm" not in data:
        return jsonify({"error": "weight_kg and height_cm are required"}), 400
    weight = float(data["weight_kg"])
    height_m = float(data["height_cm"]) / 100
    if height_m <= 0 or weight <= 0:
        return jsonify({"error": "Weight and height must be positive"}), 400
    bmi = round(weight / (height_m ** 2), 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return jsonify({"bmi": bmi, "category": category}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
