from haversine import haversine
import csv
import sys
import re
import math
import scipy.stats
from itertools import tee, izip
import networkx as nx
import matplotlib.pyplot as plt
import pandas

def get_perp( X1, Y1, X2, Y2, X3, Y3):
	" Compute the projection"
	"""************************************************************************************************ 
	Purpose - X1,Y1,X2,Y2 = Two points representing the ends of the line segment
			  X3,Y3 = The offset point 
	'Returns - X4,Y4 = Returns the Point on the line perpendicular to the offset or None if no such
						point exists
	'************************************************************************************************ """
	XX = X2 - X1 
	YY = Y2 - Y1 
	ShortestLength = ((XX * (X3 - X1)) + (YY * (Y3 - Y1))) / ((XX * XX) + (YY * YY)) 
	X4 = X1 + XX * ShortestLength 
	Y4 = Y1 + YY * ShortestLength
	#if X4 < X2 and X4 > X1 and Y4 < Y2 and Y4 > Y1:
	return X4,Y4
	#return None

def normpdf(x, mean, sd):
	" Compute the probability (standart deviation)"
	var = float(sd)**2
	pi = 3.1415926
	denom = (2*pi*var)**.5
	num = math.exp(-(float(x)-float(mean))**2/(2*var))
	return num/denom


def floatify(x):
	" convert a list to float"
	try:
		return float(x)
	except ValueError:
		return x

def getShortestPath(pointA, pointB):
	" return the size of the shortest path, A and B should be the value name of the link and not it's index"
	return len(nx.shortest_path(G,source=int(pointA),target=int(pointB)))


def computeDistance( a , b ) :
	" Compute the distance (km) between two points"
	return haversine(a, b)


def computeCandidates(posx,zipped, lower, upper):
	"Compute the candidates + projection + distances (to projection) + spatial_analysis (normal proba) for a beacon UNDER < 150 meters"
	#Global variables defined in this function
	global roads

	roads = dict()
	candidates = []
	lower = 0
	upper = 5
	for index_l, links  in enumerate(zipped[lower:upper]) :
		for index_p,link_points in enumerate(links[:-1]):
			current = get_perp(links[index_p][0],links[index_p][1],links[index_p+1][0],links[index_p+1][1],posx[0],posx[1])
			if(computeDistance(current, posx ) < 0.15):
				candidates.append(current)
				roads[current] = index_l
	return candidates

def computeTransition(projection, previous):
	"Compute the likelyhood for an object to move from one point to another"
	return computeDistance(projection,previous)/getShortestPath(projection,previous)
'''
def spatialAnalysis(candidates, previous_candidates, probabilities, previous probabilities):
	"Performs spatial analysis for the given probes"
	#return an array of tuples (origin,destination, probability)'''

def computeProbCandidates(probe, candidates):
	"Compute the probabilities for each candidate in candidates to be the right position for probe"
	probabilities = []
	for index_c, projection in enumerate(candidates):
		distance = computeDistance(probe,projection)
		print "Distance: "
		print distance
		current = normpdf(distance,0,0.02)
		probabilities.append(current)
	return probabilities

def linksParser(file):
	"Extract relevant infos from the CSV containing the links, also creates a graph of all the links"
	#Global variables defined in this function
	global links_data
	global road_segments

	#Parsing using panda
	colnames = ['linkPVID', 'refNodeID', 'nrefNodeID', 'length', 'functionalClass', 'directionOfTravel', 'speedCategory', 'fromRefSpeedLimit', 'toRefSpeedLimit', 'fromRefNumLanes', 'toRefNumLanes', 'multiDigitized', 'urban', 'timeZone', 'shapeInfo', 'curvatureInfo', 'slopeInfo']
	
	links_data = pandas.read_csv(file, names=colnames)
	
	#Extracting the segments from the parsed file
	shape = links_data.shapeInfo.tolist() 
	
	latitude = []
	longitude = []

	#Split the column into list of segment coordinates 
	shape = [x.split("|")   for x in shape]
	
	#Split the segment coordinates
	shape = [[x.split("/") for x in row] for row in shape]

	#Extract lists of latitude and longitude
	latitude = [[x[0] for x in row] for row in shape]
	longitude = [[x[1] for x in row] for row in shape]
	
	#Convert strings in the lists to floats
	latitude  = [[floatify(x) for x in row] for row in latitude]
	longitude  = [[floatify(x) for x in row] for row in longitude]

	road_segments = []

	for linkx,linky in zip(latitude,longitude):
		current = zip(linkx,linky)
		road_segments.append(current)
	
def probesParser(file):
	"Extract relevant infos from the CSV containing the links, also creates a graph of all the links"
	global probes_data
	global probes_coordinates
	colnames = ['sampleID', 'dateTime', 'sourceCode', 'latitude', 'longitude', 'altitude', 'speed', 'heading']
	probes_data = pandas.read_csv(file, names=colnames)
	latitude = []
	longitude = []
	latitude = probes_data.latitude.tolist()
	longitude = probes_data.longitude.tolist()
	probes_coordinates = zip(latitude,longitude)

'''
List of global variables:
links_data - Data extracted from the Links CSV using pandas
road_segments - List of tuples (latitude/longitude) describing the road netorwk
roads - Dictionnary used to map a projection to the road it belongs to, keys are the projections, values are the line number of the road
probes_data - Data extracted from the Probes CSV using pandas
probes_coordinates - A list of tuples containing latitude and longitude for each probe
'''

print "Parsing: " + sys.argv[1]
linksParser(sys.argv[1])

print "Printing first 10 segments:"
print road_segments[0:1]

print "Parsing: " + sys.argv[2]
probesParser(sys.argv[2])

print "Printing first 10 probes:"
print probes_coordinates[0:1]

print "All files have been parsed."

print "Computing candidates."

all_candidates =  []
#
lower = 0
upper = 5

for index, currentPosition in enumerate(probes_coordinates[0:1]):

	all_candidates.append(computeCandidates(currentPosition, road_segments, lower, upper))
	upper += 1
	if index > 5:
		lower += 1

print "Printing Candidates for the first 2 probes: "
print all_candidates[0:1]

print "Printing Dictionnary: "
print roads
