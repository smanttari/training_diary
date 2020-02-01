from treenipaivakirja.models import harjoitus, aika, laji, teho, tehoalue, kausi
from django.db.models import Sum, Max, Min

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
    elif h == '0':
        return mins + 'min'
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
    if x is None or pd.isnull(x):
        return val
    else:
        return x


def trainings_datatable(user_id):
    """
    Fetch training data from database and return cleaned pandas dataframe of it
    """
    startdate = harjoitus.objects.filter(user=user_id).aggregate(Min('aika_id'))['aika_id__min']
    if startdate is None:
        return None
    enddate = datetime.now().date().strftime('%Y%m%d')

    days = aika.objects.filter(vvvvkkpp__gte = int(startdate),vvvvkkpp__lte = int(enddate)
        ).values_list('pvm','vvvvkkpp','viikonpaiva_lyh','vko')
    days_df = pd.DataFrame(list(days), columns=['Pvm','vvvvkkpp','Viikonpäivä','Vko'])

    trainings = harjoitus.objects.filter(user=user_id).values_list(
        'id','id','aika_id','kesto','kesto_h','kesto_min','laji__laji_nimi',
        'laji__laji_ryhma','matka','vauhti_km_h','vauhti_min_km','keskisyke',
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
    zones = teho.objects.filter(harjoitus_id__user=user_id).values_list('harjoitus_id','tehoalue_id__tehoalue','kesto_h','kesto_min')
    if zones:
        zones_df = pd.DataFrame(list(zones),columns = ['id','teho','kesto_h','kesto_min'])
        zones_df = zones_df.fillna(np.nan)  #replace None with NaN
        zones_df = zones_df.groupby(['id','teho']).sum().reset_index()
        zones_df['kesto'] = zones_df.apply(lambda row: duration_to_string(row['kesto_h'], row['kesto_min']), axis=1)
        zones_df = zones_df.pivot(index='id', columns='teho', values='kesto')
        zones_df.index = zones_df.index.map(str)
        trainings_df = trainings_df.merge(zones_df, how='left', left_on='edit', right_index=True)

    return trainings_df


def sports_dict(user_id):
    sports = {}
    sports['Kaikki'] = []
    other = []
    laji_set = laji.objects.filter(user=user_id)
    if laji_set:
        for l in laji_set:
            if l.laji_ryhma is None or l.laji_ryhma == '':
                other.append(l.laji_nimi)
            else:
                if l.laji_ryhma not in sports.keys():
                    sports[l.laji_ryhma] = []
                sports[l.laji_ryhma].append(l.laji_nimi)
    sports['Muut'] = other
    return sports


def sports_list(user_id):
    sports = laji.objects.filter(user=user_id).values_list('laji_nimi',flat=True).order_by('laji_nimi')
    return list(sports)


def trainings(user_id):
    trainings_objects = harjoitus.objects.filter(user=user_id).values_list(
        'id','pvm','kesto','matka','aika_id__vuosi','aika_id__kk','aika_id__kk_nimi',
        'aika_id__vko','aika_id__hiihtokausi','laji_id__laji_nimi',
        'laji_id__laji','laji_id__laji_ryhma','vauhti_km_h','vauhti_min_km','keskisyke')
    trainings_df = pd.DataFrame(list(trainings_objects), 
        columns = [
            'id','pvm','kesto','matka','vuosi','kk','kk_nimi','vko','hiihtokausi',
            'laji_nimi','laji','laji_ryhma','vauhti_km_h','vauhti_min_km','keskisyke'
            ])
    trainings_df = trainings_df.fillna(np.nan)  #replace None with NaN
    trainings_df['vuosi'] = trainings_df['vuosi'].astype(str)
    trainings_df['pvm'] = pd.to_datetime(trainings_df['pvm'])
    trainings_df[['kesto','matka','vauhti_km_h','vauhti_min_km']] = trainings_df[['kesto','matka','vauhti_km_h','vauhti_min_km']].astype(float)
    trainings_df['laji_ryhma'] = trainings_df['laji_ryhma'].fillna('Muut')
    # lookup season
    season_objects = kausi.objects.filter(user=user_id)
    date = []
    season = []
    for i in season_objects:
        date_range = pd.date_range(start=i.alkupvm, end=i.loppupvm).tolist()
        date += date_range
        season += ([i.kausi] * len(date_range))
    seasons_df = pd.DataFrame.from_dict({'kausi':season, 'pvm':date})
    seasons_df = seasons_df.drop_duplicates(subset='pvm', keep='first') # remove overlapping seasons
    trainings_df = trainings_df.merge(seasons_df, how='left', left_on='pvm', right_on='pvm', suffixes=('', '_y'))
    return trainings_df


def trainings_per_season(trainings_df):
    trainings_per_season = trainings_df.groupby('kausi').sum().reset_index()[['kausi','kesto', 'matka']]
    trainings_per_season[['kesto','matka']] = trainings_per_season[['kesto','matka']].round(0)
    return trainings_per_season


def trainings_per_year(trainings_df):
    trainings_per_year = trainings_df.groupby('vuosi').sum().reset_index()[['vuosi','kesto', 'matka']]
    trainings_per_year[['kesto','matka']] = trainings_per_year[['kesto','matka']].round(0)
    return trainings_per_year


def trainings_per_month(trainings_df,user_id):
    current_day = datetime.now().date()
    current_year = str(current_day.year)
    current_month = str(current_day.strftime("%m"))
    first_day_yyyymmdd = harjoitus.objects.filter(user=user_id).aggregate(Min('aika_id'))['aika_id__min']
    years_months = aika.objects.filter(vvvvkkpp__gte = first_day_yyyymmdd, vvvvkkpp__lte = current_year + '1231').values_list('vuosi','kk').distinct()
    years_months = pd.DataFrame(list(years_months), columns=['vuosi','kk'])
    years_months['vuosi'] = years_months['vuosi'].astype(str)
    trainings_per_month = trainings_df.groupby(['vuosi','kk']).sum().reset_index()[['vuosi','kk','kesto','matka']]
    trainings_per_month = years_months.merge(trainings_per_month,how='left',right_on=['vuosi','kk'],left_on=['vuosi','kk'])
    trainings_per_month[['kesto','matka']] = trainings_per_month[['kesto','matka']].round(0)
    trainings_per_month[(trainings_per_month['vuosi'] < current_year) | (trainings_per_month['kk'] <= int(current_month))] = trainings_per_month[(trainings_per_month['vuosi'] < current_year) | (trainings_per_month['kk'] <= int(current_month))].fillna(0)
    return trainings_per_month


def trainings_per_week(trainings_df,user_id):
    current_day = datetime.now().date()
    current_year = str(current_day.year)
    current_week = str(current_day.strftime("%V"))
    first_day_yyyymmdd = harjoitus.objects.filter(user=user_id).aggregate(Min('aika_id'))['aika_id__min']
    years_weeks = aika.objects.filter(vvvvkkpp__gte = first_day_yyyymmdd, vvvvkkpp__lte = current_year + '1231').values_list('vuosi','vko').distinct()
    years_weeks = pd.DataFrame(list(years_weeks), columns=['vuosi','vko'])
    years_weeks['vuosi'] = years_weeks['vuosi'].astype(str)
    trainings_per_week = trainings_df.groupby(['vuosi','vko']).sum().reset_index()[['vuosi','vko','kesto','matka']]
    trainings_per_week = years_weeks.merge(trainings_per_week,how='left',right_on=['vuosi','vko'],left_on=['vuosi','vko'])
    trainings_per_week[['kesto','matka']] = trainings_per_week[['kesto','matka']].round(1)
    trainings_per_week[(trainings_per_week['vuosi'] < current_year) | (trainings_per_week['vko'] <= int(current_week))] = trainings_per_week[(trainings_per_week['vuosi'] < current_year) | (trainings_per_week['vko'] <= int(current_week))].fillna(0)
    return trainings_per_week


def hours_per_season(trainings_per_season):
    hours_per_season = trainings_per_season[['kausi','kesto']].rename(columns={'kausi': 'category', 'kesto': 'series'})
    return hours_per_season.to_json(orient='records')


def hours_per_year(trainings_per_year):
    hours_per_year = trainings_per_year[['vuosi','kesto']].rename(columns={'vuosi': 'category', 'kesto': 'series'})
    return hours_per_year.to_json(orient='records')


def hours_per_month(trainings_per_month):
    month_names = dict(aika.objects.values_list('kk','kk_nimi').distinct())
    hours_per_month_pivot = trainings_per_month.pivot(index='kk',columns='vuosi',values='kesto').sort_values(by='kk').rename(index = month_names)
    return dataframe_to_json(hours_per_month_pivot)


def hours_per_week(trainings_per_week):
    hours_per_week_pivot = trainings_per_week.pivot(index='vko',columns='vuosi',values='kesto').sort_values(by='vko')
    return dataframe_to_json(hours_per_week_pivot)


def kilometers_per_season(trainings_per_season):
    kilometers_per_season = trainings_per_season[['kausi','matka']].rename(columns={'kausi': 'category', 'matka': 'series'})
    return kilometers_per_season.to_json(orient='records')


def kilometers_per_year(trainings_per_year):
    kilometers_per_year = trainings_per_year[['vuosi','matka']].rename(columns={'vuosi': 'category', 'matka': 'series'})
    return kilometers_per_year.to_json(orient='records')


def hours_per_sport(trainings_df):
    hours_per_sport = trainings_df.groupby(['vuosi','laji_nimi']).sum().reset_index()[['vuosi','laji_nimi','kesto']].round(1)
    hours_per_sport_pivot = hours_per_sport.pivot(index='laji_nimi',columns='vuosi',values='kesto').sort_values(by='laji_nimi') 
    return dataframe_to_json(hours_per_sport_pivot)


def hours_per_sport_group(trainings_df):
    hours_per_sport_group = trainings_df.groupby(['vuosi','laji_ryhma']).sum().reset_index()[['vuosi','laji_ryhma','kesto']].round(1)
    hours_per_sport_group_pivot = hours_per_sport_group.pivot(index='laji_ryhma',columns='vuosi',values='kesto').sort_values(by='laji_ryhma') 
    return dataframe_to_json(hours_per_sport_group_pivot)


def trainings_per_sport(trainings_df, by):
    f = {'laji':['count'], 'kesto':['sum','mean'], 'matka':['sum','mean'], 'vauhti_km_h':['mean'], 'vauhti_min_km':['mean'], 'keskisyke':['mean']}
    trainings_per_sport = trainings_df.groupby([by,'laji_nimi']).agg(f).round(1).reset_index(1)
    trainings_per_sport.columns = ['_'.join(tup).rstrip('_') for tup in trainings_per_sport.columns.values]
    trainings_per_sport = trainings_per_sport.reset_index()
    trainings_per_sport = trainings_per_sport.rename(columns={
        'laji_count':'lkm', 'kesto_sum':'kesto (h)', 'kesto_mean':'kesto (h) ka.',
        'matka_sum':'matka (km)', 'matka_mean':'matka (km) ka.', 'vauhti_km_h_mean':'vauhti (km/h)',
        'vauhti_min_km_mean':'vauhti (min/km)','keskisyke_mean':'keskisyke'
        })
    return trainings_per_sport


def hours_per_zone(trainings_df,user_id):
    zones = list(teho.objects.filter(harjoitus_id__user=user_id).values_list('tehoalue_id__tehoalue',flat=True).distinct().order_by('tehoalue_id__jarj_nro')) + ['Muu']
    zones_objects = teho.objects.filter(harjoitus_id__user=user_id).values_list('harjoitus_id','harjoitus_id__aika_id__vuosi','tehoalue_id__tehoalue','kesto')
    if not zones_objects:
        return []
    else:
        zones_df = pd.DataFrame(list(zones_objects),columns = ['harjoitus_id','vuosi','teho','kesto'])
        zones_df = zones_df.merge(trainings_df[['id','kausi']], how='inner', left_on='harjoitus_id', right_on='id')
        zones_df['kesto'] = zones_df['kesto'].astype(float)
        zones_df = zones_df.fillna(np.nan)  #replace None with NaN

        # count training hours without zone defined
        zones_per_training = zones_df[['harjoitus_id','kesto']].groupby('harjoitus_id').sum()
        zones_per_training = trainings_df.merge(zones_per_training,how='left',left_on='id',right_index=True,suffixes=('','_zone'))[['id','vuosi','kausi','kesto','kesto_zone']].fillna(0)
        zones_per_training['Muu'] = zones_per_training['kesto'] - zones_per_training['kesto_zone']
        zone_not_defined_per_year = zones_per_training[['vuosi','Muu']].groupby('vuosi').sum().round(1)
        zone_not_defined_per_season = zones_per_training[zones_per_training['kausi'] != 0][['kausi','Muu']].groupby('kausi').sum().round(1)
        
        # count training hours per zone per year
        zones_per_year = zones_df.groupby(['vuosi','teho']).sum().reset_index()
        zones_per_year = zones_per_year.pivot(index='vuosi', columns='teho', values='kesto').round(1)
        zones_per_year.index = zones_per_year.index.astype(str)
        zones_per_year = zone_not_defined_per_year.merge(zones_per_year, how='left', left_index=True, right_on='vuosi')
        zones_per_year = zones_per_year[zones] 

        # count training hours per zone per season
        zones_per_season = zones_df.groupby(['kausi','teho']).sum().reset_index()
        if not zones_per_season.empty:
            zones_per_season = zones_per_season.pivot(index='kausi', columns='teho', values='kesto').round(1)
            zones_per_season.index = zones_per_season.index.astype(str)
            zones_per_season = zone_not_defined_per_season.merge(zones_per_season, how='left', left_index=True, right_on='kausi')
            zones_per_season = zones_per_season.loc[:,[z for z in zones if z in list(zones_per_season)]]
        
        hours_per_zone = {}
        hours_per_zone['year'] = json.loads(dataframe_to_json(zones_per_year))
        hours_per_zone['season']  = json.loads(dataframe_to_json(zones_per_season))

        return hours_per_zone


def zones_per_training(training_id):
    zones = list(teho.objects.filter(harjoitus=training_id).values(
        'nro', 'tehoalue_id__tehoalue', 'kesto_h', 'kesto_min', 'keskisyke', 
        'maksimisyke', 'matka', 'vauhti_min_km').order_by('nro'))
    return zones