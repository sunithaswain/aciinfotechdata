import configparser
import os
import platform
from couchbase import LOCKMODE_WAIT
from couchbase.cluster import Cluster, PasswordAuthenticator

DEFAULT_APP_INSTANCE = "DEV"


class Config(object):
    def __init__(self, app_instance):
        self.app_instance = app_instance
        self.cb_conn = None

    @property
    def cb(self):
        if self.cb_conn is None:
            self.cb_conn = self._get_cb_connection()
        return self.cb_conn

    def _get_cb_connection(self):
        # instance_type = self.config['GLOBAL']['INSTANCE_TYPE']
        cluster = Cluster(self.CB_URL)
        authenticator = PasswordAuthenticator(
            self.CB_APPS_USER, self.CB_APPS_PASSWORD)
        cluster.authenticate(authenticator)
        return cluster.open_bucket(self.CB_INSTANCE, lockmode=LOCKMODE_WAIT)



class EnvConfig(Config):
    def __init__(self, app_instance):
        super().__init__(app_instance)

    def __getattr__(self, item):
        """
        :param item: eg tv_uri/TV_URI (item can be queried as config.tv_uri)
        get item from env and return
        The method is used when asked object is not
        present as instance attribute
        """
        return os.environ[item.upper()]


class DefaultConfig(Config):
    def __init__(self, app_instance):
        self.config = configparser.ConfigParser(os.environ)
        if platform.system() == 'Darwin':
            self.config.read(f"{os.getcwd()}/config.ini")
        elif platform.system() == 'linux':
            self.config.read("../../config.ini")
        else:
            self.config.read('config.ini')
        super().__init__(app_instance)

    def __getattr__(self, item):
        return self.config[self.app_instance][item.upper()]


def Configuration():
    instance_type = os.environ.get("INSTANCE_TYPE")
    return EnvConfig(instance_type) if instance_type else DefaultConfig(DEFAULT_APP_INSTANCE)
