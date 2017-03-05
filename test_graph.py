import networkx as nx
from haversine import haversine
import csv
import sys
import re
import matplotlib.pyplot as plt
import math
import scipy.stats
from itertools import tee, izip

with open(sys.argv[1]) as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

names =  [x.split(',')[0] for x in content]
names2 = [x.split(',')[1] for x in content]
names3 = [x.split(',')[2] for x in content]

#print "names2"
#print names2[0:10]
#print "names 3"
#print names3[0:10]


result = [a +" "+ b for a, b in zip(names2, names3)]
#print "coucou"
#print result[0:20]

G = nx.parse_edgelist(result[0:4], nodetype = int)
nx.draw(G, with_labels = True)
print "result:"
print(nx.shortest_path(G,source=163152693,target=162981512))

#nx.draw(G)
plt.savefig("save2.png")