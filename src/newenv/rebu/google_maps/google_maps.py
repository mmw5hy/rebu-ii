import googlemaps
from datetime import datetime
import json

gmaps = googlemaps.Client(key='AIzaSyChjIV6mR2KeiCIrBbpTBMMs_YauA9ZZDQ')

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)
print(geocode_result)



def test_geocode_result():
	geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

	print(geocode_result[0]['address_components'][0]['short_name'] == "1600")

def test_reverse_geocode_result():
	reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
	print(reverse_geocode_result[0]['address_components'][1]['long_name'] == "Bedford Avenue")

test_geocode_result()
test_reverse_geocode_result()