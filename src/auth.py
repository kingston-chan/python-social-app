from src.data_store import data_store
from src.error import InputError
from src import config
from string import digits, ascii_letters
from random import choice
import urllib.request
from src.config import url
import hashlib, jwt, re, secrets, time

# helper function to search the data store for duplicate items
def dict_search(item, users, item_name):
    return len(list(filter(lambda user: user[item_name] == item, users)))

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
    token_id = secrets.token_urlsafe()
    if u_id in store["sessions"]:
        store["sessions"][u_id].append((session_id, token_id))
    else:
        store["sessions"][u_id] = [(session_id, token_id)]
    data_store.set(store)
    payload = {
        'user_id': u_id,
        'session_id': session_id,
        'token_id': token_id
    }
    return jwt.encode(payload, config.hashcode, algorithm='HS256')

def store_new_password(user, email, password):
    if user["email"] == email:
        # Encrypt password
        user["password"] = hashlib.sha256(password.encode()).hexdigest()
    return user

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

    login_user = list(filter(lambda user: user["email"] == email, users))

    # No registered user corresponding to given email
    if not login_user:
        raise InputError(description='Email does not exist')
    # when the email is correct determine if the password matches
    if login_user[0]["password"] != hashed_password:
        raise InputError(description='Password is incorrect')

    return {
        'auth_user_id': login_user[0]['id'],
        'token': create_jwt(login_user[0]['id'])
    }

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
    
    token_dict = jwt.decode(token, config.hashcode, algorithms=['HS256'])

    user_id = token_dict["user_id"]
    user_session = token_dict["session_id"]
    token_id = token_dict["token_id"]
    
    store['sessions'][user_id].remove((user_session, token_id))
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
            raise InputError(description='Email is already being used by another user')
            

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
        user_dict = {
            'email': email, 
            'password': hashed_password, 
            'name_first': name_first, 
            'name_last': name_last, 
            'handle': handle, 
            'id': u_id, 
            'permission': permission,
            'user_metrics': {
                'channels_joined': [{'num_channels_joined': 0, 'time_stamp': int(time.time())}],
                'dms_joined': [{'num_dms_joined': 0, 'time_stamp': int(time.time())}], 
                'messages_sent': [{'num_messages_sent': 0, 'time_stamp': int(time.time())}], 
                'involvement_rate': None
            },
            'message_count': 0,
            'profile_img_url': f"{url}/imgurl/default.jpg"
        }
        
        users.append(user_dict)
        
        data_store.set(store)

        
    # when any of the inputs are invalid raise an input error
    elif len(password) < 6:
        raise InputError(description='Password too short')
    
    elif not 1 <= len(name_first) <= 50:
        raise InputError(description='First name too long or short')
    
    elif not 1 <= len(name_last) <= 50:
        raise InputError(description='Last name too long or short')
    else:
        raise InputError(description='Email is an invalid format')
    
    return {
        'auth_user_id': u_id,
        'token': create_jwt(u_id)
    }

def auth_passwordreset_reset_v1(reset_code, password):
    """
    Given a valid reset code corresponding to valid email, reset email's password with
    given password which is valid
    
    Arguments:
        reset_code (string) - reset_code given by user
        password (string) - password to change to given by user

    Exceptions:
        InputError - occurs if any of the following is satisfied:
            - the reset code is invalid i.e. does not correspond to any password reset request
            - the password is shorter than 6 characters

    Return Value:
        Returns empty dictionary on successful password reset
    """
    # Check given password is at least 6 characters
    if len(password) < 6:
        raise InputError(description="Password must be at least 6 characters")
    store = data_store.get()
    # Find email corresponding to reset code
    encoded_reset_code = hashlib.sha256(reset_code.encode()).hexdigest()
    email = [email for (email, code) in store["password_reset_codes"].items() if code == encoded_reset_code]
    # Check if no email is found corresponding to given reset code
    if not email:
        raise InputError(description="Invalid code")

    # Find user corresponding to email and store new password
    store["users"] = list(map(lambda user: store_new_password(user, email[0], password), store["users"]))

    # Remove reset code and email from dictionary so it cannot be used again
    store["password_reset_codes"] = {key: value for (key, value) in store["password_reset_codes"].items() if (key, value) != (email[0], encoded_reset_code)}
    data_store.set(store)
    return {}

def auth_passwordreset_request_v1(email):
    """
    Given an email, send them an email containing a specific secret code to
    reset their password.
    
    Arguments:
        email (string) - the email input by the user

    Exceptions:
        None

    Return Value:
        Retuns a secret code (string) if email is valid, i.e. email corresponds to user
        of Streams, else returns None
    """
    store = data_store.get()
    # Find user corresponding to email
    user = list(filter(lambda user: (user["email"] == email), store["users"]))
    # Email does not correspond to any user of Streams
    if len(user) == 0:
        return None

    user = user[0]
    # Log out all sessions for user
    store["sessions"][user["id"]].clear()
    # Generate a 5 alphanumeric code
    code = ''.join(choice(digits + ascii_letters) for i in range(6))
    # Store code with email
    store["password_reset_codes"][email] = hashlib.sha256(code.encode()).hexdigest()
    data_store.set(store)
    return code