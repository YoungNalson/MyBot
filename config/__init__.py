import os
import sys
import random
from typing import Union

from .defineprofile import DefineProfile
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

if sys.version_info.minor < 12:
    from undetected_chromedriver import ChromeOptions as UndetectedOptions


class BrowserNotSupported(Exception):
    def __init__(self, message:str='The browser is not supported.', browser:str=None):
        self.browser = browser
        if browser == None:
            self.message = message
        else:
            self.message = message + ' ' + browser
        super().__init__(self.message)

class ChromiumPathNotInformed(Exception):
    def __init__(self, message:str='The Chromium executable must be informed.'):
        self.message = message
        super().__init__(self.message)

class BotOptions(DefineProfile):
    def __init__(
                self,
                browser:str,
                download_folder:str,
                profile:str,
                extensions:list,
                num_bot:int,
                chromium_executable:str,
                options: ArgOptions,
                copy_profile:bool
            ) -> None:
        super().__init__(profile, num_bot, copy_profile)
        self.browser = browser
        self.download_folder = download_folder
        self.extensions = extensions
        self.chromium_executable = chromium_executable
        self.options = options


    @property
    def browser(self):
        return self._browser
    
    @browser.setter
    def browser(self, browser):
        if browser not in ['firefox', 'chrome', 'chromium', 'undetected-chrome', 'edge']:
            raise BrowserNotSupported(browser=browser)
        self._browser = browser.lower()
    

    @property
    def download_folder(self):
        return self._download_folder
    
    @download_folder.setter
    def download_folder(self, download_folder):
        if download_folder is None:
            self._download_folder = fr'{self._profile}\.downloads'
        else:
            self._download_folder = download_folder
        try:
            os.makedirs(self._download_folder)
        except FileExistsError:
            pass


    @property
    def chromium_executable(self):
        return self._chromium_executable

    @chromium_executable.setter
    def chromium_executable(self, chromium_executable):
        if self._browser == 'chromium' and chromium_executable == None:
            raise ChromiumPathNotInformed
        self._chromium_executable = chromium_executable


    def different_browser(self, browser):
        return True if browser.lower() not in ['firefox', 'chrome', 'chromium' 'edge'] else False

    def define_options(
            self,
            browser:str,
            extensions:str=None,
            download_folder:str=None,
            profile:str=None,
            chromium_executable:str=None
        ) -> ArgOptions:

        userAgent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1{random.randint(10, 20)}.0.0.0 Safari/537.36'
        args = [f'--user-agent={userAgent}',
                f'--user-data-dir={profile}',
                '--no-sandbox',
                '--mute-audio',
                '--enable-webgl',
                '--no-first-run',
                '--lang=en-US,en;q=0.9',
                '--password-store=basic',
                '--window-size=1920,1080',
                '--no-default-browser-check',
                '--ignore-certificate-errors',
                '--allow-running-insecure-content',
                '--disable-gpu',
                '--disable-infobars',
                '--disable-dev-shm-usage',]
        
        prefs = {
                "pdfjs.disabled": True,
                "browser.download.folderList": 2,
                "download.prompt_for_download": False,
                "browser.download.panel.shown": False,
                "webdriver_enable_native_events": False,
                "browser.download.dir": download_folder,
                # "plugins.always_open_pdf_externally": True,
                "browser.helperApps.alwaysAsk.force": False,
                "browser.download.manager.useWindow": False,
                "download.default_directory": download_folder,
                "browser.download.manager.showWhenStarting": False,
                "savefile.default_directory": fr"{download_folder}",
                "browser.helperApps.neverAsk.openFile": "application/pdf;",
                "browser.helperApps.neverAsk.saveToDisk": "application/pdf;",
                'printing.print_preview_sticky_settings.appState': '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}'}
        
        load_extensions = '--load-extension='
        
        if browser.lower() == 'firefox':
            options = FirefoxOptions()
            for key, value in prefs.items():
                options.set_preference(key, value)

        elif browser.lower() == 'chrome' or browser.lower() == 'chromium' or browser.lower() == 'undetected-chrome':        
            if browser.lower() == 'chrome':
                options = ChromeOptions()
            elif browser.lower() == 'chromium':
                options = ChromiumOptions()
                options.binary_location = chromium_executable
            elif browser.lower() == 'undetected-chrome':
                options = UndetectedOptions()

            args.extend(
                ['--no-xshm',
                '--no-zygote',
                '--kiosk-printing',
                '--enable-low-end-device-mode',
                '--disable-logging', ######
                '--disable-breakpad',
                '--disable-canvas-aa',
                '--disable-gpu-sandbox',
                '--disable-web-security',
                '--disable-notifications', ######
                '--disable-popup-blocking', ######
                '--disable-2d-canvas-clip-aa',
                '--disable-software-rasterizer',
                '--disable-gl-drawing-for-tests',
                '--disable-renderer-backgrounding',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process']
            )
            
            prefs.update({
                'plugins.plugins_disabled': ['Chrome PDF Viewer', 'Adobe Acrobat'],
                "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream;application/xml;",
            })

            options.add_experimental_option('prefs', prefs)
        
            for extension in extensions:
                load_extensions += extension + ','
        
        elif browser.lower() == 'edge':
            options = EdgeOptions()
            for key, value in prefs.items():
                options.set_capability(key, value)
        
        elif self.different_browser(browser):
            raise BrowserNotSupported
        
        for arg in args:
            options.add_argument(arg)

        if browser.lower() in ['edge', 'chrome', 'chromium', 'undetected-chrome']:
            for extension in extensions:
                if extension.endswith('.crx'):
                    options.add_extension(extension)
                else:
                    load_extensions += extension + ','
            if extensions:
                options.add_argument(load_extensions[:-1])

        return options
    
    
    @property
    def options(self):
        return self._options
    
    @options.setter
    def options(self, options):
        if options is None:
            self._options = self.define_options(
                    browser=self._browser,
                    extensions=self.extensions,
                    download_folder=self._download_folder,
                    profile=self._profile,
                    chromium_executable=self._chromium_executable
                )
        else:
            self._options = options