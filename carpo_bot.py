import requests  
import datetime

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
            last_update = get_result[len(get_result)]

        return last_update


carpo_bot = BotHandler('630168364:AAGihSK-Jki5nMZfw6IdRQs-PEwaJpZ30Cw')  
now = datetime.datetime.now()


def main():  
    new_offset = None

    while True:
        carpo_bot.get_updates(new_offset)

        last_update = carpo_bot.get_last_update()

        last_update_id = last_update['update_id']
        #last_chat_text = last_update['message']['text'] if 'text' in last_update['message'] else ''
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']

        carpo_bot.send_message(last_chat_id, str(last_update))

        new_offset = last_update_id + 1

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()