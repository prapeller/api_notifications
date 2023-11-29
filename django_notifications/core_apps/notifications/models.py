from django.db import models


def cronexp(field):
    return field if field not in ('', None) else '-'


class CrontabScheduleModel(models.Model):
    minute = models.CharField(max_length=240, blank=True, null=True)
    hour = models.CharField(max_length=96, blank=True, null=True)
    day_of_week = models.CharField(max_length=64, blank=True, null=True)
    day_of_month = models.CharField(max_length=124, blank=True, null=True)
    month_of_year = models.CharField(max_length=64, blank=True, null=True)
    timezone = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "public\".\"celery_crontab_schedule"

    def __str__(self):
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY) {5}'.format(
            cronexp(self.minute), cronexp(self.hour),
            cronexp(self.day_of_week), cronexp(self.day_of_month),
            cronexp(self.month_of_year), cronexp(str(self.timezone))
        )

    def __repr__(self):
        return str(self)


class IntervalScheduleModel(models.Model):
    every = models.IntegerField()
    period = models.CharField(max_length=24, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "public\".\"celery_interval_schedule"
        unique_together = (('every', 'period'),)

    def __str__(self):
        return f'{self.every} {self.period}'


class PeriodicTaskModel(models.Model):
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    task = models.CharField(max_length=255, blank=True, null=True)
    interval = models.ForeignKey(IntervalScheduleModel, models.DO_NOTHING, blank=True, null=True)
    crontab = models.ForeignKey(CrontabScheduleModel, models.DO_NOTHING, blank=True, null=True)
    args = models.TextField(blank=True, null=True)
    kwargs = models.TextField(blank=True, null=True)
    queue = models.CharField(max_length=255, blank=True, null=True)
    exchange = models.CharField(max_length=255, blank=True, null=True)
    routing_key = models.CharField(max_length=255, blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    one_off = models.BooleanField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField(blank=True, null=True)
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.IntegerField(default=0)
    date_changed = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        fmt = '{0.name}: {0.task} {{no schedule}}'
        if self.interval:
            fmt = '{0.name}: {0.task} every: {0.interval}'
        elif self.crontab:
            fmt = '{0.name}: {0.task} crontab: {0.crontab}'
        return fmt.format(self)

    class Meta:
        managed = False
        db_table = "public\".\"celery_periodic_task"
