"""UI automated tests for DaveAI web application using Selenium WebDriver.

Primary UI suite. Uses the Page Object Model (POM) pattern.
"""

import pytest
from pages.contact_page import ContactPage
from pages.demo_page import DemoPage
from pages.home_page import HomePage


@pytest.mark.ui
def test_homepage_load_and_branding(driver, ui_base_url):
    """Verify homepage title contains the DaveAI brand, header is visible, and hero heading is correct."""
    home = HomePage(driver)
    home.load()

    # Use a substring check instead of exact equality — marketing copy can change
    # without breaking the brand identity assertion.
    page_title = home.get_title()
    assert "DaveAI" in page_title, f"Expected 'DaveAI' in page title, got '{page_title}'"

    assert home.is_header_present(), "Site header container is not present on the homepage"
    assert home.has_brand_logo_rendered(), "DaveAI brand logo was not found in the DOM"

    hero_text = home.get_hero_heading_text()
    assert "Automotive Intelligence" in hero_text, (
        f"Hero heading should contain 'Automotive Intelligence', got: '{hero_text}'"
    )


@pytest.mark.ui
def test_navigation_flow_to_platform_page(driver, ui_base_url):
    """Verify navigation from homepage to the platform page."""
    home = HomePage(driver)
    home.load()

    home.click_more_about_platform()
    home.wait_for_url_contains("/platform/")

    current_url = home.get_current_url()
    assert "/platform/" in current_url, f"Expected URL to contain '/platform/', got '{current_url}'"

    current_title = home.get_title()
    assert "Platform" in current_title and "DaveAI" in current_title, (
        f"Expected 'Platform' and 'DaveAI' in page title, got '{current_title}'"
    )


@pytest.mark.ui
def test_navigation_to_book_demo(driver, ui_base_url):
    """Verify navigation from homepage to the demo booking form."""
    home = HomePage(driver)
    home.load()

    home.click_book_demo_cta()
    home.wait_for_url_contains("/book-demo/")
    assert "/book-demo/" in home.get_current_url()

    demo_page = DemoPage(driver)
    assert demo_page.is_demo_form_displayed(), "Lead capture form fields are not visible on demo page"


@pytest.mark.ui
def test_contact_form_interactions_and_validation(driver, ui_base_url):
    """Verify contact form input handling and HTML5 email validation.

    Form is NOT submitted to avoid generating spam records in production CRM.
    """
    contact = ContactPage(driver)
    contact.load()

    test_payload = {
        "name": "Automation QA Tester",
        "email": "tester.automation@example.com",
        "company": "Quality Engineering Corp",
        "phone": "+1-555-0199",
        "message": "Automated regression test verifying form field inputs and validation rules.",
    }

    contact.fill_contact_form(**test_payload)

    actual_values = contact.get_input_values()
    assert actual_values["name"] == test_payload["name"], "Name input field value mismatch"
    assert actual_values["email"] == test_payload["email"], "Email input field value mismatch"
    assert actual_values["company"] == test_payload["company"], "Company input field value mismatch"
    assert actual_values["phone"] == test_payload["phone"], "Phone input field value mismatch"
    assert actual_values["message"] == test_payload["message"], "Message textarea value mismatch"

    contact.type_text(contact.INPUT_EMAIL, "invalid_email_format")
    assert not contact.is_email_valid(), "Email field should report invalid for 'invalid_email_format'"

    contact.type_text(contact.INPUT_EMAIL, "valid.email@example.com")
    assert contact.is_email_valid(), "Email field should report valid for standard email format"
