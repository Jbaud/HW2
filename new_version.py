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



'''
python new_version.py Partition6467LinkData.csv Partition6467ProbePoints.csv > output.txt

'''

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

def computeTransition(projection, previous, posx, posy):
	"2 first args are the road ID and the 2 last are the probes tuples"
	return computeDistance(posx,posy)/getShortestPath(projection, previous)


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
	print "Distance: "
	print distance
	return normpdf(distance,0,0.02)


def FindMatchedSequence (cisArray,all_probes):
	" Main function, get an array of array of Cis (tuples of projected points) and returns a list of optimal path "
	f =  []
	pre = []
	for index,line in enumerate(cisArray):
		f.append([0.0] * len(line))

	for index,line in enumerate(cisArray):
		pre.append([0.0] * len(line))

	print " f "
	print f
	print 'f 1'
	print f[0]
	print " new f 1:1"
	f[0][0] 

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

	for index in range(0,sizeOfFirstLine) :
		# need a function that  takes a  projected point an returns prob of that projection
		f[0][index] = NewComputeProbCandidates(all_probes[0],cisArray,0,index)
	# main algorithm, starts from the second line

	print "coucou"
	print f

	for index in range(1,numberoflines):
		# size of current line
		sizeOfCurrentLine = len(cisArray[index]) 
		for element in range(0,sizeOfCurrentLine):
			max = -999999999.9999999
			# size of previous line
			sizeofPreviousLine = len(cisArray[index -1 ]) 
			for elementInPreviousLine in range(0,sizeofPreviousLine):

				alt = f[index-1][elementInPreviousLine] + NewComputeProbCandidates(all_probes[index],cisArray,index,element)
				print "alt :"  + str(alt)
				if alt > max:
					max = alt
					pre[index][element] = cisArray[index][elementInPreviousLine]
				print "update :"
				print f
				f[index][element] = max
	print "final"
	print f
	

roads = dict()

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

print "All files have been parsed."
all_probes=zip(latitude, longitude)

# Now we have parsed all the input files

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


# tested -> Works
def recursive_len(item):
	" compute the total size of element in the lsit of list of probes"
	if type(item) == list:
		return sum(recursive_len(subitem) for subitem in item)
	else:
		return 1

#print " sum of elements"
#print recursive_len(all_candidates)

FindMatchedSequence(all_candidates,all_probes)

