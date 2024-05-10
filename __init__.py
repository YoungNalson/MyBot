from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from undetected_chromedriver import Chrome as UndetectedChrome

from .config import BotOptions

class BrowserNotSupported(Exception):
    def __init__(self, message:str='The browser is not supported.', browser:str=None):
        self.browser = browser
        if browser == None:
            self.message = message
        else:
            self.message = message + ' ' + browser
        super().__init__(self.message)

class MyBot(BotOptions):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.chromium_executable = kwargs.get('chromium_executable', None)
        self.driver_executable = kwargs.get('driver_executable', None)
        self.driver = None

    @property
    def driver(self):
        return self._driver
        
    @driver.setter
    def driver(self, driver):
        if driver is None:
            
            if self._browser == 'firefox':
                self._driver = FirefoxDriver(options=self._options)
            
            elif self._browser == 'chrome':
                self._driver = ChromeDriver(options=self._options)
            
            elif self._browser == 'chromium':
                self._driver = ChromiumDriver(options=self._options)
            
            elif self._browser == 'undetected-chrome':
                self._driver = UndetectedChrome(
                    options=self._options,
                    browser_executable_path=self.chromium_executable,
                    driver_executable_path=self.driver_executable
                )
            
            elif self._browser == 'edge':
                self._driver = EdgeDriver(options=self._options)
        
        else:
            self._driver = driver(options=self._options)