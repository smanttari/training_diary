import json
from datetime import datetime

import pandas as pd
import numpy as np

from treenipaivakirja.models import Harjoitus, Aika, Laji, Teho, Tehoalue, Kausi, PolarSleep, PolarRecharge
from treenipaivakirja.utils import duration_to_string, dataframe_to_dict,coalesce
from treenipaivakirja.calculations import first_training_date
from django.db.models import Min


def trainings_to_df(user_id, columns, startdate=None, enddate=None, sport='Kaikki', restdays=True, duration_format='str', date_format='%Y-%m-%d'):
    """
    Fetch training data from database and return cleaned pandas dataframe of it
    """
    if not Harjoitus.objects.filter(user=user_id):
        return None

    startdate = int(coalesce(startdate, first_training_date(user_id).strftime('%Y%m%d')))
    enddate = int(coalesce(enddate, datetime.now().date().strftime('%Y%m%d')))
    join_type = 'left' if restdays is True else 'inner'

    days = Aika.objects.filter(vvvvkkpp__gte=startdate,vvvvkkpp__lte=enddate).values_list('pvm','vvvvkkpp','viikonpaiva_lyh','vko')
    days_df = pd.DataFrame(days, columns=['Pvm','vvvvkkpp','Viikonpäivä','Vko'])
    trainings = Harjoitus.objects.filter(user=user_id).values_list(
        'id','id','aika_id','kesto','kesto_h','kesto_min','laji__laji_nimi','matka','vauhti_km_h','keskisyke','tuntuma','kommentti')
    trainings_df = pd.DataFrame(trainings, columns=[
        'edit','delete','vvvvkkpp','Kesto','h','min','Laji','Matka (km)','Vauhti (km/h)','Keskisyke','Tuntuma','Kommentti'])
    trainings_df['details'] = np.nan
    trainings_df = days_df.merge(trainings_df, how=join_type, left_on='vvvvkkpp', right_on='vvvvkkpp')

    # cleaning data
    trainings_df['Laji'].fillna('Lepo', inplace=True)
    trainings_df['Pvm'] = pd.to_datetime(trainings_df['Pvm']).dt.strftime(date_format)
    trainings_df[['Matka (km)','Vauhti (km/h)']] = trainings_df[['Matka (km)','Vauhti (km/h)']].astype(float).round(1)
    trainings_df[['delete','edit','Keskisyke','Tuntuma']] = trainings_df[['delete','edit','Keskisyke','Tuntuma']].fillna(-1).astype(int).astype(str).replace('-1', np.nan)
    trainings_df['Päivä'] = trainings_df[['Pvm','Viikonpäivä']].apply(lambda x: ' '.join(x), axis=1)
    if duration_format == 'str':
        trainings_df['Kesto'] = trainings_df.apply(lambda row: duration_to_string(row['h'], row['min']), axis=1)

    # calculate duration per zone
    zones = Teho.objects.filter(harjoitus_id__user=user_id).values_list(
        'harjoitus_id','tehoalue_id__tehoalue','kesto','kesto_h','kesto_min')
    if zones:
        zones_df = pd.DataFrame(zones, columns=['id','teho','kesto','h','min']).fillna(np.nan)
        zones_df['kesto'] = zones_df['kesto'].astype(float)
        zones_df = zones_df.groupby(['id','teho']).sum().reset_index()
        if duration_format == 'str':
            zones_df['kesto'] = zones_df.apply(lambda row: duration_to_string(row['h'], row['min']), axis=1)
        zones_df = zones_df.pivot(index='id', columns='teho', values='kesto')
        zones_df.index = zones_df.index.map(str)
        trainings_df = trainings_df.merge(zones_df, how='left', left_on='edit', right_index=True)

    # filter by sport
    if sport != 'Kaikki':
        user_sports = sports_to_dict(user_id)
        if sport in user_sports.keys():
            trainings_df = trainings_df[trainings_df['Laji'].isin(user_sports[sport])]
        else:
            trainings_df = trainings_df[trainings_df['Laji'] == sport]

    trainings_df.sort_values(by='vvvvkkpp', ascending=False, inplace=True)
    return trainings_df[columns]


def sports_to_dict(user_id):
    sports = {}
    sports['Kaikki'] = []
    other = []
    laji_set = Laji.objects.filter(user=user_id)
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


def sports_to_list(user_id):
    sports = Laji.objects.filter(user=user_id).values_list('laji_nimi',flat=True).order_by('laji_nimi')
    return list(sports)


def trainings_base_to_df(user_id):
    trainings_objects = Harjoitus.objects.filter(user=user_id).values_list(
        'id','pvm','kesto','matka','aika_id__vuosi','aika_id__kk','aika_id__kk_nimi','aika_id__vko',
        'laji_id__laji_nimi','laji_id__laji','laji_id__laji_ryhma','vauhti_km_h','vauhti_min_km','keskisyke')
    trainings_df = pd.DataFrame(list(trainings_objects), columns=[
        'id','pvm','kesto','matka','vuosi','kk','kk_nimi','vko',
        'laji_nimi','laji','laji_ryhma','vauhti_km_h','vauhti_min_km','keskisyke']).fillna(np.nan)
    trainings_df['vuosi'] = trainings_df['vuosi'].astype(str)
    trainings_df['pvm'] = pd.to_datetime(trainings_df['pvm'])
    trainings_df[['kesto','matka','vauhti_km_h','vauhti_min_km']] = trainings_df[['kesto','matka','vauhti_km_h','vauhti_min_km']].astype(float)
    trainings_df['laji_ryhma'].fillna('Muut',inplace=True)
    # lookup season
    season_objects = Kausi.objects.filter(user=user_id)
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


def trainings_per_season_to_df(trainings_df):
    trainings = trainings_df.groupby('kausi').sum().reset_index()[['kausi','kesto', 'matka']]
    trainings[['kesto','matka']] = trainings[['kesto','matka']].round(0)
    return trainings


def trainings_per_year_to_df(trainings_df):
    trainings_per_year = trainings_df.groupby('vuosi').sum().reset_index()[['vuosi','kesto', 'matka']]
    trainings_per_year[['kesto','matka']] = trainings_per_year[['kesto','matka']].round(0)
    return trainings_per_year


def trainings_per_month_to_df(trainings_df,user_id):
    current_day = datetime.now().date()
    current_year = str(current_day.year)
    current_month = int(current_day.strftime("%m"))
    first_day_yyyymmdd = first_training_date(user_id).strftime('%Y%m%d')
    first_month = int(first_day_yyyymmdd[4:6])
    years_months = Aika.objects.filter(vvvvkkpp__gte=first_day_yyyymmdd, vvvvkkpp__lte=current_year + '1231').values_list('vuosi','kk').distinct()
    years_months = pd.DataFrame(list(years_months), columns=['vuosi','kk'])
    years_months['vuosi'] = years_months['vuosi'].astype(str)
    df = trainings_df.groupby(['vuosi','kk']).sum().reset_index()[['vuosi','kk','kesto','matka']]
    df = years_months.merge(df,how='left',right_on=['vuosi','kk'],left_on=['vuosi','kk'])
    df[['kesto','matka']] = df[['kesto','matka']].round(0)
    df[(df['vuosi'] < current_year) & (df['kk'] >= first_month)] = df[(df['vuosi'] < current_year) & (df['kk'] >= first_month)].fillna(0)
    df[(df['vuosi'] == current_year) & (df['kk'] <= current_month)] = df[(df['vuosi'] == current_year) & (df['kk'] <= current_month)].fillna(0)
    return df


def trainings_per_week_to_df(trainings_df,user_id):
    current_day = datetime.now().date()
    current_year = str(current_day.year)
    current_week = int(current_day.strftime("%V"))
    first_day = first_training_date(user_id)
    first_day_yyyymmdd = first_day.strftime('%Y%m%d')
    first_week = int(first_day.strftime("%V"))
    years_weeks = Aika.objects.filter(vvvvkkpp__gte=first_day_yyyymmdd, vvvvkkpp__lte=current_year + '1231').values_list('vuosi','vko').distinct()
    years_weeks = pd.DataFrame(list(years_weeks), columns=['vuosi','vko'])
    years_weeks['vuosi'] = years_weeks['vuosi'].astype(str)
    df = trainings_df.groupby(['vuosi','vko']).sum().reset_index()[['vuosi','vko','kesto','matka']]
    df = years_weeks.merge(df,how='left',right_on=['vuosi','vko'],left_on=['vuosi','vko'])
    df[['kesto','matka']] = df[['kesto','matka']].round(1)
    df[(df['vuosi'] < current_year) & (df['vko'] >= first_week)] = df[(df['vuosi'] < current_year) & (df['vko'] >= first_week)].fillna(0)
    df[(df['vuosi'] == current_year) & (df['vko'] <= current_week)] = df[(df['vuosi'] == current_year) & (df['vko'] <= current_week)].fillna(0)
    return df


def hours_per_season_to_json(trainings_per_season):
    hours = trainings_per_season[['kausi','kesto']].rename(columns={'kausi': 'category', 'kesto': 'series'})
    return hours.to_json(orient='records')


def hours_per_year_to_json(trainings_per_year):
    hours = trainings_per_year[['vuosi','kesto']].rename(columns={'vuosi': 'category', 'kesto': 'series'})
    return hours.to_json(orient='records')


def hours_per_month_to_json(trainings_per_month):
    month_names = dict(Aika.objects.values_list('kk','kk_nimi').distinct())
    hours = trainings_per_month.pivot(index='kk',columns='vuosi',values='kesto').sort_values(by='kk').rename(index=month_names)
    hours = dataframe_to_dict(hours)
    return json.dumps(hours)


def hours_per_week_to_json(trainings_per_week):
    hours = trainings_per_week.pivot(index='vko',columns='vuosi',values='kesto').sort_values(by='vko')
    hours = dataframe_to_dict(hours)
    return json.dumps(hours)


def kilometers_per_season_to_json(trainings_per_season):
    kilometers = trainings_per_season[['kausi','matka']].rename(columns={'kausi': 'category', 'matka': 'series'})
    return kilometers.to_json(orient='records')


def kilometers_per_year_to_json(trainings_per_year):
    kilometers = trainings_per_year[['vuosi','matka']].rename(columns={'vuosi': 'category', 'matka': 'series'})
    return kilometers.to_json(orient='records')


def hours_per_sport_to_json(trainings_df):
    hours = trainings_df.groupby(['vuosi','laji_nimi']).sum().reset_index()[['vuosi','laji_nimi','kesto']].round(1)
    hours_pivot = hours.pivot(index='laji_nimi',columns='vuosi',values='kesto').sort_values(by='laji_nimi') 
    hours_pivot = dataframe_to_dict(hours_pivot)
    return json.dumps(hours_pivot)


def hours_per_sport_group_to_json(trainings_df):
    hours = trainings_df.groupby(['vuosi','laji_ryhma']).sum().reset_index()[['vuosi','laji_ryhma','kesto']].round(1)
    hours_pivot = hours.pivot(index='laji_ryhma',columns='vuosi',values='kesto').sort_values(by='laji_ryhma') 
    hours_pivot = dataframe_to_dict(hours_pivot)
    return json.dumps(hours_pivot)


def trainings_per_sport_to_df(trainings_df, by):
    f = {'laji':['count'], 'kesto':['sum','mean'], 'matka':['sum','mean'], 'vauhti_km_h':['mean'], 'vauhti_min_km':['mean'], 'keskisyke':['mean']}
    trainings = trainings_df.groupby([by,'laji_nimi']).agg(f).round(1).reset_index(1)
    trainings.columns = ['_'.join(tup).rstrip('_') for tup in trainings.columns.values]
    trainings = trainings.reset_index()
    trainings = trainings.rename(columns={
        'laji_count':'lkm', 'kesto_sum':'kesto (h)', 'kesto_mean':'kesto (h) ka.','matka_sum':'matka (km)', 
        'matka_mean':'matka (km) ka.', 'vauhti_km_h_mean':'vauhti (km/h)',
        'vauhti_min_km_mean':'vauhti (min/km)','keskisyke_mean':'keskisyke'
        })
    return trainings


def hours_per_zone_to_json(trainings_df,user_id):
    zones = list(Teho.objects.filter(harjoitus_id__user=user_id).values_list('tehoalue_id__tehoalue',flat=True).distinct().order_by('tehoalue_id__jarj_nro')) + ['Muu']
    zones_objects = Teho.objects.filter(harjoitus_id__user=user_id).values_list('harjoitus_id','harjoitus_id__aika_id__vuosi','tehoalue_id__tehoalue','kesto')
    if not zones_objects:
        return json.dumps([])       
    zones_df = pd.DataFrame(list(zones_objects),columns=['harjoitus_id','vuosi','teho','kesto']).fillna(np.nan)
    zones_df = zones_df.merge(trainings_df[['id','kausi']], how='inner', left_on='harjoitus_id', right_on='id')
    zones_df['kesto'] = zones_df['kesto'].astype(float)

    # count training hours without zone defined
    zones_per_training = zones_df[['harjoitus_id','kesto']].groupby('harjoitus_id').sum()
    zones_per_training = trainings_df.merge(zones_per_training,how='left',left_on='id',right_index=True,suffixes=('','_zone'))[['id','vuosi','kausi','kesto','kesto_zone']].fillna(0)
    zones_per_training['Muu'] = zones_per_training['kesto'] - zones_per_training['kesto_zone']
    zone_not_defined_per_year = zones_per_training[['vuosi','Muu']].groupby('vuosi').sum().round(1).reset_index()
    zone_not_defined_per_season = zones_per_training[zones_per_training['kausi'] != 0][['kausi','Muu']].groupby('kausi').sum().round(1).reset_index()

    # count training hours per zone per year
    zones_per_year = zones_df.groupby(['vuosi','teho']).sum().reset_index()    
    zones_per_year = zones_per_year.pivot(index='vuosi', columns='teho', values='kesto').round(1)
    zones_per_year.index = zones_per_year.index.astype(str)
    zones_per_year = zone_not_defined_per_year.merge(zones_per_year, how='left', left_on='vuosi', right_on='vuosi').set_index('vuosi') 
    zones_per_year = zones_per_year[zones] 

    # count training hours per zone per season
    zones_per_season = zones_df.groupby(['kausi','teho']).sum().reset_index()
    if not zones_per_season.empty:
        zones_per_season = zones_per_season.pivot(index='kausi', columns='teho', values='kesto').round(1)
        zones_per_season.index = zones_per_season.index.astype(str)
        zones_per_season = zone_not_defined_per_season.merge(zones_per_season, how='left', left_on='kausi', right_on='kausi').set_index('kausi')
        zones_per_season = zones_per_season.loc[:,[z for z in zones if z in list(zones_per_season)]]
    
    hours_per_zone = {}
    hours_per_zone['year'] = dataframe_to_dict(zones_per_year)
    hours_per_zone['season']  = dataframe_to_dict(zones_per_season)
    return json.dumps(hours_per_zone)


def zones_per_training_to_list(training_id):
    zones = Teho.objects.filter(harjoitus=training_id).values(
        'nro', 'tehoalue_id__tehoalue', 'kesto_h', 'kesto_min', 'keskisyke', 
        'maksimisyke', 'matka', 'vauhti_min', 'vauhti_s').order_by('nro')
    return list(zones)


def zone_areas_to_list(user_id):
    zones_areas = Teho.objects.filter(harjoitus_id__user=user_id).values_list(
        'tehoalue_id__tehoalue',flat=True).distinct().order_by('tehoalue_id__jarj_nro')
    return list(zones_areas)


def years_to_list(user_id):
    years = Harjoitus.objects.filter(user=user_id).values_list(
        'aika_id__vuosi',flat=True).distinct().order_by('-aika_id__vuosi')
    years = [str(y) for y in years]
    return years


def seasons_to_list(user_id):
    seasons = Kausi.objects.filter(user=user_id).values_list('kausi',flat=True).order_by('-alkupvm')
    return list(seasons)


def sleep_to_df(user_id):
    sleep = PolarSleep.objects.filter(polar_user_id__user=user_id).values_list(
        'date','duration','sleep_score').order_by('date')
    sleep_df = pd.DataFrame(sleep, columns = ['date','duration','score'])
    return sleep_df


def sleep_duration_to_json(sleep_df):
    duration = sleep_df[['date','duration']].rename(columns={'date':'category', 'duration':'series'})
    return duration.to_json(orient='records')


def sleep_score_to_json(sleep_df):
    score = sleep_df[['date','score']].rename(columns={'date':'category', 'score':'series'})
    return score.to_json(orient='records')


def recharge_to_df(user_id):
    recharge = PolarRecharge.objects.filter(polar_user_id__user=user_id).values_list(
        'date','heart_rate_avg','heart_rate_variability_avg').order_by('date')
    recharge_df = pd.DataFrame(recharge, columns=['date','heart_rate_avg','heart_rate_variability_avg'])
    return recharge_df


def recharge_hr_to_json(recharge_df):
    hr = recharge_df[['date','heart_rate_avg']].rename(
        columns={'date':'category', 'heart_rate_avg':'series'})
    return hr.to_json(orient='records')


def recharge_hrv_to_json(recharge_df):
    hrv = recharge_df[['date','heart_rate_variability_avg']].rename(
        columns={'date':'category', 'heart_rate_variability_avg':'series'})
    return hrv.to_json(orient='records')