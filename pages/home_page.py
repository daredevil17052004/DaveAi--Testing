"""
Home Page Object for https://www.iamdave.ai/
Encapsulates homepage locators, branding verification, and navigation actions.
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://www.iamdave.ai/"

    # Locators
    HERO_HEADING = (By.TAG_NAME, "h1")
    HEADER_CONTAINER = (By.CSS_SELECTOR, ".elementor-location-header, header")
    BRAND_LOGO_IMG = (By.CSS_SELECTOR, "img[src*='DaveAI_Logo.svg'], img[src*='dave']")
    
    # CTA Buttons
    CTA_MORE_ABOUT_PLATFORM = (By.CSS_SELECTOR, "a.elementor-button[href*='/platform/']")
    CTA_SEE_ACTION = (By.CSS_SELECTOR, "a.elementor-button[href*='/book-demo/']")
    PARTNER_LOGOS = (By.CSS_SELECTOR, "img[src*='Google-Cloud'], img[src*='NvidiaInception'], img[src*='meta']")

    def __init__(self, driver):
        super().__init__(driver)

    def load(self):
        """Navigate directly to the DaveAI homepage."""
        self.open(self.URL)

    def get_hero_heading_text(self) -> str:
        """Fetch the text of the primary H1 headline."""
        return self.get_text(self.HERO_HEADING)

    def is_header_present(self) -> bool:
        """Verify the site header container is rendered."""
        return self.is_visible(self.HEADER_CONTAINER)

    def has_brand_logo_rendered(self) -> bool:
        """Verify that DaveAI brand logo element is present in DOM."""
        try:
            logo = self.find(self.BRAND_LOGO_IMG)
            return logo is not None and "DaveAI" in (logo.get_attribute("src") or "")
        except Exception:
            return False

    def click_more_about_platform(self):
        """Click the 'MORE ABOUT OUR PLATFORM' button to navigate to Platform page."""
        self.click(self.CTA_MORE_ABOUT_PLATFORM)

    def click_book_demo_cta(self):
        """Click high-conversion CTA button to navigate to Demo booking."""
        self.click(self.CTA_SEE_ACTION)
