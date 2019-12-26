# ---- pip install gql ----

# import our modules
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import pprint
import json
import csv
import time
import codecs


# define our authentication process.
header = {'Authorization': 'bearer _Aj96-oKvSorKrsmJxlOXdRtkhEtdKRRQoR4yzUjX0EybSKXTM3drlWALbC_oOFzQwrGVYQTVyUKeaT3N9TRT4UQ8qr781wGlHtGxT3rUdRBqnoKYnSUtD3lEfTtXXYx', 'Content-Type':"application/json"}
# Build the request framework
transport = RequestsHTTPTransport(url='https://api.yelp.com/v3/graphql', headers=header, use_json=True)
# Create the client
client = Client(transport=transport, fetch_schema_from_transport=True)

bizdict = []
with open('LA_county_zip.txt', 'r') as zip:
    content = zip.readlines()
content = [x.strip() for x in content]
limit = 50
nah = 0

for czip in content:
    print("bizdict: ", len(bizdict))
    print("current zip: ", czip)
    total = 1
    i = 0
    while (i < total) and (i <1000):
        print("offset counter", i)
        query = gql('''{
          search(sort_by: "distance"
                  categories: "nightlife",
            location: "zip_code:''' + czip + "\""
                + 'limit:' + str(limit) + ''',
                offset: ''' 
                + str(i) +
            ''') {
            total
            business {
              name
              id
              coordinates{
            latitude
            longitude
              }
              rating
              review_count
              price
              url
              categories {
            alias
              }
              location {
            address1
            address2
            address3
            city
            state
            postal_code
            country
            formatted_address
              }
            }
          }
        }
        ''')
        try:
            offsetoutput = client.execute(query)
        except:
            print ("Http Error:")
            nah = 1
            with open('losangeles' + str(czip) + '.json', 'w') as fp:
                json.dump(bizdict, fp)
            break;
            
        if i == 0:
            total = offsetoutput['search']['total']
        tempquery = offsetoutput['search']['business']
        for biz in tempquery:
            if biz not in bizdict:
                bizdict.append(biz)
        i += limit
    if nah:
        break;
        
print ("done! len,", len(bizdict))
print ("len,", len(bizdict))
with open('losangeles.json', 'w') as fp:
    json.dump(bizdict, fp)