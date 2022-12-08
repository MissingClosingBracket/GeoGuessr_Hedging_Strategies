import osmnx as ox
from helperFunctions import pointsToListOfLatAndLongs, getDistance, generate_random_point_within_convex_hull
from osmnx.utils_geo import sample_points
import statistics
from shapely.geometry import Point
import geopandas as gpd

#List of best guesses (dist to goal)
bestGuessesDist = []

#List of all guesses (dist to goal)
allGuessesDist = []
bestGuessesDist = []

#Get graph from bbox
graph = ox.graph_from_bbox(55.3002, 54.9855, 14.6770, 15.1604, network_type='drive').to_undirected()
graph.graph['crs'] = "epsg:3857"
node_points = [Point((data["x"], data["y"])) for node, data in graph.nodes(data=True)]
convexHull = gpd.GeoSeries(node_points).unary_union.convex_hull

#Run through i iterations and fill array. i = number of rounds
i = 10000000
n_guesses = 3
randomGuesses = pointsToListOfLatAndLongs(generate_random_point_within_convex_hull(n_guesses*i,convexHull))
randomGoal = pointsToListOfLatAndLongs(sample_points(graph,1*i))

for elem in range(0,i*n_guesses,n_guesses):
    dist = []
    goalI = int(elem / n_guesses)
    for x in range(0, n_guesses):
        #print((randomGuesses[0][elem+x], randomGuesses[1][elem+x]), (randomGoal[0][goalI], randomGoal[1][goalI]))
        dist.append(getDistance((randomGuesses[0][elem+x], randomGuesses[1][elem+x]), (randomGoal[0][goalI], randomGoal[1][goalI])))
    dist.sort()
    #print(dist)
    #print('---')
    bestGuessesDist.append(dist[0])
    for d in dist:
        allGuessesDist.append(d)

print(len(allGuessesDist))
print(len(bestGuessesDist))

#Get statistics
print("Best guesses mean: " + str(statistics.mean(bestGuessesDist)))
print("All guesses mean: " + str(statistics.mean(allGuessesDist)))

#Results from runs: 
    #_100 rounds:
        #Best guesses mean: 11.499045201317461 (out of 100)
        #All guesses mean: 19.604587003476986 (out of 300)
    #_10000 times:
        #Best guesses mean: 11.425957699888812 (out of 10.000)
        #All guesses mean: 20.04195537986655 (out of 30.000)
    #_1000000 times: (approx. 1 1/2 hours)
        #Best guesses mean: 11.448282384125966 (out of 1.000.000)
        #All guesses mean: 20.01014984341671 (out of 3.000.000)