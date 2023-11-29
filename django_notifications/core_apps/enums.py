from enum import Enum


class PeriodEnum(str, Enum):
    days = 'days'
    hours = 'hours'
    minutes = 'minutes'
    seconds = 'seconds'
    microseconds = 'microseconds'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class NotificatorCeleryTasksEnum(str, Enum):
    send_email_task = 'send_email_task'
    send_individual_immediate_message_task = 'send_individual_immediate_message_task'
    send_individual_pending_message_task = 'send_individual_pending_message_task'
    check_availability_and_notify_pending_messages_all_task = 'check_availability_and_notify_pending_messages_all_task'
    send_mass_message_to_filtered_users_task = 'send_mass_message_to_filtered_users_task'
    send_mass_message_to_all_users_task = 'send_mass_message_to_all_users_task'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
