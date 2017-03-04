from haversine import haversine
import csv
import sys
import re

from itertools import tee, izip


#
i = 1
#

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
print test[0:10]
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
			candidates.append(names[index])
			print "Found a candidate"
	
print candidates

