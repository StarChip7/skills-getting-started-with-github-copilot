import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Create a copy of the original activities for resetting
original_activities = copy.deepcopy(activities)

@pytest.fixture
def client():
    # Reset activities before each test
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    return TestClient(app)

def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Club" in data
    assert "description" in data["Basketball Club"]
    assert "participants" in data["Basketball Club"]

def test_signup_success(client):
    response = client.post("/activities/Basketball%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@mergington.edu for Basketball Club" in data["message"]
    
    # Check that the participant was added
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" in data["Basketball Club"]["participants"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up(client):
    # First signup
    client.post("/activities/Basketball%20Club/signup?email=test@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Basketball%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]

def test_unregister_success(client):
    # First signup
    client.post("/activities/Basketball%20Club/signup?email=test@mergington.edu")
    
    # Then unregister
    response = client.delete("/activities/Basketball%20Club/unregister?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered test@mergington.edu from Basketball Club" in data["message"]
    
    # Check that the participant was removed
    response = client.get("/activities")
    data = response.json()
    assert "test@mergington.edu" not in data["Basketball Club"]["participants"]

def test_unregister_activity_not_found(client):
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_not_signed_up(client):
    response = client.delete("/activities/Basketball%20Club/unregister?email=notsignedup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is not signed up for this activity" in data["detail"]