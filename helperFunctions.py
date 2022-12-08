from math import sin, cos, sqrt, atan2, radians
from numpy import random
from shapely.geometry import Point, mapping
import numpy as np

#extract lat,long and make list [[lat1,lat2,...],[lon1,lon2,...]] from Point
def pointsToListOfLatAndLongs(geom):
    lat = []
    lon = []
    for geo in geom:
        lat.append(geo.x)
        lon.append(geo.y)
    return [lat,lon]

#this method should return the nearest node by lat and lon - not following the graph!
def getNearestNode(guesses,goal):
    shortestDist = -1
    nearestNode = ()
    for x in range(0,len(guesses[0])):
        if shortestDist == -1:
            nearestNode = (guesses[0][x], guesses[1][x])
            shortestDist = getDistance(nearestNode, (goal[0][0], goal[1][0]))
        else: 
            if (getDistance((guesses[0][x], guesses[1][x]), (goal[0][0], goal[1][0]))) <= shortestDist:
                shortestDist = getDistance((guesses[0][x], guesses[1][x]), (goal[0][0], goal[1][0]))
                nearestNode = (guesses[0][x], guesses[1][x])
    return [shortestDist, nearestNode]

def getDistance(x,y):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(x[0])
    lon1 = radians(x[1])
    lat2 = radians(y[0])
    lon2 = radians(y[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

class FakeDoubleClickEvent( object ):
    def __init__ ( self ):
        self.dblclick = True

class Box( object ):
    def __init__ ( self, lat_range, lon_range, x, y ):
        self.min_lat, self.max_lat = lat_range
        self.min_lon, self.max_lon = lon_range
        self.totalWeight = 0
        self.points = []
        self.x = x
        self.y = y
        self.inside = True


def generate_random_point_within_convex_hull(number, polygon):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)
    return points

def makeGrid(grid_x,grid_y,convexHull):
    min_lat = 1000
    max_lat = -1000
    min_lon = 1000
    max_lon = -1000
    convexLat = [elem[0] for elem in mapping(convexHull)['coordinates'][0]]
    convexLon = [elem[1] for elem in mapping(convexHull)['coordinates'][0]]

    for lat in convexLat:
        if lat < min_lat:
            min_lat = lat
        if lat > max_lat:
            max_lat = lat   
    for lon in convexLon:
        if lon < min_lon:
            min_lon = lon
        if lon > max_lon:
            max_lon = lon

    lat_range = [ min_lat + (x * (max_lat-min_lat)/grid_x) for x in range(0, grid_x + 1) ]
    lon_range = [ min_lon + (x * (max_lon-min_lon)/grid_y) for x in range(0, grid_y + 1) ]

    boxes = []

    for latIndex in range(0, len(lat_range)-1):
        for lonIndex in range(0, len(lon_range)-1):
            boxes.append(Box((lat_range[latIndex], lat_range[latIndex+1]), (lon_range[lonIndex], lon_range[lonIndex+1]), latIndex, lonIndex))

    for box in boxes:
        b1 = convexHull.contains(Point(box.min_lat, box.max_lon))
        b2 = convexHull.contains(Point(box.max_lat, box.max_lon))
        b3 = convexHull.contains(Point(box.max_lat, box.min_lon))
        b4 = convexHull.contains(Point(box.min_lat, box.min_lon))
        if not b1 and not b2 and not b3 and not b4:
            box.inside = False
        
    return boxes

def placeInBoxes(centerPoints, boxes, dim):
    min_lat = boxes[0].min_lat
    max_lat = boxes[dim[0]*dim[1]-1].max_lat

    max_lon = boxes[dim[1]-1].max_lon
    min_lon = boxes[0].min_lon

    hits = 0
    gridTotalWeight = 0

    #search in boxes for fit (time complex. is dimLat times dimLon):
    for cp in centerPoints:
        lat,lon = cp[0]
        weight = cp[1]
        for x in range(0, len(boxes)):
            box = boxes[x]
            if (lat >= box.min_lat and lat <= box.max_lat and lon >= box.min_lon and lon <= box.max_lon):
                boxes[x].points.append(cp)
                boxes[x].totalWeight += weight
                hits+=1
                gridTotalWeight += weight
                break
            if x == len(boxes)-1:
                print(cp[0])

    #assert hits is equal to len(cp's)
    assert hits == len(centerPoints)

    #return the boxes
    return (boxes, gridTotalWeight)


      
