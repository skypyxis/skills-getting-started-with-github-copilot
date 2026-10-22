from fastapi.testclient import TestClient
import pytest

from src.app import activities, app


TEST_ACTIVITY = "Test Activity"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_activity(monkeypatch):
    activity = {
        "description": "Activity for API tests",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [],
    }
    monkeypatch.setitem(activities, TEST_ACTIVITY, activity)
    return activity


def test_signup_adds_participant(client, test_activity):
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up student@example.com for {TEST_ACTIVITY}"
    }
    assert test_activity["participants"] == ["student@example.com"]


def test_signup_rejects_duplicate_participant(client, test_activity):
    test_activity["participants"].append("student@example.com")

    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 400
    assert test_activity["participants"] == ["student@example.com"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, test_activity):
    test_activity["participants"].append("student@example.com")

    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed student@example.com from {TEST_ACTIVITY}"
    }
    assert test_activity["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unregistered_participant(client, test_activity):
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert test_activity["participants"] == []