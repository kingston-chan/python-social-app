import requests, pytest
from src.config import url

# Valid inputs

# Permission change from member to global owner is successful:
# Can join private channels
# Can remove users
# Can also change others permission

# Permission change from global owner to member is successful:
# Cannot join private channels
# Cannot remove users
# Cannot change others permission

# Invalid inputs

# InputError when any of:
      
# - u_id does not refer to a valid user
# - u_id refers to a user who is the only global owner and they are being demoted to a user
# - permission_id is invalid
      
# AccessError when:

# - the authorised user is not a global owner

# Invalid token

# Invalid session