# coding: utf-8

import importlib
from starmachine.settings.profile_type import ProfileType

version = '${version}'
git_version = '${git_version}'
release_time = '${release_time}'

def init(profile, log_dir='/tmp', port=None):
    global_settings = globals()
    global_settings['LOG_DIR'] = log_dir
    if port:
        global_settings['PORT'] = port

    Profile = ProfileType(profile)
    global_settings['Profile'] = Profile
    settings_mod = importlib.import_module('starmachine.settings.%s' % Profile.current_name)

    for setting in dir(settings_mod):
        if setting == setting.upper():
            setting_value = getattr(settings_mod, setting)
            global_settings[setting] = setting_value

init('product')