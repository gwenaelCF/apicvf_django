from django.contrib import admin

# Register your models here.
from apicvf.models import Abonnement, Grain

admin.site.register(Abonnement, admin.ModelAdmin)
admin.site.register(Grain, admin.ModelAdmin)
