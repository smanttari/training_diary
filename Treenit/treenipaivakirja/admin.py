from .models import aika, laji, harjoitus, tehot, tehoalue
from django.contrib import admin


class harjoitusAdmin(admin.ModelAdmin):
    list_display = ('pvm','laji_fk','kesto','matka')
    list_filter = ('pvm','laji_fk')
    fields = ['pvm','laji_fk','kesto','matka',('vauhti_km_h','vauhti_min_km'),'keskisyke','kalorit','tuntuma','kommentti']
    
class lajiAdmin(admin.ModelAdmin):
    list_display = ('laji','laji_nimi','laji_ryhma')
	
class aikaAdmin(admin.ModelAdmin):
    list_display = ('pvm','viikonpaiva_lyh','kk','kk_nimi','vko')

class tehotAdmin(admin.ModelAdmin):
    list_display = ('harjoitus_fk','teho','kesto')

class tehoalueAdmin(admin.ModelAdmin):
    list_display = ('jarj_nro','teho','alaraja','ylaraja')

admin.site.register(harjoitus, harjoitusAdmin)
admin.site.register(laji, lajiAdmin)
admin.site.register(aika, aikaAdmin)
admin.site.register(tehot, tehotAdmin)
admin.site.register(tehoalue, tehoalueAdmin)

admin.site.site_header = 'Treenipäiväkirja'
admin.site.site_title = 'Treenit'
admin.site.index_title = 'Treenit'