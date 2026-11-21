"""Playwright UI automated tests for DaveAI web application.

Bonus suite — an alternative implementation alongside the primary Selenium POM suite.
"""

import pytest
from playwright.sync_api import expect, sync_playwright


@pytest.fixture(scope="function")
def playwright_page():
    """Setup and teardown fixture for Playwright browser context."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.set_default_timeout(20000)
        yield page
        context.close()
        browser.close()


@pytest.mark.playwright
def test_pw_homepage_title_and_hero(playwright_page, ui_base_url):
    """Verify homepage title contains 'DaveAI' and hero heading is visible with Playwright."""
    playwright_page.goto(ui_base_url)

    assert "DaveAI" in playwright_page.title()

    hero = playwright_page.locator("h1").first
    expect(hero).to_be_visible()
    assert "Automotive Intelligence" in hero.inner_text()


@pytest.mark.playwright
def test_pw_navigation_to_platform(playwright_page, ui_base_url):
    """Verify navigation to platform page with Playwright."""
    playwright_page.goto(ui_base_url)

    platform_button = playwright_page.locator("a.elementor-button[href*='/platform/']").first
    platform_button.scroll_into_view_if_needed()
    platform_button.click()

    playwright_page.wait_for_url("**/platform/**")
    assert "/platform/" in playwright_page.url
    assert "Platform" in playwright_page.title()


@pytest.mark.playwright
def test_pw_contact_form_inputs(playwright_page, ui_base_url):
    """Verify contact form inputs and HTML5 email validation with Playwright.

    Form is NOT submitted to avoid generating spam records in production CRM.
    """
    playwright_page.goto(f"{ui_base_url}/contact-us/")

    name_input = playwright_page.locator("#form-field-name")
    email_input = playwright_page.locator("#form-field-email")
    message_input = playwright_page.locator("#form-field-message")

    name_input.fill("Playwright Tester")
    email_input.fill("invalid-email")
    message_input.fill("Automated Playwright interaction check.")

    expect(name_input).to_have_value("Playwright Tester")
    expect(message_input).to_have_value("Automated Playwright interaction check.")

    is_valid = email_input.evaluate("el => el.checkValidity()")
    assert not is_valid, "Invalid email format should fail HTML5 validity check"

    email_input.fill("playwright.engineer@example.com")
    assert email_input.evaluate("el => el.checkValidity()"), "Valid email should pass checkValidity"
