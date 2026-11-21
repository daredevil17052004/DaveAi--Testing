"""Base page object providing common WebDriver interactions."""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
        self.driver.get(url)

    def get_title(self) -> str:
        return self.driver.title

    def get_current_url(self) -> str:
        return self.driver.current_url

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def scroll_into_view(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
            element,
        )

    def click(self, locator):
        element = self.find(locator)
        self.scroll_into_view(element)
        self.wait.until(EC.visibility_of(element))
        try:
            clickable = self.wait.until(EC.element_to_be_clickable(locator))
            clickable.click()
        except (ElementClickInterceptedException, TimeoutException):
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator, text: str, clear_first: bool = True):
        element = self.find_visible(locator)
        self.scroll_into_view(element)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator) -> str:
        return self.find_visible(locator).text.strip()

    def is_visible(self, locator) -> bool:
        try:
            return self.find_visible(locator).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_url_contains(self, fragment: str) -> bool:
        return self.wait.until(EC.url_contains(fragment))
