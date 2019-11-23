from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
        
        
class harjoitus(models.Model):

    pvm = models.DateField(verbose_name='Päivä')
    aika = models.ForeignKey('aika', on_delete=models.PROTECT, verbose_name='vvvvkkpp',blank=True)
    laji = models.ForeignKey('laji', on_delete=models.PROTECT, verbose_name='Laji')
    kesto = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    kesto_h = models.PositiveIntegerField(null=True, blank=True, verbose_name='h')
    kesto_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    matka = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (km/h)', blank=True)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (min/km)', blank=True)
    keskisyke = models.IntegerField(null=True, blank=True)
    kalorit = models.IntegerField(null=True, blank=True)
    
    tuntuma_choices = ((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10))
    
    tuntuma = models.IntegerField(choices=tuntuma_choices,null=True, blank=True)
    kommentti = models.TextField(max_length=250, null=True, blank=True)

    vuorokaudenaika_choices = ((1,'aamu'),(2,'ilta'),)
    vuorokaudenaika = models.IntegerField(choices=vuorokaudenaika_choices, blank=False, default=2, verbose_name="")
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)

    nousu = models.IntegerField(null=True, blank=True, verbose_name='Nousu (m)')

    def __str__(self):
        return '%s %s %s h' % (self.id ,self.laji, self.kesto)
        
    class Meta:
        verbose_name_plural = "Harjoitus"
        
    def get_absolute_url(self):
        """
        Returns the url to access a particular harjoitus instance.
        """
        return reverse('treeni-detail', args=[str(self.id)])

    
    def vvvvkkpp(self):
        return self.pvm.strftime('%Y%m%d')
    
    def save(self, *args, **kwargs):
        if not self.aika_id:
            self.aika_id = self.vvvvkkpp()
        super(harjoitus, self).save(*args, **kwargs)
    
    
class laji(models.Model):
    
    laji = models.CharField(max_length=10, verbose_name='Lyhenne')
    laji_nimi = models.CharField(max_length=50, verbose_name='Laji')
    laji_ryhma = models.CharField(max_length=50, verbose_name='Lajiryhmä',null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)

    def __str__(self):
        return self.laji_nimi
        
    class Meta:
        verbose_name_plural = "Laji"
        unique_together = (("laji_nimi","user"))

        

class aika(models.Model):
    
    vvvvkkpp = models.IntegerField(primary_key=True)
    pvm = models.DateField()
    vuosi = models.IntegerField(verbose_name='Vuosi')
    kk = models.IntegerField()
    kk_nimi = models.CharField(max_length=20)
    paiva = models.IntegerField()
    vko = models.IntegerField()
    viikonpaiva = models.IntegerField()
    viikonpaiva_lyh = models.CharField(max_length=20)
    hiihtokausi = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return str(self.vvvvkkpp)
        
    class Meta:
        verbose_name_plural = "Aika"


class tehot(models.Model):

    harjoitus = models.ForeignKey('harjoitus', on_delete=models.CASCADE)
    nro = models.IntegerField(blank=False)
    kesto = models.DecimalField(max_digits=5, decimal_places=2, null=True,blank=True)
    kesto_h = models.PositiveIntegerField(null=True, blank=True,verbose_name='h')
    kesto_min = models.PositiveIntegerField(null=True, blank=True, verbose_name='min')
    keskisyke = models.IntegerField(null=True, blank=True)
    maksimisyke = models.IntegerField(null=True, blank=True,verbose_name='Max.syke')
    matka = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vauhti_km_h = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (km/h)', blank=True)
    vauhti_min_km = models.DecimalField(max_digits=5, decimal_places=2, null=True, verbose_name='Vauhti (min/km)', blank=True)
    teho = models.ForeignKey('tehoalue',on_delete=models.PROTECT, null=True,blank=True)

    class Meta:
        verbose_name_plural = "Tehot"


class tehoalue(models.Model):

    jarj_nro = models.IntegerField(blank=False, verbose_name='Järj.Nro')
    teho = models.CharField(max_length=100)
    alaraja = models.IntegerField(null=True, blank=True, verbose_name='Alaraja')
    ylaraja = models.IntegerField(null=True, blank=True, verbose_name='Yläraja')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Tehoalue"
        unique_together = (("teho", "user"),)

    def __str__(self):
        return self.teho