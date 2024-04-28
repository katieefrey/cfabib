from django.db import models


# table for bibcodes
class Bibgroup(models.Model):
    bibgroup = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.bibgroup}"


# table for batches
class Batch(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    bibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE)
    closed = models.BooleanField()
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Closed: {self.closed} | Batch #: {self.id}"


# NYI ADS search criteria
class Criteria(models.Model):
    name = models.CharField(max_length=20, unique=True)
    bibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE)
    authorlist = models.TextField(null=True, blank=True)
    instlist = models.TextField(null=True, blank=True)
    exclstem = models.TextField(null=True, blank=True)
    exclvol = models.TextField(null=True, blank=True)
    inclstem = models.TextField(null=True, blank=True)
    inclvol = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.bibgroup} {self.created}"


# NYI for criteria work
class PastSearch(models.Model):
    criteria = models.ForeignKey(Criteria, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} {self.criteria} {self.created}"
