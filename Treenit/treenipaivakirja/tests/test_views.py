import datetime
from freezegun import freeze_time

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from treenipaivakirja.models import Laji,Harjoitus,Aika


@freeze_time("2020-01-12")
class ViewTest(TestCase):
    fixtures = ['test_aika.json']

    @classmethod
    def setUpTestData(cls):
        # create users
        user1 = User.objects.create_user(username='user1', password='top_secret1')
        user2 = User.objects.create_user(username='user2', password='top_secret2')
        # create sports
        running = Laji.objects.create(laji="R", laji_nimi="Running", user=user1)
        skiing = Laji.objects.create(laji="S", laji_nimi="Skiing", user=user1)
        gym = Laji.objects.create(laji="G", laji_nimi="Gym", user=user2)
        # create trainings
        running1 = Harjoitus.objects.create(
            pvm = datetime.date(2019,12,20),
            laji = running,
            kesto_h = 1,
            kesto_min = 15,
            tuntuma = 4,
            user = user1
            )
        running2 = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,2),
            laji = running,
            kesto_h = 0,
            kesto_min = 45,
            tuntuma = 7,
            user = user1
            )
        skiing1 = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,8),
            laji = skiing,
            kesto_h = 1,
            kesto_min = 30,
            tuntuma= 8,
            user = user1
            )
        gym1 = Harjoitus.objects.create(
            pvm = datetime.date(2019,12,28),
            laji = gym,
            kesto_h = 10,
            tuntuma = 6,
            user = user2
            )

    def test_index_for_user1(self):
        login = self.client.login(username='user1', password='top_secret1')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['hours_current_year'],2)
        self.assertEqual(response.context['hours_change'],2)
        self.assertEqual(response.context['hours_per_week_current_year'],1.1)
        self.assertEqual(response.context['hours_per_week_change'],1.1)
        self.assertEqual(response.context['feeling_current_period'],7.5)
        self.assertEqual(response.context['feeling_change'],3.5)

    def test_index_for_user2(self):
        login = self.client.login(username='user2', password='top_secret2')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['hours_current_year'],0)
        self.assertEqual(response.context['hours_change'],0)
        self.assertEqual(response.context['hours_per_week_current_year'],0)
        self.assertEqual(response.context['hours_per_week_change'],-0.2)
        self.assertEqual(response.context['feeling_current_period'],0)
        self.assertEqual(response.context['feeling_change'],-6)
