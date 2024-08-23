from os import getenv, path
import yaml

# implements localization

current_dir = path.dirname(__file__)

# load languages dict
languages_dict_path = path.join(current_dir, "locales", "languages_dict.yaml")
with open(
    languages_dict_path,
    "r",
    encoding=f"{getenv('TEXT_TEMPLATES_FILE_ENCODING')}",
) as f:
    languages_dict = yaml.safe_load(f.read())["LANGUAGES_DICT"]

text_templates = None


def load_text_templates(lang_code):
    if lang_code is None:
        lang_code = "ru"

    lang_file = f"{lang_code}.yaml"

    curr_language_path = path.join(current_dir, "locales", "languages", "ru.yaml")

    with open(
        curr_language_path,
        "r",
        encoding=f"{getenv('TEXT_TEMPLATES_FILE_ENCODING')}",
    ) as f:
        global text_templates
        text_templates = yaml.safe_load(f.read())


# load default language
if text_templates is None:
    load_text_templates(getenv("DEFAULT_LANGUAGE"))
