import json
import requests
from cStringIO import StringIO

import requests_cache


def query_registry(postcode, street, number):
    ql_file = open('sparql.post','r')
    ql = ql_file.read().format(postcode,street,number)
    res = requests.post('http://landregistry.data.gov.uk/app/root/qonsole/query',data={
        'output':'json',
        'url':'/landregistry/query',
        'q':ql})
    if res.status_code == 200:
        ret = StringIO(res.content)
        parsed = json.loads(ret.read())
        ret = json.loads(parsed['result'])['results']['bindings']
    data = list()
    for entry in ret:
        ret={'date':'','amount':''}
        ret['date'] = entry['date']['value']
        ret['amount'] = entry['amount']['value']
        data.append(ret)
    return data


requests_cache.install_cache(
        expire_after=60*60,
        allowable_methods=('POST',))
