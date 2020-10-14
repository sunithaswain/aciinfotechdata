import os
from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
from couchbase.cluster import Bucket
from couchbase.n1ql import N1QLQuery
from app.utility.bootstrap import Configs


cf = Configs.config()
cluster = Cluster(cf.CB_URL)
authenticator = PasswordAuthenticator(cf.CB_APPS_USER, cf.CB_APPS_PASSWORD)
cluster.authenticate(authenticator)
bucket_name = cf.CB_INSTANCE
cb = cluster.open_bucket(bucket_name)
cb.remove('icncounter', quiet=True)
rv = cb.counter('icncounter', delta=1, initial=1)
