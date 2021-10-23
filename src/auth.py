from src.data_store import data_store
from src.error import InputError
import hashlib, jwt, re, time

HASHCODE = "LKJNJLKOIHBOJHGIUFUTYRDUTRDSRESYTRDYOJJHBIUYTF"

def auth_login_v1(email, password):
    """
    Given a users email and password return their user id
    
    Arguments:
        email (string) - the email input by the user
        password (string) - the password input by the user

    Exceptions:
        InputError - occurs when the email does not exist in the data store or the 
        password does not match the email
        AccessError - does not occur in this function

    Return Value:
        Returns a dictionary containing the user id and a token if the user has succesfully logged in

    """
    
    
    store = data_store.get()
    users = store['users']
        
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # when the email is correct determine if the password matches
    for u in users:
        if u['email'] == email and not u['password'] == hashed_password:
            raise InputError('Password is incorrect')
        elif u['email'] == email and u['password'] == hashed_password:
            return {
                'auth_user_id': u['id'],
                'token': create_jwt(u['id'])
            }

    raise InputError('Email does not exist')


def auth_logout_v1(token):
    """
    Given a users token, invalidate it to log the user out 
    
    Arguments:
        token (string) - a token storing the following: {'user_id': 1, 'session_id': 1}

    Exceptions:
        None

    Return Value:
        Empty dictionary

    """
    
    store = data_store.get()
    
    token_dict = jwt.decode(token, HASHCODE, algorithms=['HS256'])

    user_id = token_dict["user_id"]
    user_session = token_dict["session_id"]
    time_created = token_dict["time_created"]
    
    store['sessions'][user_id].remove((user_session, time_created))
    data_store.set(store)
    
    return {}
    

def auth_register_v1(email, password, name_first, name_last):
    """
    Given a users email, password, first name and last name, generate a handle and return their user id
    
    Arguments:
        email (string) - the email input by the user
        password (string) - the password input by the user
        name_first (string) - the first name input by the user
        name_last (string) - the last name input by the user

    Exceptions:
        InputError - occurs if any of the following is satisfied:
            - the email does not follow the specified format
            - the password is shorter than 6 characters
            - the first name is not between 1 and 50 characters inclusive
            - the last name is not between 1 and 50 characters inclusive
        AccessError - does not occur in this function

    Return Value:
        Returns a dictionary containing the user id and a token
        Adds the following information to data_store in a dictionary:
            - email
            - password
            - name_first
            - name_last
            - handle
            - id
            - permission

    """

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
        handle_cut = len(handle)
        while dict_search(handle, users, 'handle'):
            i += 1
            handle = handle[:handle_cut]
            handle += str(i)


        # search the data store for existing u_id's and produce an id that has
        # not been taken already
        u_id = 1
        while dict_search(u_id, users, 'id'):
            u_id += 1

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # add all given data into a dictionary to be added to the data store
        user_dict = {'email': email, 'password': hashed_password, 'name_first': name_first, 'name_last': name_last, 'handle': handle, 'id': u_id, 'permission': permission}
        
        users.append(user_dict)
        
        data_store.set(store)

        
    # when any of the inputs are invalid raise an input error
    elif len(password) < 6:
        raise InputError('Password too short')
    
    elif not 1 <= len(name_first) <= 50:
        raise InputError('First name too long or short')
    
    elif not 1 <= len(name_last) <= 50:
        raise InputError('Last name too long or short')
    else:
        raise InputError('Email is an invalid format')
    
    return {
        'auth_user_id': u_id,
        'token': create_jwt(u_id)
    }


# helper function to search the data store for duplicate items
def dict_search(item, users, item_name):
    for u in users:
        if u[item_name] == item:
            return 1

# helper fucntion to create a session for the user
def create_session():
    store = data_store.get()
    store["session_count"] += 1
    data_store.set(store)
    return store["session_count"]

# helper function to create a jwt for the user given their u_id
def create_jwt(u_id):
    store = data_store.get()
    session_id = create_session()
    time_created = int(time.time())
    if u_id in store["sessions"]:
        store["sessions"][u_id].append((session_id, time_created))
    else:
        store["sessions"][u_id] = [(session_id, time_created)]
    data_store.set(store)
    payload = {
        'user_id': u_id,
        'session_id': session_id,
        'time_created': time_created
    }
    return jwt.encode(payload, HASHCODE, algorithm='HS256')
