"""
Base Page Object providing reusable WebDriver interactions with explicit waits,
safe clicks, text retrieval, and failure diagnostics.
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


class BasePage:
    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
        """Navigate to the specified URL."""
        self.driver.get(url)

    def get_title(self) -> str:
        """Return the current page title."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Return the current browser URL."""
        return self.driver.current_url

    def find(self, locator):
        """Find an element after waiting for its presence in the DOM."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        """Wait until an element is visible on the page."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def scroll_into_view(self, element):
        """Scroll an element into the center of the viewport."""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element)

    def click(self, locator):
        """
        Robust click handler:
        Waits for presence, scrolls into view, and executes a click.
        Falls back to JavaScript click if standard click is intercepted by overlays.
        """
        element = self.find(locator)
        self.scroll_into_view(element)
        self.wait.until(EC.visibility_of(element))
        try:
            clickable_element = self.wait.until(EC.element_to_be_clickable(locator))
            clickable_element.click()
        except (ElementClickInterceptedException, TimeoutException):
            # Fallback to JavaScript click for sticky headers / animations
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator, text: str, clear_first: bool = True):
        """Type text into an input field with optional clearing."""
        element = self.find_visible(locator)
        self.scroll_into_view(element)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator) -> str:
        """Retrieve visible inner text of an element."""
        return self.find_visible(locator).text.strip()

    def is_visible(self, locator) -> bool:
        """Check if an element is visible without throwing TimeoutException."""
        try:
            return self.find_visible(locator).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_url_contains(self, fragment: str) -> bool:
        """Wait for the URL to contain a specific string fragment."""
        return self.wait.until(EC.url_contains(fragment))
