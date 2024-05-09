import sys
from typing import Union

from .config import BotOptions
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver

if sys.version_info.minor < 12:
    from undetected_chromedriver import Chrome as UndetectedChrome


class BrowserNotSupported(Exception):
    def __init__(self, message:str='The browser is not supported.', browser:str=None):
        self.browser = browser
        if browser == None:
            self.message = message
        else:
            self.message = message + ' ' + browser
        super().__init__(self.message)

class MyBot(BotOptions):
    def __init__(
                self,
                browser:str,
                download_folder:str = None,
                profile:str = None,
                extensions:list = [],
                num_bot:int = None,
                options: ArgOptions = None,
                chromium_executable:str = None,
                driver_executable:str = None,
                copy_profile: bool = False
            ) -> None:
        super().__init__(
            browser,
            download_folder,
            profile,
            extensions,
            num_bot,
            chromium_executable,
            options,
            copy_profile
        )
        self.chromium_executable = chromium_executable
        self.driver_executable = driver_executable
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