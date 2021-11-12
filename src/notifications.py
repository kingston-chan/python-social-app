from src.data_store import data_store

def notifications_v1(auth_user_id):
    """
    Returns the last 20 notifications of a user, starting from
    most recent

    Arguments: 
        auth_user_id (integer) - ID to the user fetching the notifications

    Exceptions:
        None
        
    Return Value:
        Returns the last 20 notifications, starting from most recent. If
        user has no notifications, empty list is returned
    """
    store = data_store.get()
    if auth_user_id in store["notifications"]:
        return list(reversed(store["notifications"][auth_user_id][-20:]))
    else:
        return []

def store_notif(u_id, notification):
    """Helper function to store the notification for the user"""
    store = data_store.get()
    if u_id in store["notifications"]:
        store["notifications"][u_id].append(notification)
    else:
        store["notifications"][u_id] = [notification]
    data_store.set(store)