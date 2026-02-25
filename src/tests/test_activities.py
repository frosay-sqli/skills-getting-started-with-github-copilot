"""
Comprehensive tests for the Mergington High School Activities API
Tests all endpoints and error cases
"""

import pytest
from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
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
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interscholastic play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Volleyball Club": {
            "description": "Volleyball practice and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["sarah@mergington.edu", "maya@mergington.edu"]
        },
        "Art Studio": {
            "description": "Drawing, painting, and mixed media creation",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alice@mergington.edu"]
        },
        "Theater Production": {
            "description": "Acting and stage performance for school plays",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
        },
        "Debate Society": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["alex@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific research projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["david@mergington.edu", "nina@mergington.edu"]
        }
    }
    
    # Clear and reset activities dict
    activities.clear()
    activities.update(original_activities)
    
    yield


# ===== Tests for GET /activities =====

class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities_returns_200(self, client):
        """GET /activities returns HTTP 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_all_activities_returns_all_activities(self, client):
        """GET /activities returns all 9 activities"""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9
    
    def test_get_all_activities_includes_required_activities(self, client):
        """GET /activities includes all expected activity names"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Volleyball Club", "Art Studio", "Theater Production", 
            "Debate Society", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_get_all_activities_has_correct_structure(self, client):
        """Each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in {activity_name}"
    
    def test_get_all_activities_participants_is_list(self, client):
        """Participants field is a list in each activity"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list), \
                f"participants for {activity_name} is not a list"


# ===== Tests for POST /activities/{activity_name}/signup =====

class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_happy_path_returns_200(self, client):
        """POST signup with valid activity and new email returns HTTP 200"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_happy_path_adds_student(self, client):
        """POST signup adds student to participants list"""
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_happy_path_response_message(self, client):
        """POST signup response includes success message"""
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """POST signup with non-existent activity returns HTTP 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_signup_nonexistent_activity_error_message(self, client):
        """POST signup with non-existent activity returns proper error message"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_email_returns_400(self, client):
        """POST signup with email already in activity returns HTTP 400"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
    
    def test_signup_duplicate_email_error_message(self, client):
        """POST signup with duplicate email returns proper error message"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_at_capacity_returns_400(self, client):
        """POST signup when activity is full returns HTTP 400"""
        # Create a full activity by filling all spots
        activities["Test Activity"] = {
            "description": "Test activity",
            "schedule": "Test time",
            "max_participants": 2,
            "participants": ["student1@mergington.edu", "student2@mergington.edu"]
        }
        
        response = client.post(
            "/activities/Test Activity/signup",
            params={"email": "student3@mergington.edu"}
        )
        assert response.status_code == 400
    
    def test_signup_activity_at_capacity_error_message(self, client):
        """POST signup when activity is full returns proper error message"""
        activities["Test Activity"] = {
            "description": "Test activity",
            "schedule": "Test time",
            "max_participants": 2,
            "participants": ["student1@mergington.edu", "student2@mergington.edu"]
        }
        
        response = client.post(
            "/activities/Test Activity/signup",
            params={"email": "student3@mergington.edu"}
        )
        data = response.json()
        assert "detail" in data
        assert "full" in data["detail"].lower()
    
    def test_signup_can_fill_activity_to_capacity(self, client):
        """POST signup can fill an activity to its max capacity"""
        # Programming Class has max 20, currently has 2
        # We should be able to add 18 more
        test_email = "testfill@mergington.edu"
        
        # First signup should work
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": test_email}
        )
        assert response.status_code == 200
        
        # Verify it was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data["Programming Class"]["participants"]
        assert len(activities_data["Programming Class"]["participants"]) == 3
    
    def test_signup_multiple_activities_independent(self, client):
        """Student can sign up for multiple different activities"""
        email = "multiactivity@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]
