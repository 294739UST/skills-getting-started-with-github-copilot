import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


class TestActivitiesAPI:
    """Test suite for the Activities API"""

    def setup_method(self):
        """Reset the activities data before each test"""
        # Reset to initial state
        activities.clear()
        activities.update({
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            }
        })

    def test_root_redirect(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.url.path == "/static/index.html"

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

        # Check structure of activity data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

        # Verify the participant was added
        response = client.get("/activities")
        data = response.json()
        assert "test@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self):
        """Test signup when student is already signed up"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

        # Try to signup again
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_remove_participant_successful(self):
        """Test successful removal of a participant"""
        # First add a participant
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

        # Now remove them
        response = client.delete("/activities/Chess%20Club/participants/test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

        # Verify the participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "test@mergington.edu" not in data["Chess Club"]["participants"]

    def test_remove_participant_activity_not_found(self):
        """Test removing participant from non-existent activity"""
        response = client.delete("/activities/NonExistent/participants/test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self):
        """Test removing participant who is not signed up"""
        response = client.delete("/activities/Chess%20Club/participants/nonexistent@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]