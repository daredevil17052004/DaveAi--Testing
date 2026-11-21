"""Page object for the DaveAI homepage."""

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    URL = "https://www.iamdave.ai/"

    HERO_HEADING = (By.TAG_NAME, "h1")
    HEADER_CONTAINER = (By.CSS_SELECTOR, ".elementor-location-header, header")
    BRAND_LOGO_IMG = (By.CSS_SELECTOR, "img[src*='DaveAI_Logo.svg'], img[src*='dave']")
    CTA_MORE_ABOUT_PLATFORM = (By.CSS_SELECTOR, "a.elementor-button[href*='/platform/']")
    CTA_SEE_ACTION = (By.CSS_SELECTOR, "a.elementor-button[href*='/book-demo/']")
    PARTNER_LOGOS = (By.CSS_SELECTOR, "img[src*='Google-Cloud'], img[src*='NvidiaInception'], img[src*='meta']")

    def load(self):
        self.open(self.URL)

    def get_hero_heading_text(self) -> str:
        return self.get_text(self.HERO_HEADING)

    def is_header_present(self) -> bool:
        return self.is_visible(self.HEADER_CONTAINER)

    def has_brand_logo_rendered(self) -> bool:
        try:
            logo = self.find(self.BRAND_LOGO_IMG)
            return logo is not None and "DaveAI" in (logo.get_attribute("src") or "")
        except WebDriverException:
            return False

    def click_more_about_platform(self):
        self.click(self.CTA_MORE_ABOUT_PLATFORM)

    def click_book_demo_cta(self):
        self.click(self.CTA_SEE_ACTION)
