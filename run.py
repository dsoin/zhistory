import zoopla
import requests
from cStringIO import StringIO
import json
import elasticsearch
import hashlib

import entry_utils




es = elasticsearch.Elasticsearch(hosts=['192.168.0.10'])

#if es.indices.exists(index="zoopla"):
#    es.indices.delete(index="zoopla")

api = zoopla.api(version=1, api_key='h8w8e3vza6wprx4qeeyvhdd3')
listings = api.property_listings(
        area='KT7',
        max_results=None,
        listing_status='sale')

bulk_data=[]
for listing in listings:
    es_entry=entry_utils.fill_esentry_zoopla(listing)
    entry_utils.update_esentry_geo(es_entry)
    entry_utils.update_appeareance(es_entry)
    print(es_entry)

    es.create(index='zoopla',doc_type='z_data', body=es_entry)