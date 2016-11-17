from bottle import route, run, template
from entry_utils import get_addr
import json
from land_registry import query_registry

def get_zoopla_data(lat,lon):
    return ""

@route('/land/<lat>/<lon>')
def index(lat,lon):
    addr = get_addr(lat,lon)
    land_data = query_registry(addr['postcode'],addr['street'],addr['number'])
    zoopla_data = get_zoopla_data(lat,lon)
    return json.dumps({'history':{'land_data':land_data,'zoopla_data':zoopla_data}})

run(host='localhost', port=8080)
#index(51.387585,-0.32609)
