import ssdb
from django.conf import settings

SSDB_HOST = getattr(settings, 'SSDB_HOST', 'localhost')
SSDB_PORT = getattr(settings, 'SSDB_PORT', 8888)
SSDB_AUTH = getattr(settings, 'SSDB_AUTH', '')


def get_ssdb_client():
    ssdb_client = ssdb.Client(SSDB_HOST, SSDB_PORT)
    if SSDB_AUTH:
        ssdb_client.auth(SSDB_AUTH)
    return ssdb_client


ssdb_client = get_ssdb_client()
