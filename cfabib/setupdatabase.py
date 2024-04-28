# standard lib packages
import sys
import os
import requests
import json
import urllib.parse
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE','cfabib.settings')

import django
django.setup()

from django.conf import settings

from bibtool.models import Status, Affil, Guess
from bibmanage.models import Bibgroup, Batch, Criteria
from users.models import AccessLvl

print (settings.DATABASES)

cont = input("Continue?")

def add_Status(data1):
    d, created = Status.objects.get_or_create(status=data1)
    return d

def add_Affil(data1):
    d, created = Affil.objects.get_or_create(name=data1)
    return d

def add_Guess(data1):
    d, created = Guess.objects.get_or_create(guess=data1)
    return d

def add_Bibgroup(data1):
    d, created = Bibgroup.objects.get_or_create(bibgroup=data1)
    return d

def add_Criteria(data1, data2, data3, data4, data5, data6, data7, data8):
    d, created = Criteria.objects.get_or_create(name=data1,bibgroup_id=data2,authorlist=data3,instlist=data4,exclstem=data5,exclvol=data6,inclstem=data7,inclvol=data8)
    return d

def add_AccessLvl(data1):
    d, created = AccessLvl.objects.get_or_create(status=data1)
    return d


def populate():

    add_Status("CfA")
    add_Status("NOT CfA")
    add_Status("maybe")
    add_Status("doubtful")

    add_Affil("HCO")
    add_Affil("SAO")
    add_Affil("both HCO and SAO")
    add_Affil("unknown")
    add_Affil("neither")
    add_Affil("either HCO or SAO")

    add_Guess("likely")
    add_Guess("review")
    add_Guess("review-visiting")
    add_Guess("review-nonSAO")
    add_Guess("review-nonCfA")
    add_Guess("doubtful")

    add_Bibgroup("CfA")
    add_Bibgroup("Chandra")
    add_Bibgroup("HST")
    add_Bibgroup("NOAO")

    add_AccessLvl("user")
    add_AccessLvl("bibliographer")
    add_AccessLvl("bibmanager")

#     name="cfa-test"

#     bibg=1

#     auth="""Bouquin, Daina
# Frey, Katie
# Accomazzi, Alberto
# Alcock, Charles
# Aldcroft, Thomas"""

#     inst="""harvard-smithsonian
# 60 garden"""

#     estem="""arXiv
# ATel1
# ATel.
# yCat.
# MPEC.
# sptz.
# Cosp.
# DPS..
# IAUC.
# SPD..
# AGUFM
# AGUSM
# APS..
# IAUFM
# AAS..
# HEAD.
# DDA.."""

#     evol="""prop
# .tmp"""

#     istem="""CBET."""

#     ivol="""conf
# book"""
#     add_Criteria(name, bibg, auth, inst, estem, evol, istem, ivol)


#     name="cfa-test2"

#     bibg=1

#     auth="""Bouquin, Daina
# Frey, Katie
# Accomazzi, Alberto
# Alcock, Charles
# Aldcroft, Thomas"""

#     inst="""harvard-smithsonian
# 60 garden"""

#     estem="""arXiv
# ATel1
# ATel.
# yCat.
# MPEC.
# sptz.
# Cosp.
# DPS..
# IAUC.
# SPD..
# AGUFM
# AGUSM
# APS..
# IAUFM
# AAS..
# HEAD.
# DDA.."""

#     evol="""prop
# .tmp"""

#     istem="""CBET."""

#     ivol="""conf
# book"""
#     add_Criteria(name, bibg, auth, inst, estem, evol, istem, ivol)


#     name="hst-test"

#     bibg=3

#     auth="""Novacescu, Jenny
# Koekemoer, Anton
# Ferguson, Henry"""

#     inst="""hubble space telescope
# space telescope science institute"""

#     estem="""arXiv
# ATel1
# ATel.
# yCat.
# MPEC.
# sptz.
# Cosp.
# DPS..
# IAUC.
# SPD..
# AGUFM
# AGUSM
# APS..
# IAUFM
# AAS..
# HEAD.
# DDA.."""

#     evol="""prop
# .tmp"""

#     istem="""CBET."""

#     ivol="""conf
# book"""

#     add_Criteria(name, bibg, auth, inst, estem, evol, istem, ivol)



    print ("finished")


if __name__ == "__main__":
    populate()
