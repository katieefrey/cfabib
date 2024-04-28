from django.db import models
from bibmanage.models import Batch, Bibgroup
from users.models import CustomUser

# status of the paper, is it CfA?
class Status(models.Model):
    status = models.CharField(max_length=50)
    # table contains only the following options:
    # yes, no, maybe, doubtful

    def __str__(self):
        return f"{self.status}"

# list of valid affiliations
class Affil(models.Model):
    name = models.CharField(max_length=50)
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    # table contains only the following options:
    # HCO, SAO, both, unknown, neither, either

    def __str__(self):
        return f"{self.name}"

# list of valid gueses
class Guess(models.Model):
    guess = models.CharField(max_length=50)
    # table contains only the following options:
    # likely, review, reivew-visiting, review-nonSAO, review-nonCfA, doubtful

    def __str__(self):
        return f"{self.guess}"

# NewArticle table valid for entries after Feb 2021
# affiliation info is disconnected from article now
class NewArticle(models.Model):
    bibcode = models.CharField(max_length=19, unique=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    adminbibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE, null=True, blank=True)
    authnum = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    completed = models.BooleanField(default=False)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.bibcode}"

# Author table is where the real affiliation information is tracked, mulitple authors can be connected to the same Article
class Author(models.Model):
    bibcode = models.ForeignKey(NewArticle, on_delete=models.CASCADE, null=True, blank=True)
    name = models.TextField(null=True, blank=True) #author name text string
    affil = models.TextField(null=True, blank=True) #affiliation text string
    guess = models.ForeignKey(Guess, on_delete=models.CASCADE)
    query = models.CharField(max_length=100, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    inst = models.ForeignKey(Affil, on_delete=models.CASCADE, null=True, blank=True)
    adminbibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE)
    autoclass = models.BooleanField(default=False) # was it auto classified?
    verified = models.BooleanField(default=False) # has it been verified?
    edited = models.BooleanField(default=False) # has it been edited?
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ('bibcode', 'name', 'affil', 'adminbibgroup')

    def __str__(self):
        return f"{self.bibcode.bibcode} {self.name} {self.inst}"

# pre Feb2021 Article model, affiliation attached to article not authors
class Article(models.Model):
    bibcode = models.CharField(max_length=19, unique=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    adminbibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE)
    #bibgroupcheck = models.ForeignKey(Bibgroup, on_delete=models.CASCADE)
    guess = models.ForeignKey(Guess, on_delete=models.CASCADE)
    query = models.CharField(max_length=100, null=True, blank=True)
    affils = models.TextField(null=True, blank=True)
    authnum = models.IntegerField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    inst = models.ForeignKey(Affil, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.bibcode} {self.status} {self.inst}"

# keeping track of the work a user did on a given author or old article record
class Work(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    bibcode = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} {self.bibcode}"