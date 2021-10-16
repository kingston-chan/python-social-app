from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'].clear()
    store['sessions'].clear()
    store['dms'].clear()
    store['channels'].clear()
    store['message_count'] = 0
    store['session_count'] = 0
    data_store.set(store)
