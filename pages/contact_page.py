"""
Contact Us Page Object for https://www.iamdave.ai/contact-us/
Encapsulates form inputs, validation checks, and user interaction automation.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class ContactPage(BasePage):
    URL = "https://www.iamdave.ai/contact-us/"

    # Locators
    PAGE_HEADING = (By.TAG_NAME, "h1")
    CONTACT_FORM = (By.ID, "contact_us_form")
    INPUT_NAME = (By.ID, "form-field-name")
    INPUT_EMAIL = (By.ID, "form-field-email")
    INPUT_COMPANY = (By.ID, "form-field-field_93bc8cc")
    INPUT_PHONE = (By.ID, "form-field-field_597bd0b")
    INPUT_MESSAGE = (By.ID, "form-field-message")
    BTN_SUBMIT = (By.CSS_SELECTOR, "form#contact_us_form button[type='submit']")

    def __init__(self, driver):
        super().__init__(driver)

    def load(self):
        """Navigate to Contact Us page."""
        self.open(self.URL)

    def fill_contact_form(self, name: str, email: str, company: str, phone: str, message: str):
        """Fill all visible contact form input fields."""
        self.type_text(self.INPUT_NAME, name)
        self.type_text(self.INPUT_EMAIL, email)
        self.type_text(self.INPUT_COMPANY, company)
        self.type_text(self.INPUT_PHONE, phone)
        self.type_text(self.INPUT_MESSAGE, message)

    def get_input_values(self) -> dict:
        """Return the current values typed into the contact fields."""
        return {
            "name": self.find_visible(self.INPUT_NAME).get_attribute("value"),
            "email": self.find_visible(self.INPUT_EMAIL).get_attribute("value"),
            "company": self.find_visible(self.INPUT_COMPANY).get_attribute("value"),
            "phone": self.find_visible(self.INPUT_PHONE).get_attribute("value"),
            "message": self.find_visible(self.INPUT_MESSAGE).get_attribute("value"),
        }

    def is_email_valid(self) -> bool:
        """Query HTML5 constraint validation for the email field."""
        email_elem = self.find_visible(self.INPUT_EMAIL)
        return self.driver.execute_script("return arguments[0].checkValidity();", email_elem)

    def get_email_validation_message(self) -> str:
        """Fetch the browser native validation message when invalid data is input."""
        email_elem = self.find_visible(self.INPUT_EMAIL)
        return self.driver.execute_script("return arguments[0].validationMessage;", email_elem)
