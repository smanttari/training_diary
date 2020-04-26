import os
import sys
from importlib import import_module
from datetime import date
import django


class DjangoORM:

    def __init__(self, project_root):
        # add project root to sys path
        self.project_root = project_root
        sys.path.append(project_root)

        # load Django settings for accessing its ORM
        os.environ['DJANGO_SETTINGS_MODULE'] = 'treenit.settings'
        django.setup()

        # load Django models
        self.models = import_module('treenipaivakirja.models')
        self.auth_models = import_module('django.contrib.auth.models')


    def setup_testdata(self, username, password):
        # create user
        testuser = self.auth_models.User.objects.create_user(
            username=username, 
            password=password,
            first_name='Test',
            last_name='User',
            email='test.user@mailbox.com'
            )

        # create sports
        running = self.models.Laji.objects.create(
            laji='R', 
            laji_nimi='Running', 
            laji_ryhma=None,
            user=testuser
            )
        skiing_classic = self.models.Laji.objects.create(
            laji='SC', 
            laji_nimi='Skiing (classic)', 
            laji_ryhma='Skiing', 
            user=testuser
            )
        skiing_free = self.models.Laji.objects.create(
            laji='SF', 
            laji_nimi='Skiing (free)', 
            laji_ryhma='Skiing', 
            user=testuser
            )

        # create zone areas
        aerobic = self.models.Tehoalue.objects.create(
            jarj_nro=1, 
            tehoalue='Aerobic',
            alaraja=120, 
            ylaraja=150, 
            user=testuser
            )
        anaerobic = self.models.Tehoalue.objects.create(
            jarj_nro=2, 
            tehoalue='Anaerobic',
            alaraja=150, 
            ylaraja=190, 
            user=testuser
            )

        # create seasons
        season1 = self.models.Kausi.objects.create(
            kausi='2018-2019', 
            alkupvm=date(2018,5,1), 
            loppupvm=date(2019,4,30), 
            user=testuser
            )
        season2 = self.models.Kausi.objects.create(
            kausi='2019-2020', 
            alkupvm=date(2019,5,1), 
            loppupvm=date(2020,4,30), 
            user=testuser
            )

        # create trainings
        running1 = self.models.Harjoitus.objects.create(
            pvm = date(2019,3,20),
            vuorokaudenaika = 1,
            laji = running,
            kesto_h = 1,
            kesto_min = 15,
            matka = 13,
            keskisyke = 145,
            vauhti_km_h = 10.5,
            kalorit = 345,
            tuntuma = 9,
            nousu = 124,
            kommentti = '',
            user = testuser
        )
        running2 = self.models.Harjoitus.objects.create(
            pvm = date(2019,3,24),
            vuorokaudenaika = 2,
            laji = running,
            kesto_h = 0,
            kesto_min = 45,
            matka = 7,
            keskisyke = 138,
            vauhti_km_h = 9,
            kalorit = 215,
            tuntuma = 6,
            nousu = 287,
            kommentti = 'Trail running',
            user = testuser
        )
        skiing1 = self.models.Harjoitus.objects.create(
            pvm = date(2019,12,25),
            vuorokaudenaika = 1,
            laji = skiing_classic,
            kesto_h = 1,
            kesto_min = 45,
            matka = 22,
            keskisyke = 130,
            vauhti_km_h = 13,
            kalorit = 615,
            tuntuma = 4,
            nousu = 387,
            kommentti = 'Ylläs',
            user = testuser
        )
        skiing2 = self.models.Harjoitus.objects.create(
            pvm = date(2020,1,25),
            vuorokaudenaika = 1,
            laji = skiing_free,
            kesto_h = 1,
            matka = 14,
            keskisyke = 148,
            vauhti_km_h = 14,
            kalorit = 537,
            tuntuma = 7,
            nousu = 192,
            kommentti = 'Intervals',
            user = testuser
        )
        zone1 = self.models.Teho.objects.create(
            harjoitus = skiing2,
            nro = 1,
            tehoalue = aerobic,
            kesto_min = 40,
            keskisyke = 133
        )
        zone2 = self.models.Teho.objects.create(
            harjoitus = skiing2,
            nro = 2,
            tehoalue = anaerobic,
            kesto_min = 20,
            keskisyke = 165,
            maksimisyke = 176,
            matka = 6,
            vauhti_min = 3,
            vauhti_s = 20
        )


    def remove_testdata(self, username):
        testuser = self.auth_models.User.objects.get(username=username)
        self.models.Teho.objects.filter(harjoitus__user=testuser).delete()
        self.models.Harjoitus.objects.filter(user=testuser).delete()
        self.models.Kausi.objects.filter(user=testuser).delete()
        self.models.Tehoalue.objects.filter(user=testuser).delete()
        self.models.Laji.objects.filter(user=testuser).delete()
        testuser.delete()


if __name__ == '__main__':
    orm = DjangoORM('../treenit')
    try:
        orm.setup_testdata('test_user','top_secret')
    except django.db.utils.IntegrityError:
        orm.remove_testdata('test_user')
        orm.setup_testdata('test_user','top_secret')
    orm.remove_testdata('test_user')