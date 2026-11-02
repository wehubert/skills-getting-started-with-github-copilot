import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def api_client(monkeypatch):
    # Arrange shared state for one test.
    test_activities = {
        "Chess Club": {
            "description": "Practice strategy",
            "schedule": "Fridays at 3:30 PM",
            "max_participants": 3,
            "participants": ["alex@mergington.edu"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Thursdays at 3:30 PM",
            "max_participants": 2,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as client:
        yield client, test_activities


def test_get_activities_returns_activity_details_and_participants(api_client):
    # Arrange
    client, test_activities = api_client

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == test_activities


def test_signup_adds_participant(api_client):
    # Arrange
    client, test_activities = api_client
    activity = "Art Club"
    email = "sam@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in test_activities[activity]["participants"]


def test_signup_rejects_duplicate_participant(api_client):
    # Arrange
    client, test_activities = api_client
    activity = "Chess Club"
    email = test_activities[activity]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert test_activities[activity]["participants"] == [email]


def test_signup_returns_not_found_for_unknown_activity(api_client):
    # Arrange
    client, _ = api_client

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "sam@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(api_client):
    # Arrange
    client, test_activities = api_client
    activity = "Chess Club"
    email = test_activities[activity]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in test_activities[activity]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(api_client):
    # Arrange
    client, _ = api_client

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "sam@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_participant(api_client):
    # Arrange
    client, test_activities = api_client
    activity = "Chess Club"
    email = "sam@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up for this activity"}
    assert test_activities[activity]["participants"] == ["alex@mergington.edu"]
