"""
Alias module for test_ui.py to support naming requirement `tests/ui_tests.py`.
"""

from tests.test_ui import (
    test_homepage_load_and_branding,
    test_navigation_flow_to_platform_page,
    test_navigation_to_book_demo,
    test_contact_form_interactions_and_validation,
)

__all__ = [
    "test_homepage_load_and_branding",
    "test_navigation_flow_to_platform_page",
    "test_navigation_to_book_demo",
    "test_contact_form_interactions_and_validation",
]
