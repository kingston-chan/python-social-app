from src.data_store import data_store

def notifications_v1(auth_user_id):
    store = data_store.get()
    if auth_user_id in store["notifications"]:
        notification_list = []
        for dicts in store["notifications"][auth_user_id]:
            notification_list.append(dicts["notification_message"])
            return_list = notification_list[-20:]
            return return_list
    else:
        store["notifications"][auth_user_id] = []
        return []
