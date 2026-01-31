"""
Basic API Tests for Inventix AI Backend

Run with: python -m pytest test_api.py -v
"""
import pytest
import os
import tempfile
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test_inventix.db"
os.environ["UPLOAD_DIR"] = "./test_uploads"

from main import app
from database import init_db, Base, engine


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database for each test"""
    # Create fresh database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Ensure test upload directory exists
    os.makedirs("./test_uploads", exist_ok=True)
    
    with TestClient(app) as c:
        yield c
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ai_enabled"] == False
        assert data["phase"] == 1


class TestProjects:
    """Project CRUD tests"""
    
    def test_create_project(self, client):
        response = client.post("/api/projects", json={
            "name": "Test Project",
            "type": "RESEARCH",
            "description": "A test project",
            "idea_text": "My test idea",
            "domain": "AI"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["type"] == "RESEARCH"
        assert data["analysis_state"]["idea_received"] == True
        assert data["analysis_state"]["analysis_status"] == "NOT_STARTED"
    
    def test_create_project_minimal(self, client):
        response = client.post("/api/projects", json={
            "name": "Minimal Project"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Project"
        assert data["type"] == "RESEARCH"  # Default
    
    def test_list_projects(self, client):
        # Create two projects
        client.post("/api/projects", json={"name": "Project 1"})
        client.post("/api/projects", json={"name": "Project 2"})
        
        response = client.get("/api/projects")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["projects"]) == 2
    
    def test_get_project(self, client):
        # Create project
        create_response = client.post("/api/projects", json={
            "name": "Single Project",
            "idea_text": "Some idea"
        })
        project_id = create_response.json()["id"]
        
        # Get project
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Single Project"
        assert "analysis_state" in data
        assert "files" in data
    
    def test_get_project_not_found(self, client):
        response = client.get("/api/projects/999")
        assert response.status_code == 404
    
    def test_update_project(self, client):
        # Create project
        create_response = client.post("/api/projects", json={"name": "Original"})
        project_id = create_response.json()["id"]
        
        # Update project
        response = client.put(f"/api/projects/{project_id}", json={
            "name": "Updated",
            "idea_text": "New idea"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["analysis_state"]["idea_received"] == True
    
    def test_delete_project(self, client):
        # Create project
        create_response = client.post("/api/projects", json={"name": "To Delete"})
        project_id = create_response.json()["id"]
        
        # Delete project
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 404


class TestAnalysisState:
    """Analysis state honesty tests"""
    
    def test_analysis_always_not_started(self, client):
        """Analysis status should ALWAYS be NOT_STARTED in Phase 1"""
        response = client.post("/api/projects", json={
            "name": "Test",
            "idea_text": "Idea with lots of text to suggest progress"
        })
        data = response.json()
        assert data["analysis_state"]["analysis_status"] == "NOT_STARTED"
        assert "not implemented" in data["analysis_state"]["notes"].lower()
    
    def test_idea_received_flag(self, client):
        """idea_received should accurately reflect idea_text presence"""
        # Without idea
        response1 = client.post("/api/projects", json={"name": "No Idea"})
        assert response1.json()["analysis_state"]["idea_received"] == False
        
        # With idea
        response2 = client.post("/api/projects", json={
            "name": "With Idea",
            "idea_text": "My idea"
        })
        assert response2.json()["analysis_state"]["idea_received"] == True


class TestSystemStatus:
    """System status endpoint tests"""
    
    def test_system_status(self, client):
        response = client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert data["phase"] == 1
        assert "not_implemented" in data
        assert len(data["not_implemented"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
