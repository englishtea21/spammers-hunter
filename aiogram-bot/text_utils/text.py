from os import getenv
import yaml

# implements localization

# load languages dict
with open(
    f"{getenv('LANGUAGES_DICT_PATH')}",
    "r",
    encoding=f"{getenv('TEXT_TEMPLATES_FILE_ENCODING')}",
) as f:
    languages_dict = yaml.safe_load(f.read())["LANGUAGES_DICT"]

text_templates = None


def load_text_templates(lang_code):
    if lang_code is None:
        lang_code = "ru"
    with open(
        f"{getenv('LANGUAGES_DIR_PATH')}/{lang_code}.yaml",
        "r",
        encoding=f"{getenv('TEXT_TEMPLATES_FILE_ENCODING')}",
    ) as f:
        global text_templates
        text_templates = yaml.safe_load(f.read())


# load default language
if text_templates is None:
    load_text_templates(getenv("DEFAULT_LANGUAGE"))
