import pandas as pd
import numpy as np
import json

def duration_to_string(h,mins):
    """ 
    Formats duration given in hours and minutes to string "hh:mm". 
    """
    if (h is None or np.isnan(h)) and (mins is None or np.isnan(mins)):
        return None
    if h is None or np.isnan(h):
        h = '00'
    else:
        h = '0{}'.format(int(h))[-2:]
    if mins is None or np.isnan(mins):
        mins = '00'
    else:
        mins = '0{}'.format(int(mins))[-2:]
    return '{}:{}'.format(h,mins)


def duration_to_decimal(h,mins):
    """ 
    Calculates duration in hours (decimal) when given hours and minutes seperately. 
    """
    if h is None or np.isnan(h):
        h = 0
    if mins is None or np.isnan(mins):
        mins = 0
    hours = h + mins/60
    return hours


def speed_min_per_km(m,s):
    """ 
    Calculates speed in min/km when given minutes and seconds seperately. 
    """
    if m is None and s is None:
        speed_min_per_km = None
    elif m is None and s is not None:
        speed_min_per_km = s/60.0
    elif m is not None and s is None:
        speed_min_per_km = m
    else:
        speed_min_per_km = m + s/60.0
    return speed_min_per_km


def dataframe_to_json(df):
    """
    Converts pandas dataframe to json which is compatible with d3Charts.js.
    Dataframe index should be chart category and columns represent chart series.
    """
    data_list = []
    for index, row in df.iterrows():
        row_dict = {}
        row_dict['category'] = index
        row_dict['series'] = row.fillna('').to_dict()
        data_list.append(row_dict)
    return json.dumps(data_list)


def coalesce(x,val):
    """ Returns given value if x is None. """
    if x is None or pd.isnull(x):
        return val
    else:
        return x