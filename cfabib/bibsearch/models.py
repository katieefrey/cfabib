from django.db import models

from users.models import CustomUser
from bibmanage.models import Bibgroup 

# table of generated reports
class Report(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    jnum = models.IntegerField(default=0)
    anum = models.IntegerField(default=0)
    daterange = models.CharField(max_length=250, null=True, blank=True)
    namelist = models.TextField(null=True, blank=True)
    bibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.id}: {self.username.first_name}, {self.daterange}"

# info about a journal, per report
class Journal(models.Model):
    resultset = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    jname = models.CharField(max_length=250, null=True, blank=True)
    articlenum = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.resultset} {self.jname} {self.articlenum}"

# info about an author, per report
class Name(models.Model):
    resultset = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    aname = models.CharField(max_length=250, null=True, blank=True)
    vrart = models.IntegerField(default=0)
    vnrart = models.IntegerField(default=0)
    vrcite = models.IntegerField(default=0)
    vnrcite = models.IntegerField(default=0)
    vrfirst = models.IntegerField(default=0)
    vnrfirst = models.IntegerField(default=0)
    urart = models.IntegerField(default=0)
    unrart = models.IntegerField(default=0)
    urcite = models.IntegerField(default=0)
    unrcite = models.IntegerField(default=0)
    urfirst = models.IntegerField(default=0)
    unrfirst = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.resultset} {self.aname}"

# table for summary report
class SummaryReport(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    bibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE, null=True, blank=True)
    daterange = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.id}: {self.username.first_name}, {self.daterange}"

# yearly summary, per report
class Summary(models.Model):
    resultset = models.ForeignKey(SummaryReport, on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(default=0)
    refart = models.IntegerField(default=0)
    refcite = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.resultset} {self.year}"