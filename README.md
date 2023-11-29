## Search service
https://github.com/prapeller/Async_API_sprint_2

- provides films search possibility by name/genre and other film properties


## Auth service
https://github.com/prapeller/Auth_sprint_2

- provides user session control by authentication/authorization


## UGC service
https://github.com/prapeller/ugc_sprint_2

- provides possibility for users collect and control their activity
- provides possibility for analytics team analise users activity, make business conclusions, and improve online cinema based on these conclusions


## Notification service
https://github.com/prapeller/notifications_sprint_1

- provides possibility for users to receive/not receive (switch off/on) notifications (email / telegram / interface)
- provides possibility for cinema to send notifications:

#### notes:
- 'pending messages' - messages that were created in db, but waiting till user's timezone will allow to deliver it 
- interface messages - messages that user can see at frontend
- message sending can be triggered by api call or by scheduler
- for triggering by scheduler - staff can create periodic tasks (repeating or single-time tasks) with 'crontab schedule' or 'interval schedule' and other settings
- after creating/updating periodic task - worker reloading not needed, scheduler will be updated dynamically
- for delivering 'pending messages' - staff must create periodic task (once an hour, for example) called 'check_availability_and_notify_pending_messages_all_task' 
- message text can have placeholders, for rendering individual user data, if placeholders are found in msg_text - notificator renders it with user data from other service db (auth_postgres)

#### 1) individual message (to single user). from system and other site services (site event based):
  > if triggered by api call: implementing can be by api main process (default) or queued worker process (optional with '?as_celery_task=true' query param)
  > as far as this is simple task - triggering preferred by api call, and default is set to implementing by api main process

- 1.1) to single user
  - by email to email only (user haven't confirmed account email yet and can't accept at interface/telegram), 
  - immediate message (doesn't depend on user's timezone)

- 1.2) to single user
  - by uuid to all communication ways (user confirmed account email and have access to accepting email/telegram/interface and turn on/off user.is_accepting_email/.is_accepting_telegram/.is_accepting_interface settings,)
  - immediate message (doesn't depend on user's timezone)

- 1.3) to single user
  - by uuid to all user's communication ways
  - message becomes pending (if user's timezone does not allow to send now, till scheduled 'pending-message-checker' delivers it)


#### 2) the same message (to many users). message text created 'scheduled_message_task' by staff in admin panel (they can create/update/list/read such tasks)
  > if triggered by api call: implementing can be by queued worker process (default) or api main process (optional with '?as_celery_task=false' query param)
  > as far as this is hard task - triggering preferred by scheduler, and default is set to implementing by queued worker process

- 2.1) to filtered users
  - by user_uuid_list (for example provided from analytics team, or from some filtering rules)
  - message becomes pending

- 2.2) to all users
  - by db select all existing user rows
  - message becomes pending


#### task priority in task queue:
- #1 - 1.1) Messages for confirmation something.. emailing for email confirmation or others having OTP)
- #2 - 1.2) Messages with Individual message body, immediate message
- #3 - 1.3) Messages with Individual message body, pending message
- #4 - Deliver_pending_messages_task, task to filter message_uuid_list by `message.priority` and launch another tasks with corresponding priority for sending all those messages from filtered uuid_list 
- #5 - 2.1) The same message body to filtered users, pending message
- #6 - 2.2) The same message body to all users, pending message


#### examples:

1.1) email
  - 'Hey, Pablo! Welcome to our cinema, here's your link to confirm email...', (from api_auth microservice, it has name already and can prepare email text that not needed to render user_data)

1.2) individual message, immediate
  - 'Hey, %user_name%! You successfully got your 'Premium' subscription!', (by api_billing microservice)

1.2) individual message, pending
  - '%user_name%, hey! your film_comment 'likes_sum' is > 10, you are popular commenter now!', (from ugc service, triggered by api call) 
  - '%user_name%, hey! your subscription is expiring soon, prolong it today and get discount 10%!', (from billing service, triggered by api call)
  - '%user_name%, hey! you have finished 3 'horror' genre films. you got new achievement "fearless"', (from ugc service, triggered by api call)

2.1) mass message, to filtered users, pending
  - '%user_name%, hey! don't miss october art-fest! buy a year of subscription and get a free 2 tickets to the cinema!', (from staff, triggered by scheduler)
  - '%user_name%, hey! happy birthday! wish you all the best, here are some great comedies for you! have fun and take care!', (from staff, triggered by scheduler)

2.2) mass message, to all users, pending
  - '%user%, hey! great news! this week we have released the following new movies: 'fifth element', 'terminator 2' and 'thor: ragnarok', (from staff, triggered by scheduler)
  - '%user%, hey! we offer you to spend this weekend without coming out to daylight: watch all 'lord of the rings' episodes and win free beer!', (from staff, triggered by scheduler)

# 1) Deploy locally (api at host)
- > make postgres-build-loc
- > make api-redis-build-loc
- > make api-rabbit-build-loc
- > cd api_notifications && python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements/local.txt
- > export DEBUG=True && export DOCKER=False && python main.py
- swagger docs can be found at 127.0.0.1:8083/docs
- restore there postgres with POST /api/v1/postgres/restore-from-dump choosing file ./api_notifications_postgres_dump and 'env' = 'local'
- > make django-build-loc
- > make django-superuser-loc
- django admin can be found at 127.0.0.1:89/admin

# 2) Deploy locally (api at docker container)
- > make build-loc
- if some services cant build bcz other unhealthy - try again make build-loc...
- swagger docs can be found at 127.0.0.1:83/docs
- > make django-superuser-loc
- django admin can be found at 127.0.0.1:89/admin


### Data storage volume estimation:
postgres_auth.public.user
- 1_000_000 users
