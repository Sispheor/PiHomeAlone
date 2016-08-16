import yaml
import os


def get_settings():
    """
    Load settings file
    :return:
    """
    # Load settings. Will be used to convert slot number into GPIO pin number
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(__location__, "../settings.yml")) as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg
