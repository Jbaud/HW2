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
import scipy.stats
import operator

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
	'''var = float(sd)**2
	pi = 3.1415926
	denom = (2*pi*var)**.5
	num = math.exp(-(float(x)-float(mean))**2/(2*var))'''
	return scipy.stats.norm(mean, sd).pdf(x)


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

	candidates = []

	for index_l, links  in enumerate(zipped[lower:upper]) :
		for index_p,link_points in enumerate(links[:-1]):
			current = get_perp(links[index_p][0],links[index_p][1],links[index_p+1][0],links[index_p+1][1],posx[0],posx[1])
			if(computeDistance(current, posx ) < 0.100):
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

def NewComputeProbCandidates(probe, candidates,index1,index2):
	"Compute the probabilities for each candidate in candidates to be the right position for probe"
	probabilities = 0.0
	distance = computeDistance(probe,candidates[index1][index2])
	return normpdf(distance,0,0.02)

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

def buildCSV(line, index):
	"Build one line of the output CSV"
	#sampleID
	out_line = str(probes_data.sampleID[index])
	out_line += ","
	#dateTime
	out_line += str(probes_data.dateTime[index])
	out_line += ","
	#sourceCode
	out_line += str(probes_data.sourceCode[index])
	out_line += ","
	#latitude
	out_line += str(probes_data.latitude[index])
	out_line += ","
	#longitude
	out_line += str(probes_data.longitude[index])
	out_line += ","	
	#altitude
	out_line += str(probes_data.altitude[index])
	out_line += ","
	#linkPVID
	out_line += str(links_data.linkPVID[line])
	out_line += ","
	return out_line

def FindMatchedSequence (cisArray,all_probes):
	" Main function, get an array of array of Cis (tuples of projected points) and returns a list of optimal path "
	f =  []
	pre = []
	for index,line in enumerate(cisArray):
		f.append([0.0] * len(line))

	for index,line in enumerate(cisArray):
		pre.append([0.0] * len(line))

	# get the total numbe of elements in array
	#numberOfElements = recursive_len(cisArray)
	numberoflines = len(cisArray)
	# will be used later to store size of current line
	sizeOfCurrentLine = 0
	sizeofPreviousLine  = 0
	# alt will stiore the temp value
	alt = 0.0
	#  compute size of the array
	sizeOfArray = len(cisArray)
	#  compute the probabilities for the first line only
	sizeOfFirstLine = len(cisArray[0]) 

	print all_probes[0]
	print "fff"

	for index in range(0,sizeOfFirstLine) :
		# need a function that  takes a  projected point an returns prob of that projection
		f[0][index] = NewComputeProbCandidates(all_probes[65],cisArray,0,index)
	# main algorithm, starts from the second line
	print f
	print " jjjjjjjjjjjjjjjjjjjjjjjjjj"
	for index in range(1,numberoflines):
		# size of current line
		sizeOfCurrentLine = len(cisArray[index]) 
		for element in range(0,sizeOfCurrentLine):
			max2 = -999999999.9999999
			# size of previous line
			sizeofPreviousLine = len(cisArray[index -1 ]) 
			for elementInPreviousLine in range(0,sizeofPreviousLine):

				alt = f[index-1][elementInPreviousLine] + NewComputeProbCandidates(all_probes[65+index],cisArray,index,element)
				#print "alt :"  + str(alt)
				#print ">>>>>" + str(elementInPreviousLine)
				#print len(cisArray[index])
				if alt > max2:
					max2 = alt
					pre[index][element] = cisArray[index-1][elementInPreviousLine]
				f[index][element] = max2
	
	print f
	print " -----------"
	print "pre :"
	print pre
	
	#loop back 
	returnList = []
	for element in range(numberoflines-1,0,-1):
		print f[element]
		index, value = max(enumerate(f[element]), key=operator.itemgetter(1))
		print str(index) + "   " + str(value) 
		returnList.append(pre[element][index])
	

	index2, value2 = max(enumerate(f[0]), key=operator.itemgetter(1))
	returnList.append(cisArray[0][index2])
	'''
	print " HERE ="	
	print returnList
	'''
	return returnList

'''
List of global variables:
links_data - Data extracted from the Links CSV using pandas
road_segments - List of tuples (latitude/longitude) describing the road netorwk
roads - Dictionnary used to map a projection to the road it belongs to, keys are the projections, values are the line number of the road
probes_data - Data extracted from the Probes CSV using pandas
probes_coordinates - A list of tuples containing latitude and longitude for each probe
'''

roads = dict()

print "Parsing: " + sys.argv[1]
linksParser(sys.argv[1])

print "Printing segments 65 to 70:"
print road_segments[65:70]

print "Parsing: " + sys.argv[2]
probesParser(sys.argv[2])

print "Printing probes 65 to 70: "
print probes_coordinates[65:70]

print "All files have been parsed."

print "Computing candidates."

all_candidates =  []
#
lower = 65
upper = 125

for index, currentPosition in enumerate(probes_coordinates[65:125]):

	all_candidates.append(computeCandidates(currentPosition, road_segments, lower, upper))
	upper += 1
	if index > 65:
		lower += 1

for index, probes in enumerate(probes_coordinates[65:125]):
	print probes
'''
print "#########################"

for index, cand in enumerate(all_candidates[60:125]):
	print cand
'''

final_candidates = FindMatchedSequence(all_candidates,probes_coordinates)

print "#########################"
for n in final_candidates:
	print n
#for index, out in enumerate(final_candidates[65:125]):
#	print out		
'''
print "Printing Candidates 65 to 70:"
print all_candidates[65:70]
'''
'''
print "Printing Dictionnary: "
print roads

print "Finding sequence."
final_candidates = FindMatchedSequence(all_candidates,probes_coordinates)

print "Printing the first 5 selected candidates:"
print final_candidates

print "Performing link line number lookup."
candidate_lines = []

for candidate in final_candidates:
	candidate_lines.append(roads[candidate])

print "Lookup result:"
print candidate_lines

print "Building output csv."
output_csv = []

for index,line_id in enumerate(candidate_lines):
	output_csv.append(buildCSV(line_id, index))

print "Output CSV:"
print output_csv
'''
