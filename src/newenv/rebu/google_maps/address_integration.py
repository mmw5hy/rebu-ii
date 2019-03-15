import googlemaps
from datetime import datetime
import json
import requests

# https://googlemaps.github.io/google-maps-services-python/docs/

#https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=40.6655101,-73.89188969999998&destinations=enc:_kjwFjtsbMt%60EgnKcqLcaOzkGari%40naPxhVg%7CJjjb%40cqLcaOzkGari%40naPxhV:&key=AIzaSyChjIV6mR2KeiCIrBbpTBMMs_YauA9ZZDQ

#https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=40.6655101,-73.89188969999998&destinations=40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.6905615%2C-73.9976592%7C40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626%7C40.659569%2C-73.933783%7C40.729029%2C-73.851524%7C40.6860072%2C-73.6334271%7C40.598566%2C-73.7527626&key=YOUR_API_KEY

# gmaps client
gmaps = googlemaps.Client(key='AIzaSyChjIV6mR2KeiCIrBbpTBMMs_YauA9ZZDQ')


# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

geocode_result = gmaps.geocode('validate ')
print(geocode_result)
# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))






# Distance matrix between two places (address)

def distance_between_addresses(origin, destination):
	distance_matrix = gmaps.distance_matrix(origins=origin, destinations=destination)
	meters = distance_matrix['rows'][0]['elements'][0]['distance']['value']
	miles = meters * 0.000621371
	return miles



# Distance matrix between two places (geocode)

def distance_between_geocodes(origin, destination):
	distance_matrix = gmaps.distance_matrix(origins=origin, destinations=destination)
	meters = distance_matrix['rows'][0]['elements'][0]['distance']['value']
	miles = meters * 0.000621371
	return miles



# Time matrix between two places (address)

def time_between_addresses(origin, destination):
	distance_matrix = gmaps.distance_matrix(origins=origin, destinations=destination)
	seconds = distance_matrix['rows'][0]['elements'][0]['duration']['value']
	minutes = seconds / 60
	return minutes


# Time matrix between two places (geocode)

def time_between_geocodes(origin, destination):
	distance_matrix = gmaps.distance_matrix(origins=origin, destinations=destination)
	seconds = distance_matrix['rows'][0]['elements'][0]['duration']['value']
	minutes = seconds / 60
	return minutes



# validate a real address 

def validate_address(address):
	geocode_result = gmaps.geocode(address)
	if geocode_result:
		return geocode_result
	else:
		return None


miles = distance_between_addresses('briar woods high school', 'university of virginia')
minutes = time_between_addresses('briar woods high school', 'university of virginia')
valid = validate_address('uva')
print(miles)
print(minutes)
print(valid)




# Test distance between address
def test_distance_between_addresses():
	miles = distance_between_addresses('briar woods high school', 'university of virginia')
	print(miles == 97.752221607)

# Test time between address
def test_time_between_addresses():
	minutes = time_between_addresses('briar woods high school', 'university of virginia')
	print(minutes == 124.56666666666666)



# testing test_geocode_result
def test_geocode_result_address():
	geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

	print(geocode_result[0]['address_components'][0]['short_name'] == "1600")


# testing test_reverse_geocode_result
def test_reverse_geocode_result_long_and_lat():
	reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
	print(reverse_geocode_result[0]['address_components'][1]['long_name'] == "Bedford Avenue")


# Test validating an address
def test_validate_address():
	validate = validate_address("not a real address")
	print(validate == None)


test_geocode_result_address()
test_reverse_geocode_result_long_and_lat()
test_distance_between_addresses()
test_time_between_addresses()
test_validate_address()

# validate address, create optimized routes, directions for producers or consumers, geocoding, live map location for producers and consumers, validating delivery addresses and many other use cases
# milage between two addresses
