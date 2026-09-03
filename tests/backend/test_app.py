from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    endpoint = "/"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details():
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    response_activities = response.json()
    assert set(response_activities) == set(activities)
    for activity in response_activities.values():
        assert {"description", "schedule", "max_participants", "participants"} <= set(activity)


def test_signup_adds_participant_and_returns_message():
    # Arrange
    activity_name = "Chess Club"
    original_participants = activities[activity_name]["participants"][:]
    email = "newstudent@example.com"

    try:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_signup_for_unknown_activity_is_rejected():
    # Arrange
    endpoint = "/activities/Unknown Club/signup"

    # Act
    response = client.post(
        endpoint, params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_is_rejected():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


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


def test_unregister_removes_participant_and_returns_message():
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
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants


def test_unregister_missing_participant_is_rejected():
    # Arrange
    endpoint = "/activities/Chess Club/signup"

    # Act
    response = client.delete(
        endpoint, params={"email": "missing@example.com"}
    )

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_from_unknown_activity_is_rejected():
    # Arrange
    endpoint = "/activities/Unknown Club/signup"

    # Act
    response = client.delete(
        endpoint, params={"email": "student@example.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_without_email_is_rejected():
    # Arrange
    endpoint = "/activities/Chess Club/signup"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 422


def test_unregister_without_email_is_rejected():
    # Arrange
    endpoint = "/activities/Chess Club/signup"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 422
