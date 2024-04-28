from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from users.models import Bibgroup, CustomUser
from .forms import DevkeyForm, BibgroupForm

import urllib.parse
import requests
import time
import csv

from bibsearch.models import Report, Journal, Name, SummaryReport, Summary
from bibsearch.tasks import adsquery, summaryquery

# serving static help page
def help(request):

    context = {}

    return render(request, "bibsearch/help.html", context)

# serving static about page
def about(request):

    context = {}

    return render(request, "bibsearch/about.html", context)

# serving the search page
def search(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    bib = username.bibgroup
    bibgroups = Bibgroup.objects.all();

    context = {
        "err" : "",
        "bibgroups": bibgroups,
        "bib"   : bib
        }

    return render(request, "bibsearch/search.html", context)

# queuing a search request for ADS
def queued(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    context = {
        "err" : ""
        }

    namelist = request.POST["authorlist"]
    startdate = request.POST["startdate"]
    enddate = request.POST["enddate"]
    bibgroup = username.bibgroup #id
    bib = bibgroup.bibgroup #string
    daterange = startdate+" TO "+enddate

    devkey = username.devkey

    if namelist == "":
        error = "Please provide a name to search!"
        context ["err"] = error
        return render(request, "bibsearch/search.html", context)

    elif startdate == "" or enddate == "":
        error = "Please provide valid dates!"
        context["err"] = error
        return render(request, "bibsearch/search.html", context)

    else:
        authorlist = namelist.splitlines()

        makeset = Report.objects.create(username=username)
        makeset.namelist = namelist
        makeset.bibgroup_id = bibgroup.id
        makeset.save()

        reid = makeset.id

        # send query to ADS via Celery & RabbitMQ...!
        adsquery.delay(namelist,daterange,bib,devkey,reid)
        makeset.save()
        
        context = {
            "namelist"  :  authorlist,
            "daterange" :  daterange,
            "bibgroup"  :  bib,
            "curset"    :  reid,
            }

    return render(request, "bibsearch/queued.html", context)

# history of request, per user
def history(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    allsets = Report.objects.filter(username=username).order_by('-created')
    

    context = {
        "allsets"   :  allsets,
        }

    return render(request, "bibsearch/history.html", context)

# serving a report
def report(request, reid):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    resultset = Report.objects.get(id=reid)

    try:
    
        allauths = resultset.namelist.splitlines()
    
    except AttributeError:
        allauths = []

    journals = Journal.objects.filter(resultset_id=reid).order_by('articlenum')

    authors = Name.objects.filter(resultset_id=reid).order_by('urart')

    # to help resize the graphs as needed
    authnum1 = len(authors)

    jnum1 = (len(journals))#*60

    if jnum1*40 <= 300:
        jnum = 350
    else:
        jnum = jnum1*30

    if authnum1*40 <= 300:
        authnum = 350
    else:
        authnum = authnum1*40

    context = {
        "journals"  :  journals,
        "authors"   :  authors,
        "resultset" :  resultset,
        "allauths"  :  allauths,
        "authnum"   :  authnum,
        "jnum"      :  jnum
        }

    return render(request, "bibsearch/results.html", context)

# export a csv of author information from a report
def export_author(request):
    reid = request.POST["reid"]
    auths = Name.objects.filter(resultset_id=reid).order_by('aname')

    report = Report.objects.get(id=reid)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Authors_report'+reid+'_'+str(report.created)+'.csv"'

    writer = csv.writer(response)

    writer.writerow(["Author Name"]+["Total Articles"]+["Total Verified Articles"]+["Total Verified Citations"]+["Verified Refereed Articles"]+["Verified Refereed Citations"]+["Verified Non Refereed Articles"]+["Verified Non Refereed Citations"]+["Total Unverified Articles"]+["Total Unverified Citations"]+["Unverified Refereed Articles"]+["Unverified Refereed Citations"]+["Unverified Non Refereed Articles"]+["Unverified Non Refereed Citations"])

    for x in auths:
        writer.writerow([x.aname]+[x.vrart+x.vnrart+x.urart+x.unrart]+[x.vrart+x.vnrart]+[x.vrcite+x.vnrcite]+[x.vrart]+[x.vrcite]+[x.vnrart]+[x.vnrcite]+[x.urart+x.unrart]+[x.urcite+x.unrcite]+[x.urart]+[x.urcite]+[x.unrart]+[x.unrcite])

    return response

# export a csv of journal information from a report
def export_journal(request):
    reid = request.POST["reid"]
    jours = Journal.objects.filter(resultset_id=reid).order_by('-articlenum')

    report = Report.objects.get(id=reid)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Journals_report'+reid+'_'+str(report.created)+'.csv"'

    writer = csv.writer(response)

    writer.writerow(["Journal Name"]+["Total Articles"])

    for x in jours:
        writer.writerow([x.jname]+[x.articlenum])

    return response

# queuing a request for a summary report for ADS
def sumqueue(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    context = {
        "err" : ""
        }

    startdate = request.POST["startdate"]
    enddate = request.POST["enddate"]
    bibgroup = username.bibgroup #id
    bib = bibgroup.bibgroup #string
    daterange = startdate+" TO "+enddate

    devkey = username.devkey

    print (bibgroup.bibgroup)

    if startdate == "" or enddate == "":
        error = "Please provide valid dates!"
        context["err"] = error
        return render(request, "bibsearch/sumhistory.html", context)

    else:

        makeset = SummaryReport.objects.create(username=username)
        makeset.bibgroup_id = bibgroup.id
        makeset.save()

        reid = makeset.id

        print("Sending the query to ADS...")

        # send query to ADS via Celery...!
        summaryquery.delay(startdate,enddate,bib,devkey,reid)
        
        makeset.save()
        
        context = {
            "daterange" :  daterange,
            "bibgroup"  :  bib,
            "curset"    :  reid,
            }

    return redirect(summaries)

# a list of summary reports, per user
def summaries(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    allsums = SummaryReport.objects.filter(username=username).order_by('-created')
    
    context = {
        "err" : "",
        "allsums"   :  allsums,
        "bib": username.bibgroup,
        }

    #response = redirect('/redirect-success/')
    return render(request, "bibsearch/sumhistory.html", context)

# serving a summary report
def summary(request, reid):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibsearch/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    resultset = SummaryReport.objects.get(id=reid)

    summaries = Summary.objects.filter(resultset_id=reid).order_by('-year')

    context = {
        "resultset"  :  resultset,
        "summaries"   :  summaries,

        }

    return render(request, "bibsearch/summary.html", context)

# export a csv of summary report info
def export_summary(request):
    reid = request.POST["reid"]
    summaries = Summary.objects.filter(resultset_id=reid).order_by('-year')

    report = SummaryReport.objects.get(id=reid)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Journals_report'+reid+'_'+str(report.created)+'.csv"'

    writer = csv.writer(response)

    writer.writerow(["Summary Report Created On"]+[report.created])
    writer.writerow(["Year"]+["Total Refereed Articles"]+["Total Citations"])

    for x in summaries:
        writer.writerow([x.year]+[x.refart]+[x.refcite])

    return response