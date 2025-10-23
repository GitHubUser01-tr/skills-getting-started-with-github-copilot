import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test that the activities endpoint returns a list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Test structure of an activity
    first_activity = list(activities.values())[0]
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the student was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Try to sign up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First sign up
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Try to unregister again (should fail)
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()