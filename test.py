import requests  
import datetime
import csv
from sklearn import neighbors
import numpy as np

def loadPlaces(filename):

    with open(filename) as f:
        reader = csv.reader(f, delimiter=';', skipinitialspace=True)
        header = next(reader)
        places_dict_list = [dict(zip(header, map(str, row))) for row in reader]
        return places_dict_list

def getKDTree(places):
    coords = [[i['lat'], i['lng']] for i in places]
    X = np.array(coords)
    tree = neighbors.KDTree(X, leaf_size=2)

    return tree

def getNearestPlacesIndexes(tree, lat, lng, radius):
    return tree.query_radius([[lat, lng]], r=radius)


places = loadPlaces('places.csv')
tree = getKDTree(places)
coords = getNearestPlacesIndexes(tree, 59.944009, 30.295718, 0.3)
for i in coords[0]:
    print(i)