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

def spatialAnalysis(candidates, previous_candidates, probabilities, previous probabilities)
	"Performs spatial analysis for the given probes"
	#return an array of tuples (origin,destination, probability)

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
			#roads[link_points] = index_l
			
	'''
			if( computeDistance(lines2, posx ) < 0.15) :
				if index not in candidates:
					candidates.append(index)
					print "Found a candidate"
	
	return candidates
	projections =[]
	distances = []
	spatial_analysis = []
	# compute the ci's -> the projections for the candidates beacon point
	for index,candidate in enumerate(candidates):
		projections.append(get_perp(zipped[candidate][1][0],zipped[candidate][1][1],zipped[candidate][0][0],zipped[candidate][0][1],posx[0],posx[1]))
		distances.append(computeDistance(posx,projections[index] ))
		spatial_analysis.append( normpdf(distances[index],0,20))
	return candidate,projections,distances,spatial_analysis
	'''
roads = dict()
posx = (51.496868217364,9.38602223061025)

print "Parsing: " + sys.argv[1]
with open(sys.argv[1]) as f:
	content = f.readlines()

# =============== Parse the CSV =================================

# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

names =  [x.split(',')[0] for x in content]
names2 = [x.split(',')[1] for x in content]
names3 = [x.split(',')[2] for x in content]

# stores the links as [ " a b" ," c d" , ...]
# used to search shortest links
result = [a +" "+ b for a, b in zip(names2, names3)]
#populate the graph with the links
print "Creating a graph of all the Links."
G = nx.parse_edgelist(result[0:4], nodetype = int)

# get the coordinates
test = [x.split("0.0,",1)[1]  for x in content]
# strip the / and replace by " , "
test = [x.replace("/"," ")  for x in test]

test = [x.split(",,",1)[0]  for x in test]

# delete the end of line separator
test = [x.replace(" ,,", "")  for x in test]
#print test[0:10]
# delete the extra space 
test = [x.replace(" |", "|")  for x in test]
# add , between long and lat
test = [x.replace(" ", ",")  for x in test]
# delete the pipe (could be done before test)
test = [x.replace("|", " , ")  for x in test]
#split the string into list 
test = [x.split(",")   for x in test ]

# convert to float
test2 = [[floatify(x) for x in row] for row in test]
# convert to  list of tuples
zipped = [zip(x[0::2], x[1::2]) for x in test2]

f.close()

# =============== Parse probes CSV =================================

colnames = ['ID', 'Date', 'Type', 'latitude', 'longitude','altitute','speed','heading']
data = pandas.read_csv(sys.argv[2], names=colnames)
latitude = data.latitude.tolist()
longitude = data.longitude.tolist()

print "All files have been parsed."
all_probes=zip(latitude, longitude)



#

print "Computing candidates."

all_candidates =  []
#
lower = 0
upper = 5

for index, currentPosition in enumerate(all_probes[0:5]):

	all_candidates.append(computeCandidates(currentPosition,zipped, lower, upper))
	upper += 1
	if index > 5:
		lower += 1

print "Printing Candidates: "
print all_candidates[0:5]
print "Printing Dictionnary: "
print roads

print "Computing probabilities."

all_probabilities = []

for index, currentPosition in enumerate(all_probes[0:5]):
	all_probabilities.append(computeProbCandidates(currentPosition,all_candidates[index]))

print "Printing Probabilities: "
print all_probabilities[0:5]

print "Computing spatial analysis."



def recursive_len(item):
	" compute the total size of element in the lsit of list of probes"
    if type(item) == list:
        return sum(recursive_len(subitem) for subitem in item)
    else:
        return 1


def FindMatchedSequence (cisArray):
	" Main function, get an array of array of Cis (tuples of projected points) and returns a list of optimal path "
	f = []
	pre = []

            # will be used later to store size of current line
            sizeOfCurrentLine = 0
            sizeofPreviousLine  = 0
            # alt will stiore the temp value 
            alt = 0.0
	#  compute size of the array
	sizeOfArray = len(cisArray)
	#  compute the probabilities for the first line only
	sizeOfFirstLine = len(cisArray[0])
	for index in range(0,sizeOfFirstLine) :
		# need a function that  takes a  projected point an returns prob of that projection
		f[index] = 
	# main algorithm, starts from the second line
	for index in range(1,sizeOfArray):
		# size of current line
		sizeOfCurrentLine = len(cisArray[index])
		for element in range(0,sizeOfFirstLine): 
			max = -999999999.9999999
			# size of previous line 
			sizeofPreviousLine = len(cisArray[index -1 ])
				for elementInPreviousLine in range(0,sizeofPreviousLine): 
					alt = f[elementInPreviousLine]


'''
candidates = []
for index, lines  in enumerate(zipped) : 
	for index2,lines2 in enumerate(lines):
		#print lines2
		if( computeDistance(lines2, posx ) < 0.15) :
			if index not in candidates:
				candidates.append(index)
				print "Found a candidate"
	
print candidates
projections =[]
distances = []
spatial_analysis = []
# compute the ci's -> the projections for the candidates beacon point
for index,candidate in enumerate(candidates):
	projections.append(get_perp(zipped[candidate][1][0],zipped[candidate][1][1],zipped[candidate][0][0],zipped[candidate][0][1],posx[0],posx[1]))
	distances.append(computeDistance(posx,projections[index] ))
	spatial_analysis.append( normpdf(distances[index],0,20))

	



print "Below, the projections found : "
print projections
print " and distance associated"
print distances
print "computed probabilities"
print spatial_analysis


#compute for another point - will need to create functions to do that

posy = (51.497267531231,9.38445162959397)
print "     ======================================== new point ========================================"

candidates2 = []
for index, lines  in enumerate(zipped) : 
	for index2,lines2 in enumerate(lines):
		#print lines2
		if( computeDistance(lines2, posy ) < 0.15) :
			if index not in candidates2:
				candidates2.append(index)
				print "Found a candidate"
	
print candidates2

projections2 =[]
distances2 = []
spatial_analysis2 = []
# compute the ci's -> the projections for the candidates beacon point
for index2,candidate2 in enumerate(candidates2):
	projections2.append(get_perp(zipped[candidate2][1][0],zipped[candidate2][1][1],zipped[candidate2][0][0],zipped[candidate2][0][1],posy[0],posy[1]))
	distances2.append(computeDistance(posy,projections2[index2] ))
	spatial_analysis2.append( normpdf(distances2[index2],0,20))

print "Below, the projections found : "
print projections2
print " and distance associated"
print distances2
print "computed probabilities"
print spatial_analysis2

# compute the proba with the previous position
# example to be automated

# done for only one point, need to be done for all 
print "from "+ names2[candidates[0]] + " to : " + names2[candidates[3]]
print " here :"
print result[0:4]
V = computeDistance(posx,posy)/getShortestPath(names2[candidates[0]],names2[candidates[3]])
print "this is the probability:"
print V
'''
