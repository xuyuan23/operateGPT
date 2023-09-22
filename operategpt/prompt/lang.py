from enum import Enum


class Language(Enum):
    ENGLISH = "en"
    CHINESE = "zh"

    @classmethod
    def get_all_langs(cls):
        return [language.value for language in cls]
