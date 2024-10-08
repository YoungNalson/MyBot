import os
import platform
from contextlib import suppress

from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from undetected_chromedriver import ChromeOptions as UndetectedOptions

from .defineprofile import DefineProfile


class BrowserNotSupported(Exception):
    def __init__(self, message:str='The browser is not supported.', browser:str=None):
        self.browser = browser
        if browser is None:
            self.message = message
        else:
            self.message = message + ' ' + browser
        super().__init__(self.message)

class ChromiumPathNotInformed(Exception):
    def __init__(self, message:str='The Chromium executable must be informed.'):
        self.message = message
        super().__init__(self.message)

class BotOptions(DefineProfile):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.op_sys = platform.system()
        self.browser = kwargs.get('browser', 'chrome')
        self.userAgent = UserAgent(browsers=[self._browser if self._browser != 'undetected-chrome' else 'chrome'],
                                   os=[self._op_sys],
                                   min_version=self._min_version)
        
        # Resources for Firefox:
        # https://wiki.mozilla.org/Firefox/CommandLineOptions
        # https://kb.mozillazine.org/About:config_entries
        # https://kb.mozillazine.org/Category:Preferences
        
        # Resources for Chrome:
        # https://src.chromium.org/viewvc/chrome/trunk/src/chrome/common/chrome_switches.cc?view=markup
        
        self.download_folder = kwargs.get('download_folder', None)
        self.args = kwargs.get('args', [])
        self.prefs = kwargs.get('prefs', {})
        
        self.extensions = kwargs.get('extensions', [])
        self.browser_executable = kwargs.get('browser_executable', None)
        self.options = kwargs.get('options', None)


    @property
    def op_sys(self):
        return self._op_sys
    
    @op_sys.setter
    def op_sys(self, op_sys):
        if op_sys is None or op_sys.lower() not in ['windows',
                                                    'linux',
                                                    'darwin']:
            op_sys = 'windows'
        if op_sys.lower() == 'darwin':
            op_sys = 'macos'
        self._op_sys = op_sys.lower()


    @property
    def browser(self):
        return self._browser
    
    @browser.setter
    def browser(self, browser):
        if browser.lower() not in ['firefox', 
                                   'chrome', 
                                   'chromium', 
                                   'undetected-chrome', 
                                   'edge']:
            raise BrowserNotSupported(browser=browser)
        
        self._min_version = 110.0
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
        with suppress(FileExistsError):
            os.makedirs(self._download_folder)


    @property
    def browser_executable(self):
        return self._browser_executable

    @browser_executable.setter
    def browser_executable(self, browser_executable):
        if browser_executable is None:
            browser_executable = ""
        self._browser_executable = browser_executable

    
    @property
    def options(self):
        return self._options
    
    @options.setter
    def options(self, options):
        if options is None:
            self._options = self.define_options()
        else:
            self._options = options
    

    @property
    def args(self):
        return self._args
    
    @args.setter
    def args(self, args):
        if not isinstance(args, list):
            args = [args]
        
        # TODO implement firefox args
        if self._browser.lower() == 'firefox' and not args:
            args = ['-profile',
                    self._profile,
                    # '-headless',
                    '-preferences',
                    '-proxy-server="direct://"',
                    '-proxy-bypass-list=*',]
        elif not args:
            args = ['--user-agent=%s' % self.userAgent.random,
                    '--user-data-dir=%s' % self._profile,
                    # '--headless',
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
        # TODO implement firefox args
        
        self._args = args
    

    @property
    def prefs(self):
        return self._prefs
    
    @prefs.setter
    def prefs(self, prefs):
        if not isinstance(prefs, dict):
            prefs = {}

        if self._browser.lower() == 'firefox' and not prefs:
            prefs = {"browser.download.folderList": 2,
                     "browser.download.dir": self._download_folder,
                     "browser.download.manager.showWhenStarting": False,
                     "browser.helperApps.neverAsk.openFile": "application/pdf",
                     "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/octet-stream,application/xml,",
                     "browser.tabs.warnOnClose": False,
                     "browser.tabs.warnOnCloseOther": False,
                     "pdfjs.disabled": True,}
        elif self._browser.lower() in ['chrome', 'chromium', 'undetected-chrome'] and not prefs:
            prefs = {'plugins.plugins_disabled': ['Chrome PDF Viewer', 'Adobe Acrobat'],
                     "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream;application/xml;",
                     "pdfjs.disabled": True,
                     "browser.download.folderList": 2,
                     "download.prompt_for_download": False,
                     "browser.download.panel.shown": False,
                     "webdriver_enable_native_events": False,
                     "plugins.always_open_pdf_externally": True,
                     "browser.helperApps.alwaysAsk.force": False,
                     "browser.download.manager.useWindow": False,
                     "browser.download.dir": self._download_folder,
                     "download.default_directory": self._download_folder,
                     "browser.download.manager.showWhenStarting": False,
                     "savefile.default_directory": "%s" % self._download_folder,
                     "browser.helperApps.neverAsk.openFile": "application/pdf;",
                     "browser.helperApps.neverAsk.saveToDisk": "application/pdf;",
                     'printing.print_preview_sticky_settings.appState': '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}'}
        # TODO implement edge prefs
        

        self._prefs = prefs


    def define_options(self) -> ArgOptions:
        load_extensions = '--load-extension='
        
        if self._browser.lower() == 'firefox':
            options = FirefoxOptions()
            for key, value in self._prefs.items():
                options.set_preference(key, value)

        elif self._browser.lower() in ['chrome', 
                                       'chromium', 
                                       'undetected-chrome']:
            if self._browser.lower() == 'chrome':
                options = ChromeOptions()
            elif self._browser.lower() == 'chromium':
                options = ChromiumOptions()
            else:
                options = UndetectedOptions()

            options.add_experimental_option('prefs', self._prefs)
        
        elif self._browser.lower() == 'edge':
            options = EdgeOptions()
            for key, value in self._prefs.items():
                options.set_capability(key, value)
        
        for arg in self._args:
            options.add_argument(arg)

        if self._browser.lower() in ['edge', 
                                     'chrome', 
                                     'chromium', 
                                     'undetected-chrome']:
            for extension in self.extensions:
                if extension.endswith('.crx'):
                    options.add_extension(extension)
                else:
                    load_extensions += extension + ','
            if load_extensions.split('=')[1]:
                options.add_argument(load_extensions[:-1])

        options.binary_location = self._browser_executable
        return options