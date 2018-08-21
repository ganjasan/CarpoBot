import requests  
import datetime
import csv
from sklearn import neighbors
import numpy as np

import xml.etree.ElementTree as ET


ns = {'kml': 'http://www.opengis.net/kml/2.2'}

def loadPlacesFromKML(kml_filename):
    tree = ET.parse(kml_filename)
    root = tree.getroot()

    document = root.find("kml:Document", ns)

    folders = document.findall("kml:Folder", ns)

    places = {
        'Все заведения':[],
    }

    for folder in folders:
        folder_name = folder.find('kml:name',ns).text

        places[folder_name]  = []

        places_in_folder = folder.findall('kml:Placemark', ns)

        for placemark in places_in_folder:
            place = {}
            
            kml_name = placemark.find('kml:name',ns)
            place['name'] = kml_name.text if kml_name is not None else ''

            kml_description = placemark.find('kml:description', ns)
            place['description'] = kml_description.text if kml_description is not None else ''

            point = placemark.find('kml:Point', ns)

            if point is not None:
                kml_coords = point.find('kml:coordinates', ns)
                coords = kml_coords.text.strip().split(',') if kml_coords is not None else [0,0,0]
                place['lat'] = coords[0]
                place['lng'] = coords[1]

            places['Все заведения'].append(place)
            places[folder_name].append(place)

    return places


def getKDTrees(places):

    trees = {}

    for place_type in places.keys():
        coords = [[i['lat'], i['lng']] for i in places[place_type]]
        X = np.array(coords)
        tree = neighbors.KDTree(X, leaf_size=2)

        trees[place_type] = tree

    return trees

def getNearestPlacesIndexes(tree, lat, lng, neighbors_k ):
    dist, ind = tree.query([[lat, lng]], k=neighbors_k)

    return ind[0]



places = loadPlacesFromKML('places.kml')
trees = getKDTrees(places)

print (getNearestPlacesIndexes(trees['Все заведения'], 30.3164613, 59.9592536, 10))