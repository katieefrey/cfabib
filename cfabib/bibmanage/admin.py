from django.contrib import admin

from .models import Bibgroup, Batch, Criteria, PastSearch

# Register your models here.

admin.site.register(Bibgroup)
admin.site.register(Batch)
admin.site.register(Criteria)
admin.site.register(PastSearch)