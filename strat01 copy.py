import osmnx as ox
import geopandas as gpd
from helperFunctions import getDistance, makeGrid, placeInBoxes, pointsToListOfLatAndLongs
from shapely.geometry import Point,mapping,LineString
import matplotlib.lines as lines
import matplotlib.pyplot as plt
import math
import statistics
from osmnx.utils_geo import sample_points

#start here by defining area and grid size:
gridSize = (35,35)
guesses = 3
area = {
    'north': 55.3002,
    'south': 54.9855,
    'east': 14.6770,
    'west': 15.1604
}

#get graph from bbox
graph = ox.graph_from_bbox(area['north'], area['south'], area['east'], area['west'], network_type='drive').to_undirected()

#get edges and their length
edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)

#define empty array that will contain centerpoint, distance (weight) for every edge
centerPoints = []

#iterate through edges
for index, row in edges.iterrows():

    #get the points for each edge
    coords = [(coords) for coords in (row['geometry'].coords)]

    #get pairs of points for each edge (in many cases an edge is a collection of points)
        #possible "optimization": just use first and last node -> however, this will lead to a bigger uncertainty... 
        #for i.e. an entire big country using all edges is maybe not viable. Easily implement code-change here.
    #after that, calculate the distance (km) and get the center of the two points
    length = len(coords)
    for x in range(0, length-1):
        distance = getDistance(coords[x], coords[x+1])
        centerPoint = (
            (coords[x][0] + coords[x+1][0])/2.0, 
            (coords[x][1] + coords[x+1][1])/2.0
            )
        centerPoints.append([centerPoint, distance])    

#make a grid of gridSize boxes that span the rectangle of the convex hull of the networks center points
#each grid box has a bounding box and will contain the total of weights and the points (points = edge representations)
node_points = [Point((data[0][0], data[0][1])) for data in centerPoints]
convexHull = gpd.GeoSeries(node_points).unary_union.convex_hull
grid = makeGrid(gridSize[0], gridSize[1], convexHull)

#run through the centerPoints and place them in the boxes
gridWithBoxes, totalWeight = placeInBoxes(centerPoints, grid, gridSize)

#plot graph, leave open
fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=4, figsize=(14,13))

#TEMP: make grid
#for x in range(0, len(grid)):
    #b = grid[x]
    #boxX = [[b.min_lat, b.max_lat, b.max_lat, b.min_lat,b.min_lat]]
    #boxY = [[b.max_lon, b.max_lon, b.min_lon, b.min_lon,b.max_lon]]
    #if x != 34 and x != 34+35 and x != 34+35+35:
        #ax.add_line(lines.Line2D(xdata=boxX,ydata=boxY,color='orange',linewidth=2,zorder=1000))
    #if x == 0:    
        #ax.add_line(lines.Line2D(xdata=boxX,ydata=boxY,color='orange',linewidth=2,zorder=1001, label='grid'))

#run through the grid and collect boxes into n (n = number of guesses) bigger areas
queue = []
width = gridSize[0]
height = gridSize[1]

biggerBoxes = []

for x in range(0, guesses):
    biggerBoxes.append([])
currWeight = 0
currBigBox = 0
colors = ['yellow', 'purple', 'green', 'blue', 'orange']
isLastPrinted = False
for k in range (0, width + height - 1):
    for j in range(0, k+1):
        i = k-j
        if (i < height and j < width):
            index = j * width + i
            b = gridWithBoxes[index]
            #if b.totalWeight > 0:
            if b.inside:
                currWeight += b.totalWeight
                biggerBoxes[currBigBox].append(b)
                boxX = [[b.min_lat, b.max_lat, b.max_lat, b.min_lat,b.min_lat]]
                boxY = [[b.max_lon, b.max_lon, b.min_lon, b.min_lon,b.max_lon]]
                #ax.add_line(lines.Line2D(xdata=boxX,ydata=boxY,color=colors[currBigBox],linewidth=2,zorder=1000))
                if currWeight >= totalWeight/guesses:
                    #ax.add_line(lines.Line2D(xdata=boxX,ydata=boxY,color=colors[currBigBox],linewidth=2,zorder=1000, label="area: " + str(currBigBox+1)))
                    currWeight = 0
                    currBigBox += 1
                if isLastPrinted == False and currBigBox == guesses-1:
                    #ax.add_line(lines.Line2D(xdata=boxX,ydata=boxY,color=colors[currBigBox],linewidth=2,zorder=1000, label="area: " + str(currBigBox+1)))
                    isLastPrinted = True   

#for n bigger box (n = # of guesses), make the convex hulls
convexHullsForGuessAreas = []
for x in range(0, guesses):
    points = []
    for box in biggerBoxes[x]:
        points.append(Point(box.min_lat,box.max_lon))
        points.append(Point(box.max_lat,box.max_lon))
        points.append(Point(box.max_lat,box.min_lon))
        points.append(Point(box.min_lat,box.min_lon))
    convexHullsForGuessAreas.append(gpd.GeoSeries(points).unary_union.convex_hull)

#show convex hull of the guess areas:
for x in range(0, len(convexHullsForGuessAreas)):
    x_data = [elem[0] for elem in mapping(convexHullsForGuessAreas[x])['coordinates'][0]]
    y_data = [elem[1] for elem in mapping(convexHullsForGuessAreas[x])['coordinates'][0]]
    #ax.add_line(lines.Line2D(xdata=x_data,ydata=y_data,color=colors[x],linewidth=2, zorder=0, label="convex hull: " + str(currBigBox+1)))

#calculate the centroids
centroids = []
for x in range(0, len(convexHullsForGuessAreas)):
    centroids.append(convexHullsForGuessAreas[x].centroid)

#show centroids for the convex hulls of the areas
for x in range(0, len(centroids)):
    centroid = centroids[x]
    #ax.scatter(centroid.x, centroid.y, color=colors[x],s=180,zorder=1000, label="centroid: " + str(currBigBox+1))

#weights in each bigBox
bigBoxTotalWeight = totalWeight / guesses

#make an array for the new centroids
weightedCentroids = []

#make a linear interpolation from the centroid to every center of the boxes within it.
#the interpolation is calculated by: (dist * box_weight_percentage)
printed = False
for x in range(0, len(centroids)):
    centroid = (centroids[x].x, centroids[x].y)
    points = []
    for box in biggerBoxes[x]:
        box_center = ((box.min_lat + box.max_lat)/2.0, (box.min_lon + box.max_lon)/2.0)
        line = LineString([centroid, box_center])
        weightedMultiplier = (box.totalWeight / bigBoxTotalWeight)
        new_point = line.interpolate(weightedMultiplier, normalized=True)
        points.append((new_point.x, new_point.y))
        if printed == False and x == 1:
            ax.add_line(lines.Line2D(xdata=[centroid[0], box_center[0]],ydata=[centroid[1], box_center[1]],color=colors[x],linewidth=1, label='line from box to center of area: ' + str(x+1)))
            ax.scatter(new_point.x, new_point.y, color='white',s=10,zorder=1001, label="interpolated point")
        if printed == True:
            ax.add_line(lines.Line2D(xdata=[centroid[0], box_center[0]],ydata=[centroid[1], box_center[1]],color=colors[x],linewidth=1))
            ax.scatter(new_point.x, new_point.y, color='white',s=10,zorder=1001)
        printed = True
    printed = False
    weightedPoint = (statistics.mean(point[0] for point in points), statistics.mean(point[1] for point in points))
    weightedCentroids.append(weightedPoint)

#show centroids for the convex hulls of the areas
for x in range(0, len(weightedCentroids)):
    centroid = weightedCentroids[x]
    #ax.scatter(centroid[0], centroid[1], color=colors[x],s=100,zorder=1000)
    #ax.scatter(centroid[0], centroid[1], color='white',s=30,zorder=1001)

#show centerPoints
#centerPointsLat = [elem[0][0] for elem in centerPoints]
#centerPointsLon = [elem[0][1] for elem in centerPoints]
#ax.scatter(centerPointsLat, centerPointsLon, color="red",s=50,zorder=100, label='center point')

#draw and show
ax.legend(loc="upper left")
plt.draw()
plt.show()
