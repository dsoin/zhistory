import hashlib
import json
import time
from cStringIO import StringIO
from google_lookup import get_saved_geo, copy_geo_data

import requests

# run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
run_time = timestamp = int(time.time() * 1000)


def get_addr(lat, long):
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=false".format(lat, long);
    response = requests.get(url)
    ret = StringIO(response.content)
    parsed = json.loads(ret.read())
    address = {'postcode': '', 'street': '', 'number': '', 'town': '', 'county': '', 'borough': ''};
    for entry in parsed["results"]:
        for subentry in entry["address_components"]:
            type_entry = json.dumps(subentry["types"])
            long_name = json.dumps(subentry["long_name"])
            # print(subentry)
            if "postal_code" in type_entry and "postal_code_prefix" not in type_entry:
                address['postcode'] = long_name.replace("\"", "")
            if "route" in type_entry:
                address['street'] = long_name.replace("\"", "")
            if "street_number" in type_entry:
                address['number'] = long_name.replace("\"", "")
            if "postal_town" in type_entry:
                address['town'] = long_name.replace("\"", "")
            if "administrative_area_level_2" in type_entry:
                address['county'] = long_name.replace("\"", "")
            if "administrative_area_level_3" in type_entry:
                address['borough'] = long_name.replace("\"", "")
    return address


def fill_esentry_zoopla(listing):
    es_entry = {}
    es_entry['asking_price'] = listing.price
    es_entry['geo_loc'] = {}
    es_entry['geo_loc']['lat'] = listing.latitude
    es_entry['geo_loc']['lon'] = listing.longitude
    es_entry['bed'] = listing.num_bedrooms
    es_entry['bath'] = listing.num_bathrooms
    es_entry['floors'] = listing.num_floors
    es_entry['thumb_url'] = listing.thumbnail_url
    es_entry['img_url'] = listing.image_url
    es_entry['details_url'] = listing.details_url
    similarity_hash = hashlib.sha1("{}{}{}".format(listing.latitude, listing.longitude, listing.num_bedrooms).encode())
    es_entry['similarity_hash'] = similarity_hash.hexdigest()
    es_entry['fetched_time'] = run_time
    es_entry['last_published_date'] = listing.last_published_date
    es_entry['first_published_date'] = listing.first_published_date
    return es_entry


def update_esentry_geo(es_entry):
    hit = get_saved_geo(es_entry['geo_loc']['lat'], es_entry['geo_loc']['lon'])
    if hit:
        addr = hit[0]['_source']
    else:
        addr = get_addr(es_entry['geo_loc']['lat'], es_entry['geo_loc']['lon'])
    copy_geo_data(addr,es_entry)


def update_appeareance(last_set, current_set):
    if len(last_set) > 0:
        for current_entry in current_set:
            if not any(last_test_entry['similarity_hash'] == current_entry['similarity_hash']
                       for last_test_entry in last_set):
                current_entry['status'] = "added"
                print("{}:{}:{}added".format(current_entry['address'],current_entry['bed'],current_entry['asking_price']))
            else:
                current_entry['status'] = "retained"

        for last_entry in last_set:
            if not any(current_test_entry['similarity_hash'] == last_entry['similarity_hash']
                       for current_test_entry in current_set):
                last_entry['status'] = "removed"
                last_entry['fetched_time'] = run_time
                current_set.append(last_entry)
                print("{}:{}:{}removed".format(current_entry['address'],current_entry['bed'],current_entry['asking_price']))
    else:
        for entry in current_set:
            entry['status'] = "initial"


def remove_duplicates(d_set):
    res = list()
    for i in range (0,len(d_set)-1):
        if d_set[i]['similarity_hash'] not in d_set[i+1]['similarity_hash']:
            res.append(d_set[i])
        else:
            print("{} dup of {}".format(d_set[i]['address'],d_set[i+1]['address']))
    return res

def print_totals(p_set):
    total = 0
    added = 0
    removed = 0
    reappeared = 0
    retained = 0
    for entry in p_set:
        total += 1;
        if "added" in entry['status']: added += 1
        if "removed" in entry['status']: removed += 1
        if "retained" in entry['status']: retained += 1
        if "reappeared" in entry['status']: reappeared += 1

    print("Total     :{}\r\nRetained  :{}\r\nAdded     :{}\r\nRemoved   :{}\r\nReappeared:{}".
          format(total, retained, added, removed, reappeared))

