# from ..client import Client


class ScribeClient(object):
    def __init__(self):
        self.messages = []

    def Log(self, messages):
        self.messages.append(messages)


class DummyClient(object):
    _client = ScribeClient()

    @classmethod
    def configure(cls, settings, prefix):
        pass

    @classmethod
    def get_connection(cls):
        return cls._client

    @classmethod
    def log(cls, trace):
        return cls._client.Log(trace)

    @classmethod
    def reset(cls):
        cls._client = ScribeClient()


def dummy_log(trace):
    DummyClient.log(trace)
