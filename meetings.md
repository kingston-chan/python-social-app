Iteration 1

Taken from wiki from project-backend on gitlab

**23/09**
Meeting started: 2:00 pm
2:00 - 2:10 pm : discussing allocation of certain work through the first iteration of the assignment , this including completing stubbed function and creating dictionaries.
2:20 - 2:28 pm : Assigning (stubbed) functions to complete and writing there subsequent tests

auth_register_v1, auth_login_v1 : Julian Winzer
channel_join_v1, channel_invite_v1: Abbas Zaidi
channels_create_v1, channel_list_v1: Kingston Chan
channel_list_alll_v1, channel_detail_v1:Keefe Vuong
channel_messages_v1, clear_v1 : Josh Cruzado

2:35 - 2:45 pm : We listed and allocated all functions of iteration 1 to be allocated in the issues  under 'list'. Furthermore we organized what task are to be done and are being completed in the issue board.

**27/09**
meeting: 2:00 - 3:00 pm
2:00 - 2:40 The team discussed methods in how to proceed with the assignment showing each other the progress we've made with completing the stubbed functions of iteration 1 as well as discussing the timeline of how we are to progress with the assignment.

2:40 - 3:00 collectively worked on each part of the assignment


**3/10**
meeting: 6:00 - 6:25
6:00 - 6:15:
Reviewing each other's code style.
Checked that we followed the spec and haven't missed anything important.
6:15 - 6:25:
Fixed up any of the issues brought up and sent merge requests for those changes. (Waiting for pipelines to be fixed before merging into master)
Issues:

- Used camelCase instead of snake_case
- Added more assumptions

**Iteration 2**

Taken from wiki from project-backend on gitlab

**11/10**
meeting: 7:00 pm - 7:45 pm
- 7:00 pm - started talking about Iteration 2. About talking about changing the datastore.py with the additions of tokens as well as changing the clear function.
- 7:10 pm - talked about adding issues to the board.
- 7:15 pm - scheduled the stand-ups to be every third day.
- 7:20 pm - discussed the order of completing which functions. We decided to complete the version 2 functions then the version 1 functions, so it's familiar.
- 7:25 pm - decided on milestones. Set deadlines to ourselves. We made one: "By this Sunday, we need to finish all iteration 1 functions."
- 7:30 pm - we started working on our functions.

**16/10**
meeting: 8:00 pm - 9:15 pm

Agenda:

1. APP.route
    - Not just stubs
    - For now, just auth registration route

2. Token Generation
    - How to generate a token
    - How to implement token

3. Auth functions -> Julian

8:00 – 8:20 pm:
The meeting began by creating a agenda of what work is due in the very near future and targeted or most current problem which is figuring out the function auth/register/v2 app route so we can ultimately gain a better understanding of our tests and the subsequent implementation.
Completing 1st point in the agenda.
8:20 – 8:40 pm:
After looking through lecture materials and referencing lecture code we identified a type that involved arguments which was corrected to argument. Thus, after clearing up the typo error, we were able to generate and print a token which was essential to our tests and our implementation of iteration 2 functions. Completing 2nd point in the agenda. Completing 3rd point in the agenda.
8:40 – 9:15 pm:
We subsequently discussed app routes of channels/create/v2 as well as proceeded with debugging as well as incorporating tokens into testing and implementation.

**21/10**
meeting: 2:45 pm - 5:00 pm

2:45 - 3:15 = Discussing what bugs could be causing a loss in marks.
3:15 - 4:15 = Started to play with the frontend and look for any bugs.
4:15 - 4:30 = Found a few problems with the code regarding channel_addowner and channel_removeowner
4:30 - 5:00 = Fixed up the issues and merge requested it in before the leaderboards ran.

**Iteration 3**

Taken from wiki from project-backend on gitlab

Meeting 8th November 8pm
8:00pm - 8:20pm

We talked about user_profile_uploadphoto, Josh was in charge of this function.
There's a problem with changing the route from 'static' to 'imgurl'
As well as the location of the static/imgurl folder
Keefe assisted with it.
8:20pm - 8:50pm

Abbas and Kingston seperate from the group to work on the notifications function.
8:50pm - 9:10pm

The user_profile_uploadphoto problem was solved.
Abbas and Kingston came back.
Julian was working on user_stats_v1

