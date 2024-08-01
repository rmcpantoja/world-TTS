import configparser
import os

class Translator:
    def __init__(self, base_language="en"):
        self.base_language = base_language
        self.configs = {}

    def load_language(self, language_name):
        if language_name not in self.configs:
            config = configparser.ConfigParser()
            langfile = os.path.join(os.getcwd(), "lng", f"{language_name}.lang")
            if language_name == self.base_language and os.path.exists(langfile):
                raise Exception("There must not be a language file with the base language.")
            if os.path.exists(langfile):
                config.read(langfile, encoding="utf-8")
                self.configs[language_name] = config
            else:
                print(f"Warning: as specified language file {langfile} doesn't exists, using the base language.")


    def translate(self, language_name, string):
        if language_name == self.base_language:
            return string
        elif language_name not in self.configs:
            self.load_language(language_name)
        config = self.configs[language_name]
        try:
            return config.get("Strings", string)
        except (configparser.NoOptionError, configparser.NoSectionError):
            if string:
                return string
            else:
                raise Exception("language engine error: This translation is corrupt!")