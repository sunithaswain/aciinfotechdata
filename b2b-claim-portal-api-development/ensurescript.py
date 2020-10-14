from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
from couchbase.cluster import Bucket
from couchbase.n1ql import N1QLQuery
import os
import configparser

config = configparser.SafeConfigParser(os.environ)
config.read('config.ini')
instance_type = config['INSTANCE_TYPE']
cluster = Cluster(config['CB_URL'])
authenticator = PasswordAuthenticator(
    config['CB_APPS_USER'], config['CB_APPS_PASSWORD'])
cluster.authenticate(authenticator)
cb = cluster.open_bucket(config[instance_type]['CB_INSTANCE'])
instance = config[instance_type]['CB_INSTANCE']


def ensureScript():

    indexes = [
        'CREATE INDEX `Index_type_claim` ON `' + instance + '`(`type`) WHERE(`type`="claim")', 'CREATE INDEX `Index_type_restricted_npis` ON `' + instance + '`(`type`) WHERE(`type`="restricted_npis")', 'CREATE INDEX `index_npi` ON `' + instance + '`(`type`) WHERE(`type`="prescriber")', 'CREATE INDEX `Index_type_user` ON `' + instance + '`(`type`) WHERE(`type`="user")']

    for index in indexes:
        try:
            query = N1QLQuery(index)
            cb.n1ql_query(query).execute()
        except Exception as e:
            print(e, '---')


ensureScript()
