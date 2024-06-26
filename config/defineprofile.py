import contextlib
import os
import shutil
import time


class ProfileNotCreated(Exception):
    def __init__(self, message="The profile folder was not created"):
        self.message = message
        super().__init__(self.message)

class FolderDoesNotExist(Exception):
    def __init__(self, message="The folder doesn't exist"):
        self.message = message
        super().__init__(self.message)


def check_folder(folder_path:str, timeout_seconds=60):
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            if os.path.exists(folder_path):
                return True
            else:
                time.sleep(1)
        
        raise FolderDoesNotExist

class DefineProfile:
    def __init__(self, **kwargs) -> None:
        self.copy_profile = kwargs.get('copy_profile', False)
        self.num_bot = kwargs.get('num_bot', 0)
        self.profile = kwargs.get('profile', None)


    @property
    def num_bot(self):
        return self._num_bot
    
    @num_bot.setter
    def num_bot(self, num_bot):
        if num_bot is None:
            num_bot = 0
        if num_bot < 0:
            num_bot /= -1
        self._num_bot = num_bot


    @property
    def profile(self):
        return self._profile
    
    @profile.setter
    def profile(self, profile):
        if profile is None or self.copy_profile is True:
            self._profile = self.define_profile(profile)
        else:
            self._profile = profile


    def define_profile(self, profile) -> str:
        current_directory = os.getcwd()
        profile_directory = fr'{current_directory}\bots\bot{self._num_bot}'

        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(profile_directory)

        if self.copy_profile is True:
            shutil.copytree(profile, profile_directory)
        else:
            os.makedirs(profile_directory)
        
        try: 
            check_folder(profile_directory)
        except FolderDoesNotExist:
            raise ProfileNotCreated
        
        return profile_directory