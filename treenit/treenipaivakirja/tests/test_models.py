import datetime

from django.test import TestCase
from treenipaivakirja.models import Laji,Harjoitus,Tehoalue,Teho


class ModelTest(TestCase):
    fixtures = ['test_aika.json']

    def test_harjoitus_model_save_aika_id(self):
        running = Laji.objects.create(laji='R', laji_nimi='Running')
        training = Harjoitus.objects.create(pvm = datetime.date(2020,1,1), laji = running)
        h = Harjoitus.objects.all()[0]
        self.assertEqual(h.aika_id,20200101)
        
    def test_harjoitus_model_save_kesto(self):
        running = Laji.objects.create(laji='R', laji_nimi='Running')
        training = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,1),
            laji = running,
            kesto_h = 1,
            kesto_min = 15
            )
        h = Harjoitus.objects.all()[0]
        self.assertEqual(h.kesto,1.25)

    def test_harjoitus_model_save_vauhti_min_km(self):
        running = Laji.objects.create(laji='R', laji_nimi='Running')
        training = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,1),
            laji = running,
            vauhti_km_h = 8
            )
        h = Harjoitus.objects.all()[0]
        self.assertEqual(h.vauhti_min_km,7.5)
        self.assertEqual(h.vauhti_min,7)
        self.assertEqual(h.vauhti_s,30)

    def test_harjoitus_model_save_vauhti_km_h(self):
        running = Laji.objects.create(laji='R', laji_nimi='Running')
        training = Harjoitus.objects.create(
            pvm = datetime.date(2020,1,1),
            laji = running,
            vauhti_min = 6,
            vauhti_s = 15
            )
        h = Harjoitus.objects.all()[0]
        self.assertEqual(float(h.vauhti_min_km),6.25)
        self.assertEqual(float(h.vauhti_km_h),9.60)

    def test_teho_model_save(self):
        running = Laji.objects.create(laji='R', laji_nimi='Running')
        training = Harjoitus.objects.create(pvm = datetime.date(2020,1,1), laji = running)
        zone_area = Tehoalue.objects.create(jarj_nro = 1, tehoalue = 'Aerobic')
        zone = Teho.objects.create(
            harjoitus = training,
            nro = 1,
            tehoalue = zone_area,
            kesto_min = 15,
            vauhti_min = 5,
            vauhti_s = 12
        )
        t = Teho.objects.all()[0]
        self.assertEqual(float(t.vauhti_min_km),5.2)
        self.assertEqual(float(t.vauhti_km_h),11.54)
        self.assertEqual(float(t.kesto),0.25)