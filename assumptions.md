Assumptions:

auth_register_v1:
- **accepts all characters for name_first, name_last and password, including leading and trailing whitespace**

channels_create_v1:
- **Cannot create channel with the same name (case sensitive)**
- **Trims trailing/leading whitespace characters in given name for the channel**
- Channel name accepts all characters
- Lists for owner_members and all_members are a list of the members id

channel_message_v1:
- **For Iteration 1, all channels are assumed to have no messages**

channel_invite_v1:
- **For iteration 1, none of the user id present in the users list of dictionary were ever equal in number value**

channel_join_v1:
- **For iteration 1, none of the channel id present in the channels list of dictionary were ever equal in number value**
