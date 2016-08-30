import yaml
import os
import importlib


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


def get_argument_backends(backend_name):
    """
    Get argument dict from settings file for the corresponding backend name
    :param backend_name: Name of the backend. Must be present in settings file
    :return: Return a dict of argument from the settings file
    """
    config = get_settings()
    try:
        argv_backends = config[backend_name]

    except KeyError:
        raise NotImplementedError("No config for backend %s " % backend_name)

    return argv_backends


def notify(message):
    """
    Send the message to each configured backend
    :param message: Message to send via backend
    :return:
    """
    # get config
    cfg = get_settings()
    backends = cfg["backends"]

    # for each backend we send the message
    for backend in backends:
        # get the plugin
        mod = importlib.import_module("notification_backends." + backend)
        # get argument used for the plugin
        arguments_backends = get_argument_backends(backend)
        # send the message via the plugin
        mod.notify(message, **arguments_backends)





