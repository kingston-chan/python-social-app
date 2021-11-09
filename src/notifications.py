from src.data_store import data_store

def notifications_v1(auth_user_id):
    store = data_store.get()
    if auth_user_id in store["notifications"]:
        return list(reversed(store["notifications"][auth_user_id][-20:]))
    else:
        return []
