import elasticsearch
from elasticsearch import helpers

es = elasticsearch.Elasticsearch(hosts=['192.168.0.23'])

def get_saved_geo(lat, lon):
    geo_exist = es.search(index="zoopla", body={"query": {
        "bool": {
            "must": [
                {"term": {"geo_loc.lon": lon }},
                {"term": {"geo_loc.lat": lat }}
            ],
            "must_not": {"term": {"postcode": ""}}
        }}})
    return geo_exist['hits']['hits']


def copy_geo_data(origin_entry, dest_entry):
    dest_entry['postcode'] = origin_entry['postcode']
    dest_entry['number'] = origin_entry['number']
    dest_entry['street'] = origin_entry['street']
    dest_entry['town'] = origin_entry['town']
    dest_entry['county'] = origin_entry['county']
    dest_entry['borough'] = origin_entry['borough']
    dest_entry['address'] = "{} {} {} {} {} {}".format(origin_entry['number'],
                                                       origin_entry["street"],
                                                       origin_entry["town"],
                                                       origin_entry["postcode"],
                                                       origin_entry["borough"],
                                                       origin_entry["county"])


res = es.search(index="zoopla", body={
    "size": "10000",
    "query": {
        "match": {
            "postcode": ""
        }
    }
})
print res['hits']['total']
for entry in res['hits']['hits']:
    print entry
    hit = get_saved_geo(entry['_source']['geo_loc']['lat'],entry['_source']['geo_loc']['lon'])
    if hit:
        addr = hit[0]['_source']
        entry_to_update = {}
        copy_geo_data(addr,entry_to_update)
        es.delete(index="zoopla",doc_type="z_data",id=entry['_id'])
        es.index(index="zoopla",doc_type="z_data",body=entry_to_update)
        print entry_to_update


