from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_duplicate_signup_is_rejected():
    # Arrange
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    email = "newstudent@example.com"

    try:
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)

        # Act
        endpoint = f"/activities/{activity_name}/signup"
        first_response = client.post(endpoint, params={"email": email})
        second_response = client.post(endpoint, params={"email": email})

        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"].lower()
    finally:
        activities[activity_name]["participants"] = original_participants


def test_full_activity_rejects_new_signup():
    # Arrange
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    original_limit = activities[activity_name]["max_participants"]

    try:
        activities[activity_name]["participants"] = [
            f"student{i}@mergington.edu" for i in range(original_limit)
        ]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "overflow@example.com"},
        )

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    finally:
        activities[activity_name]["participants"] = original_participants
        activities[activity_name]["max_participants"] = original_limit


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    email = "removeme@example.com"

    try:
        activities[activity_name]["participants"].append(email)

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_missing_participant_is_rejected():
    # Arrange
    endpoint = "/activities/Chess Club/signup"
    email = "missing@example.com"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
