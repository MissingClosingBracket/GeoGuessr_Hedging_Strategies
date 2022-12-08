import osmnx as ox
from helperFunctions import pointsToListOfLatAndLongs, getDistance, generate_random_point_within_convex_hull
from osmnx.utils_geo import sample_points
import statistics

#List of best guesses (dist to goal)
bestGuessesDist = []

#List of all guesses (dist to goal)
allGuessesDist = []
bestGuessesDist = []

#Get graph from bbox
graph = ox.graph_from_bbox(55.3002, 54.9855, 14.6770, 15.1604, network_type='drive').to_undirected()
graph.graph['crs'] = "epsg:3857"

#Run through i iterations and fill array
i = 1000000
n_guesses = 3
randomGuesses = pointsToListOfLatAndLongs(generate_random_point_within_convex_hull(graph,n_guesses*i))
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

#print(len(distances))

#Get statistics
print("Best guesses mean: " + str(statistics.mean(bestGuessesDist)))
print("All guesses mean: " + str(statistics.mean(allGuessesDist)))

#Results from runs: 
    #_100 times:
        #Best guesses mean: 11.34198341975492
        #All guesses mean: 20.97098631237931
    #_10000 times:
        #Best guesses mean: 11.540039865028723
        #All guesses mean: 20.84663900628839
    #_1000000 times: (approx. 2-3 minutes)
        #Best guesses mean: 11.5810596336926
        #All guesses mean: 20.943891247653607