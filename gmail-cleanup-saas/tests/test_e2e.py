"""End-to-end tests using Playwright."""

import pytest
from playwright.async_api import Page, expect


class TestAuthenticationFlow:
    """Test authentication-related flows."""
    
    @pytest.mark.asyncio
    async def test_login_page_loads(self, page: Page, base_url: str):
        """Test that the login page loads correctly."""
        await page.goto(base_url)
        
        # Should see the login page initially
        await expect(page.locator("text=Sign in with Google")).to_be_visible()
        await expect(page.locator("h1")).to_contain_text("Gmail Cleanup")
    
    @pytest.mark.asyncio
    async def test_login_button_exists(self, page: Page, base_url: str):
        """Test that the login button is present and clickable."""
        await page.goto(base_url)
        
        login_button = page.locator("button", has_text="Sign in with Google")
        await expect(login_button).to_be_visible()
        await expect(login_button).to_be_enabled()


class TestDashboardNavigation:
    """Test dashboard navigation and layout."""
    
    @pytest.mark.asyncio
    async def test_dashboard_navigation_authenticated(self, page: Page, base_url: str):
        """Test navigation between dashboard sections when authenticated."""
        await page.goto(base_url)
        
        # Mock authentication by directly navigating to dashboard
        # In a real test, you'd complete the OAuth flow
        await page.evaluate("""
            // Mock authentication state
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        # Navigate to dashboard
        await page.goto(f"{base_url}/#/dashboard")
        
        # Check for dashboard elements
        await expect(page.locator("nav")).to_be_visible()
        await expect(page.locator("text=Dashboard")).to_be_visible()
        await expect(page.locator("text=Rules")).to_be_visible()
        await expect(page.locator("text=Analysis")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_sidebar_navigation(self, page: Page, base_url: str):
        """Test sidebar navigation works correctly."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/dashboard")
        
        # Test navigation to Rules page
        await page.click("text=Rules")
        await expect(page.url).to_contain("rules")
        await expect(page.locator("text=Email Rules")).to_be_visible()
        
        # Test navigation to Analysis page
        await page.click("text=Analysis")
        await expect(page.url).to_contain("analysis")
        await expect(page.locator("text=Mailbox Analysis")).to_be_visible()
        
        # Test navigation back to Dashboard
        await page.click("text=Dashboard")
        await expect(page.url).to_contain("dashboard")


class TestRulesManagement:
    """Test rules management functionality."""
    
    @pytest.mark.asyncio
    async def test_rules_page_loads(self, page: Page, base_url: str):
        """Test that the rules page loads with correct elements."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/rules")
        
        # Check for rules page elements
        await expect(page.locator("text=Email Rules")).to_be_visible()
        await expect(page.locator("text=Create New Rule")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_create_rule_modal(self, page: Page, base_url: str):
        """Test that the create rule modal opens and closes."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/rules")
        
        # Click create rule button
        await page.click("button", has_text="Create New Rule")
        
        # Modal should open
        await expect(page.locator("[role='dialog']")).to_be_visible()
        await expect(page.locator("text=Create New Rule")).to_be_visible()
        
        # Modal should have form fields
        await expect(page.locator("input[placeholder*='rule name']")).to_be_visible()
        await expect(page.locator("textarea")).to_be_visible()
        
        # Close modal by clicking outside or close button
        await page.press("body", "Escape")
        await expect(page.locator("[role='dialog']")).not_to_be_visible()
    
    @pytest.mark.asyncio
    async def test_rule_templates_section(self, page: Page, base_url: str):
        """Test that rule templates are displayed."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/rules")
        
        # Check for templates section
        await expect(page.locator("text=Rule Templates")).to_be_visible()
        
        # Should have template cards
        template_cards = page.locator("[class*='cursor-pointer']:has-text('template')")
        await expect(template_cards.first).to_be_visible(timeout=10000)


class TestAnalysisPage:
    """Test analysis page functionality."""
    
    @pytest.mark.asyncio
    async def test_analysis_page_loads(self, page: Page, base_url: str):
        """Test that the analysis page loads with correct elements."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/analysis")
        
        # Check for analysis page elements
        await expect(page.locator("text=Mailbox Analysis")).to_be_visible()
        await expect(page.locator("text=Analyze Mailbox")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_analysis_stats_display(self, page: Page, base_url: str):
        """Test that analysis stats are displayed."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/analysis")
        
        # Should show stats cards
        await expect(page.locator("text=Total Messages")).to_be_visible()
        await expect(page.locator("text=Total Rules")).to_be_visible()


class TestProcessingPage:
    """Test processing page functionality."""
    
    @pytest.mark.asyncio
    async def test_processing_page_loads(self, page: Page, base_url: str):
        """Test that the processing page loads with correct elements."""
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/processing")
        
        # Check for processing page elements
        await expect(page.locator("text=Rule Processing")).to_be_visible()


class TestResponsiveDesign:
    """Test responsive design on different screen sizes."""
    
    @pytest.mark.asyncio
    async def test_mobile_layout(self, page: Page, base_url: str):
        """Test mobile layout."""
        # Set mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/dashboard")
        
        # Should be responsive
        await expect(page.locator("nav")).to_be_visible()
    
    @pytest.mark.asyncio
    async def test_tablet_layout(self, page: Page, base_url: str):
        """Test tablet layout."""
        # Set tablet viewport
        await page.set_viewport_size({"width": 768, "height": 1024})
        
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/dashboard")
        
        # Should be responsive
        await expect(page.locator("nav")).to_be_visible()


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_404_page_navigation(self, page: Page, base_url: str):
        """Test navigation to non-existent page."""
        await page.goto(f"{base_url}/#/non-existent-page")
        
        # Should handle gracefully (either redirect or show 404)
        # This depends on your Vue router configuration
        await page.wait_for_load_state("networkidle")
        
        # Page should still be responsive
        await expect(page).not_to_have_title("Error")
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, page: Page, base_url: str):
        """Test handling of network errors."""
        # Mock network failure for API calls
        await page.route("**/api/**", lambda route: route.abort())
        
        await page.goto(base_url)
        
        # Mock authentication
        await page.evaluate("""
            localStorage.setItem('auth_token', 'mock_token');
            localStorage.setItem('user_info', JSON.stringify({
                email: 'test@example.com',
                name: 'Test User'
            }));
        """)
        
        await page.goto(f"{base_url}/#/dashboard")
        
        # Should handle network errors gracefully
        # This will depend on your error handling implementation
        await page.wait_for_load_state("networkidle")