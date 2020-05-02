import json
import logging
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from django.shortcuts import render,redirect
from django.forms import inlineformset_factory, formset_factory
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse

from treenipaivakirja.models import Harjoitus, Aika, Laji, Teho, Tehoalue, Kausi
from treenipaivakirja.forms import HarjoitusForm, LajiForm, TehoForm, TehoalueForm, UserForm, RegistrationForm, KausiForm
import treenipaivakirja.utils as utils
import treenipaivakirja.transformations as tr
import treenipaivakirja.calculations as cl


LOGGER_DEBUG = logging.getLogger(__name__)


@login_required
def index(request):
    """ 
    Front page 
    """
    current_user_id = request.user.id
    current_day = datetime.now().date()
    current_year = current_day.year
    current_week = utils.week_number(current_day)
    current_day_pd = pd.Timestamp(current_day)
    current_day_minus_14 = pd.Timestamp(current_day_pd - timedelta(days=14))
    current_day_minus_28 = pd.Timestamp(current_day_pd - timedelta(days=28))

    if not Harjoitus.objects.filter(user=current_user_id):
        hours_current_year = 0
        hours_change = 0
        hours_per_week_current_year = 0
        hours_per_week_change = 0
        feeling_current_period = 0
        feeling_change = 0
    else:
        hours_current_year = cl.hours_year_to_date(current_user_id)
        hours_past_year = cl.hours_past_year_to_date(current_user_id)
        hours_change = hours_current_year - hours_past_year

        total_hours_past_year = cl.total_hours_per_year(current_user_id, current_year-1)
        hours_per_week_current_year = hours_current_year / current_week
        hours_per_week_past_year = total_hours_past_year / 52
        hours_per_week_change = hours_per_week_current_year - hours_per_week_past_year

        feeling_current_period = cl.avg_feeling_per_period(current_user_id,current_day_minus_14,current_day)
        feeling_last_period = cl.avg_feeling_per_period(current_user_id,current_day_minus_28,current_day_minus_14)
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
    startdate = utils.coalesce(cl.first_training_date(current_user_id),current_day).strftime('%d.%m.%Y')
    enddate = current_day.strftime('%d.%m.%Y') 
    sports = tr.sports_to_dict(current_user_id)
    sport = 'Kaikki'
    zones = tr.zone_areas_to_list(current_user_id)
    table_headers = ['details','Vko','Päivä','Laji','Kesto','Keskisyke','Matka (km)','Vauhti (km/h)','Tuntuma','Kommentti','edit','delete']
    table_headers = table_headers[:-3] + zones + table_headers[-3:]
    
    if request.method == "POST":
        sport = request.POST['sport']
        startdate = request.POST['startdate']
        enddate = request.POST['enddate']
        if 'lepo' in request.POST:
            restdays = True
        else:
            restdays = False
        export_columns = ['Vko','Pvm','Viikonpäivä','Kesto','Laji','Matka (km)','Vauhti (km/h)','Keskisyke','Tuntuma', 'Kommentti'] + zones
        trainings_df = tr.trainings_to_df(
            user_id=current_user_id, 
            columns=export_columns, 
            startdate=datetime.strptime(startdate,'%d.%m.%Y').strftime('%Y%m%d'), 
            enddate=datetime.strptime(enddate,'%d.%m.%Y').strftime('%Y%m%d'),
            sport=sport,
            restdays=restdays,
            duration_format='decimal', 
            date_format='%d.%m.%Y', 
            asc=True)

        if trainings_df is None or trainings_df.empty:
            messages.add_message(request, messages.ERROR, 'Ei harjoituksia')
        else:
            try:
                if 'export_csv' in request.POST:
                    return utils.dataframe_to_csv(trainings_df,'treenit')
                if 'export_xls' in request.POST:
                    return utils.dataframe_to_excel(trainings_df,'treenit')
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
def reports_amounts(request):
    """ 
    Training amount reports 
    """
    current_user_id = request.user.id

    if not Harjoitus.objects.filter(user=current_user_id):
        years = []
        sport = ''
        sports = []
        hours_per_season_json = []
        hours_per_year_json = []
        kilometers_per_season_json = []
        kilometers_per_year_json = []
        hours_per_month_json = []
        hours_per_week_json = []
        hours_per_sport_json = []
        hours_per_sport_group_json = []
    else:
        trainings_df = tr.trainings_base_to_df(current_user_id)
        sports = tr.sports_to_list(current_user_id) 
        years = tr.years_to_list(current_user_id)
        sport = sports[0]
        
        trainings_per_season = tr.trainings_per_season_to_df(trainings_df)
        trainings_per_year = tr.trainings_per_year_to_df(trainings_df)
        trainings_per_month = tr.trainings_per_month_to_df(trainings_df,current_user_id)
        trainings_per_week = tr.trainings_per_week_to_df(trainings_df,current_user_id)

        hours_per_season_json = tr.hours_per_season_to_json(trainings_per_season)
        hours_per_year_json = tr.hours_per_year_to_json(trainings_per_year)
        hours_per_month_json = tr.hours_per_month_to_json(trainings_per_month)
        hours_per_week_json = tr.hours_per_week_to_json(trainings_per_week)
        hours_per_sport_json = tr.hours_per_sport_to_json(trainings_df)
        hours_per_sport_group_json = tr.hours_per_sport_group_to_json(trainings_df)

        kilometers_per_season_json = tr.kilometers_per_season_to_json(trainings_per_season)
        kilometers_per_year_json = tr.kilometers_per_year_to_json(trainings_per_year)

    return render(request, 'reports_amounts.html',
        context = {
            'years': years,
            'sport': sport,
            'sports': sports,
            'hours_per_season_json': hours_per_season_json,
            'hours_per_year_json': hours_per_year_json,
            'hours_per_month_json': hours_per_month_json,
            'hours_per_week_json': hours_per_week_json,
            'hours_per_sport_json': hours_per_sport_json,
            'hours_per_sport_group_json': hours_per_sport_group_json,
            'kilometers_per_season_json': kilometers_per_season_json,
            'kilometers_per_year_json': kilometers_per_year_json
            })


@login_required
def reports_sports(request):
    """ 
    Trainings reports per sport
    """
    current_user_id = request.user.id

    if not Harjoitus.objects.filter(user=current_user_id):
        sport = ''
        sports = []
        avg_per_sport = []
        amounts_per_sport = []
        avg_per_sport_table = []
        hours_per_sport = []
        kilometers_per_sport = []
    else:    
        sports = tr.sports_to_list(current_user_id) 
        sport = sports[0]
        trainings_df = tr.trainings_base_to_df(current_user_id)
        trainings_per_sport_per_year = tr.trainings_per_sport_to_df(trainings_df, 'vuosi')
        trainings_per_sport_per_season = tr.trainings_per_sport_to_df(trainings_df, 'kausi')

        hours_per_sport = {'year':{}, 'season':{}}
        kilometers_per_sport = {'year':{}, 'season':{}}
        avg_per_sport = {'year':{}, 'season':{}}
        avg_per_sport_table = {'year':{}, 'season':{}}
        amounts_per_sport = {'year':{}, 'season':{}}

        for s in sports:
            data_per_year = trainings_per_sport_per_year[trainings_per_sport_per_year['laji_nimi'].astype(str) == s]
            data_per_season = trainings_per_sport_per_season[trainings_per_sport_per_season['laji_nimi'].astype(str) == s]
            if not data_per_year.empty:
                amounts_per_sport['year'][s] = data_per_year[['vuosi','lkm','kesto (h)','matka (km)']].fillna('').to_dict(orient='records')
                avg_per_sport_table['year'][s] = data_per_year[['vuosi','kesto (h) ka.','matka (km) ka.','vauhti (km/h)','keskisyke']].rename(columns={'kesto (h) ka.':'kesto (h)','matka (km) ka.':'matka (km)'}).fillna('').to_dict(orient='records')
                data_per_year = data_per_year.set_index('vuosi')
                hours_per_sport['year'][s] = utils.dataframe_to_dict(data_per_year[['kesto (h)']])
                kilometers_per_sport['year'][s] = utils.dataframe_to_dict(data_per_year[['matka (km)']])
                avg_per_sport['year'][s] = utils.dataframe_to_dict(data_per_year[['vauhti (km/h)','keskisyke']])
            if not data_per_season.empty:
                amounts_per_sport['season'][s] = data_per_season[['kausi','lkm','kesto (h)','matka (km)']].fillna('').to_dict(orient='records')
                avg_per_sport_table['season'][s] = data_per_season[['kausi','kesto (h) ka.','matka (km) ka.','vauhti (km/h)','keskisyke']].rename(columns={'kesto (h) ka.':'kesto (h)','matka (km) ka.':'matka (km)'}).fillna('').to_dict(orient='records')
                data_per_season = data_per_season.set_index('kausi')
                hours_per_sport['season'][s] = utils.dataframe_to_dict(data_per_season[['kesto (h)']])
                kilometers_per_sport['season'][s] = utils.dataframe_to_dict(data_per_season[['matka (km)']])
                avg_per_sport['season'][s] = utils.dataframe_to_dict(data_per_season[['vauhti (km/h)','keskisyke']])

    return render(request, 'reports_sports.html',
        context = {
            'sport': sport,
            'sports': sports,
            'avg_per_sport': json.dumps(avg_per_sport),
            'amounts_per_sport': json.dumps(amounts_per_sport),
            'avg_per_sport_table': json.dumps(avg_per_sport_table),
            'hours_per_sport': json.dumps(hours_per_sport),
            'kilometers_per_sport': json.dumps(kilometers_per_sport)
            })



@login_required
def reports_zones(request):
    """ 
    Trainings reports per zone
    """
    current_user_id = request.user.id
    seasons = tr.seasons_to_list(current_user_id)
    
    if not Harjoitus.objects.filter(user=current_user_id):
        years = []
        hours_per_zone_json = []
    else:
        years = tr.years_to_list(current_user_id)
        trainings_df = tr.trainings_base_to_df(current_user_id)
        hours_per_zone_json = tr.hours_per_zone_to_json(trainings_df,current_user_id)

    return render(request, 'reports_zones.html',
        context = {
            'years': years,
            'seasons': seasons,
            'hours_per_zone_json': hours_per_zone_json
            })


@login_required
def training_add(request):
    """ 
    Inserts new training 
    """
    TehoFormset = inlineformset_factory(Harjoitus,Teho,form=TehoForm,extra=1,can_delete=True)
    required_fields = utils.get_required_fields(Teho)
    if request.method == "POST":
        harjoitus_form = HarjoitusForm(request.user,request.POST)
        teho_formset = TehoFormset(request.POST)
        if harjoitus_form.is_valid() and harjoitus_form.has_changed():
            instance = harjoitus_form.save(commit=False)
            instance.user = request.user
            instance.save()
            training = Harjoitus.objects.get(id=instance.id)
            teho_formset = TehoFormset(request.POST, request.FILES, instance=training)
            if teho_formset.is_valid() and teho_formset.has_changed():
                teho_formset.save()
            messages.add_message(request, messages.SUCCESS, 'Harjoitus tallennettu.')
            return redirect('trainings')
    else:
        harjoitus_form = HarjoitusForm(request.user,initial={'pvm': datetime.now()})
        teho_formset = TehoFormset(queryset=Teho.objects.none())
        for form in teho_formset:
            form.fields['tehoalue'].queryset = Tehoalue.objects.filter(user=request.user).order_by('jarj_nro')

    return render(request, 'training_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Lisää harjoitus',
            'page_header': 'LISÄÄ HARJOITUS',
            'teho_formset': teho_formset,
            'harjoitus_form': harjoitus_form,
            'required_fields': required_fields
            })


@login_required
def training_modify(request,pk):
    """ 
    Modifies training information 
    """
    TehoFormset = inlineformset_factory(Harjoitus,Teho,form=TehoForm,extra=1,can_delete=True)
    required_fields = utils.get_required_fields(Teho)
    training = Harjoitus.objects.get(id=pk,user_id=request.user.id)
    if request.method == "POST":
        harjoitus_form = HarjoitusForm(request.user,request.POST,instance=training)
        teho_formset = TehoFormset(request.POST,request.FILES,instance=training)
        if harjoitus_form.is_valid() and harjoitus_form.has_changed():
            harjoitus_form.save()
        if teho_formset.is_valid() and teho_formset.has_changed():
            teho_formset.save()
        messages.add_message(request, messages.SUCCESS, 'Harjoitus tallennettu.')
        return redirect('trainings')
    else:
        harjoitus_form = HarjoitusForm(request.user,instance=training)
        teho_formset = TehoFormset(instance=training)
        for form in teho_formset:
            form.fields['tehoalue'].queryset = Tehoalue.objects.filter(user=request.user).order_by('jarj_nro')
    
    return render(request, 'training_form.html',
        context = {
            'page_title': 'Treenipäiväkirja | Muokkaa harjoitusta',
            'page_header': 'MUOKKAA HARJOITUSTA',
            'teho_formset': teho_formset,
            'harjoitus_form': harjoitus_form,
            'required_fields': required_fields
            })


@login_required
def training_delete(request,pk):
    """ 
    Deletes training 
    """
    training = Harjoitus.objects.get(id=pk,user_id=request.user.id)

    if request.method == "POST":
        response = request.POST['confirm']
        if response == 'no':
            return redirect('trainings')
        if response == 'yes':
            training.delete()
            messages.add_message(request, messages.SUCCESS, 'Harjoitus poistettu.')
            return redirect('trainings')

    return render(request,'training_delete.html',
        context = {
            'day': training.pvm,
            'sport': training.laji,
            'duration': training.kesto
            })


@login_required
def settings_view(request):
    """ 
    Settings page 
    """
    current_user = request.user

    SeasonsFormset = inlineformset_factory(User, Kausi, form=KausiForm, extra=1, can_delete=True)
    ZonesFormset = inlineformset_factory(User, Tehoalue, form=TehoalueForm, extra=1, can_delete=True)
    SportsFormset = inlineformset_factory(User, Laji, form=LajiForm, extra=1, can_delete=True)

    zones_required_fields = utils.get_required_fields(Tehoalue)
    seasons_required_fields = utils.get_required_fields(Kausi)
    sports_required_fields = utils.get_required_fields(Laji)
    
    user_form = UserForm(instance=current_user)
    pw_form = PasswordChangeForm(user=current_user)
    seasons_formset = SeasonsFormset(instance=current_user)
    zones_formset = ZonesFormset(instance=current_user)
    sports_formset = SportsFormset(instance=current_user)

    if request.method == 'GET':
        page = request.GET.get('page','')
        if page not in ['profile','pw_reset','seasons','sports','zones']:
            page = 'profile'
    
    if request.method == 'POST':
        if 'profile_save' in request.POST:
            page = 'profile'
            user_form = UserForm(request.POST, instance=current_user)
            if user_form.is_valid():
                user_form.save()
                messages.add_message(request, messages.SUCCESS, 'Profiili tallennettu.')
                return redirect('settings')

        if 'pw_save' in request.POST:
            page = 'pw_reset'
            pw_form = PasswordChangeForm(data=request.POST, user=current_user)
            if pw_form.is_valid():
                pw_form.save()
                update_session_auth_hash(request, pw_form.user)
                messages.add_message(request, messages.SUCCESS, 'Salasana vaihdettu.')
                return redirect('settings')

        if 'sports_save' in request.POST:
            page = 'sports'
            sports_formset = SportsFormset(request.POST, request.FILES, instance=current_user)
            if sports_formset.is_valid() and sports_formset.has_changed():
                try:
                    sports_formset.save()
                    messages.add_message(request, messages.SUCCESS, 'Muutokset tallennettu.')
                    return redirect(reverse('settings') + '?page=' + page)
                except ProtectedError:
                    messages.add_message(request, messages.ERROR, 'Lajia ei voida poistaa, koska siihen on liitetty harjoituksia.')

        if 'zones_save' in request.POST:
            page = 'zones'
            zones_formset = ZonesFormset(request.POST, request.FILES, instance=current_user)
            if zones_formset.is_valid() and zones_formset.has_changed():
                try:
                    zones_formset.save()
                    messages.add_message(request, messages.SUCCESS, 'Muutokset tallennettu.')
                    return redirect(reverse('settings') + '?page=' + page)
                except ProtectedError:
                    messages.add_message(request, messages.ERROR, 'Tehoaluetta ei voida poistaa, koska siihen on liitetty harjoituksia.')

        if 'seasons_save' in request.POST:
            page = 'seasons'
            seasons_formset = SeasonsFormset(request.POST, request.FILES, instance=current_user)
            if seasons_formset.is_valid() and seasons_formset.has_changed():
                seasons_formset.save()
                messages.add_message(request, messages.SUCCESS, 'Muutokset tallennettu.')
                return redirect(reverse('settings') + '?page=' + page)

        if 'profile_del' in request.POST:
            u = User.objects.get(username = current_user)
            u.delete()
            messages.add_message(request, messages.SUCCESS, 'Profiili poistettu.') 
            return redirect('index')

    return render(request,'settings.html',
        context = {
            'user_form': user_form,
            'pw_form': pw_form,
            'sports_formset': sports_formset,
            'sports_required_fields': sports_required_fields,
            'seasons_formset': seasons_formset,
            'seasons_required_fields': seasons_required_fields,
            'zones_formset': zones_formset,
            'zones_required_fields': zones_required_fields,
            'page': page
            })


def register(request):
    """ User registration """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Käyttäjätili luotu.') 
            return redirect('accounts/login')
    else:
        form = RegistrationForm() 
    return render(request, 'register.html', 
        context = {'form': form})


@login_required
def trainings_data(request):
    current_user_id = request.user.id
    table_columns = request.POST.getlist('columns[]')
    trainings_df = tr.trainings_to_df(current_user_id, table_columns)
    if trainings_df is None:
        trainings_list = []
    else:
        trainings_list = trainings_df.fillna('').values.tolist()
    return JsonResponse({'data': trainings_list})


@login_required
def training_details(request, pk):
    training_details = tr.zones_per_training_to_list(pk)
    return JsonResponse({'data':training_details})