# coding: utf-8

class ProfileType(object):
    LOCAL = 1
    DEVELOP = 2
    PRODUCT = 3

    _MAPPING = {
        'local': LOCAL,
        'develop': DEVELOP,
        'product': PRODUCT
    }

    def __init__(self, profile=None):
        if profile in ProfileType._MAPPING:
            self._current = ProfileType._MAPPING[profile]
        else:
            self._current = ProfileType.LOCAL

    @property
    def current(self):
        return self._current

    @property
    def current_name(self):
        for key, value in self._MAPPING.items():
            if value == self._current:
                return key

    @property
    def is_local(self):
        return self._current == ProfileType.LOCAL

    @property
    def is_develop(self):
        return self._current == ProfileType.DEVELOP

    @property
    def is_product(self):
        return self._current == ProfileType.PRODUCT