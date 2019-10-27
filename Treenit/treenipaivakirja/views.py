from treenipaivakirja.models import harjoitus,aika,laji,tehot,tehoalue
from treenipaivakirja.forms import HarjoitusForm,LajiForm,TehotForm,TehoalueForm,UserForm,RegistrationForm
from treenipaivakirja.serializers import HarjoitusSerializer
import treenipaivakirja.data_operations as data_operations
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
from django.http import Http404, JsonResponse, HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import numpy as np
import os
import json
import logging

LOGGER_DEBUG = logging.getLogger('django')


@login_required
def index(request):
    """ 
    Front page 
    """
    current_user_id = request.user.id
    current_day = datetime.now().date()
    current_year = current_day.year
    current_week = current_day.strftime("%V")
    current_day_pd = pd.Timestamp(current_day)
    current_day_minus_14 = pd.Timestamp(current_day_pd - timedelta(days=14))
    current_day_minus_28 = pd.Timestamp(current_day_pd - timedelta(days=28))

    if not harjoitus.objects.filter(user=current_user_id):
        hours_current_year = 0
        hours_change = 0
        hours_per_week_current_year = 0
        hours_per_week_change = 0
        feeling_current_period = 0
        feeling_change = 0
    else:
        trainings = harjoitus.objects.filter(user=current_user_id).values_list('pvm_fk_id__pvm','pvm_fk_id__vuosi','pvm_fk_id__vko','kesto','tuntuma')
        trainings_df = pd.DataFrame(list(trainings), columns=['Päivä','Vuosi','Viikko','Kesto','Tuntuma'])
        trainings_df = trainings_df.fillna(np.nan)  #replace None with NaN
        trainings_df['Päivä'] = pd.to_datetime(trainings_df['Päivä'])
        trainings_df['Kesto'] = trainings_df['Kesto'].fillna(0).astype(float).round(1)

        hours_current_year = trainings_df[(trainings_df['Vuosi'] == current_year) & (trainings_df['Päivä'] <= current_day_pd)]['Kesto'].sum()
        hours_past_year = trainings_df[(trainings_df['Vuosi'] == (current_year-1)) & (trainings_df['Päivä'] <= pd.Timestamp(current_day_pd - timedelta(days=365)))]['Kesto'].sum()
        hours_change = hours_current_year - hours_past_year

        hours_per_week_current_year = hours_current_year / (int(current_week)-1)
        hours_per_week_past_year = trainings_df[trainings_df['Vuosi'] == (current_year-1)]['Kesto'].sum() / 52
        hours_per_week_change = hours_per_week_current_year - hours_per_week_past_year

        feeling_current_period = data_operations.coalesce(trainings_df[(trainings_df['Päivä'] >= current_day_minus_14) & (trainings_df['Päivä'] <= current_day_pd)]['Tuntuma'].mean(),0)
        feeling_last_period = data_operations.coalesce(trainings_df[(trainings_df['Päivä'] >= current_day_minus_28) & (trainings_df['Päivä'] <= current_day_minus_14)]['Tuntuma'].mean(),0)
        feeling_change = feeling_current_period - feeling_last_period

    return render(request,'index.html',
        context = {
            'hours_current_year': int(round(hours_current_year,0)),
            'hours_change': int(round(hours_change,0)),
            'hours_per_week_current_year': round(hours_per_week_current_year,1),
            'hours_per_week_change': round(hours_per_week_change,1),
            'feeling_current_period': round(feeling_current_period,1),
            'feeling_change': round(feeling_change,1),
            'current_day': current_day
            })


@login_required
def trainings_view(request):
    """ 
    List of trainings 
    """
    current_user_id = request.user.id
    current_day = datetime.now().date()
    first_day = harjoitus.objects.filter(user=current_user_id).aggregate(Min('pvm_fk__pvm'))['pvm_fk__pvm__min']
    startdate = data_operations.coalesce(first_day,current_day).strftime('%d.%m.%Y')
    enddate = current_day.strftime('%d.%m.%Y') 
    sports = data_operations.sports_dict(current_user_id)
    sport = 'Kaikki'

    zones = list(tehot.objects.filter(harjoitus_fk_id__user=current_user_id).values_list('teho_id__teho',flat=True).distinct().order_by('teho_id__jarj_nro'))
    table_headers = ['edit','delete','Vko','Päivä','Laji','Kesto','Keskisyke','Matka (km)','Vauhti (km/h)','Tuntuma','Kommentti']
    table_headers = table_headers[:-1] + zones + table_headers[-1:]
    
    if request.method == "POST":
        sport = request.POST['sport']
        startdate = request.POST['startdate']
        enddate = request.POST['enddate']
        startdate_dt = datetime.strptime(startdate,'%d.%m.%Y')
        startdate_yyyymmdd = startdate_dt.strftime('%Y%m%d')
        enddate_dt = datetime.strptime(enddate,'%d.%m.%Y')
        enddate_yyyymmdd = enddate_dt.strftime('%Y%m%d')

        trainings_df = data_operations.trainings_datatable(current_user_id)

        if trainings_df is None:
            messages.add_message(request, messages.ERROR, 'Ei harjoituksia')
        else:
            trainings_df = trainings_df[(trainings_df['vvvvkkpp']>=int(startdate_yyyymmdd)) & (trainings_df['vvvvkkpp']<=int(enddate_yyyymmdd))]    
            if sport != 'Kaikki':
                if sport in sports.keys():
                    trainings_df = trainings_df[trainings_df['Lajiryhmä'] == sport]
                else:
                    trainings_df = trainings_df[trainings_df['Laji'] == sport]
            if trainings_df.empty:
                messages.add_message(request, messages.ERROR, 'Ei harjoituksia')
            else:
                export_columns = ['Vko','Pvm','Viikonpäivä','Kesto (h)','Laji','Matka (km)','Vauhti (km/h)','Vauhti (min/km)','Keskisyke', 'Nousu (m)','Tuntuma', 'Kommentti'] + zones
                trainings_export = trainings_df[export_columns]
                trainings_export = trainings_export.sort_values(by='Pvm', ascending=True)
                trainings_export['Pvm'] = pd.to_datetime(trainings_df['Pvm']).dt.strftime('%d.%m.%Y')

                if 'export_csv' in request.POST:
                    try:
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename="treenit.csv"'
                        trainings_export.to_csv(response,sep=';',header=True,index=False,encoding='utf-8')
                        return response
                    except Exception as e:
                        messages.add_message(request, messages.ERROR, 'Lataus epäonnistui: {}'.format(str(e)))

                if 'export_xls' in request.POST:
                    try:
                        response = HttpResponse(content_type='application/ms-excel')
                        response['Content-Disposition'] = 'attachment; filename="treenit.xlsx"'
                        wb = Workbook()
                        ws = wb.active
                        for r in dataframe_to_rows(trainings_export, index=False, header=True):
                            ws.append(r)
                        wb.save(response)
                        return response
                    except Exception as e:
                        messages.add_message(request, messages.ERROR, 'Lataus epäonnistui: {}'.format(str(e)))

    return render(request, 'trainings.html',
        context = {
            'sport': sport,
            'sports': sports,
            'startdate': startdate,
            'enddate': enddate,
            'table_headers': table_headers
            })


@login_required
def reports(request):
    """ 
    Trainings reports 
    """
    current_user_id = request.user.id
    current_year = str(datetime.now().year)

    if not harjoitus.objects.filter(user=current_user_id):
        years = [current_year]
        sport = ''
        sports = []
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
        hours_per_year_per_zone_json = []
    else:
        trainings_df = data_operations.trainings(current_user_id)
        sports = data_operations.sports_list(current_user_id) 
        sport = sports[0]
        years = trainings_df.sort_values('vuosi')['vuosi'].unique()

        trainings_per_year = data_operations.trainings_per_year(trainings_df)
        trainings_per_month = data_operations.trainings_per_month(trainings_df,current_user_id)
        trainings_per_week = data_operations.trainings_per_week(trainings_df,current_user_id)
        trainings_per_sport = data_operations.trainings_per_sport(trainings_df)

        hours_per_year_json = data_operations.hours_per_year(trainings_per_year)
        hours_per_month_json = data_operations.hours_per_month(trainings_per_month)
        hours_per_week_json = data_operations.hours_per_week(trainings_per_week)
        hours_per_sport_json = data_operations.hours_per_sport(trainings_df)
        hours_per_sport_group_json = data_operations.hours_per_sport_group(trainings_df)
        kilometers_per_year_json = data_operations.kilometers_per_year(trainings_per_year)
        hours_per_year_per_zone_json = data_operations.hours_per_year_per_zone(trainings_df,current_user_id)
        
        hours_per_year_per_sport = {}
        kilometers_per_year_per_sport = {}
        avg_per_year_per_sport = {}
        avg_per_year_per_sport_table = {}
        amounts_per_year_per_sport = {}

        for s in sports:
            data = trainings_per_sport[trainings_per_sport['laji_nimi'] == s]
            if not data.empty:
                amounts_per_year_per_sport[s] = data[['vuosi','lkm','kesto (h)','matka (km)']].fillna('').to_dict(orient='records')
                avg_per_year_per_sport_table[s] = data[['vuosi','kesto (h) ka.','matka (km) ka.','vauhti (km/h)','keskisyke']].rename(columns={'kesto (h) ka.':'kesto (h)','matka (km) ka.':'matka (km)'}).fillna('').to_dict(orient='records')
                data = data.set_index('vuosi')
                hours_per_year_per_sport[s] = json.loads(data_operations.dataframe_to_json(data[['kesto (h)']]))
                kilometers_per_year_per_sport[s] = json.loads(data_operations.dataframe_to_json(data[['matka (km)']]))
                avg_per_year_per_sport[s] = json.loads(data_operations.dataframe_to_json(data[['vauhti (km/h)','keskisyke']]))
        
        hours_per_year_per_sport_json = json.dumps(hours_per_year_per_sport)
        kilometers_per_year_per_sport_json = json.dumps(kilometers_per_year_per_sport)

    return render(request, 'reports.html',
        context = {
            'current_year': current_year,
            'years': years,
            'sport': sport,
            'sports': sports,
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
            'hours_per_year_per_zone_json': hours_per_year_per_zone_json
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
            kesto_h = data_operations.coalesce(harjoitus_form.cleaned_data['kesto_h'],0)
            kesto_min = data_operations.coalesce(harjoitus_form.cleaned_data['kesto_min'],0)
            instance.kesto_h = kesto_h
            instance.kesto_min = kesto_min
            instance.kesto = data_operations.h_min_to_hours(kesto_h,kesto_min)
            vauhti_m = harjoitus_form.cleaned_data['vauhti_min']
            vauhti_s = harjoitus_form.cleaned_data['vauhti_s']
            instance.vauhti_min_km = data_operations.vauhti_min_km(vauhti_m,vauhti_s)
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
            kesto_h = data_operations.coalesce(harjoitus_form.cleaned_data['kesto_h'],0)
            kesto_min = data_operations.coalesce(harjoitus_form.cleaned_data['kesto_min'],0)
            post.kesto_h = kesto_h
            post.kesto_min = kesto_min
            post.kesto = data_operations.h_min_to_hours(kesto_h,kesto_min)
            vauhti_km_h = harjoitus_form.cleaned_data['vauhti_km_h']
            vauhti_m = harjoitus_form.cleaned_data['vauhti_min']
            vauhti_s = harjoitus_form.cleaned_data['vauhti_s']
            post.vauhti_min_km = data_operations.vauhti_min_km(vauhti_m,vauhti_s)
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

    sports_df = data_operations.sports(current_user_id)
    sports_values = sports_df.to_dict(orient='index')
    sports_headers = list(sports_df)
    sports_headers[0:2] = ['','']

    zones_df = data_operations.zones(current_user_id)
    zones_values = zones_df.to_dict(orient='index')
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


@login_required
def trainings_data(request):
    current_user_id = request.user.id
    table_columns = request.POST.getlist('columns[]')
    trainings_df = data_operations.trainings_datatable(current_user_id)
    if trainings_df is None:
        trainings_list = []
    else:
        trainings_df = trainings_df[table_columns]
        trainings_list = trainings_df.fillna('').values.tolist()
    return JsonResponse(trainings_list, safe=False)



@api_view(['GET', 'POST'])
@permission_classes((IsAdminUser, ))
def trainings_api(request):
    """ 
    List all trainings or create a new training.
    """
    if request.method == 'GET':
        trainings = harjoitus.objects.all()
        serializer = HarjoitusSerializer(trainings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = HarjoitusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAdminUser, ))
def trainings_api_by_id(request,pk):
    """
    Retrieve, update or delete a training.
    """
    try:
        training = harjoitus.objects.get(id=pk)
    except harjoitus.DoesNotExist:
        raise Http404

    if request.method == 'GET':
        serializer = HarjoitusSerializer(training)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = HarjoitusSerializer(training, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        training.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)