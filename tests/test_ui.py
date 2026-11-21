"""
UI Automated Test Suite for DaveAI (https://www.iamdave.ai/)
Implements Page Object Model (POM) using Selenium WebDriver.
Covers brand verification, multi-page navigation flows, element presence, and form input interactions.
"""

import pytest
from pages.home_page import HomePage
from pages.contact_page import ContactPage
from pages.demo_page import DemoPage


@pytest.mark.ui
def test_homepage_load_and_branding(driver, ui_base_url):
    """
    Test Case 1: Verify Homepage Load, Page Title, and Brand Elements
    - Navigates to DaveAI homepage
    - Asserts page title matches the expected brand positioning
    - Asserts primary hero headline (H1) is rendered and contains expected copy
    - Verifies site header and brand logo elements exist in the DOM
    """
    home = HomePage(driver)
    home.load()

    # 1. Page Title Verification
    expected_title_fragment = "AI-Native Automotive Intelligence Platform | DaveAI"
    assert home.get_title() == expected_title_fragment, (
        f"Expected title '{expected_title_fragment}', but got '{home.get_title()}'"
    )

    # 2. Header and Branding Presence
    assert home.is_header_present(), "Site header container is not present on the homepage"
    assert home.has_brand_logo_rendered(), "DaveAI brand logo was not found in the DOM"

    # 3. Main Hero Heading Verification
    hero_text = home.get_hero_heading_text()
    assert "Automotive Intelligence" in hero_text, (
        f"Hero H1 heading should mention 'Automotive Intelligence', got: '{hero_text}'"
    )


@pytest.mark.ui
def test_navigation_flow_to_platform_page(driver, ui_base_url):
    """
    Test Case 2: Test Navigation Flow - Explore Platform
    - Starts on the homepage
    - Interacts with the 'MORE ABOUT OUR PLATFORM' CTA
    - Explicitly waits for browser URL to transition to /platform/
    - Asserts target page title and URL confirm successful navigation
    """
    home = HomePage(driver)
    home.load()

    # Trigger Navigation
    home.click_more_about_platform()

    # Explicit wait for page transition
    home.wait_for_url_contains("/platform/")

    current_url = home.get_current_url()
    assert "/platform/" in current_url, f"Expected URL to contain '/platform/', got '{current_url}'"

    current_title = home.get_title()
    assert "Platform" in current_title and "DaveAI" in current_title, (
        f"Expected 'Platform' and 'DaveAI' in page title, got '{current_title}'"
    )


@pytest.mark.ui
def test_navigation_to_book_demo(driver, ui_base_url):
    """
    Test Case 3: Test Navigation Flow - High-Intent Demo CTA
    - Starts on homepage
    - Clicks high-intent conversion CTA ('SEE DAVEAI IN ACTION' or 'GET A FREE DEMO')
    - Explicitly waits for navigation to /book-demo/
    - Verifies that the Book Demo form inputs (Name, Email, Message) are rendered
    """
    home = HomePage(driver)
    home.load()

    # Trigger CTA Click
    home.click_book_demo_cta()

    # Verify Navigation to Demo Page
    home.wait_for_url_contains("/book-demo/")
    assert "/book-demo/" in home.get_current_url()

    demo_page = DemoPage(driver)
    assert demo_page.is_demo_form_displayed(), "Lead capture form fields are not visible on the demo page"


@pytest.mark.ui
def test_contact_form_interactions_and_validation(driver, ui_base_url):
    """
    Test Case 4: Test Form Input Field Interaction & Client-side Validation
    - Navigates to Contact Us page (/contact-us/)
    - Fills out user details: Name, Email, Company, Phone, and Message
    - Asserts that all form inputs correctly retain the user's keystrokes
    - Validates HTML5 email input constraint:
        a) Rejects invalid email formats (e.g., 'invalid-user-format')
        b) Accepts valid email formats (e.g., 'qa.engineer@example.com')
    - Note: Form is NOT submitted to avoid generating spam records in production CRM.
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

    # Step 1: Input text into fields
    contact.fill_contact_form(**test_payload)

    # Step 2: Verify inputs retain typed values
    actual_values = contact.get_input_values()
    assert actual_values["name"] == test_payload["name"], "Name input field value mismatch"
    assert actual_values["email"] == test_payload["email"], "Email input field value mismatch"
    assert actual_values["company"] == test_payload["company"], "Company input field value mismatch"
    assert actual_values["phone"] == test_payload["phone"], "Phone input field value mismatch"
    assert actual_values["message"] == test_payload["message"], "Message textarea value mismatch"

    # Step 3: Test HTML5 Client-side Validation with invalid email
    contact.type_text(contact.INPUT_EMAIL, "invalid_email_format")
    assert not contact.is_email_valid(), "Email field should report invalid for 'invalid_email_format'"

    # Step 4: Restore valid email and verify validation passes
    contact.type_text(contact.INPUT_EMAIL, "valid.email@example.com")
    assert contact.is_email_valid(), "Email field should report valid for standard email format"
