"""
FastAPI Backend API Tests

Tests for the Mergington High School API using the AAA (Arrange-Act-Assert) pattern.
"""
import pytest
import httpx


class TestRootEndpoint:
    """Tests for the root endpoint (GET /)"""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Create test client
        Act: Make GET request to root endpoint
        Assert: Verify redirect to /static/index.html
        """
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Create test client
        Act: Make GET request to /activities
        Assert: Verify all 9 activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Verify we have all 9 activities
        assert len(activities) == 9
        
        # Verify each activity has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_returns_correct_participant_counts(self, client):
        """
        Arrange: Create test client
        Act: Make GET request to /activities
        Assert: Verify participant counts match the data
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert activities["Chess Club"]["max_participants"] == 12
        assert len(activities["Chess Club"]["participants"]) == 2
        assert activities["Programming Class"]["max_participants"] == 20
        assert len(activities["Programming Class"]["participants"]) == 2
        assert activities["Gym Class"]["max_participants"] == 30
        assert len(activities["Gym Class"]["participants"]) == 2


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """
        Arrange: Create test client with unique test email
        Act: Make POST request to sign up for Chess Club
        Assert: Verify successful signup with status 200
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"
        assert test_email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Create test client with non-existent activity
        Act: Make POST request to sign up for non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Non-Existent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_student_already_registered(self, client):
        """
        Arrange: Create test client with student already in activity
        Act: Make POST request to sign up student who is already registered
        Assert: Verify 400 error is returned
        """
        # Arrange
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_different_activity(self, client):
        """
        Arrange: Create test client with unique test email
        Act: Make POST request to sign up for Programming Class
        Assert: Verify successful signup for different activity
        """
        # Arrange
        test_email = "another.student@mergington.edu"
        activity_name = "Programming Class"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert test_email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client):
        """
        Arrange: Create test client with student already in activity
        Act: Make DELETE request to remove student from Chess Club
        Assert: Verify successful removal with status 200
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"

        # First, sign up the student
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {test_email} from {activity_name}"
        assert test_email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Create test client with non-existent activity
        Act: Make DELETE request to remove from non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Non-Existent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        """
        Arrange: Create test client with student not in activity
        Act: Make DELETE request to remove student who is not registered
        Assert: Verify 400 error is returned
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_different_activity(self, client):
        """
        Arrange: Create test client with student in Programming Class
        Act: Make DELETE request to remove student from Programming Class
        Assert: Verify successful removal from different activity
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Programming Class"

        # First, sign up the student
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert test_email not in activities[activity_name]["participants"]
