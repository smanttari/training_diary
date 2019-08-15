from treenipaivakirja.models import harjoitus,aika,laji,tehot,tehoalue
from treenipaivakirja.forms import HarjoitusForm,LajiForm,TehotForm,TehoalueForm,UserForm,RegistrationForm
from treenipaivakirja.serializers import HarjoitusSerializer
from django.db.models import Sum,Max,Min
from django.shortcuts import render,redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError
from django.http import Http404
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from datetime import datetime
import pandas as pd
import numpy as np
import os
import json


# HELPER FUNCTIONS
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


# VIEWS
@login_required
def index(request):
    """ 
    Front page 
    """
    current_user_id = request.user.id
    current_day = datetime.now().date()
    current_year = current_day.year
    current_week = current_day.strftime("%V")
    trainings_latest_cols = ['Päivä', 'Laji', 'Kesto', 'Tuntuma']

    trainings = harjoitus.objects.filter(user=current_user_id).values_list(
        'pvm_fk_id__pvm','pvm_fk_id__vuosi','pvm_fk_id__vko','pvm_fk_id__viikonpaiva_lyh',
        'laji_fk__laji_nimi','kesto','kesto_h','kesto_min','tuntuma')

    if not trainings:
        training_hours_total = 0
        trainings_per_week_avg = 0
        trainings_latest = []
        trainings_per_week_json = []
    else:
        trainings_df = pd.DataFrame(list(trainings), columns=['Päivä','Vuosi','Viikko','Viikonpäivä','Laji','Kesto','Kesto_h','Kesto_min','Tuntuma'])
        trainings_df = trainings_df.fillna(np.nan)  #replace None with NaN
        trainings_df['Päivä'] = pd.to_datetime(trainings_df['Päivä'])
        trainings_df['Kesto'] = trainings_df['Kesto'].astype(float).round(1)

        trainings_latest = trainings_df.sort_values(by='Päivä', ascending=False).head(5)
        trainings_latest['Päivä'] = trainings_latest['Päivä'].dt.strftime('%d.%m')
        trainings_latest['Viikonpäivä'] = trainings_latest['Viikonpäivä'].str.capitalize()
        trainings_latest['Päivä'] = trainings_latest[['Päivä', 'Viikonpäivä']].apply(lambda x: ' - '.join(x), axis=1)
        trainings_latest['Kesto'] = trainings_latest.apply(lambda row: duration_to_string(row['Kesto_h'], row['Kesto_min']), axis=1)
        trainings_latest['Tuntuma'] = trainings_latest['Tuntuma'].fillna(-1).astype(int).astype(str).replace('-1', '')
        trainings_latest = trainings_latest[trainings_latest_cols].values.tolist()

        weeks = aika.objects.filter(vuosi=current_year).order_by('vko').values_list('vko', flat=True).distinct()
        weeks = pd.DataFrame(list(weeks), columns=['Viikko'])

        trainings_per_week = trainings_df[trainings_df['Vuosi'] == current_year].groupby('Viikko').agg({'Kesto':'sum', 'Tuntuma':'mean'})
        trainings_per_week = weeks.merge(trainings_per_week, how='left', right_index=True, left_on='Viikko')
        trainings_per_week = trainings_per_week[trainings_per_week['Viikko'] <= int(current_week)]
        trainings_per_week = trainings_per_week.set_index('Viikko').round(1)
        trainings_per_week = trainings_per_week.rename(columns={'Kesto': 'Tunnit','Tuntuma': 'Tuntuma (1-10)'})
        
        trainings_per_week_json = dataframe_to_json(trainings_per_week)
        trainings_per_week_avg = round(trainings_per_week.mean()['Tunnit'],1)

        training_hours_total = int(round(trainings_df[trainings_df['Vuosi'] == current_year]['Kesto'].sum(),0))

    return render(request,'index.html',
        context = {
            'training_hours_total': training_hours_total,
            'trainings_per_week_avg': trainings_per_week_avg,
            'trainings_latest': trainings_latest,
            'trainings_latest_cols': trainings_latest_cols,
            'trainings_per_week_json': trainings_per_week_json
            })


@login_required
def trainings_view(request):
    """ 
    List of trainings 
    """
    message_header = ''
    current_user_id = request.user.id
    current_day = datetime.now().date()
    current_day_yyyymmdd = current_day.strftime('%Y%m%d')
    first_day_yyyymmdd = harjoitus.objects.filter(user=current_user_id).aggregate(Min('pvm_fk_id'))['pvm_fk_id__min']
    table_columns = [
        'delete','edit','Vko','Päivä','Laji','Kesto','Keskisyke','Matka (km)',
        'Vauhti (km/h)','Tuntuma','Kommentti'
        ]

    # get filtering parameters
    if 'sport' in request.GET:
        sport = request.GET['sport']
    else:
        sport = 'Kaikki'

    if 'startdate' in request.GET:
        startdate = request.GET['startdate']
    else:
        startdate = '01.01.{}'.format(current_day.year)
    startdate_dt = datetime.strptime(startdate,'%d.%m.%Y')
    startdate_yyyymmdd = startdate_dt.strftime('%Y%m%d')

    if 'enddate' in request.GET:
        enddate = request.GET['enddate']
    else:
        enddate = current_day.strftime('%d.%m.%Y')
    enddate_dt = datetime.strptime(enddate,'%d.%m.%Y')
    enddate_yyyymmdd = enddate_dt.strftime('%Y%m%d')

    # sports to dropdown list
    sports = {}
    sports['Kaikki'] = []
    other = []
    laji_set = laji.objects.filter(user=current_user_id)
    if laji_set:
        for l in laji_set:
            if l.laji_ryhma is None or l.laji_ryhma == '':
                other.append(l.laji_nimi)
            else:
                if l.laji_ryhma not in sports.keys():
                    sports[l.laji_ryhma] = []
                sports[l.laji_ryhma].append(l.laji_nimi)
    sports['Muut'] = other

    if first_day_yyyymmdd is None:
        trainings_dict = {}
    else:
        # trainings to dataframe
        days = aika.objects.filter(
            vvvvkkpp__gte = max(int(startdate_yyyymmdd),int(first_day_yyyymmdd)),
            vvvvkkpp__lte = min(int(enddate_yyyymmdd),int(current_day_yyyymmdd))
            ).values_list('pvm','vvvvkkpp','viikonpaiva_lyh','vko')
        days_df = pd.DataFrame(list(days), columns=['Pvm','vvvvkkpp','Viikonpäivä','Vko'])

        trainings = harjoitus.objects.filter(user = current_user_id).values_list(
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
        
        if sport != 'Kaikki':
            if sport in sports.keys():
                trainings_df = trainings_df[trainings_df['Lajiryhmä'] == sport]
            else:
                trainings_df = trainings_df[trainings_df['Laji'] == sport]

        # cleaning data
        trainings_df['Pvm'] = pd.to_datetime(trainings_df['Pvm'])
        trainings_df = trainings_df.sort_values(by='Pvm', ascending=False)
        trainings_df['Pvm'] = trainings_df['Pvm'].dt.strftime('%Y-%m-%d')
        trainings_df[['Kesto (h)','Matka (km)','Vauhti (km/h)','Vauhti (min/km)']] = trainings_df[['Kesto (h)','Matka (km)','Vauhti (km/h)','Vauhti (min/km)']].astype(float).round(1)
        trainings_df['Viikonpäivä'] = trainings_df['Viikonpäivä'].str.capitalize()
        trainings_df[['delete','edit','Keskisyke','Tuntuma','Nousu (m)']] = trainings_df[['delete','edit','Keskisyke','Tuntuma','Nousu (m)']].fillna(-1).astype(int).astype(str).replace('-1', np.nan)
        
        if not trainings_df.empty:
            trainings_df['Päivä'] = trainings_df[['Pvm', 'Viikonpäivä']].apply(lambda x: ' '.join(x), axis=1)
            trainings_df['Kesto'] = trainings_df.apply(lambda row: duration_to_string(row['Kesto_h'], row['Kesto_min']), axis=1)
        else:
            trainings_df['Päivä'] = np.nan
            trainings_df['Kesto'] = np.nan

        # calculate duration per zone
        zones_duration = tehot.objects.filter(harjoitus_fk_id__user=current_user_id).values_list('harjoitus_fk_id','teho_id__teho','kesto_h','kesto_min')
        if zones_duration:
            zones_duration_df = pd.DataFrame(list(zones_duration),columns = ['id','teho','kesto_h','kesto_min'])
            zones_duration_df = zones_duration_df.fillna(np.nan)  #replace None with NaN
            zones_duration_df = zones_duration_df.groupby(['id','teho']).sum().reset_index()
            zones_duration_df['kesto'] = zones_duration_df.apply(lambda row: duration_to_string(row['kesto_h'], row['kesto_min']), axis=1)
            zones_duration_df = zones_duration_df.pivot(index='id', columns='teho', values='kesto')
            zones_duration_df.index = zones_duration_df.index.map(str)
            zones = list(tehoalue.objects.values_list('teho',flat=True).filter(user=current_user_id).order_by('jarj_nro'))
            zones = [zone for zone in zones if zone in zones_duration_df.columns]
            table_columns = table_columns[:-1] + zones + table_columns[-1:]
            trainings_df = trainings_df.merge(zones_duration_df, how='left', left_on='edit', right_index=True)
        else:
            zones = []

        trainings_table = trainings_df[table_columns]
        trainings_dict = trainings_table.fillna('').to_dict(orient='index')

    # export data
    if 'export' in request.GET:
        try: 
            trainings_df
        except:
            message_header = 'ERROR'
            messages.add_message(request, messages.ERROR, 'Ei harjoituksia')
        else:
            export_type = request.GET['export']
            export_columns = ['Vko','Pvm','Viikonpäivä','Kesto (h)','Laji','Matka (km)','Vauhti (km/h)','Vauhti (min/km)',
                            'Keskisyke', 'Nousu (m)','Tuntuma', 'Kommentti'] + zones
            trainings_export = trainings_df[export_columns]
            trainings_export = trainings_export.sort_values(by='Pvm', ascending=True)
            trainings_export['Pvm'] = pd.to_datetime(trainings_df['Pvm']).dt.strftime('%d.%m.%Y')

            export_path = settings.FILEPATH_EXPORT
            if not os.path.exists(export_path):
                os.makedirs(export_path)

            if export_type == 'csv':
                filename = 'treenit.csv'
                try:
                    trainings_export.to_csv(export_path + filename,sep=';',header=True,index=False,encoding='utf-8')
                    message_header = 'Tallennettu'
                    messages.add_message(request, messages.INFO, 'Harjoitukset tallennettu onnistuneesti tiedostoon <br><br><b>{}{}</b>'.format(export_path,filename))
                except Exception as e:
                    message_header = 'Virhe'
                    messages.add_message(request, messages.ERROR, 'Tallennus epäonnistui:<p class="text-danger">{}</p>'.format(str(e)))

            if export_type == 'xls':
                filename = 'treenit.xlsx'
                try:
                    writer = pd.ExcelWriter(export_path + filename)
                    trainings_export.to_excel(writer,header=True,index=False)
                    writer.save()
                    message_header = 'Tallennettu'
                    messages.add_message(request, messages.SUCCESS, 'Harjoitukset tallennettu onnistuneesti tiedostoon <br><br><b>{}{}</b>'.format(export_path,filename))
                except Exception as e:
                    message_header = 'Virhe'
                    messages.add_message(request, messages.ERROR, 'Tallennus epäonnistui <p class="text-danger">{}</p>'.format(str(e)))

    return render(request, 'trainings.html',
        context = {
            'message_header': message_header,
            'sport': sport,
            'startdate': startdate,
            'enddate': enddate,
            'trainings_headers': table_columns,
            'trainings_dict': trainings_dict,
            'sports': sports
            })


@login_required
def reports(request):
    """ 
    Trainings reports 
    """
    current_user = request.user
    current_user_id = current_user.id
    current_day = datetime.now().date()
    current_day_yyyymmdd = current_day.strftime('%Y%m%d')
    current_year = str(current_day.year)
    current_week = str(current_day.strftime("%V"))

    first_day_yyyymmdd = harjoitus.objects.filter(user=current_user_id).aggregate(Min('pvm_fk_id'))['pvm_fk_id__min']
    
    if first_day_yyyymmdd is None:
        years = [current_year]
        sport = ''
        sports_list = []
        hours_per_year_json = []
        kilometers_per_year_json = []
        hours_per_month_json = []
        hours_per_week_json = []
        hours_per_sport_json = []
        hours_per_sport_group_json = []
        hours_per_year_per_sport_json = []
        kilometers_per_year_per_sport_json = []
        avg_per_year_per_sport = []
        amounts_per_year_per_sport = []
        avg_per_year_per_sport_table = []
        amount_per_zone_per_year_json = []
    else:
        month_names = dict(aika.objects.values_list('kk','kk_nimi').distinct())
        
        years_months = aika.objects.filter(vvvvkkpp__gte = first_day_yyyymmdd, vvvvkkpp__lte = current_day_yyyymmdd).values_list('vuosi','kk').distinct()
        years_months = pd.DataFrame(list(years_months), columns=['vuosi','kk'])
        years_months['vuosi'] = years_months['vuosi'].astype(str)

        years_weeks = aika.objects.filter(vvvvkkpp__gte = first_day_yyyymmdd, vvvvkkpp__lte = current_day_yyyymmdd).values_list('vuosi','vko').distinct()
        years_weeks = pd.DataFrame(list(years_weeks), columns=['vuosi','vko'])
        years_weeks['vuosi'] = years_weeks['vuosi'].astype(str)

        sports = laji.objects.filter(user=current_user_id).values_list('id','laji','laji_nimi','laji_ryhma')
        sports_df = pd.DataFrame(list(sports), columns=['id','laji','laji_nimi','laji_ryhma']).set_index('id').sort_values('laji_nimi')
        sports_list = sports_df['laji_nimi'].values.tolist()
        sport = sports_list[0]

        trainings = harjoitus.objects.filter(user=current_user_id).values_list(
            'id','pvm','kesto','matka','pvm_fk_id__vuosi','pvm_fk_id__kk','pvm_fk_id__kk_nimi',
            'pvm_fk_id__vko','pvm_fk_id__hiihtokausi','laji_fk_id__laji_nimi',
            'laji_fk_id__laji','laji_fk_id__laji_ryhma','vauhti_km_h','vauhti_min_km','keskisyke')

        trainings_df = pd.DataFrame(list(trainings), 
            columns = [
                'id','pvm','kesto','matka','vuosi','kk','kk_nimi','vko','hiihtokausi',
                'laji_nimi','laji','laji_ryhma','vauhti_km_h','vauhti_min_km','keskisyke'
                ])
        trainings_df = trainings_df.fillna(np.nan)  #replace None with NaN
        trainings_df['vuosi'] = trainings_df['vuosi'].astype(str)
        trainings_df['pvm'] = pd.to_datetime(trainings_df['pvm'])
        trainings_df[['kesto','matka','vauhti_km_h','vauhti_min_km']] = trainings_df[['kesto','matka','vauhti_km_h','vauhti_min_km']].astype(float)
        trainings_df['laji_ryhma'] = trainings_df['laji_ryhma'].fillna('Muut')

        years = trainings_df.sort_values('vuosi')['vuosi'].unique()

        trainings_per_year = trainings_df.groupby('vuosi').sum().reset_index()[['vuosi','kesto', 'matka']]
        trainings_per_year[['kesto','matka']] = trainings_per_year[['kesto','matka']].round(0)

        hours_per_year = trainings_per_year[['vuosi','kesto']].rename(columns={'vuosi': 'category', 'kesto': 'series'})
        hours_per_year_json = hours_per_year.to_json(orient='records')

        kilometers_per_year = trainings_per_year[['vuosi','matka']].rename(columns={'vuosi': 'category', 'matka': 'series'})
        kilometers_per_year_json = kilometers_per_year.to_json(orient='records')

        trainings_per_month = trainings_df.groupby(['vuosi','kk']).sum().reset_index()[['vuosi','kk','kesto','matka']]
        trainings_per_month = years_months.merge(trainings_per_month,how='left',right_on=['vuosi','kk'],left_on=['vuosi','kk'])
        trainings_per_month[['kesto','matka']] = trainings_per_month[['kesto','matka']].round(0)
        
        hours_per_month_pivot = trainings_per_month.pivot(index='kk',columns='vuosi',values='kesto').sort_values(by='kk').rename(index = month_names)
        hours_per_month_json = dataframe_to_json(hours_per_month_pivot)

        trainings_per_week = trainings_df.groupby(['vuosi','vko']).sum().reset_index()[['vuosi','vko','kesto','matka']]
        trainings_per_week = years_weeks.merge(trainings_per_week,how='left',right_on=['vuosi','vko'],left_on=['vuosi','vko'])
        trainings_per_week[['kesto','matka']] = trainings_per_week[['kesto','matka']].round(1)
        trainings_per_week[(trainings_per_week['vuosi'] < current_year) | (trainings_per_week['vko'] <= int(current_week))] = trainings_per_week[(trainings_per_week['vuosi'] < current_year) | (trainings_per_week['vko'] <= int(current_week))].fillna(0)

        hours_per_week_pivot = trainings_per_week.pivot(index='vko',columns='vuosi',values='kesto').sort_values(by='vko')
        hours_per_week_json = dataframe_to_json(hours_per_week_pivot)

        hours_per_sport = trainings_df.groupby(['vuosi','laji_nimi']).sum().reset_index()[['vuosi','laji_nimi','kesto']].round(1)
        hours_per_sport_pivot = hours_per_sport.pivot(index='laji_nimi',columns='vuosi',values='kesto').sort_values(by='laji_nimi') 
        hours_per_sport_json = dataframe_to_json(hours_per_sport_pivot)

        hours_per_sport_group = trainings_df.groupby(['vuosi','laji_ryhma']).sum().reset_index()[['vuosi','laji_ryhma','kesto']].round(1)
        hours_per_sport_group_pivot = hours_per_sport_group.pivot(index='laji_ryhma',columns='vuosi',values='kesto').sort_values(by='laji_ryhma') 
        hours_per_sport_group_json = dataframe_to_json(hours_per_sport_group_pivot)

        f = {'laji':['count'], 'kesto':['sum','mean'], 'matka':['sum','mean'], 'vauhti_km_h':['mean'], 'vauhti_min_km':['mean'], 'keskisyke':['mean']}

        trainings_per_sport1 = trainings_df[~trainings_df['laji_nimi'].isin(['Hiihto (p)', 'Hiihto (v)'])]
        if not trainings_per_sport1.empty:
            trainings_per_sport1 = trainings_per_sport1.groupby(['vuosi','laji_nimi']).agg(f).round(1).reset_index(1)
            trainings_per_sport1.columns = ['_'.join(tup).rstrip('_') for tup in trainings_per_sport1.columns.values]

        trainings_per_sport2 = trainings_df[trainings_df['laji_nimi'].isin(['Hiihto (p)', 'Hiihto (v)'])]
        if not trainings_per_sport2.empty:
            trainings_per_sport2 = trainings_per_sport2.groupby(['hiihtokausi','laji_nimi']).agg(f).round(1).reset_index(1)
            trainings_per_sport2.index = trainings_per_sport2.index.rename('vuosi')
            trainings_per_sport2.columns = ['_'.join(tup).rstrip('_') for tup in trainings_per_sport2.columns.values]

        if trainings_per_sport1.empty:
            trainings_per_sport = trainings_per_sport2.reset_index()
        elif trainings_per_sport2.empty:
            trainings_per_sport = trainings_per_sport1.reset_index()
        else:
            trainings_per_sport = pd.concat([trainings_per_sport1,trainings_per_sport2])
            trainings_per_sport = trainings_per_sport.reset_index().rename(columns={'index':'vuosi'})
        trainings_per_sport = trainings_per_sport.rename(columns={
            'laji_count':'lkm', 'kesto_sum':'kesto (h)', 'kesto_mean':'kesto (h) ka.',
            'matka_sum':'matka (km)', 'matka_mean':'matka (km) ka.', 'vauhti_km_h_mean':'vauhti (km/h)',
            'vauhti_min_km_mean':'vauhti (min/km)','keskisyke_mean':'keskisyke'
            })
        trainings_per_sport[['kesto (h)','matka (km)','vauhti (km/h)','vauhti (min/km)']] = trainings_per_sport[['kesto (h)','matka (km)','vauhti (km/h)','vauhti (min/km)']].round(1)
        
        zones_duration = tehot.objects.filter(harjoitus_fk_id__user=current_user_id).values_list('harjoitus_fk_id','harjoitus_fk_id__pvm_fk__vuosi','teho_id__teho','kesto')
        if zones_duration:
            zones_duration_df = pd.DataFrame(list(zones_duration),columns = ['harjoitus_id','vuosi','teho','kesto'])
            zones_duration_df['kesto'] = zones_duration_df['kesto'].astype(float)
            zones_duration_df = zones_duration_df.fillna(np.nan)  #replace None with NaN

            # count training hours without zone defined
            zones_per_training = zones_duration_df[['harjoitus_id','kesto']].groupby('harjoitus_id').sum()
            zones_per_training = trainings_df.merge(zones_per_training,how='left',left_on='id',right_index=True,suffixes=('','_zone'))[['id','vuosi','kesto','kesto_zone']].fillna(0)
            zones_per_training['Muu'] = zones_per_training['kesto'] - zones_per_training['kesto_zone']
            zones_per_training = zones_per_training[['vuosi','Muu']].groupby('vuosi').sum().round(0)
            
            zones_duration_df = zones_duration_df.groupby(['vuosi','teho']).sum().reset_index()
            zones_duration_df = zones_duration_df.pivot(index='vuosi', columns='teho', values='kesto').round(0)
            zones_duration_df.index = zones_duration_df.index.astype(str)
            zones_duration_df = zones_per_training.merge(zones_duration_df, how='left', left_index=True, right_on='vuosi')
            
            zones = list(tehoalue.objects.values_list('teho',flat=True).filter(user=current_user_id).order_by('jarj_nro'))
            zones = [zone for zone in zones if zone in zones_duration_df.columns] + ['Muu']
            zones_duration_df = zones_duration_df[zones]

            amount_per_zone_per_year_json = dataframe_to_json(zones_duration_df)
        else:
            amount_per_zone_per_year_json = []

        hours_per_year_per_sport = {}
        kilometers_per_year_per_sport = {}
        avg_per_year_per_sport = {}
        avg_per_year_per_sport_table = {}
        amounts_per_year_per_sport = {}

        for s in sports_list:
            data = trainings_per_sport[trainings_per_sport['laji_nimi'] == s]
            if not data.empty:
                amounts_per_year_per_sport[s] = data[['vuosi','lkm','kesto (h)','matka (km)']].fillna('').to_dict(orient='records')
                avg_per_year_per_sport_table[s] = data[['vuosi','kesto (h) ka.','matka (km) ka.','vauhti (km/h)','keskisyke']].rename(columns={'kesto (h) ka.':'kesto (h)','matka (km) ka.':'matka (km)'}).fillna('').to_dict(orient='records')
                data = data.set_index('vuosi')
                hours_per_year_per_sport[s] = json.loads(dataframe_to_json(data[['kesto (h)']]))
                kilometers_per_year_per_sport[s] = json.loads(dataframe_to_json(data[['matka (km)']]))
                avg_per_year_per_sport[s] = json.loads(dataframe_to_json(data[['vauhti (km/h)','keskisyke']]))
        
        hours_per_year_per_sport_json = json.dumps(hours_per_year_per_sport)
        kilometers_per_year_per_sport_json = json.dumps(kilometers_per_year_per_sport)

    return render(request, 'reports.html',
        context = {
            'current_year': current_year,
            'years': years,
            'sport': sport,
            'sports_list': sports_list,
            'hours_per_year_json': hours_per_year_json,
            'kilometers_per_year_json': kilometers_per_year_json,
            'hours_per_month_json': hours_per_month_json,
            'hours_per_week_json': hours_per_week_json,
            'hours_per_sport_json': hours_per_sport_json,
            'hours_per_sport_group_json': hours_per_sport_group_json,
            'hours_per_year_per_sport_json': hours_per_year_per_sport_json,
            'kilometers_per_year_per_sport_json': kilometers_per_year_per_sport_json,
            'avg_per_year_per_sport': avg_per_year_per_sport,
            'amounts_per_year_per_sport': amounts_per_year_per_sport,
            'avg_per_year_per_sport_table': avg_per_year_per_sport_table,
            'amount_per_zone_per_year_json': amount_per_zone_per_year_json
            })


@login_required
def training_add(request):
    """ 
    Inserts new training 
    """
    max_count = 20
    TehotFormset = inlineformset_factory(harjoitus,tehot,form=TehotForm,extra=max_count,max_num=max_count,can_delete=True)
    if request.method == "POST":
        harjoitus_form = HarjoitusForm(request.user,request.POST)
        tehot_formset = TehotFormset(request.POST)
        if harjoitus_form.is_valid() and harjoitus_form.has_changed():
            instance = harjoitus_form.save(commit=False)
            instance.pvm_fk_id = instance.pvm.strftime('%Y%m%d')
            instance.user = request.user
            kesto_h = coalesce(harjoitus_form.cleaned_data['kesto_h'],0)
            kesto_min = coalesce(harjoitus_form.cleaned_data['kesto_min'],0)
            instance.kesto_h = kesto_h
            instance.kesto_min = kesto_min
            instance.kesto = h_min_to_hours(kesto_h,kesto_min)
            vauhti_m = harjoitus_form.cleaned_data['vauhti_min']
            vauhti_s = harjoitus_form.cleaned_data['vauhti_s']
            instance.vauhti_min_km = vauhti_min_km(vauhti_m,vauhti_s)
            vauhti_km_h = harjoitus_form.cleaned_data['vauhti_km_h']
            if instance.vauhti_min_km is None and vauhti_km_h is not None:
                instance.vauhti_min_km = 60 / vauhti_km_h
            elif instance.vauhti_min_km is not None and vauhti_km_h is None:
                instance.vauhti_km_h = 60 / instance.vauhti_min_km
            instance.save()
            training = harjoitus.objects.get(id=instance.id)
            tehot_formset = TehotFormset(request.POST, request.FILES,instance=training)
            if tehot_formset.is_valid() and tehot_formset.has_changed():
                tehot_formset.save()
            return redirect('trainings')
    else:
        harjoitus_form = HarjoitusForm(request.user,initial={'pvm': datetime.now()})
        tehot_formset = TehotFormset(queryset=tehot.objects.none())
        for form in tehot_formset:
            form.fields['teho'].queryset = tehoalue.objects.filter(user=request.user).order_by('jarj_nro')

    return render(request, 'training_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Lisää harjoitus',
            'page_header': 'LISÄÄ HARJOITUS',
            'tehot_formset': tehot_formset,
            'harjoitus_form': harjoitus_form,
            'max_count':max_count
            })


@login_required
def training_modify(request,pk):
    """ 
    Modifies training information 
    """
    max_count = 20
    TehotFormset = inlineformset_factory(harjoitus,tehot,form=TehotForm,extra=max_count,max_num=max_count,can_delete=True)
    training = harjoitus.objects.get(id=pk,user_id=request.user.id)
    if request.method == "POST":
        harjoitus_form = HarjoitusForm(request.user,request.POST,instance=training)
        tehot_formset = TehotFormset(request.POST,request.FILES,instance=training)
        if harjoitus_form.is_valid() and harjoitus_form.has_changed():
            post = harjoitus_form.save(commit=False)
            post.pvm_fk_id = post.pvm.strftime('%Y%m%d')
            kesto_h = coalesce(harjoitus_form.cleaned_data['kesto_h'],0)
            kesto_min = coalesce(harjoitus_form.cleaned_data['kesto_min'],0)
            post.kesto_h = kesto_h
            post.kesto_min = kesto_min
            post.kesto = h_min_to_hours(kesto_h,kesto_min)
            vauhti_km_h = harjoitus_form.cleaned_data['vauhti_km_h']
            vauhti_m = harjoitus_form.cleaned_data['vauhti_min']
            vauhti_s = harjoitus_form.cleaned_data['vauhti_s']
            post.vauhti_min_km = vauhti_min_km(vauhti_m,vauhti_s)
            if post.vauhti_min_km is None and vauhti_km_h is not None:
                post.vauhti_min_km = 60 / vauhti_km_h
            elif post.vauhti_min_km is not None and vauhti_km_h is None:
                post.vauhti_km_h = 60 / post.vauhti_min_km
            post.save()
        if tehot_formset.is_valid() and tehot_formset.has_changed():
            tehot_formset.save()
        return redirect('trainings')
    else:
        if training.vauhti_min_km is None:
            vauhti_m = None
            vauhti_s = None
        else:
            vauhti_m = int(training.vauhti_min_km)
            vauhti_s = round((training.vauhti_min_km*60) % 60,0)
        harjoitus_form = HarjoitusForm(request.user,instance=training,initial={'vauhti_min': vauhti_m, 'vauhti_s': vauhti_s })
        tehot_formset = TehotFormset(instance=training)
        for form in tehot_formset:
            form.fields['teho'].queryset = tehoalue.objects.filter(user=request.user)
    
    return render(request, 'training_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Muokkaa harjoitusta',
            'page_header': 'MUOKKAA HARJOITUSTA',
            'tehot_formset': tehot_formset,
            'harjoitus_form': harjoitus_form,
            'max_count':max_count
            })


@login_required
def training_delete(request,pk):
    """ 
    Deletes training 
    """
    training = harjoitus.objects.get(id=pk,user_id=request.user.id)
    day = training.pvm
    sport = training.laji_fk
    duration = training.kesto

    if request.method == "POST":
        response = request.POST['confirm']
        if response == 'no':
            return redirect('trainings')
        if response == 'yes':
            training.delete()
            return redirect('trainings')

    return render(request,'training_delete.html',
        context = {
            'day': day,
            'sport': sport,
            'duration': duration
            })


@login_required
def sport_modify(request,pk):
    """ 
    Modifies sport 
    """
    error_message = None
    sport = laji.objects.get(id=pk, user_id=request.user.id)
    form = LajiForm(instance=sport)

    if request.method == "POST":
        form = LajiForm(request.POST, instance=sport)
        if form.is_valid() and form.has_changed():
            try:
                sport.save()
                return redirect('settings')
            except IntegrityError as e:
                error_message = "Laji nimellä '{}' on jo olemassa".format(sport.laji_nimi)

    return render(request, 'sport_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Muokkaa lajia',
            'page_header': 'MUOKKAA LAJIA',
            'form': form,
            'error_message': error_message
            })


@login_required
def sport_add(request):
    """ 
    Adds new sport 
    """
    error_message = None
    form = LajiForm()

    if request.method == "POST":
        prev_url = request.POST['prevURL']
        form = LajiForm(request.POST)
        if form.is_valid() and form.has_changed():
            instance = form.save(commit=False)
            instance.user = request.user
            try:
                instance.save()
                return redirect(prev_url)
            except IntegrityError as e:
                error_message = "Laji nimellä '{}' on jo olemassa".format(instance.laji_nimi)

    return render(request, 'sport_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Lisää laji',
            'page_header': 'LISÄÄ LAJI',
            'form': form,
            'error_message': error_message
            })


@login_required
def sport_delete(request,pk):
    """ 
    Deletes sport 
    """
    sport = laji.objects.get(id=pk,user_id=request.user.id)
    sport_name = sport.laji_nimi
    btn_status = ''

    if request.method == "POST":
        response = request.POST['confirm']
        if response == 'no':
            return redirect('settings')
        if response == 'yes':
            try:
                sport.delete()
                return redirect('settings')
            except ProtectedError:
                btn_status = 'disabled'
                messages.add_message(request, messages.INFO, 'Lajia "{}" ei voida poistaa, koska siihen on liitetty harjoituksia.'.format(sport_name))

    return render(request,'sport_delete.html',
        context = {
            'sport_name': sport_name,
            'btn_status': btn_status
            })


@login_required
def zone_add(request):
    """ 
    Adds new training zone 
    """
    error_message = None
    form = TehoalueForm()

    if request.method == "POST":
        form = TehoalueForm(request.POST)
        if form.is_valid() and form.has_changed():
            instance = form.save(commit=False)
            instance.user = request.user
            try:
                instance.save()
                return redirect('settings')
            except IntegrityError as e:
                error_message = "Tehoalue nimellä '{}' on jo olemassa".format(instance.teho)

    return render(request, 'zone_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Lisää tehoalue',
            'page_header': 'LISÄÄ TEHOALUE',
            'form': form,
            'error_message': error_message
            })


@login_required
def zone_modify(request,pk):
    """ 
    Modifies training zone 
    """
    instance = tehoalue.objects.get(id=pk,user_id=request.user.id)
    form = TehoalueForm(instance=instance)
    error_message = None

    if request.method == "POST":
        form = TehoalueForm(request.POST,instance=instance)
        if form.is_valid() and form.has_changed():
            try:
                instance.save()
                return redirect('settings')
            except IntegrityError as e:
                error_message = "Tehoalue nimellä '{}' on jo olemassa".format(instance.teho)

    return render(request, 'zone_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Muokkaa tehoaluetta',
            'page_header': 'MUOKKAA TEHOALUETTA',
            'form': form,
            'error_message': error_message
            })


@login_required
def zone_delete(request,pk):
    """ 
    Deletes training zone 
    """
    instance = tehoalue.objects.get(id=pk, user_id=request.user.id)
    zone = instance.teho
    btn_status = ''

    if request.method == "POST":
        response = request.POST['confirm']
        if response == 'no':
            return redirect('settings')
        if response == 'yes':
            try:
                instance.delete()
                return redirect('settings')
            except ProtectedError:
                btn_status = 'disabled'
                messages.add_message(request, messages.INFO, 'Tehoaluetta "{}" ei voida poistaa, koska siihen on liitetty harjoituksia.'.format(zone))

    return render(request,'zone_delete.html',
        context = {
            'zone': zone,
            'btn_status': btn_status
            })


@login_required
def settings_view(request):
    """ 
    Settings page 
    """
    current_user = request.user
    current_user_id = current_user.id

    prev_url = request.META.get('HTTP_REFERER','')
    if 'zone' in prev_url:
        active_div = 'zones'
    elif 'sport' in prev_url:
        active_div = 'sports'
    else:
        active_div = 'profile'

    if request.method == 'POST':
        if 'profile_save' in request.POST:
            active_div = 'profiili'
            user_form = UserForm(request.POST, instance=current_user)
            if user_form.is_valid():
                user_form.save()
                return redirect('settings')
            else:
                pw_form = PasswordChangeForm(user=current_user)

        if 'pw_save' in request.POST:
            active_div = 'pw_reset'
            pw_form = PasswordChangeForm(data=request.POST, user=current_user)
            if pw_form.is_valid():
                pw_form.save()
                update_session_auth_hash(request,pw_form.user)
                messages.add_message(request, messages.SUCCESS, 'Salasana vaihdettu.')
                return redirect('settings')
            else:
                user_form = UserForm(instance=current_user)
    else:
        user_form = UserForm(instance=current_user)
        pw_form = PasswordChangeForm(user=current_user)

    sports = laji.objects.filter(user=current_user_id).values_list('id','id','laji','laji_nimi','laji_ryhma')
    sports_df = pd.DataFrame(list(sports), columns=['delete','edit','Lyhenne','Laji','Lajiryhmä']).sort_values(by='Laji')
    sports_values = sports_df.fillna('').to_dict(orient='index')
    sports_headers = list(sports_df)
    sports_headers[0:2] = ['','']

    zones = tehoalue.objects.filter(user=current_user_id).values_list('id','id','jarj_nro','teho','alaraja','ylaraja')
    zones_df = pd.DataFrame(list(zones), columns=['delete','edit','Järj.Nro', 'Teho', 'Alaraja', 'Yläraja']).sort_values(by='Järj.Nro')
    zones_df[['Alaraja','Yläraja']] = zones_df[['Alaraja','Yläraja']].fillna(-1).astype(int).astype(str).replace('-1', '')
    zones_values = zones_df.fillna(value='').to_dict(orient='index')
    zones_headers = list(zones_df)
    zones_headers[0:2] = ['','']

    return render(request,'settings.html',
        context = {
            'user_form': user_form,
            'pw_form': pw_form,
            'sports_values': sports_values,
            'sports_headers': sports_headers,
            'zones_values': zones_values,
            'zones_headers': zones_headers,
            'active_div': active_div
            })


def register(request):
    """ User registration """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts/login')
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', 
        context = {'form': form})


class TrainingsList(APIView):
    """ 
    List all trainings or create a new training.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        trainings = harjoitus.objects.all()
        serializer = HarjoitusSerializer(trainings, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = HarjoitusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class TrainingDetail(APIView):
    """
    Retrieve, update or delete a training.
    """
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        try:
            return harjoitus.objects.get(id=pk)
        except harjoitus.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        training = self.get_object(pk)
        serializer = HarjoitusSerializer(training)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        training = self.get_object(pk)
        serializer = HarjoitusSerializer(training, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        training = self.get_object(pk)
        training.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)