import sys

import elasticsearch
from elasticsearch import helpers

import entry_utils
import zoopla
import zoopla

index = "zoopla"
postcode = "KT6"

es = elasticsearch.Elasticsearch(hosts=['192.168.0.23'])

# add line 
# add another line 

def get_last_set(post_code):
    ret = list()
    res = es.search(index=index, body={"query":
                                           {"match":
                                                {"fetch_query": post_code}
                                            },
                                       "sort": [{"fetched_time": "desc"}]})
    if res['hits']['total'] < 1:
        return ret
    first_date = res['hits']['hits'][0]['_source']['fetched_time']
    res = es.search(index=index, body={"size": "10000", "query": {"bool":
        {"must": [
            {"term": {"fetched_time": first_date}},
            {"match": {"fetch_query": post_code}}],
            "must_not":
                {"term": {"status": "removed"}}
        }
    }})
    for hit in res['hits']['hits']:
        ret.append(hit['_source'])
    return ret


def check_reappeared(r_set):
    for entry in r_set:
        if "added" in entry['status']:
            res = es.search(index=index, body={"query": {"term": {"similarity_hash": entry['similarity_hash']}}})
            print("Checking reappearance for {}:{}".format(entry['address'], res['hits']['total']))
            if res['hits']['total'] > 0:
                entry['status'] = "reappeared"


def get_current(post_code):
    api = zoopla.api(version=1, api_key='h8w8e3vza6wprx4qeeyvhdd3', cache_seconds=0)
    ret = list()
    listings = api.property_listings(
        area=post_code,
        max_results=None,
        listing_status='sale')
    for listing in listings:
        es_entry = entry_utils.fill_esentry_zoopla(listing)
        es_entry['fetch_query'] = post_code
        entry_utils.update_esentry_geo(es_entry)
        ret.append(es_entry)
    return ret

    # es.create(index=index, doc_type='z_data', body=es_entry)

def get_cached_addr(geo_loc):
    res = es.search(index=zoopla,body={})

def index_set(i_set):
    actions = list()
    for entry in i_set:
        action = {"_index": index, "_type": "z_data", "_source": entry}
        actions.append(action)
    if len(actions) > 0:
        helpers.bulk(es, actions)


# if es.indices.exists(index="zoopla"):
#    es.indices.delete(index="zoopla")
if len(sys.argv) > 1:
    postcode = sys.argv[1]
print("Running for: {}".format(postcode))
print("Getting previous results from ES")
last_set = get_last_set(postcode)
print("Getting current results from Zoopla")
current_set = get_current(postcode)
#current_set = entry_utils.remove_duplicates(current_set)
print("Processing {} results".format(len(current_set)))
# current_set.remove(current_set[0])
print("Getting geo data from Google")
entry_utils.update_appeareance(last_set, current_set)
check_reappeared(current_set)
index_set(current_set)
entry_utils.print_totals(current_set)
