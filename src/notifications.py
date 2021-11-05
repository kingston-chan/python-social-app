from src.data_store import data_store

def notifications_v1(auth_user_id):
    store = data_store.get()
    return_list = store["notifications"][auth_user_id][-20:]
    return return_list