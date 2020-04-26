from datetime import datetime, timedelta

import pandas as pd

import treenipaivakirja.utils as utils
from treenipaivakirja.models import Harjoitus
from django.db.models import Sum, Avg, Min


def hours_year_to_date(user_id):
    current_day = datetime.now().date()
    hours = Harjoitus.objects.filter(
        user=user_id,
        aika__vuosi=current_day.year,
        aika__pvm__lte=current_day
        ).aggregate(Sum('kesto'))['kesto__sum']
    hours = float(utils.coalesce(hours,0))
    return hours


def hours_past_year_to_date(user_id):
    current_day = datetime.now().date()
    current_day_minus_365 = pd.Timestamp(current_day - timedelta(days=365))
    hours = Harjoitus.objects.filter(
        user=user_id,
        aika__vuosi=current_day.year-1,
        aika__pvm__lte=current_day_minus_365
        ).aggregate(Sum('kesto'))['kesto__sum']
    hours = float(utils.coalesce(hours,0))
    return hours


def total_hours_per_year(user_id,year):
    hours = Harjoitus.objects.filter(
        user=user_id,
        aika__vuosi=year
        ).aggregate(Sum('kesto'))['kesto__sum']
    hours = float(utils.coalesce(hours,0))
    return hours


def avg_feeling_per_period(user_id,start_date,end_date):
    feeling = Harjoitus.objects.filter(
        user=user_id,
        aika__pvm__gte=start_date,
        aika__pvm__lte=end_date,
        ).aggregate(Avg('tuntuma'))['tuntuma__avg']
    feeling = float(utils.coalesce(feeling,0))
    return feeling

def first_training_date(user_id):
    date = Harjoitus.objects.filter(user=user_id).aggregate(Min('aika__pvm'))['aika__pvm__min']
    return date