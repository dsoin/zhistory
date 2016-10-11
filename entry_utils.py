import requests
from cStringIO import StringIO
import json
import hashlib
from datetime import datetime

run_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def get_addr(lat,long):
    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=false".format(lat,long);
    response = requests.get(url)
    ret = StringIO(response.content)
    parsed = json.loads(ret.read())
    address = {'postcode':'','street':'','number':'','town':'','county':'','borough':''};
    for entry in parsed["results"]:
        for subentry in entry["address_components"]:
            type_entry = json.dumps(subentry["types"])
            long_name = json.dumps(subentry["long_name"])
            if "postal_code" in type_entry:
                address['postcode']= long_name
            if "route" in type_entry:
                address['street']=long_name
            if "street_number" in type_entry:
                address['number']=long_name
            if "postal_town" in type_entry:
                address['town']=long_name
            if "administrative_area_level_2" in type_entry:
                address['county']=long_name
            if "administrative_area_level_3" in type_entry:
                address['borough']=long_name
    return address

def fill_esentry_zoopla(listing):
    es_entry={}
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
    similarity_hash = hashlib.sha1("{}{}{}".format(listing.latitude,listing.longitude,listing.num_bedrooms).encode())
    es_entry['similarity_hash'] = similarity_hash.hexdigest()
    es_entry['fetched_time'] = run_time
    es_entry['last_published_date'] = listing.last_published_date
    es_entry['first_published_date'] = listing.first_published_date
    return es_entry

def update_esentry_geo(es_entry):
    addr = get_addr(es_entry['geo_loc']['lat'],es_entry['geo_loc']['lon'])
    es_entry['postcode']=addr['postcode'].replace("\"","")
    es_entry['number']=addr['number'].replace("\"","")
    es_entry['street']=addr['street'].replace("\"","")
    es_entry['town']=addr['town'].replace("\"","")
    es_entry['county']=addr['county'].replace("\"","")
    es_entry['borough']=addr['borough'].replace("\"","")

def update_appeareance(es_entry):
    es_entry['added']='false';
    es_entry['removed']='false';
    es_entry['retained']='false';
    es_entry['reappeared']='false';