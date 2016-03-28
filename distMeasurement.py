
# Joe Jensen - jpj35 - EECS 325 - P2

# TO RUN: on comman line call "sudo python distMeasurement.py"
# for each address in targets.txt, a block will appear as follows

# Finding hops, RTT, and Geo Dist for [address]
# [IP address of address]
# hops: [#]
# rtt: [#] ms
# dist: [#] miles
# (empty line)


from socket import *
import sys
import time
# from struct import *
import struct
import math

# hops prints out the number of hops it takes to hit the input_name address

def hops(input_name, tries):

	# Remote IP's, should be changed when using all of targets.txt
	dest_name = input_name
	dest_ip = gethostbyname(dest_name)
	# print ("dest ip: {}".format(dest_ip))

	# Part of this code was taken from Oracle Tutorials
	ttl = 1
	max_hops = 32

	while True:
		current_address = hopSpecificTTL(dest_ip, ttl, 0)
		
		if current_address == dest_ip:
			break
		if ttl > max_hops:
			# print "ttl > max hops, tries: {}".format(tries)
			tries += 1
			# if (tries > 2):
				# print ("too many tries...")
				
			hops(input_name, tries)
		ttl += 1

	print ("hops: {}".format(ttl))

# this function is a helper for hops, and finds the current address of the router
# at the specific ttl

def hopSpecificTTL(my_dest_ip, my_ttl, attempts):
	send_socket = socket(AF_INET, SOCK_DGRAM, getprotobyname('udp'))
	recv_socket = socket(AF_INET, SOCK_RAW, getprotobyname('icmp'))
	send_socket.setsockopt(SOL_IP, IP_TTL, my_ttl)
	recv_socket.settimeout(1)
	recv_socket.bind(("", 33434))
	# joes packet signifies my message
	send_socket.sendto("joespacket", (my_dest_ip, 33434))

	current_address = None
	try:
		data, current_address = recv_socket.recvfrom(5120)
		current_address = current_address[0]
		if current_address == None:
			if attempts > 5:
				# print ("***")
				return "***"
			else:
				hopSpecificTTL(my_dest_ip, my_ttl, attempts+1)
	except error:
		if attempts > 5:
			# print "***"
			return "***"
		else:
			hopSpecificTTL(my_dest_ip, my_ttl, attempts+1)
	finally:
		send_socket.close()
		recv_socket.close()
	# if (current_address != None):
		# print ("ttl: {} , current_address: {}".format(my_ttl, current_address))
	return current_address


# The following code computes RTT to the desired destination

def rtt(input_name):

	dest_name = input_name
	dest_ip = gethostbyname(dest_name)

	send_socket = socket(AF_INET, SOCK_DGRAM, getprotobyname('udp'))
	recv_socket = socket(AF_INET, SOCK_RAW, getprotobyname('icmp'))
	recv_socket.settimeout(1)
	recv_socket.bind(("", 33434))
	send_socket.sendto("", (dest_ip, 33434))
	tstart = time.time()
	try:
		rec_packet = recv_socket.recvfrom(512)
		tfinish = time.time()
		ttotal = (tfinish - tstart)*1000
		print ("rtt: {} ms".format(ttotal))
	except error:
		rtt(input_name)
	
# geo_distance finds and prints the distance in miles from CWRU to the router		

def geo_distance(input_name):
	
	s = socket(AF_INET, SOCK_STREAM)
	host = 'freegeoip.net'
	port = 80
	remote_ip = gethostbyname(host)
	s.connect((remote_ip, port))
	message = "GET /xml/{} HTTP/1.1\r\n\r\n".format(gethostbyname(input_name))
	s.sendall(message)
	# reply stores the response from freegeoip.net
	reply = s.recv(4096)

	# now parse through to find lat and long
	latitude = '' # stores latitude
	longitude = '' # stores longitude
	lat_line = None
	long_line = None
	lat_line_check = "<Latitude>"
	long_line_check = "<Longitude>"

	# goes through xml text to find lines which contain lat and long
	lines = reply.splitlines()
	for line in lines:
		if (len(line) > 10):
			if (line[1:11] == lat_line_check):
				lat_line = line
			if (line[1:12] == long_line_check):
				long_line = line

	# goes through lat_line plucking only the latitude
	in_nums = False
	for c in lat_line:
		if (c == '>'):
			in_nums = True
		elif (c == '<'):
			in_nums = False
		elif (in_nums):
			latitude += str(c)

	# goes through lat_line plucking only the longitude
	in_nums = False
	for c in long_line:
		if (c == '>'):
			in_nums = True
		elif (c == '<'):
			in_nums = False
		elif (in_nums):
			longitude += str(c)

	latitude = float(latitude)
	longitude = float(longitude)

	# Now longitude and latitude store the correct values
	# MY LOCATION Lat: 41.5042, -81.6084 (googled CWRU lat/long to find this)

	dist = lat_long_distance(41.5042, -81.6084, latitude, longitude)
	print "dist: {} miles".format(dist)

# this method taken from John D. Cook's blog
# returns distance in miles given 2 lat/long coordinates

def lat_long_distance(lat1, long1, lat2, long2):
	# Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
 
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    earth_rad = 3959 # miles
    return (arc*earth_rad)

# main method...
# opens targets.txt and gets all address
# for all addresses, calls hops, rtt, and geo_distance which print specified data

if __name__ == "__main__":

	print ("\n")

	f = open('targets.txt', 'r')

	# IPs contains the input text file list of IP addresses
	IPs = []

	# loop goes through targets text file and adds IPs to IPs array
	while True:
		line = f.readline()
		if not line:
			break
		IPs.append(line[0:len(line) - 2])

	for ip in IPs:
		print ("Finding hops, RTT, and Geo Dist for {}".format(ip))
		print gethostbyname(ip)
		hops(ip, 0)
		rtt(ip)
		geo_distance(ip)
		print("")