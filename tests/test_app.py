import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["student@example.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, activities):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client, activities):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@example.edu for Chess Club"
    }
    assert activities["Chess Club"]["participants"] == [
        "student@example.edu",
        "new@example.edu",
    ]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_email_case_insensitively(client, activities):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "STUDENT@EXAMPLE.EDU"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
    assert activities["Chess Club"]["participants"] == ["student@example.edu"]


def test_unregister_removes_participant_case_insensitively(client, activities):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "STUDENT@EXAMPLE.EDU"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.edu from Chess Club"
    }
    assert activities["Chess Club"]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client, activities):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "other@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"
    assert activities["Chess Club"]["participants"] == ["student@example.edu"]