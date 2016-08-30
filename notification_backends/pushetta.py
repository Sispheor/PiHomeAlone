from __future__ import absolute_import
from pushetta import Pushetta


def notify(message, api_key=None, channel_name=None):
    """
    Send a push message via Pushetta API
    :param message: Message to send
    :param api_key: The Pushetta service secret token
    :param channel_name: Pushetta channel name
    :return:
    """
    if api_key is None:
        raise NotImplementedError("Pushetta plugin needs api_key")
    if channel_name is None:
        raise NotImplementedError("Pushetta plugin needs channel_name")

    p = Pushetta(api_key)
    p.pushMessage(channel_name, message)
