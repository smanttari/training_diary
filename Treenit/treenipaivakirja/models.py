from django.db import models
from django.contrib.auth.models import User
from treenipaivakirja.utils import coalesce, duration_to_decimal, speed_min_per_km
        
        
class Harjoitus(models.Model):
    pvm = models.DateField(verbose_name='Päivä')
    aika = models.ForeignKey('aika', on_delete=models.PROTECT, verbose_name='vvvvkkpp', blank=True)
    laji = models.ForeignKey('laji', on_delete=models.PROTECT, verbose_name='Laji')
    kesto = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    kesto_h = models.PositiveIntegerField(null=True, blank=True, verbose_name='h')
    kesto_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    matka = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (km/h)', blank=True)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (min/km)', blank=True)
    vauhti_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    vauhti_s = models.PositiveIntegerField(null=True, blank=True, verbose_name='s')
    keskisyke = models.IntegerField(null=True, blank=True)
    kalorit = models.IntegerField(null=True, blank=True)    
    tuntuma_choices = ((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10))    
    tuntuma = models.IntegerField(choices=tuntuma_choices,null=True, blank=True)
    kommentti = models.TextField(max_length=250, null=True, blank=True)
    vuorokaudenaika_choices = ((1,'aamupäivä'),(2,'iltapäivä'),)
    vuorokaudenaika = models.IntegerField(choices=vuorokaudenaika_choices, blank=False, default=2, verbose_name="")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nousu = models.IntegerField(null=True, blank=True, verbose_name='Nousu (m)')

    class Meta:
        verbose_name_plural = "Harjoitus"
    
    def save(self, *args, **kwargs):
        self.aika_id = self.pvm.strftime('%Y%m%d')
        self.kesto_h = coalesce(self.kesto_h,0)
        self.kesto_min = coalesce(self.kesto_min,0)
        self.kesto = duration_to_decimal(self.kesto_h,self.kesto_min)
        self.vauhti_min_km = speed_min_per_km(self.vauhti_min,self.vauhti_s)
        if self.vauhti_min_km is None and self.vauhti_km_h is not None and self.vauhti_km_h != 0:
            self.vauhti_min_km = 60 / self.vauhti_km_h
            self.vauhti_min = int(self.vauhti_min_km)
            self.vauhti_s = round((self.vauhti_min_km*60) % 60,0)
        elif self.vauhti_min_km is not None and self.vauhti_min_km != 0 and self.vauhti_km_h is None:
            self.vauhti_km_h = 60 / self.vauhti_min_km
        super(Harjoitus, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s h' % (self.laji, self.kesto)
    
    
class Laji(models.Model):   
    laji = models.CharField(max_length=10, verbose_name='Lyhenne')
    laji_nimi = models.CharField(max_length=50, verbose_name='Laji')
    laji_ryhma = models.CharField(max_length=50, verbose_name='Lajiryhmä', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Laji"
        ordering = ['laji_nimi']

    def __str__(self):
        return self.laji_nimi
         

class Aika(models.Model):
    vvvvkkpp = models.IntegerField(primary_key=True)
    pvm = models.DateField()
    vuosi = models.IntegerField(verbose_name='Vuosi')
    kk = models.IntegerField()
    kk_nimi = models.CharField(max_length=20)
    paiva = models.IntegerField()
    vko = models.IntegerField()
    viikonpaiva = models.IntegerField()
    viikonpaiva_lyh = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Aika" 

    def __str__(self):
        return str(self.vvvvkkpp)


class Teho(models.Model):
    harjoitus = models.ForeignKey('harjoitus', on_delete=models.CASCADE)
    nro = models.IntegerField(blank=False)
    kesto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    kesto_h = models.PositiveIntegerField(null=True, blank=True, verbose_name='h')
    kesto_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    keskisyke = models.IntegerField(null=True, blank=True)
    maksimisyke = models.IntegerField(null=True, blank=True, verbose_name='Maksimisyke')
    matka = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (km/h)', blank=True)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (min/km)', blank=True)
    vauhti_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    vauhti_s = models.PositiveIntegerField(null=True, blank=True, verbose_name='s')
    tehoalue = models.ForeignKey('tehoalue', on_delete=models.PROTECT, blank=False)

    class Meta:
        verbose_name_plural = "Teho"

    def save(self, *args, **kwargs):
        self.kesto_h = coalesce(self.kesto_h,0)
        self.kesto_min = coalesce(self.kesto_min,0)
        self.kesto = duration_to_decimal(self.kesto_h,self.kesto_min)
        self.vauhti_min_km = speed_min_per_km(self.vauhti_min,self.vauhti_s)
        if self.vauhti_min_km is not None and self.vauhti_min_km != 0:
            self.vauhti_km_h = 60 / self.vauhti_min_km
        super(Teho, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s %s h' % (self.harjoitus, self.tehoalue, self.kesto)


class Tehoalue(models.Model):
    jarj_nro = models.IntegerField(blank=False, verbose_name='Järj.Nro')
    tehoalue = models.CharField(max_length=100, verbose_name='Tehoalue')
    alaraja = models.IntegerField(null=True, blank=True, verbose_name='Alaraja')
    ylaraja = models.IntegerField(null=True, blank=True, verbose_name='Yläraja')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Tehoalue"
        ordering = ['jarj_nro']

    def __str__(self):
        return self.tehoalue


class Kausi(models.Model):
    kausi = models.CharField(max_length=20, verbose_name='Harjoituskausi')
    alkupvm = models.DateField(verbose_name='Alkupäivä')
    loppupvm = models.DateField(verbose_name='Loppupäivä')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Kausi"
        ordering = ['kausi']

    def __str__(self):
        return self.kausi