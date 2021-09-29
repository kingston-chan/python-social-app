from src.data_store import data_store
from src.error import InputError
import re

def auth_login_v1(email, password):
    store = data_store.get()
    users = store['users']

    if not dict_search(email, users, 'email'):
        raise InputError('Email does not exist')
    
    for u in users:
        if u['email'] == email and not u['password'] == password:
            raise InputError('Password is incorrect')
        elif u['email'] == email and u['password'] == password:
            return {'auth_user_id': u['id'],}


def auth_register_v1(email, password, name_first, name_last):
    
    # Check for all input conditions to be correct
    if re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email) and len(password) >= 6 and 1 <= len(name_first) <= 50 and 1 <= len(name_last) <= 50:
        
        store = data_store.get()

        users = store['users']

        if len(users) == 0: permission = 1
        else: permission = 2
        
        if dict_search(email, users, 'email'):
            raise InputError('Email is already being used by another user')
            

        # create a handle for the user
        handle = name_first.lower() + name_last.lower()
        handle = ''.join([x for x in handle if x.isalnum()])
        
        if len(handle) > 20:
            handle = handle[:20]

        # search the data store for existing handles and produce a handle that has not
        # been taken already
        i = -1
        handleCut = len(handle)
        while dict_search(handle, users, 'handle'):
            i += 1
            handle = handle[:handleCut]
            handle += str(i)

        # search the data store for existing u_id's and produce an id that has
        # not been taken already
        u_id = 1
        while dict_search(u_id, users, 'id'):
            u_id += 1

        # add all given data into a dictionary to be added to the data store
        user_dict = {'email': email, 'password': password, 'name_first': name_first, 'name_last': name_last, 'handle': handle, 'id': u_id, 'permission': permission}
        
        users.append(user_dict)
        
        data_store.set(store)

        
    # when any of the inputs are invalid raise an input error
    elif len(password) < 6:
        raise InputError('Password too short')
    
    elif 50 < len(name_first) < 1:
        raise InputError('First name too long or short')
    
    elif 50 < len(name_last) < 1:
        raise InputError('Last name too long or short')
    else:
        raise InputError('Email is an invalid format')

    return {
        'auth_user_id': u_id,
    }


# function to search the data store for duplicate items
def dict_search(item, users, type):
    for u in users:
        if u[type] == item:
            return 1