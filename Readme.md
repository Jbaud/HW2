CS513 Homework 2:
=================

Rssources:
---------

https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/Map-Matching20for20Low-Sampling-Rate20GPS20Trajectories-cameraReady.pdf

https://www.darrinward.com/lat-long/?id=2736396

TO-DO:
------
refactor the code
    for now this is mostly a proof a concept, put the code inside functions and generalize the computation for every beacon of one user

What is does : 

    1) take the first beacon (hardcoded) and search for neighbors + compute the spatial analysis 
    2) same for second beacon

implemented:
    seach for neighbors
    projections
    distance between two projections
    closest path from ci-1 to ci

I am gonna drop the time analysis, too complex (input file is a mess) and i am not sure its really worht it.

next steps:

select all beacons from 1 user and run the above methods to all its elements

