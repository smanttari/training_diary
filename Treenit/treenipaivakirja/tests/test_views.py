import json
import datetime
from freezegun import freeze_time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from treenipaivakirja.models import Laji,Harjoitus,Aika,Kausi,Tehoalue,Teho


@freeze_time('2020-01-12')
class ViewTest(TestCase):
    fixtures = ['test_aika.json']

    @classmethod
    def setUpTestData(cls):
        # create users
        user1 = User.objects.create_user(username='user1', password='top_secret1')
        user2 = User.objects.create_user(username='user2', password='top_secret2')
        # create sports
        running = Laji.objects.create(laji='R', laji_nimi='Running', laji_ryhma='Cardio' ,user=user1)
        skiing = Laji.objects.create(laji='S', laji_nimi='Skiing', laji_ryhma='Cardio', user=user1)
        gym1 = Laji.objects.create(laji='G', laji_nimi='Gym', user=user1)
        gym2 = Laji.objects.create(laji='G', laji_nimi='Gym', user=user2)
        # create seasons
        season1 = Kausi.objects.create(
            kausi = 'season1',
            alkupvm = datetime.date(2019,12,1),
            loppupvm = datetime.date(2020,1,31),
            user = user1
            )
        # create zone-areas
        zone_area1 = Tehoalue.objects.create(
            jarj_nro = 1,
            tehoalue = 'Aerobic',
            alaraja = 120,
            ylaraja = 160,
            user = user1
        )
        zone_area2 = Tehoalue.objects.create(
            jarj_nro = 2,
            tehoalue = 'Anaerobic',
            alaraja = 160,
            ylaraja = 190,
            user = user1
        )
        # create trainings
        running1 = Harjoitus.objects.create(
            pvm = datetime.date(2019,12,20),
            laji = running,
            kesto_h = 1,
            kesto_min = 15,
            matka = 10,
            keskisyke = 150,
            vauhti_km_h = 8,
            tuntuma = 4,
            user = user1
            )
        running2 = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,2),
            laji = running,
            kesto_h = 0,
            kesto_min = 45,
            matka = 8,
            keskisyke = 140,
            vauhti_km_h = 10,
            tuntuma = 7,
            user = user1
            )
        skiing1 = Harjoitus.objects.create(
            pvm = datetime.date(2019,1,7),
            laji = skiing,
            kesto_h = 1,
            kesto_min = 45,
            matka = 20,
            keskisyke = 140,
            vauhti_km_h = 15,
            tuntuma= 5,
            user = user1
            )
        skiing2 = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,8),
            laji = skiing,
            kesto_h = 1,
            matka = 13,
            keskisyke = 130,
            vauhti_km_h = 13,
            tuntuma= 8,
            user = user1
            )
        skiing3 = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,10),
            laji = skiing,
            kesto_min = 30,
            matka = 7,
            keskisyke = 140,
            tuntuma= 8,
            user = user1
            )
        gym1 = Harjoitus.objects.create(
            pvm = datetime.date(2019,11,28),
            laji = gym2,
            kesto_h = 10,
            tuntuma = 6,
            user = user2
            )
        # create zones
        zone1 = Teho.objects.create(
            harjoitus = running2,
            nro = 1,
            tehoalue = zone_area1,
            kesto_min = 30
        )
        zone2 = Teho.objects.create(
            harjoitus = running2,
            nro = 2,
            tehoalue = zone_area2,
            kesto_min = 15
        )
        zone3 = Teho.objects.create(
            harjoitus = skiing2,
            nro = 1,
            tehoalue = zone_area1,
            kesto_h = 1
        )

    def test_index_for_user1(self):
        login = self.client.login(username='user1', password='top_secret1')
        response = self.client.get(reverse('index'))
        context = response.context
        self.assertEqual(context['hours_current_year'],2)
        self.assertEqual(context['hours_change'],0)
        self.assertEqual(context['hours_per_week_current_year'],1.1)
        self.assertEqual(context['hours_per_week_change'],1.1)
        self.assertEqual(context['feeling_current_period'],7.7)
        self.assertEqual(context['feeling_change'],3.7)

    def test_index_for_user2(self):
        login = self.client.login(username='user2', password='top_secret2')
        response = self.client.get(reverse('index'))
        context = response.context
        self.assertEqual(context['hours_current_year'],0)
        self.assertEqual(context['hours_change'],0)
        self.assertEqual(context['hours_per_week_current_year'],0)
        self.assertEqual(context['hours_per_week_change'],-0.2)
        self.assertEqual(context['feeling_current_period'],0)
        self.assertEqual(context['feeling_change'],0)

    def test_trainings_view_for_user1(self):
        login = self.client.login(username='user1', password='top_secret1')
        response = self.client.get(reverse('trainings'))
        context = response.context
        self.assertEqual(context['sports'],{'Kaikki': [], 'Cardio': ['Running', 'Skiing'], 'Muut': ['Gym']})
        self.assertEqual(context['startdate'],'07.01.2019')
        self.assertEqual(context['enddate'],datetime.datetime.now().strftime('%d.%m.%Y'))
        self.assertEqual(context['table_headers'],['details', 'Vko', 'Päivä', 'Laji', 'Kesto', 'Keskisyke', 'Matka (km)', 'Vauhti (km/h)', 'Tuntuma', 'Aerobic', 'Anaerobic', 'Kommentti', 'edit', 'delete'])

    def test_trainings_view_for_user2(self):
        login = self.client.login(username='user2', password='top_secret2')
        response = self.client.get(reverse('trainings'))
        context = response.context
        self.assertEqual(context['sports'],{'Kaikki': [], 'Muut': ['Gym']})
        self.assertEqual(context['startdate'],'28.11.2019')
        self.assertEqual(context['enddate'],datetime.datetime.now().strftime('%d.%m.%Y'))
        self.assertEqual(context['table_headers'],['details', 'Vko', 'Päivä', 'Laji', 'Kesto', 'Keskisyke', 'Matka (km)', 'Vauhti (km/h)', 'Tuntuma', 'Kommentti', 'edit', 'delete'])

    def test_reports_amounts_for_user1(self):
        login = self.client.login(username='user1', password='top_secret1')
        response = self.client.get(reverse('reports_amounts'))
        context = response.context
        self.assertEqual(context['years'],['2020','2019'])
        self.assertEqual(context['sport'],'Gym')
        self.assertEqual(context['sports'],['Gym','Running','Skiing'])
        self.assertEqual(json.loads(context['hours_per_season_json']),[{'category':'season1','series':4.0}])
        self.assertEqual(json.loads(context['hours_per_year_json']),[{'category':'2019','series':3.0}, {'category':'2020','series':2.0}])
        self.assertEqual(json.loads(context['hours_per_month_json']),[
            {"category": "Tammikuu", "series": {"2019": 2.0, "2020": 2.0}}, {"category": "Helmikuu", "series": {"2019": 0.0, "2020": ""}}, 
            {"category": "Maaliskuu", "series": {"2019": 0.0, "2020": ""}}, {"category": "Huhtikuu", "series": {"2019": 0.0, "2020": ""}}, 
            {"category": "Toukokuu", "series": {"2019": 0.0, "2020": ""}}, {"category": "Kesäkuu", "series": {"2019": 0.0, "2020": ""}}, 
            {"category": "Heinäkuu", "series": {"2019": 0.0, "2020": ""}}, {"category": "Elokuu", "series": {"2019": 0.0, "2020": ""}}, 
            {"category": "Syyskuu", "series": {"2019": 0.0, "2020": ""}}, {"category": "Lokakuu", "series": {"2019": 0.0, "2020": ""}},
            {"category": "Marraskuu", "series": {"2019": 0.0, "2020": ""}}, {"category": "Joulukuu", "series": {"2019": 1.0, "2020": ""}}
        ])
        self.assertEqual(json.loads(context['hours_per_week_json']),[
            {"category": 1, "series": {"2019": "", "2020": 0.8}}, {"category": 2, "series": {"2019": 1.8, "2020": 1.5}}, {"category": 3, "series": {"2019": 0.0, "2020": ""}}, {"category": 4, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 5, "series": {"2019": 0.0, "2020": ""}}, {"category": 6, "series": {"2019": 0.0, "2020": ""}}, {"category": 7, "series": {"2019": 0.0, "2020": ""}}, {"category": 8, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 9, "series": {"2019": 0.0, "2020": ""}}, {"category": 10, "series": {"2019": 0.0, "2020": ""}}, {"category": 11, "series": {"2019": 0.0, "2020": ""}}, {"category": 12, "series": {"2019": 0.0, "2020": ""}},
            {"category": 13, "series": {"2019": 0.0, "2020": ""}}, {"category": 14, "series": {"2019": 0.0, "2020": ""}}, {"category": 15, "series": {"2019": 0.0, "2020": ""}}, {"category": 16, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 17, "series": {"2019": 0.0, "2020": ""}}, {"category": 18, "series": {"2019": 0.0, "2020": ""}}, {"category": 19, "series": {"2019": 0.0, "2020": ""}}, {"category": 20, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 21, "series": {"2019": 0.0, "2020": ""}}, {"category": 22, "series": {"2019": 0.0, "2020": ""}}, {"category": 23, "series": {"2019": 0.0, "2020": ""}}, {"category": 24, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 25, "series": {"2019": 0.0, "2020": ""}}, {"category": 26, "series": {"2019": 0.0, "2020": ""}}, {"category": 27, "series": {"2019": 0.0, "2020": ""}}, {"category": 28, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 29, "series": {"2019": 0.0, "2020": ""}}, {"category": 30, "series": {"2019": 0.0, "2020": ""}}, {"category": 31, "series": {"2019": 0.0, "2020": ""}}, {"category": 32, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 33, "series": {"2019": 0.0, "2020": ""}}, {"category": 34, "series": {"2019": 0.0, "2020": ""}}, {"category": 35, "series": {"2019": 0.0, "2020": ""}}, {"category": 36, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 37, "series": {"2019": 0.0, "2020": ""}}, {"category": 38, "series": {"2019": 0.0, "2020": ""}}, {"category": 39, "series": {"2019": 0.0, "2020": ""}}, {"category": 40, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 41, "series": {"2019": 0.0, "2020": ""}}, {"category": 42, "series": {"2019": 0.0, "2020": ""}}, {"category": 43, "series": {"2019": 0.0, "2020": ""}}, {"category": 44, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 45, "series": {"2019": 0.0, "2020": ""}}, {"category": 46, "series": {"2019": 0.0, "2020": ""}}, {"category": 47, "series": {"2019": 0.0, "2020": ""}}, {"category": 48, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 49, "series": {"2019": 0.0, "2020": ""}}, {"category": 50, "series": {"2019": 0.0, "2020": ""}}, {"category": 51, "series": {"2019": 1.2, "2020": ""}}, {"category": 52, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 53, "series": {"2019": "", "2020": ""}}
            ])
        self.assertEqual(json.loads(context['hours_per_sport_json']),[{"category": "Running", "series": {"2019": 1.2, "2020": 0.8}}, {"category": "Skiing", "series": {"2019": 1.8, "2020": 1.5}}])
        self.assertEqual(json.loads(context['hours_per_sport_group_json']),[{"category": "Cardio", "series": {"2019": 3.0, "2020": 2.2}}])
        self.assertEqual(json.loads(context['kilometers_per_season_json']),[{'category':'season1','series':38.0}])
        self.assertEqual(json.loads(context['kilometers_per_year_json']),[{"category":"2019","series":30.0},{"category":"2020","series":28.0}])

    def test_reports_amounts_for_user2(self):
        login = self.client.login(username='user2', password='top_secret2')
        response = self.client.get(reverse('reports_amounts'))
        context = response.context
        self.assertEqual(context['years'],['2019'])
        self.assertEqual(context['sport'],'Gym')
        self.assertEqual(context['sports'],['Gym'])
        self.assertEqual(json.loads(context['hours_per_season_json']),[])
        self.assertEqual(json.loads(context['hours_per_year_json']),[{'category':'2019','series':10.0}])
        self.assertEqual(json.loads(context['hours_per_month_json']),[
            {"category": "Tammikuu", "series": {"2019": "", "2020": 0.0}}, {"category": "Helmikuu", "series": {"2019": "", "2020": ""}}, 
            {"category": "Maaliskuu", "series": {"2019": "", "2020": ""}}, {"category": "Huhtikuu", "series": {"2019": "", "2020": ""}}, 
            {"category": "Toukokuu", "series": {"2019": "", "2020": ""}}, {"category": "Kesäkuu", "series": {"2019": "", "2020": ""}}, 
            {"category": "Heinäkuu", "series": {"2019": "", "2020": ""}}, {"category": "Elokuu", "series": {"2019": "", "2020": ""}}, 
            {"category": "Syyskuu", "series": {"2019": "", "2020": ""}}, {"category": "Lokakuu", "series": {"2019": "", "2020": ""}},
            {"category": "Marraskuu", "series": {"2019": 10.0, "2020": ""}}, {"category": "Joulukuu", "series": {"2019": 0.0, "2020": ""}}
        ])
        self.assertEqual(json.loads(context['hours_per_week_json']),[
            {"category": 1, "series": {"2019": "", "2020": 0.0}}, {"category": 2, "series": {"2019": "", "2020": 0.0}}, {"category": 3, "series": {"2019": "", "2020": ""}}, {"category": 4, "series": {"2019": "", "2020": ""}}, 
            {"category": 5, "series": {"2019": "", "2020": ""}}, {"category": 6, "series": {"2019": "", "2020": ""}}, {"category": 7, "series": {"2019": "", "2020": ""}}, {"category": 8, "series": {"2019": "", "2020": ""}}, 
            {"category": 9, "series": {"2019": "", "2020": ""}}, {"category": 10, "series": {"2019": "", "2020": ""}}, {"category": 11, "series": {"2019": "", "2020": ""}}, {"category": 12, "series": {"2019": "", "2020": ""}},
            {"category": 13, "series": {"2019": "", "2020": ""}}, {"category": 14, "series": {"2019": "", "2020": ""}}, {"category": 15, "series": {"2019": "", "2020": ""}}, {"category": 16, "series": {"2019": "", "2020": ""}}, 
            {"category": 17, "series": {"2019": "", "2020": ""}}, {"category": 18, "series": {"2019": "", "2020": ""}}, {"category": 19, "series": {"2019": "", "2020": ""}}, {"category": 20, "series": {"2019": "", "2020": ""}}, 
            {"category": 21, "series": {"2019": "", "2020": ""}}, {"category": 22, "series": {"2019": "", "2020": ""}}, {"category": 23, "series": {"2019": "", "2020": ""}}, {"category": 24, "series": {"2019": "", "2020": ""}}, 
            {"category": 25, "series": {"2019": "", "2020": ""}}, {"category": 26, "series": {"2019": "", "2020": ""}}, {"category": 27, "series": {"2019": "", "2020": ""}}, {"category": 28, "series": {"2019": "", "2020": ""}}, 
            {"category": 29, "series": {"2019": "", "2020": ""}}, {"category": 30, "series": {"2019": "", "2020": ""}}, {"category": 31, "series": {"2019": "", "2020": ""}}, {"category": 32, "series": {"2019": "", "2020": ""}}, 
            {"category": 33, "series": {"2019": "", "2020": ""}}, {"category": 34, "series": {"2019": "", "2020": ""}}, {"category": 35, "series": {"2019": "", "2020": ""}}, {"category": 36, "series": {"2019": "", "2020": ""}}, 
            {"category": 37, "series": {"2019": "", "2020": ""}}, {"category": 38, "series": {"2019": "", "2020": ""}}, {"category": 39, "series": {"2019": "", "2020": ""}}, {"category": 40, "series": {"2019": "", "2020": ""}}, 
            {"category": 41, "series": {"2019": "", "2020": ""}}, {"category": 42, "series": {"2019": "", "2020": ""}}, {"category": 43, "series": {"2019": "", "2020": ""}}, {"category": 44, "series": {"2019": "", "2020": ""}}, 
            {"category": 45, "series": {"2019": "", "2020": ""}}, {"category": 46, "series": {"2019": "", "2020": ""}}, {"category": 47, "series": {"2019": "", "2020": ""}}, {"category": 48, "series": {"2019": 10.0, "2020": ""}}, 
            {"category": 49, "series": {"2019": 0.0, "2020": ""}}, {"category": 50, "series": {"2019": 0.0, "2020": ""}}, {"category": 51, "series": {"2019": 0.0, "2020": ""}}, {"category": 52, "series": {"2019": 0.0, "2020": ""}}, 
            {"category": 53, "series": {"2019": "", "2020": ""}}
            ])
        self.assertEqual(json.loads(context['hours_per_sport_json']),[{"category": "Gym", "series": {"2019": 10.0}}])
        self.assertEqual(json.loads(context['hours_per_sport_group_json']),[{"category": "Muut", "series": {"2019": 10.0}}])
        self.assertEqual(json.loads(context['kilometers_per_season_json']),[])
        self.assertEqual(json.loads(context['kilometers_per_year_json']),[{"category":"2019","series":0.0}])

    def test_reports_sports_for_user1(self):
        login = self.client.login(username='user1', password='top_secret1')
        response = self.client.get(reverse('reports_sports'))
        context = response.context
        self.assertEqual(context['sport'],'Gym')
        self.assertEqual(context['sports'],['Gym','Running','Skiing'])
        self.assertEqual(json.loads(context['avg_per_sport']), {
            'year': {
                'Running': [{'category': '2019', 'series': {'vauhti (km/h)': 8.0, 'keskisyke': 150.0}}, {'category': '2020', 'series': {'vauhti (km/h)': 10.0, 'keskisyke': 140.0}}], 
                'Skiing': [{'category': '2019', 'series': {'vauhti (km/h)': 15.0, 'keskisyke': 140.0}}, {'category': '2020', 'series': {'vauhti (km/h)': 13.0, 'keskisyke': 135.0}}]
                }, 
            'season': {
                'Running': [{'category': 'season1', 'series': {'vauhti (km/h)': 9.0, 'keskisyke': 145.0}}], 
                'Skiing': [{'category': 'season1', 'series': {'vauhti (km/h)': 13.0, 'keskisyke': 135.0}}]
                }
            })
        self.assertEqual(json.loads(context['amounts_per_sport']),{
            'year': {
                'Running': [{'vuosi': '2019', 'lkm': 1, 'kesto (h)': 1.2, 'matka (km)': 10.0}, {'vuosi': '2020', 'lkm': 1, 'kesto (h)': 0.8, 'matka (km)': 8.0}], 
                'Skiing': [{'vuosi': '2019', 'lkm': 1, 'kesto (h)': 1.8, 'matka (km)': 20.0}, {'vuosi': '2020', 'lkm': 2, 'kesto (h)': 1.5, 'matka (km)': 20.0}]
                }, 
            'season': {
                'Running': [{'kausi': 'season1', 'lkm': 2, 'kesto (h)': 2.0, 'matka (km)': 18.0}], 
                'Skiing': [{'kausi': 'season1', 'lkm': 2, 'kesto (h)': 1.5, 'matka (km)': 20.0}]
                }
            })
        self.assertEqual(json.loads(context['avg_per_sport_table']),{
            "year": {
                "Running": [{"vuosi": "2019", "kesto (h)": 1.2, "matka (km)": 10.0, "vauhti (km/h)": 8.0, "keskisyke": 150}, {"vuosi": "2020", "kesto (h)": 0.8, "matka (km)": 8.0, "vauhti (km/h)": 10.0, "keskisyke": 140}], 
                "Skiing": [{"vuosi": "2019", "kesto (h)": 1.8, "matka (km)": 20.0, "vauhti (km/h)": 15.0, "keskisyke": 140}, {"vuosi": "2020", "kesto (h)": 0.8, "matka (km)": 10.0, "vauhti (km/h)": 13.0, "keskisyke": 135}]
                }, 
            "season": {
                "Running": [{"kausi": "season1", "kesto (h)": 1.0, "matka (km)": 9.0, "vauhti (km/h)": 9.0, "keskisyke": 145}], 
                "Skiing": [{"kausi": "season1", "kesto (h)": 0.8, "matka (km)": 10.0, "vauhti (km/h)": 13.0, "keskisyke": 135}]
                }
            })
        self.assertEqual(json.loads(context['hours_per_sport']),{
            "year": {
                "Running": [{"category": "2019", "series": {"kesto (h)": 1.2}}, {"category": "2020", "series": {"kesto (h)": 0.8}}], 
                "Skiing": [{"category": "2019", "series": {"kesto (h)": 1.8}}, {"category": "2020", "series": {"kesto (h)": 1.5}}]
                }, 
            "season": {
                "Running": [{"category": "season1", "series": {"kesto (h)": 2.0}}], 
                "Skiing": [{"category": "season1", "series": {"kesto (h)": 1.5}}]
                }
            })
        self.assertEqual(json.loads(context['kilometers_per_sport']),{
            "year": {
                "Running": [{"category": "2019", "series": {"matka (km)": 10.0}}, {"category": "2020", "series": {"matka (km)": 8.0}}], 
                "Skiing": [{"category": "2019", "series": {"matka (km)": 20.0}}, {"category": "2020", "series": {"matka (km)": 20.0}}]
                }, 
            "season": {
                "Running": [{"category": "season1", "series": {"matka (km)": 18.0}}], 
                "Skiing": [{"category": "season1", "series": {"matka (km)": 20.0}}]
                }
            })

    def test_reports_sports_for_user2(self):
        login = self.client.login(username='user2', password='top_secret2')
        response = self.client.get(reverse('reports_sports'))
        context = response.context
        self.assertEqual(context['sport'],'Gym')
        self.assertEqual(context['sports'],['Gym'])
        self.assertEqual(json.loads(context['avg_per_sport']), {'year': {'Gym': [{'category': '2019', 'series': {'vauhti (km/h)': '', 'keskisyke': ''}}]}, 'season': {}})
        self.assertEqual(json.loads(context['amounts_per_sport']),{'year': {'Gym': [{'vuosi': '2019', 'lkm': 1, 'kesto (h)': 10.0, 'matka (km)': 0.0}]}, 'season': {}})
        self.assertEqual(json.loads(context['avg_per_sport_table']),{"year": {"Gym": [{"vuosi": "2019", "kesto (h)": 10.0, "matka (km)": '', "vauhti (km/h)": '', "keskisyke": ''}]}, "season": {}})
        self.assertEqual(json.loads(context['hours_per_sport']),{"year": {"Gym": [{"category": "2019", "series": {"kesto (h)": 10.0}}]}, "season": {}})
        self.assertEqual(json.loads(context['kilometers_per_sport']),{"year": {"Gym": [{"category": "2019", "series": {"matka (km)": 0.0}}]}, "season": {}})

    def test_reports_zones_for_user1(self):
        login = self.client.login(username='user1', password='top_secret1')
        response = self.client.get(reverse('reports_zones'))
        context = response.context
        self.assertEqual(context['years'],['2020','2019'])
        self.assertEqual(context['seasons'],['season1'])
        self.assertEqual(json.loads(context['hours_per_zone_json']),{
            'year': [
                {'category': '2019', 'series': {'Aerobic': '', 'Anaerobic': '', 'Muu': 3.0}}, 
                {'category': '2020', 'series': {'Aerobic': 1.5, 'Anaerobic': 0.2, 'Muu': 0.5}}
                ], 
            'season': [
                {'category': 'season1', 'series': {'Aerobic': 1.5, 'Anaerobic': 0.2, 'Muu': 1.8}}
                ]
            })

    def test_reports_zones_for_user2(self):
        login = self.client.login(username='user2', password='top_secret2')
        response = self.client.get(reverse('reports_zones'))
        context = response.context
        self.assertEqual(context['years'],['2019'])
        self.assertEqual(context['seasons'],[])
        self.assertEqual(json.loads(context['hours_per_zone_json']),[])