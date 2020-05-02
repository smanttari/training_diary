import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

from django.http import HttpResponse


def duration_to_string(h,mins):
    """ 
    Formats duration given in hours and minutes to string "hh:mm". 
    """
    if (h is None or np.isnan(h)) and (mins is None or np.isnan(mins)):
        return None
    if mins is None or np.isnan(mins):
        mins = '00'
    elif mins >= 60:
        h = coalesce(h,0) + int(mins/60)
        mins = '0{}'.format(int(mins % 60))[-2:]
    else:
        mins = '0{}'.format(int(mins))[-2:]
    if h is None or np.isnan(h):
        h = '00'
    else:
        h = '0{}'.format(int(h))[-2:]
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


def coalesce(x,val):
    """ Returns given value if x is None. """
    if x is None or pd.isnull(x):
        return val
    else:
        return x


def dataframe_to_dict(df):
    """
    Converts pandas dataframe to list of dicts.
    Dataframe index should be chart category and columns represent chart series.
    """
    data_list = []
    for index, row in df.iterrows():
        row_dict = {}
        row_dict['category'] = index
        row_dict['series'] = row.fillna('').to_dict()
        data_list.append(row_dict)
    return data_list


def dataframe_to_csv(df,filename):
    """ Returns Http-response containing csv-file converted from pandas dataframe """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
    df.to_csv(response,sep=';',header=True,index=False,encoding='utf-8')
    return response


def dataframe_to_excel(df,filename):
    """ Returns Http-response containing excel-file converted from pandas dataframe """
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}.xlsx"'.format(filename)
    wb = Workbook()
    ws = wb.active
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    wb.save(response)
    return response

def get_required_fields(model):
    """ Return list of required fields in given Django Model """
    required_fields = [f.name for f in model._meta.get_fields() if not getattr(f, 'blank', False) is True]
    return required_fields
