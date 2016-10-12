import zoopla
import requests
from cStringIO import StringIO
import json
import elasticsearch
from elasticsearch import helpers
import hashlib
import entry_utils

index="zoopla"
postcode="KT7"
es = elasticsearch.Elasticsearch(hosts=['localhost'])

def get_last_set(postcode):
        ret = list()
        res= es.search(index=index,body={"query":
                                           {"match":
                                                {"fetch_query":postcode}
                                            },
                                            "sort":[{"fetched_time":"desc"}]})
        if res['hits']['total']<1:
            return ret
        first_date = res['hits']['hits'][0]['_source']['fetched_time']
        res = es.search(index=index,body={"size":"10000","query":{"term":{"fetched_time":first_date}}})
        for hit in res['hits']['hits']:
            ret.append(hit['_source'])
        return ret



def get_current(postcode):
    api = zoopla.api(version=1, api_key='h8w8e3vza6wprx4qeeyvhdd3')
    ret = list()
    listings = api.property_listings(
        area=postcode,
        max_results=None,
        listing_status='sale')
    for listing in listings:
        es_entry = entry_utils.fill_esentry_zoopla(listing)
        es_entry['fetch_query'] = postcode
        entry_utils.update_esentry_geo(es_entry)
        ret.append(es_entry)
    return ret

        #es.create(index=index, doc_type='z_data', body=es_entry)

def index_set(set):
    actions = list()
    for entry in set:
        action = {"_index":index,"_type":"z_data","_source":entry}
        actions.append(action)
    if len(actions)>0:
        helpers.bulk(es,actions)

#if es.indices.exists(index="zoopla"):
#    es.indices.delete(index="zoopla")


last_set = get_last_set("KT7")
print(len(last_set))
current_set = get_current(postcode)
entry_utils.update_appeareance(last_set,current_set)
print(current_set)
index_set(current_set)
