import http
import json

import pytz
import requests
from django import forms
from django.conf import settings
from django.contrib import admin, messages

from core_apps.enums import PeriodEnum, NotificatorCeleryTasksEnum
from core_apps.notifications.models import PeriodicTaskModel

PERIODIC_TASKS_URL = (f'http://{settings.API_NOTIFICATIONS_HOST}:{settings.API_NOTIFICATIONS_PORT}/'
                      f'api/v1/microservices-tasks/periodic-tasks')


class PeriodicTaskAdminForm(forms.ModelForm):
    # overrided PeriodicTaskModel fields:
    enabled = forms.BooleanField(label='enabled', required=False, initial=True)
    task = forms.ChoiceField(label='task', required=True,
                             choices=[(e.name, e.value) for e in NotificatorCeleryTasksEnum])
    # expires = forms.DateTimeField(widget=AdminSplitDateTime(), required=False)
    # start_time = forms.DateTimeField(widget=AdminSplitDateTime(), required=False)

    # form fields for sending as interval
    every = forms.IntegerField(label='every', required=False)
    period = forms.ChoiceField(label='period', required=False, choices=[(e.name, e.value) for e in PeriodEnum])

    # form fields for sending as crontab
    minute = forms.CharField(label='minute', required=False)
    hour = forms.CharField(label='hour', required=False)
    day_of_week = forms.CharField(label='day_of_week', required=False)
    day_of_month = forms.CharField(label='day_of_month', required=False)
    month_of_year = forms.CharField(label='month_of_year', required=False)

    # form fields for sending as kwargs
    email_to = forms.CharField(label='email_to', required=False)
    user_uuid = forms.CharField(label='user_uuid', required=False)
    user_uuid_list = forms.CharField(label='user_uuid_list', required=False)
    msg_text = forms.CharField(label='msg_text', required=False)

    class Meta:
        model = PeriodicTaskModel
        # list PeriodicTaskModel fields
        fields = ('name', 'task', 'description', 'interval', 'crontab', 'expires',
                  'start_time', 'enabled', 'last_run_at', 'total_run_count')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance is not None:
            if instance.enabled is not None:
                self.fields['enabled'].initial = instance.enabled
            if instance.kwargs is not None:
                try:
                    kwargs_data = json.loads(instance.kwargs)
                    email_to = kwargs_data.get('email_to', '')
                    user_uuid = kwargs_data.get('user_uuid', '')
                    user_uuid_list = kwargs_data.get('user_uuid_list', '')
                    msg_text = kwargs_data.get('msg_text', '')
                    self.fields['msg_text'].initial = msg_text
                    self.fields['email_to'].initial = email_to
                    self.fields['user_uuid'].initial = user_uuid
                    self.fields['user_uuid_list'].initial = user_uuid_list
                except json.JSONDecodeError:
                    raise ValueError("PeriodicTaskAdminForm can't load msg_text/email_to/user_uuid/user_uuid_list")

            if instance.interval is not None:
                self.fields['every'].initial = instance.interval.every
                self.fields['period'].initial = instance.interval.period
            if instance.crontab is not None:
                self.fields['minute'].initial = instance.crontab.minute
                self.fields['hour'].initial = instance.crontab.hour
                self.fields['day_of_week'].initial = instance.crontab.day_of_week
                self.fields['day_of_month'].initial = instance.crontab.day_of_month
                self.fields['month_of_year'].initial = instance.crontab.month_of_year


def enable_selected(modeladmin, request, queryset):
    headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
               'Service-Name': 'django_notifications'}
    # Bulk enable
    failed_updates = []
    for obj in queryset:
        obj_data = {'enabled': True,
                    'interval_id': obj.interval.id if obj.interval else None,
                    'crontab_id': obj.crontab.id if obj.crontab else None,
                    'args': obj.args,
                    'kwargs': obj.kwargs,
                    'queue': obj.queue,
                    'priority': obj.priority,
                    'description': obj.description,
                    'expires': obj.expires,
                    'start_time': obj.start_time}
        resp = requests.put(f'{PERIODIC_TASKS_URL}/{obj.id}',
                            headers=headers,
                            json=obj_data)
        if resp.status_code != http.HTTPStatus.OK:
            failed_updates.append(f'{str(obj)}: {resp.text}')
    if not failed_updates:
        messages.success(request, 'All selected tasks have been successfully enabled.')
    else:
        messages.error(request, f'Failed to enable: {", ".join(failed_updates)}')


def disable_selected(modeladmin, request, queryset):
    """Override to delete like set 'enabled=False' for every of tasks."""
    headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
               'Service-Name': 'django_notifications'}
    # Bulk disable
    failed_updates = []
    for obj in queryset:
        obj_data = {'enabled': False,
                    'interval_id': obj.interval.id if obj.interval else None,
                    'crontab_id': obj.crontab.id if obj.crontab else None,
                    'args': obj.args,
                    'kwargs': obj.kwargs,
                    'queue': obj.queue,
                    'priority': obj.priority,
                    'description': obj.description,
                    'expires': obj.expires,
                    'start_time': obj.start_time}
        resp = requests.put(f'{PERIODIC_TASKS_URL}/{obj.id}',
                            headers=headers,
                            json=obj_data)
        if resp.status_code != http.HTTPStatus.OK:
            failed_updates.append(f'{str(obj)}: {resp.text}')
    if not failed_updates:
        messages.success(request, 'All selected tasks have been successfully disabled.')
    else:
        messages.error(request, f'Failed to disable: {", ".join(failed_updates)}')


@admin.register(PeriodicTaskModel)
class PeriodicTaskModelAdmin(admin.ModelAdmin):
    form = PeriodicTaskAdminForm
    readonly_fields = ('last_run_at', 'total_run_count', 'interval', 'crontab')
    actions = (enable_selected, disable_selected)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        # save periodic_task with api call (use django like frontend only :)

        headers = {'Authorization': settings.SERVICE_TO_SERVICE_SECRET,
                   'Service-Name': 'django_notifications'}

        # pickup common fields data
        task = form.cleaned_data.get('task')
        name = form.cleaned_data.get('name')
        enabled = form.cleaned_data.get('enabled')

        data = {
            'name': name,
            'task': task,
            'enabled': enabled,
        }
        description = form.cleaned_data.get('description')
        if description is not None:
            data.update({'description': description})

        django_server_tz = pytz.timezone(settings.TIME_ZONE)
        expires = form.cleaned_data.get('expires')
        if expires is not None and expires != '':
            expires = expires.astimezone(django_server_tz).isoformat()
        data.update({'expires': expires})

        start_time = form.cleaned_data.get('start_time')
        if start_time is not None and start_time != '':
            start_time = start_time.astimezone(django_server_tz).isoformat()
        data.update({'start_time': start_time})

        # pickup interval/crontab data, should be filled or with interval or with crontab (not both)
        every = form.cleaned_data.get('every')
        period = form.cleaned_data.get('period')
        minute = form.cleaned_data.get('minute')
        hour = form.cleaned_data.get('hour')
        day_of_week = form.cleaned_data.get('day_of_week')
        day_of_month = form.cleaned_data.get('day_of_month')
        month_of_year = form.cleaned_data.get('month_of_year')

        if all((every, period)):
            data.update({'interval': {'every': every, 'period': period}})
        elif all((minute, hour, day_of_week, day_of_month, month_of_year)):
            data.update({'crontab': {'minute': minute, 'hour': hour, 'day_of_week': day_of_week,
                                     'day_of_month': day_of_month, 'month_of_year': month_of_year}})
        else:
            messages.error(request, 'or all of (every, period) or all of (minute, hour, day_of_week, '
                                    'day_of_month, month_of_year) must be provided')
            return

        # pickup periodic_task.kwargs data
        msg_text = form.cleaned_data.get('msg_text')
        email_to = form.cleaned_data.get('email_to')
        user_uuid = form.cleaned_data.get('user_uuid')
        user_uuid_list = form.cleaned_data.get('user_uuid_list')

        if task == NotificatorCeleryTasksEnum.send_email_task:
            data.update({'kwargs': json.dumps({'email_to': email_to, 'msg_text': msg_text})})

        elif (task == NotificatorCeleryTasksEnum.send_individual_immediate_message_task
              or task == NotificatorCeleryTasksEnum.send_individual_pending_message_task):
            data.update({'kwargs': json.dumps({'user_uuid': user_uuid, 'msg_text': msg_text})})

        elif task == NotificatorCeleryTasksEnum.send_mass_message_to_filtered_users_task:
            data.update({'kwargs': json.dumps({'user_uuid_list': user_uuid_list, 'msg_text': msg_text})})

        elif task == NotificatorCeleryTasksEnum.send_mass_message_to_all_users_task:
            data.update({'kwargs': json.dumps({'msg_text': msg_text})})

        # aka 'frontend' sends request to aka 'backend'
        if change:
            resp = requests.put(f'{PERIODIC_TASKS_URL}/{obj.id}', json=data, headers=headers)
        else:
            resp = requests.post(PERIODIC_TASKS_URL, json=data, headers=headers)

        if resp.status_code == http.HTTPStatus.OK:
            messages.success(request, f'{resp.text}')
        else:
            messages.error(request, f'{resp.text}')

    def delete_model(self, request, obj):
        disable_selected(self, request, [obj])

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = super().get_queryset(request)
        enabled_queryset = qs.filter(enabled=True)
        disabled_queryset = qs.filter(enabled=False)
        extra_context['enabled_queryset'] = enabled_queryset
        extra_context['disabled_queryset'] = disabled_queryset
        return super().changelist_view(request, extra_context=extra_context)
