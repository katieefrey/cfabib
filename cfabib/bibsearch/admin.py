from django.contrib import admin
from .models import Report, Journal, Name, SummaryReport, Summary

# Register your models here.

admin.site.register(Report)
admin.site.register(Journal)
admin.site.register(Name)
admin.site.register(SummaryReport)
admin.site.register(Summary)