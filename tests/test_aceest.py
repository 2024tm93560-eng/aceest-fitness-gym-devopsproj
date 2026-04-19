"""
ACEest Fitness & Gym - Pytest Test Suite
Tests for: Members, Trainers, Classes, BMI, Plans, Attendance, Diet Plans
"""

import pytest
import json
import sys
import os

# Support both v1 and v2 test runs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Create a test client for v1 app."""
    import ACEest_Fitness as fitness_app
    # Reset global state before each test
    fitness_app.members.clear()
    fitness_app.trainers.clear()
    fitness_app.classes.clear()
    fitness_app.member_id_counter = 1
    fitness_app.trainer_id_counter = 1
    fitness_app.class_id_counter = 1
    fitness_app.app.config["TESTING"] = True
    with fitness_app.app.test_client() as c:
        yield c


@pytest.fixture
def client_v2():
    """Create a test client for v2 app."""
    import ACEest_Fitness_v2 as fitness_app_v2
    fitness_app_v2.members.clear()
    fitness_app_v2.trainers.clear()
    fitness_app_v2.classes.clear()
    fitness_app_v2.attendance.clear()
    fitness_app_v2.member_id_counter = 1
    fitness_app_v2.trainer_id_counter = 1
    fitness_app_v2.class_id_counter = 1
    fitness_app_v2.app.config["TESTING"] = True
    with fitness_app_v2.app.test_client() as c:
        yield c


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Health & Home Endpoint Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_home_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_home_contains_version(self, client):
        res = client.get("/")
        data = json.loads(res.data)
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_home_contains_app_name(self, client):
        res = client.get("/")
        data = json.loads(res.data)
        assert "ACEest" in data["app"]

    def test_health_check_returns_healthy(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data["status"] == "healthy"

    def test_v2_home_has_new_features(self, client_v2):
        res = client_v2.get("/")
        data = json.loads(res.data)
        assert "new_features" in data
        assert "attendance_tracking" in data["new_features"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Member Management Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMemberManagement:
    def test_get_members_empty(self, client):
        res = client.get("/members")
        assert res.status_code == 200
        assert json.loads(res.data)["total"] == 0

    def test_add_member_success(self, client):
        res = post_json(client, "/members", {"name": "Ravi Kumar", "email": "ravi@aceest.com"})
        assert res.status_code == 201
        data = json.loads(res.data)
        assert data["name"] == "Ravi Kumar"
        assert data["id"] == 1

    def test_add_member_default_membership(self, client):
        res = post_json(client, "/members", {"name": "Priya Singh", "email": "priya@aceest.com"})
        data = json.loads(res.data)
        assert data["membership_type"] == "basic"

    def test_add_member_missing_name(self, client):
        res = post_json(client, "/members", {"email": "x@aceest.com"})
        assert res.status_code == 400

    def test_add_member_missing_email(self, client):
        res = post_json(client, "/members", {"name": "X"})
        assert res.status_code == 400

    def test_add_member_duplicate_email(self, client):
        post_json(client, "/members", {"name": "A", "email": "dup@aceest.com"})
        res = post_json(client, "/members", {"name": "B", "email": "dup@aceest.com"})
        assert res.status_code == 409

    def test_get_member_by_id(self, client):
        post_json(client, "/members", {"name": "Amit", "email": "amit@aceest.com"})
        res = client.get("/members/1")
        assert res.status_code == 200
        assert json.loads(res.data)["email"] == "amit@aceest.com"

    def test_get_member_not_found(self, client):
        res = client.get("/members/999")
        assert res.status_code == 404

    def test_update_member(self, client):
        post_json(client, "/members", {"name": "Old Name", "email": "upd@aceest.com"})
        res = client.put("/members/1",
                         data=json.dumps({"name": "New Name"}),
                         content_type="application/json")
        assert res.status_code == 200
        assert json.loads(res.data)["name"] == "New Name"

    def test_delete_member(self, client):
        post_json(client, "/members", {"name": "Del", "email": "del@aceest.com"})
        res = client.delete("/members/1")
        assert res.status_code == 200
        assert client.get("/members/1").status_code == 404

    def test_delete_nonexistent_member(self, client):
        res = client.delete("/members/999")
        assert res.status_code == 404

    def test_multiple_members_incrementing_ids(self, client):
        post_json(client, "/members", {"name": "M1", "email": "m1@x.com"})
        post_json(client, "/members", {"name": "M2", "email": "m2@x.com"})
        res = client.get("/members")
        assert json.loads(res.data)["total"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# 3. Trainer Management Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestTrainerManagement:
    def test_get_trainers_empty(self, client):
        res = client.get("/trainers")
        assert res.status_code == 200
        assert json.loads(res.data)["total"] == 0

    def test_add_trainer_success(self, client):
        res = post_json(client, "/trainers", {"name": "Coach Arjun", "specialization": "Strength"})
        assert res.status_code == 201
        assert json.loads(res.data)["specialization"] == "Strength"

    def test_add_trainer_missing_fields(self, client):
        res = post_json(client, "/trainers", {"name": "Coach"})
        assert res.status_code == 400

    def test_trainer_default_availability(self, client):
        res = post_json(client, "/trainers", {"name": "T", "specialization": "Yoga"})
        assert json.loads(res.data)["available"] is True


# ─────────────────────────────────────────────────────────────────────────────
# 4. Class Scheduling Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestClassScheduling:
    def _add_trainer(self, client):
        return post_json(client, "/trainers", {"name": "Coach X", "specialization": "HIIT"})

    def test_get_classes_empty(self, client):
        res = client.get("/classes")
        assert res.status_code == 200
        assert json.loads(res.data)["total"] == 0

    def test_add_class_success(self, client):
        self._add_trainer(client)
        res = post_json(client, "/classes", {"name": "HIIT Blast", "trainer_id": 1})
        assert res.status_code == 201
        assert json.loads(res.data)["name"] == "HIIT Blast"

    def test_add_class_invalid_trainer(self, client):
        res = post_json(client, "/classes", {"name": "Yoga", "trainer_id": 99})
        assert res.status_code == 404

    def test_enroll_in_class(self, client):
        self._add_trainer(client)
        post_json(client, "/classes", {"name": "Spin", "trainer_id": 1, "capacity": 2})
        res = post_json(client, "/classes/1/enroll", {})
        assert res.status_code == 200
        assert json.loads(res.data)["class"]["enrolled"] == 1

    def test_enroll_class_full(self, client):
        self._add_trainer(client)
        post_json(client, "/classes", {"name": "Spin", "trainer_id": 1, "capacity": 1})
        post_json(client, "/classes/1/enroll", {})
        res = post_json(client, "/classes/1/enroll", {})
        assert res.status_code == 400

    def test_enroll_nonexistent_class(self, client):
        res = post_json(client, "/classes/999/enroll", {})
        assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# 5. BMI Calculator Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestBMICalculator:
    def test_bmi_normal_weight(self, client):
        res = post_json(client, "/bmi", {"weight_kg": 70, "height_cm": 175})
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data["bmi"] == 22.86
        assert data["category"] == "Normal weight"

    def test_bmi_underweight(self, client):
        res = post_json(client, "/bmi", {"weight_kg": 45, "height_cm": 170})
        assert json.loads(res.data)["category"] == "Underweight"

    def test_bmi_overweight(self, client):
        res = post_json(client, "/bmi", {"weight_kg": 85, "height_cm": 170})
        assert json.loads(res.data)["category"] == "Overweight"

    def test_bmi_obese(self, client):
        res = post_json(client, "/bmi", {"weight_kg": 110, "height_cm": 170})
        assert json.loads(res.data)["category"] == "Obese"

    def test_bmi_missing_fields(self, client):
        res = post_json(client, "/bmi", {"weight_kg": 70})
        assert res.status_code == 400

    def test_bmi_zero_height(self, client):
        res = post_json(client, "/bmi", {"weight_kg": 70, "height_cm": 0})
        assert res.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 6. Membership Plans Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMembershipPlans:
    def test_get_all_plans(self, client):
        res = client.get("/plans")
        assert res.status_code == 200
        data = json.loads(res.data)
        assert "basic" in data["plans"]
        assert "standard" in data["plans"]
        assert "premium" in data["plans"]

    def test_get_basic_plan(self, client):
        res = client.get("/plans/basic")
        data = json.loads(res.data)
        assert res.status_code == 200
        assert data["price"] == 999

    def test_get_premium_plan(self, client):
        res = client.get("/plans/premium")
        data = json.loads(res.data)
        assert data["price"] == 3999

    def test_get_invalid_plan(self, client):
        res = client.get("/plans/gold")
        assert res.status_code == 404

    def test_plan_case_insensitive(self, client):
        res = client.get("/plans/BASIC")
        assert res.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 7. V2 - Attendance & Diet Plan Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAttendanceAndDiet:
    def test_checkin_success(self, client_v2):
        post_json(client_v2, "/members", {"name": "Sita", "email": "sita@aceest.com"})
        res = post_json(client_v2, "/attendance/checkin", {"member_id": 1})
        assert res.status_code == 200

    def test_checkin_invalid_member(self, client_v2):
        res = post_json(client_v2, "/attendance/checkin", {"member_id": 99})
        assert res.status_code == 404

    def test_get_attendance(self, client_v2):
        post_json(client_v2, "/members", {"name": "Ram", "email": "ram@aceest.com"})
        post_json(client_v2, "/attendance/checkin", {"member_id": 1})
        res = client_v2.get("/attendance/1")
        assert res.status_code == 200
        records = json.loads(res.data)["records"]
        assert len(records) == 1

    def test_get_diet_plans(self, client_v2):
        res = client_v2.get("/diet-plans")
        assert res.status_code == 200
        data = json.loads(res.data)
        assert "weight_loss" in data
        assert "muscle_gain" in data

    def test_assign_diet_plan(self, client_v2):
        post_json(client_v2, "/members", {"name": "Leela", "email": "leela@aceest.com"})
        res = post_json(client_v2, "/members/1/diet-plan", {"plan": "weight_loss"})
        assert res.status_code == 200
        assert json.loads(res.data)["diet_plan"]["plan"] == "weight_loss"

    def test_assign_invalid_diet_plan(self, client_v2):
        post_json(client_v2, "/members", {"name": "Dev", "email": "dev@aceest.com"})
        res = post_json(client_v2, "/members/1/diet-plan", {"plan": "keto_extreme"})
        assert res.status_code == 400