import copy
import pytest
from fastapi.testclient import TestClient
from src import app as app_module

# Save the initial state of activities for resetting between tests
initial_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the global activities state before each test."""
    app_module.activities = copy.deepcopy(initial_activities)


@pytest.fixture
def client():
    """Provide a TestClient instance for testing."""
    return TestClient(app_module.app)


def test_get_activities(client):
    # Arrange: TestClient is set up via fixture

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Response is successful and contains expected activities
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9  # Total activities


def test_signup_for_activity(client):
    # Arrange: Choose an activity and a new email
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Response is successful and student is added
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_email_rejected(client):
    # Arrange: Sign up an email first
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Try to sign up the same email for another activity
    another_activity = "Gym Class"
    response = client.post(f"/activities/{another_activity}/signup?email={email}")

    # Assert: Request is rejected with 400
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_unregister_participant(client):
    # Arrange: Sign up a participant first
    activity_name = "Art Studio"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert: Response is successful and participant is removed
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_nonexistent_participant(client):
    # Arrange: Choose an activity and a non-participant email
    activity_name = "Drama Workshop"
    email = "notsignedup@mergington.edu"

    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert: Request fails with 404
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_activity_not_found(client):
    # Arrange: Use a nonexistent activity name
    activity_name = "Nonexistent Activity"
    email = "test@mergington.edu"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert: Request fails with 404
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]