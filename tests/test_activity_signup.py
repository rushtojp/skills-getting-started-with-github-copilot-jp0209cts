from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_duplicate_signup_is_rejected():
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    email = "newstudent@example.com"

    try:
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)

        first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        second_response = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"].lower()
    finally:
        activities[activity_name]["participants"] = original_participants


def test_full_activity_rejects_new_signup():
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    original_limit = activities[activity_name]["max_participants"]

    try:
        activities[activity_name]["participants"] = [
            f"student{i}@mergington.edu" for i in range(original_limit)
        ]

        response = client.post(f"/activities/{activity_name}/signup?email=overflow@example.com")

        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    finally:
        activities[activity_name]["participants"] = original_participants
        activities[activity_name]["max_participants"] = original_limit


def test_unregister_removes_participant():
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    email = "removeme@example.com"

    try:
        activities[activity_name]["participants"].append(email)

        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_missing_participant_is_rejected():
    response = client.delete(
        "/activities/Chess Club/signup?email=missing@example.com"
    )

    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
