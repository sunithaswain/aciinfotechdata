import requests


def singleton(cls):
    instance = {}

    def singleton_inner(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)

        return instance[cls]
    return singleton_inner


@singleton
class VaultSession:
    def __init__(self):
        self.session = requests.Session()
