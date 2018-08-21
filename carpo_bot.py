import requests  
import datetime
from sklearn import neighbors
import numpy as np
import xml.etree.ElementTree as ET
import config
import telebot
import messages

# loader
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
                place['lat'] = coords[1]
                place['lng'] = coords[0]

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

bot = telebot.TeleBot(config.token)

places = loadPlacesFromKML(config.places_kml_file)
trees = getKDTrees(places)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, messages.repeat_messages['ru']['help'])

@bot.message_handler(content_types=["text"])
def repeat_all_text_messages(message):
    bot.send_message(message.chat.id, messages.repeat_messages['ru']['no_repeat'])

@bot.message_handler(content_types=["location"])
def send_nearest_places(message):
    location = message.location

    keyboard = telebot.types.InlineKeyboardMarkup()

    for place_type in places.keys():
        button = telebot.types.InlineKeyboardButton(text = place_type, callback_data = place_type)
        keyboard.add(button)

    bot.send_message(message.chat.id, messages.repeat_messages['ru']['place_type_repeat'], reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    place_type = call.data

    nearest_places_indexes = getNearestPlacesIndexes(trees['Все заведения'], 59.943996 , 30.295759 , 5)
    
    for i in nearest_places_indexes:
        nearest_place = places['Все заведения'][i]

        bot.send_message(call.message.chat.id, nearest_place['name'] + '\n' + nearest_place['description'])
        bot.send_location(call.message.chat.id, nearest_place['lat'], nearest_place['lng'])


#main

if __name__ == '__main__':
   bot.polling(none_stop=True)