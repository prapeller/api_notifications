from enum import Enum


class EnvEnum(str, Enum):
    local = 'local'
    docker_compose_local = 'docker-compose-local'
    prod = 'prod'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class UserDataRenderPlaceholdersEnum(str, Enum):
    user_name = '%user_name%'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class ResponseDetailEnum(str, Enum):
    ok = 'ok'
    unauthorized = 'Unauthorized for this action.'
    bad_request = 'Bad reqeust.'
    auth_postgres_error = 'Unable to get info from auth_postgres: '
    not_valid_placeholders = (f'Only the following placeholders are valid:'
                              f'{[p.value for p in UserDataRenderPlaceholdersEnum]}. '
                              f'Not valid placeholders were found:')

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class OrderEnum(str, Enum):
    asc = 'asc'
    desc = 'desc'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class ServicesNamesEnum(str, Enum):
    api_auth = 'api_auth'
    api_ugc = 'api_ugc'
    api_search = 'api_search'
    api_billing = 'api_billing'
    django_notifications = 'django_notifications'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class PeriodEnum(str, Enum):
    days = 'days'
    hours = 'hours'
    minutes = 'minutes'
    seconds = 'seconds'
    microseconds = 'microseconds'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class TaskPriorityEnum(int, Enum):
    email_task_priority = 1
    individual_immediate_message_task_priority = 2
    individual_pending_message_task_priority = 3
    check_pending_messages_task_priority = 4
    mass_message_for_filtered_users_task_priority = 5
    mass_message_for_all_users_task_priority = 6

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class MessagePriorityEnum(int, Enum):
    individual_immediate = TaskPriorityEnum.individual_immediate_message_task_priority
    individual_pending = TaskPriorityEnum.individual_pending_message_task_priority
    mass_filtered_users = TaskPriorityEnum.mass_message_for_filtered_users_task_priority
    mass_all_users = TaskPriorityEnum.mass_message_for_all_users_task_priority

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class NotificatorCeleryTasksEnum(str, Enum):
    send_email_task = 'send_email_task'
    send_individual_immediate_message_task = 'send_individual_immediate_message_task'
    send_individual_pending_message_task = 'send_individual_pending_message_task'
    check_availability_and_notify_pending_messages_all_task = 'check_availability_and_notify_pending_messages_all_task'
    send_mass_message_to_filtered_users_task = 'send_mass_message_to_filtered_users_task'
    send_mass_message_to_all_users_task = 'send_mass_message_to_all_users_task'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class UTCTimeZonesEnum(str, Enum):
    utc_p14 = "UTC+14"
    utc_p13 = "UTC+13"
    utc_p12 = "UTC+12"
    utc_p11 = "UTC+11"
    utc_p10 = "UTC+10"
    utc_p09 = "UTC+9"
    utc_p08 = "UTC+8"
    utc_p07 = "UTC+7"
    utc_p06 = "UTC+6"
    utc_p05 = "UTC+5"
    utc_p04 = "UTC+4"
    utc_p03 = "UTC+3"
    utc_p02 = "UTC+2"
    utc_p01 = "UTC+1"
    utc_p00 = "UTC+0"
    utc_m01 = "UTC−1"
    utc_m02 = "UTC−2"
    utc_m03 = "UTC−3"
    utc_m04 = "UTC−4"
    utc_m05 = "UTC−5"
    utc_m06 = "UTC−6"
    utc_m07 = "UTC−7"
    utc_m08 = "UTC−8"
    utc_m09 = "UTC−9"
    utc_m10 = "UTC−10"
    utc_m11 = "UTC−11"
    utc_m12 = "UTC−12"

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)
