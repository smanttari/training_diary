from treenipaivakirja.models import harjoitus,aika,laji,tehot,tehoalue
from django.db.models import Sum,Max,Min

from datetime import datetime
import pandas as pd
import numpy as np
import json

def duration_to_string(h,mins):
    """ 
    Formats duration given in hours and minutes to single string. 
    """
    if h is None or np.isnan(h):
        h = 0
    if mins is None or np.isnan(mins):
        mins = 0
    h = str(int(h))
    mins = str(int(mins))
    if h == '0' and mins == '0':
        return ''
    elif mins == '0':
        return h + 'h'
    else:
        return '{}h {}min'.format(h,mins)


def h_min_to_hours(h,mins):
    """ 
    Calculates duration in hours (decimal) when given hours and minutes seperately. 
    """
    if h is None:
        h = 0
    if mins is None:
        mins = 0
    hours = h + mins/60
    return hours


def vauhti_min_km(m,s):
    """ 
    Calculates speed in min/km when given minutes and seconds seperately. 
    """
    if m is None and s is None:
        vauhti_min_km = None
    elif m is None and s is not None:
        vauhti_min_km = s/60.0
    elif m is not None and s is None:
        vauhti_min_km = m
    else:
        vauhti_min_km = m + s/60.0
    return vauhti_min_km


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
    if x is None:
        return val
    else:
        return x


def get_training_data(user_id):
    """
    Fetch training data from database and return cleaned pandas dataframe of it
    """
    startdate = harjoitus.objects.filter(user=user_id).aggregate(Min('pvm_fk_id'))['pvm_fk_id__min']
    if startdate is None:
        return None
    enddate = datetime.now().date().strftime('%Y%m%d')

    days = aika.objects.filter(vvvvkkpp__gte = int(startdate),vvvvkkpp__lte = int(enddate)
        ).values_list('pvm','vvvvkkpp','viikonpaiva_lyh','vko')
    days_df = pd.DataFrame(list(days), columns=['Pvm','vvvvkkpp','Viikonpäivä','Vko'])

    trainings = harjoitus.objects.filter(user=user_id).values_list(
        'id','id','pvm_fk_id','kesto','kesto_h','kesto_min','laji_fk__laji_nimi',
        'laji_fk__laji_ryhma','matka','vauhti_km_h','vauhti_min_km','keskisyke',
        'tuntuma','kommentti','nousu')

    trainings_df = pd.DataFrame(list(trainings), 
        columns = [
            'edit','delete','vvvvkkpp','Kesto (h)','Kesto_h','Kesto_min',
            'Laji','Lajiryhmä','Matka (km)','Vauhti (km/h)','Vauhti (min/km)',
            'Keskisyke','Tuntuma','Kommentti','Nousu (m)'
            ])

    trainings_df = days_df.merge(trainings_df, how='left', left_on='vvvvkkpp', right_on='vvvvkkpp')
    trainings_df['Laji'] = trainings_df['Laji'].fillna('Lepo')
    trainings_df.loc[trainings_df['Laji'] != 'Lepo','Lajiryhmä'] = trainings_df.loc[trainings_df['Laji'] != 'Lepo','Lajiryhmä'].fillna('Muut')
    
    # cleaning data
    trainings_df['Pvm'] = pd.to_datetime(trainings_df['Pvm'])
    trainings_df = trainings_df.sort_values(by='Pvm', ascending=False)
    trainings_df['Pvm'] = trainings_df['Pvm'].dt.strftime('%Y-%m-%d')
    trainings_df[['Kesto (h)','Matka (km)','Vauhti (km/h)','Vauhti (min/km)']] = trainings_df[['Kesto (h)','Matka (km)','Vauhti (km/h)','Vauhti (min/km)']].astype(float).round(1)
    trainings_df['Viikonpäivä'] = trainings_df['Viikonpäivä'].str.capitalize()
    trainings_df[['delete','edit','Keskisyke','Tuntuma','Nousu (m)']] = trainings_df[['delete','edit','Keskisyke','Tuntuma','Nousu (m)']].fillna(-1).astype(int).astype(str).replace('-1', np.nan)
    trainings_df['Päivä'] = trainings_df[['Pvm', 'Viikonpäivä']].apply(lambda x: ' '.join(x), axis=1)
    trainings_df['Kesto'] = trainings_df.apply(lambda row: duration_to_string(row['Kesto_h'], row['Kesto_min']), axis=1)

    # calculate duration per zone
    zones_duration = tehot.objects.filter(harjoitus_fk_id__user=user_id).values_list('harjoitus_fk_id','teho_id__teho','kesto_h','kesto_min')
    if zones_duration:
        zones_duration_df = pd.DataFrame(list(zones_duration),columns = ['id','teho','kesto_h','kesto_min'])
        zones_duration_df = zones_duration_df.fillna(np.nan)  #replace None with NaN
        zones_duration_df = zones_duration_df.groupby(['id','teho']).sum().reset_index()
        zones_duration_df['kesto'] = zones_duration_df.apply(lambda row: duration_to_string(row['kesto_h'], row['kesto_min']), axis=1)
        zones_duration_df = zones_duration_df.pivot(index='id', columns='teho', values='kesto')
        zones_duration_df.index = zones_duration_df.index.map(str)
        trainings_df = trainings_df.merge(zones_duration_df, how='left', left_on='edit', right_index=True)

    return trainings_df