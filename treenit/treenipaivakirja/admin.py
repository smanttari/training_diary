from .models import Aika, Laji, Harjoitus, Teho, Tehoalue, Kausi
from django.contrib import admin


class HarjoitusAdmin(admin.ModelAdmin):
    list_display = ('pvm','laji','kesto','matka','user')
    list_filter = ('user','pvm','laji')
    fields = ['pvm','laji','kesto','matka',('vauhti_km_h','vauhti_min_km'),'keskisyke','kalorit','tuntuma','kommentti']
    
class LajiAdmin(admin.ModelAdmin):
    list_display = ('laji','laji_nimi','laji_ryhma','user')
    list_filter = ('user','laji')
	
class AikaAdmin(admin.ModelAdmin):
    list_display = ('pvm','viikonpaiva_lyh','kk','kk_nimi','vko')

class TehoAdmin(admin.ModelAdmin):
    list_display = ('harjoitus','tehoalue','kesto')

class TehoalueAdmin(admin.ModelAdmin):
    list_display = ('jarj_nro','tehoalue','alaraja','ylaraja','user')
    list_filter = ('user','tehoalue')

class KausiAdmin(admin.ModelAdmin):
    list_display = ('kausi','alkupvm','loppupvm','user')
    list_filter = ('user','kausi')

admin.site.register(Harjoitus, HarjoitusAdmin)
admin.site.register(Laji, LajiAdmin)
admin.site.register(Aika, AikaAdmin)
admin.site.register(Teho, TehoAdmin)
admin.site.register(Tehoalue, TehoalueAdmin)
admin.site.register(Kausi, KausiAdmin)

admin.site.site_header = 'Treenipäiväkirja'
admin.site.site_title = 'Treenit'
admin.site.index_title = 'Treenit'