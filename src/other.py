from src.data_store import data_store
import json
import os


def clear_v1():
    store = data_store.get()
    store['users'].clear()
    store['sessions'].clear()
    store['channels'].clear()
    store['channel_messages'].clear()
    store['dm_messages'].clear()
    store['dms'].clear()
    store["notifications"].clear()
    store['dm_id_gen'] = 0
    store['message_id_gen'] = 0
    store['session_count'] = 0
    store['img_count'] = 0
    store['password_reset_codes'].clear()
    store['metrics']['channels_exist'].clear()
    store['metrics']['dms_exist'].clear()
    store['metrics']['messages_exist'].clear()
    store['metrics']['utilization_rate'] = 0
    data_store.set(store)

    static_folder_path = "./imgurl/"
    for file in os.listdir(static_folder_path):
        print(file)
        if file != "default.jpg":
            file_path = os.path.join(static_folder_path, file)
            os.unlink(file_path)

def save():
    store = data_store.get()
    with open("datastore.json", "w") as FILE:
        json.dump(store, FILE)
