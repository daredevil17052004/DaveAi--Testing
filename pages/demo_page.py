"""
Book Demo Page Object for https://www.iamdave.ai/book-demo/
Encapsulates demo request form elements and verification.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DemoPage(BasePage):
    URL = "https://www.iamdave.ai/book-demo/"

    # Locators
    PAGE_HEADING = (By.TAG_NAME, "h1")
    INPUT_NAME = (By.ID, "form-field-name_free_audit")
    INPUT_EMAIL = (By.ID, "form-field-email")
    INPUT_COMPANY = (By.ID, "form-field-field_93bc8cc")
    SELECT_INDUSTRY = (By.ID, "form-field-field_21d99c4")
    INPUT_PHONE = (By.ID, "form-field-field_597bd0b")
    INPUT_MESSAGE = (By.ID, "form-field-message")

    def __init__(self, driver):
        super().__init__(driver)

    def is_demo_form_displayed(self) -> bool:
        """Verify key demo input fields are visible to prospective leads."""
        return (
            self.is_visible(self.INPUT_NAME)
            and self.is_visible(self.INPUT_EMAIL)
            and self.is_visible(self.INPUT_MESSAGE)
        )
