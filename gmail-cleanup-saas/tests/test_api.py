"""API endpoint tests."""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gmail-cleanup-api"
        assert "version" in data


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_auth_status_unauthenticated(self, async_client: AsyncClient):
        """Test auth status when not authenticated."""
        response = await async_client.get("/api/auth/status")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is False
        assert "not authenticated" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_auth_login_requires_body(self, async_client: AsyncClient):
        """Test that auth login requires request body."""
        response = await async_client.post("/api/auth/login")
        # Should accept empty body as AuthRequest has optional fields
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestRulesEndpoints:
    """Test rules management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_rules_empty(self, async_client: AsyncClient, mock_oauth_handler):
        """Test listing rules when none exist."""
        response = await async_client.get("/api/rules/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "rules" in data
        assert "total" in data
        assert isinstance(data["rules"], list)
    
    @pytest.mark.asyncio
    async def test_create_rule_valid(self, async_client: AsyncClient, mock_oauth_handler, sample_rule_data):
        """Test creating a valid rule."""
        response = await async_client.post("/api/rules/", json=sample_rule_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == sample_rule_data["name"]
        assert data["description"] == sample_rule_data["description"]
        assert data["enabled"] == sample_rule_data["enabled"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_rule_invalid_action_type(self, async_client: AsyncClient, mock_oauth_handler):
        """Test creating a rule with invalid action type."""
        invalid_rule_data = {
            "name": "Invalid Rule",
            "description": "Rule with invalid action",
            "criteria": {"from_email": "test@example.com"},
            "action": {"type": "invalid_action"}
        }
        
        response = await async_client.post("/api/rules/", json=invalid_rule_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_rule_missing_required_fields(self, async_client: AsyncClient, mock_oauth_handler):
        """Test creating a rule with missing required fields."""
        incomplete_rule_data = {
            "name": "Incomplete Rule"
            # Missing description, criteria, and action
        }
        
        response = await async_client.post("/api/rules/", json=incomplete_rule_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_get_rule_by_id(self, async_client: AsyncClient, mock_oauth_handler, sample_rule_data):
        """Test getting a rule by ID."""
        # First create a rule
        create_response = await async_client.post("/api/rules/", json=sample_rule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_rule = create_response.json()
        
        # Then get it by ID
        response = await async_client.get(f"/api/rules/{created_rule['id']}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == created_rule["id"]
        assert data["name"] == sample_rule_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_rule_not_found(self, async_client: AsyncClient, mock_oauth_handler):
        """Test getting a non-existent rule."""
        response = await async_client.get("/api/rules/non-existent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_rule(self, async_client: AsyncClient, mock_oauth_handler, sample_rule_data):
        """Test updating a rule."""
        # First create a rule
        create_response = await async_client.post("/api/rules/", json=sample_rule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_rule = create_response.json()
        
        # Update the rule
        update_data = {
            "description": "Updated description",
            "enabled": False
        }
        response = await async_client.put(f"/api/rules/{created_rule['id']}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["enabled"] is False
    
    @pytest.mark.asyncio
    async def test_delete_rule(self, async_client: AsyncClient, mock_oauth_handler, sample_rule_data):
        """Test deleting a rule."""
        # First create a rule
        create_response = await async_client.post("/api/rules/", json=sample_rule_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_rule = create_response.json()
        
        # Delete the rule
        response = await async_client.delete(f"/api/rules/{created_rule['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's gone
        get_response = await async_client.get(f"/api/rules/{created_rule['id']}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestTemplateEndpoints:
    """Test template endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_templates(self, async_client: AsyncClient):
        """Test listing available templates."""
        response = await async_client.get("/api/rules/templates/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "templates" in data
        assert "categories" in data
        assert isinstance(data["templates"], list)
        assert isinstance(data["categories"], list)
    
    @pytest.mark.asyncio
    async def test_create_rule_from_template(self, async_client: AsyncClient, mock_oauth_handler):
        """Test creating a rule from a template."""
        # First get available templates
        templates_response = await async_client.get("/api/rules/templates/")
        assert templates_response.status_code == status.HTTP_200_OK
        templates_data = templates_response.json()
        
        if len(templates_data["templates"]) > 0:
            template_id = templates_data["templates"][0]["id"]
            
            response = await async_client.post(f"/api/rules/templates/{template_id}", json={})
            assert response.status_code == status.HTTP_201_CREATED
            
            data = response.json()
            assert "id" in data
            assert "name" in data
            assert "description" in data
            assert "criteria" in data
            assert "action" in data
    
    @pytest.mark.asyncio
    async def test_create_rule_from_invalid_template(self, async_client: AsyncClient, mock_oauth_handler):
        """Test creating a rule from an invalid template."""
        response = await async_client.post("/api/rules/templates/invalid-template-id", json={})
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]


class TestAnalysisEndpoints:
    """Test analysis endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_stats(self, async_client: AsyncClient, mock_oauth_handler):
        """Test getting mailbox stats."""
        response = await async_client.get("/api/analysis/stats")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "total_messages" in data
        assert "total_rules" in data
        assert "enabled_rules" in data


class TestProcessingEndpoints:
    """Test processing endpoints."""
    
    @pytest.mark.asyncio
    async def test_process_rules_empty(self, async_client: AsyncClient, mock_oauth_handler):
        """Test processing rules when no rules exist."""
        request_data = {"dry_run": True}
        response = await async_client.post("/api/processing/process", json=request_data)
        
        # Should either succeed with no rules processed or give appropriate error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]