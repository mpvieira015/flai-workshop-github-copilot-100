"""
Tests for the Mergington High School API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Basketball Team": {
            "description": "Join the school basketball team for training and competitions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and play friendly matches",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and acting workshops",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": []
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": []
        },
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
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_html(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we get all activities
        assert len(data) == 9
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Chess Club" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check structure of one activity
        basketball = data["Basketball Team"]
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
        assert isinstance(basketball["participants"], list)
    
    def test_get_activities_includes_participants(self, client):
        """Test that activities include existing participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up student@mergington.edu for Basketball Team"
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "student@mergington.edu" in activities_data["Basketball Team"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        # First signup
        client.post("/activities/Basketball%20Team/signup?email=student@mergington.edu")
        
        # Try to signup again
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        response = client.post(
            "/activities/Drama%20Club/signup?email=first.last%2Btest@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # First, sign up a student
        client.post("/activities/Soccer%20Club/signup?email=student@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Soccer%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered student@mergington.edu from Soccer Club"
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "student@mergington.edu" not in activities_data["Soccer Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not registered for this activity"
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant from Chess Club"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        chess_participants = activities_data["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in chess_participants
        assert "daniel@mergington.edu" in chess_participants  # Other participant still there


class TestIntegrationScenarios:
    """Integration tests for common user scenarios"""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        activity = "Art Workshop"
        email = "newstudent@mergington.edu"
        
        # Initial state - no participants
        response = client.get("/activities")
        initial_data = response.json()
        assert email not in initial_data[activity]["participants"]
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        final_data = response.json()
        assert email not in final_data[activity]["participants"]
    
    def test_multiple_students_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Math Olympiad"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Sign up all students
        for student in students:
            response = client.post(f"/activities/{activity}/signup?email={student}")
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        data = response.json()
        for student in students:
            assert student in data[activity]["participants"]
        
        # Unregister one student
        response = client.delete(f"/activities/{activity}/unregister?email={students[1]}")
        assert response.status_code == 200
        
        # Verify only one was removed
        response = client.get("/activities")
        data = response.json()
        assert students[0] in data[activity]["participants"]
        assert students[1] not in data[activity]["participants"]
        assert students[2] in data[activity]["participants"]
