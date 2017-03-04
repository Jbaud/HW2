from haversine import haversine
import csv
import sys
import re
import math
import scipy.stats
from itertools import tee, izip

def get_perp( X1, Y1, X2, Y2, X3, Y3):
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

posx = (51.496868217364,9.38602223061025)


def computeDistance( a , b ) :
	" Compute the distance (km) between two points"
	return haversine(a, b)

with open(sys.argv[1]) as f:
	content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]
names =  [x.split(',')[0] for x in content]
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
# convert to tuples
zipped = [zip(x[0::2], x[1::2]) for x in test2]

#print zipped[0:1000]
#print computeDistance(zipped[1][1],zipped[1][2])

# ======= ======= We now have a list of tuples to look for ===================================

candidates = []
for index, lines  in enumerate(zipped) : 
	for index2,lines2 in enumerate(lines):
		#print lines2
		if( computeDistance(lines2, posx ) < 0.1) :
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


# we now want to compute the spatial analysis (5.2)



'''
#TEST
print str(zipped[133400][0][0]) + " , " + str(zipped[133400][0][1]) + " and " + str(zipped[133400][1][0]) + " , " + str(zipped[133400][1][1] )+ " and " + str (posx[0]) + " , " +str(posx[1])
print get_perp(zipped[133400][1][0],zipped[133400][1][1],zipped[133400][0][0],zipped[133400][0][1],posx[0],posx[1])
'''
