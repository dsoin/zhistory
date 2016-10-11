import zoopla
import json
import elasticsearch
import hashlib
from datetime import datetime

run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def fill_esentry_zoopla(listing):
    es_entry={}
    es_entry['asking_price'] = listing.price
    es_entry['location'] = {}
    es_entry['location']['lat'] = listing.latitude
    es_entry['location']['lon'] = listing.longitude
    es_entry['bed'] = listing.num_bedrooms
    es_entry['bath'] = listing.num_bathrooms
    es_entry['floors'] = listing.num_floors
    es_entry['thumb_url'] = listing.thumbnail_url
    es_entry['img_url'] = listing.image_url
    es_entry['details_url'] = listing.details_url
    similarity_hash = hashlib.sha1("{}{}{}".format(listing.latitude,listing.longitude,listing.num_bedrooms).encode())
    es_entry['similarity_hash'] = similarity_hash.hexdigest()
    es_entry['fetched_time'] = run_time
    es_entry['last_published_date'] = listing.last_published_date
    es_entry['first_published_date'] = listing.first_published_date
    return es_entry

es = elasticsearch.Elasticsearch()
api = zoopla.api(version=1, api_key='h8w8e3vza6wprx4qeeyvhdd3')
listings = api.property_listings(
        area='KT7',
        max_results=None,
        listing_status='sale')


for listing in listings:
    es_entry=fill_esentry_zoopla(listing)
    es.index(index='test',doc_type='td', body=es_entry)