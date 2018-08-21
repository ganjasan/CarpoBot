import requests  
import datetime
import csv
from sklearn import neighbors
import numpy as np
import config
import telebot
import messages

bot = telebot.TeleBot(config.token)

@bot.message_handler(content_types=["text"])
def repeat_all_text_messages(message):
    bot.send_message(message.chat.id, messages.repeat_messages['ru']['no_repeat'])


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



class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def send_location(self, chat_id, lat, lng):
        params = {'chat_id': chat_id, 'latitude': lat, 'longitude': lng}
        method = 'sendLocation'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = {}

        return last_update


carpo_bot = BotHandler('630168364:AAGihSK-Jki5nMZfw6IdRQs-PEwaJpZ30Cw')  
now = datetime.datetime.now()

def main():  
    new_offset = None

    places = loadPlaces('places.csv')
    tree = getKDTree(places)

    while True:
        carpo_bot.get_updates(new_offset)

        last_update = carpo_bot.get_last_update()

        if last_update:

            last_update_id = last_update['update_id']
            #last_chat_text = last_update['message']['text'] if 'text' in last_update['message'] else ''
            last_chat_id = last_update['message']['chat']['id']
            last_chat_name = last_update['message']['chat']['first_name']

            user_location = last_update['message']['location'] if 'location' in last_update['message'] else {}

            if user_location:
                nearest_places_indexes = getNearestPlacesIndexes(tree, user_location['latitude'], user_location['longitude'], 0.3)
                
                for i in nearest_places_indexes[0]:
                    carpo_bot.send_message(last_chat_id, places[i]['title'] + '\n' + places[i]['info'])
                    carpo_bot.send_location(last_chat_id, places[i]['lat'], places[i]['lng'])

            new_offset = last_update_id + 1


if __name__ == '__main__':  
   bot.polling(none_stop=True)