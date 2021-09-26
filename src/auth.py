from src.data_store import data_store
from src.error import InputError
import re

def auth_login_v1(email, password):
    return {
        'auth_user_id': 1,
    }

def auth_register_v1(email, password, name_first, name_last):
    
    if re.match(r"'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'", email) and len(password) >= 6 and 1 <= len(name_first) <= 50 and 1 <= len(name_last) <= 50:
        handle = name_first.lower() + name_last.lower()
        ''.join([x for x in handle if x.isalnum()])
        
        if len(handle) > 20:
            handle = handle[:20]

        store = data_store.get()

        if handle in store.items():
            pass


    else:
        raise InputError('Invalid registration')




    return {
        'auth_user_id': 1,
    }
