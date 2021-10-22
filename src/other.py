from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'].clear()
    store['sessions'].clear()
    store['channels'].clear()
    store['channel_messages'].clear()
    store['dm_messages'].clear()
    store['dms'].clear()
    store['dm_id_gen'] = 0
    store['message_id_gen'] = 0
    store['session_count'] = 0
    data_store.set(store)
