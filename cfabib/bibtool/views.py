from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
from django.db.models import Count, DateTimeField
from django.db.models.functions import TruncDate, TruncMonth, TruncDay, TruncHour, TruncMinute

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.core.paginator import Paginator

import urllib.parse
import requests
import time

from .models import Status, Affil, Article, Work, NewArticle, Author
from .forms import DevkeyForm, BibgroupForm


def index(request):
    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    #otherwise, if they are logged in...
    username = request.user

    context = {
        "state": "loggedin",
        "first": username.first_name
        }

    return render(request, "bibtool/index.html", context)

#send user to login form
def login_form(request):
    context = {
            "state": "login",
            "error": ""
        }
    return render(request, "bibtool/index.html", context)


#log user in
def login_view(request):
    username = request.POST["inputUsername"]
    password = request.POST["inputPassword"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        context = {
            "state": "login",
            "error": "Invalid credentials, try again."
            }
        return render(request, "bibtool/index.html", context)


#log user out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# access account info
def account(request):
    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
        #return render(request, "search/home.html", context)

    #otherwise, if they are logged in...
    username = request.user
    userid = username.id

    context = {
        "state": "loggedin",
        "error"  : "",
        "update" : ""
        }

    context["user"] = username

    history = Work.objects.filter(username_id=userid).annotate(day=TruncDay('created')).values('day').annotate(c=Count('id'))

    batchlist = []
    for y in range(0,len(history)):
        batches = {}

        batches["day"] = (history[y]["day"])
        batches["num"] = (history[y]["c"])
        batchlist.append(batches)

    if request.method == 'POST':

        try:
            devk = request.POST["inputDevKey"]
            username.devkey = devk
            username.save()
            context["update"] = "API Token Updated!"

        except:
            pass

        try:
            bibg = request.POST["inputBibgroup"]
            bibgid = Bibgroup.objects.get(bibgroup=bibg)
            username.bibgroup = bibgid
            username.save()
            context["update"] = "Bibgroup updated!"

        except:
            pass

        try:
            pwc = request.POST["pwchange"]

            if pwc == "pwchange":
                pwform = PasswordChangeForm(request.user, request.POST)

                if pwform.is_valid():
                    print("form IS valid")
                    user = pwform.save()
                    update_session_auth_hash(request, user)  # Important!
                    context["update"] = "Password updated successfully!"
                else:
                    print("form not valid")
                    context["error"] = "Problem changing password."
        except:
            pass

    context["user"] = username
    context["batchlist"] = batchlist

    devform = DevkeyForm(initial={"inputDevKey": username.devkey})
    bibform = BibgroupForm(initial={"inputBibgroup": username})
    pwform = PasswordChangeForm(request.user)

    context["devform"] = devform
    context["bibform"] = bibform
    context["pwform"] = pwform

    return render(request, "bibtool/account.html", context)

#send user to registration page
def register(request):
    context = {
        "state": "register",
        "error" : ""
        }
    return render(request, "bibsearch/index.html", context)


#register new user
def registering(request):
    try:
        username = request.POST["inputUsername"]
        firstname = request.POST["inputFirst"]
        lastname = request.POST["inputLast"]
        email = request.POST["inputEmail"]
        password = request.POST["inputPassword"]

    except ValueError:

        context = {
            "state": "register",
            "error" : "Please fill out this form entierly."
            }
        
        return render(request, "bibsearch/index.html", context)

    user = CustomUser.objects.create_user(username,email,password)
    user.save

    user1 = CustomUser.objects.get(username=username)
    user1.first_name = firstname
    user1.last_name = lastname
    user1.save()

    return HttpResponseRedirect(reverse("index"))

# a users individual work history
def history(request,year,month,day):
    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
        #return render(request, "search/home.html", context)

    #otherwise, if they are logged in...
    userid = request.user.id

    worklist = Work.objects.filter(created__year=year,created__month=month,created__day=day,username_id=userid).values("author__bibcode").distinct()
    bibs = NewArticle.objects.filter(id__in=worklist)

    context = {
        "bibs" : bibs,
        "month": month,
        "day" : day,
        "year" : year
    }

    return render(request, "bibtool/history.html", context)

# see the list of monthly batches
def batch(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup

    # dates and totals
    dates = Author.objects.filter(adminbibgroup=bibgroup).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    # dates and not mods
    notmod = Author.objects.filter(status_id=3,adminbibgroup=bibgroup).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    # dates and unknowns
    notknown = Author.objects.filter(inst_id=4,adminbibgroup=bibgroup,autoclass=False).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    # dates and unverified
    notver = Author.objects.filter(autoclass=True,verified=False,adminbibgroup=bibgroup).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    batchlist = []

    for y in range(0,len(dates)):
        batches = {}

        batches["month"] = (dates[y]["month"])
        batches["total"] = (dates[y]["c"])

        batches["notmod"] = 0
        for x in notmod:
            if x["month"] == dates[y]["month"]:
                batches["notmod"] = (x["c"])

        batches["notver"] = 0
        for x in notver:
            if x["month"] == dates[y]["month"]:
                batches["notver"] = (x["c"])

        batches["notknown"] = 0
        for x in notknown:
            if x["month"] == dates[y]["month"]:
                batches["notknown"] = (x["c"])            

        batchlist.append(batches)

    batchlist.reverse()

    ## Legacy Support

    # dates and totals
    dates1 = Article.objects.filter(adminbibgroup=bibgroup).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    # dates and not mods
    notmod1 = Article.objects.filter(status_id=3,adminbibgroup=bibgroup).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    # dates and unknowns
    notknown1 = Article.objects.filter(inst_id=4,adminbibgroup=bibgroup).annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id'))

    batchlist1 = []

    for y in range(0,len(dates1)):
        batches = {}

        batches["month"] = (dates1[y]["month"])
        batches["total1"] = (dates1[y]["c"])

        batches["notmod1"] = 0
        for x in notmod1:
            if x["month"] == dates1[y]["month"]:
                batches["notmod1"] = (x["c"])

        batches["notknown1"] = 0
        for x in notknown1:
            if x["month"] == dates1[y]["month"]:
                batches["notknown1"] = (x["c"])

        batchlist1.append(batches)
    
    batchlist1.reverse()

    ## end legacy support

    context = {
        "batches": batchlist,
        "batches1": batchlist1 # legacy batchlist
        }

    return render(request, "bibtool/batch.html", context)

# list of author entries that need to be updated by hand
def nameupdate(request,year,month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup

    # unedited records
    authors = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=False, edited=False).order_by('bibcode')

    # edited records
    numod = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=False, edited=True).order_by('bibcode').count()

    p = Paginator(authors, 250)

    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)
        
    context = {
        "page_obj": page_obj,
        #"edauthors": edauthors,
        "numod": numod,
        "numnot": len(authors),
        "year": year,
        "month": month,
        }

    return render(request, "bibtool/nameupdate.html", context)

# list of author entries that have already been updated by hand
def nameupdated(request,year,month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup

    # unedited records
    numnot = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=False, edited=False).order_by('bibcode').count()

    # edited records
    edauthors = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=False, edited=True).order_by('bibcode')

    p = Paginator(edauthors, 250)

    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    context = {
        #"authors": authors,
        "page_obj": page_obj,
        "numod": len(edauthors),
        "numnot": numnot,
        "year": year,
        "month": month,
        }

    return render(request, "bibtool/nameupdated.html", context)

# this is a list of author entries that were automatically classified by the improt script, and need to be verified by a person
def nameverify(request,year,month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup

    # unverified records
    notv = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=True, verified=False).order_by('bibcode').order_by('guess')

    # verified records
    numver = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=True, verified=True).order_by('bibcode').count()

    p = Paginator(notv, 50)

    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)
        
    context = {
        "page_obj": page_obj,
        "numver": numver,
        "numnotv": len(notv),
        "year": year,
        "month": month,
        }

    return render(request, "bibtool/nameverifyalt.html", context)

# this is a list of author entries that were auto classified and have already been verified by a person
def nameverified(request,year,month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup

    # unverified records
    numnotv = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=True, verified=False).order_by('bibcode').count()

    # verified records
    ver = Author.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup, autoclass=True, verified=True).order_by('bibcode')

    p = Paginator(ver, 250)

    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)
        
    context = {
        "numver": len(ver),
        "numnotv": numnotv,
        "page_obj": page_obj,
        "year": year,
        "month": month,
        }

    return render(request, "bibtool/nameverified.html", context)

# these authors were found by the script, but it has no idea how to classify them, or a person doesnt know how to classify it either
def nameunknown(request,year,month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup
    
    authors = Author.objects.filter(created__year=year,created__month=month,inst_id=4,autoclass=False,adminbibgroup=bibgroup)
    numunknown = len(authors)

    numtotal = Author.objects.filter(created__year=year,created__month=month,autoclass=False,adminbibgroup=bibgroup).count()

    numknown = numtotal-numunknown

    p = Paginator(authors, 250)

    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "numunknown": numunknown,
        "numknown": numknown
    }
    return render(request, "bibtool/nameunknown.html", context)

# post request to update author table
def post_nameupdate(request):

    upauthid = request.POST.getlist("authid[]")
    art = request.POST["art"]
    cfainst = request.POST["cfainst"]

    # if cfainst is 4, that means this is an unknown record
    if int(cfainst) == 4:
        # status changed to "doubtful"
        bibstatus = 4
    # if the cfainst is 5, that means this is NOT a CfA record
    elif int(cfainst) == 5:
        # status changed to "no"
        bibstatus = 2
    # every other status means that this is a CfA record
    else:
        # status changed to "yes"
        bibstatus = 1

    for x in upauthid:

        new = Author.objects.get(id=x)

        new.status_id = bibstatus
        new.inst_id = cfainst
        new.edited = True # mark as edited
        new.save()

        username = request.user
        userid = username.id

        newwork = Work.objects.create(username_id=userid,author_id=x)
        newwork.save()

    arts = Author.objects.filter(bibcode=art)

    flag = 0
    for y in arts:
        if y.status.id == 3 or y.status.id == 2 or y.edited == False:
            flag = 1

    if flag == 0:
        thisart = NewArticle.objects.get(id=art)
        thisart.completed = True
        thisart.save()

    return HttpResponseRedirect(reverse("batch"))

# post request to update the auto classed papers
def post_nameverify(request):

    upauthid = request.POST.getlist("authid[]")
    art = request.POST.getlist("art[]")
    verify = request.POST["verify"]

    if verify == str(1):
        ver = True
    else:
        ver = False

    for x in upauthid:

        new = Author.objects.get(id=x)

        new.verified = ver
        new.edited = ver # mark as edited if true, not edited if false
        # "not edited" bumps it to the main "author update" section

        if ver == False:
            new.inst_id = 4
            new.status_id = 3
            new.autoclass = False
            for y in art:
                thisart = NewArticle.objects.get(id=y)
                thisart.completed = False
                thisart.save()

        #print (ver)
        new.save()

        username = request.user
        userid = username.id

        newwork = Work.objects.create(username_id=userid,author_id=x)
        newwork.save()

    for z in art:

        arts = Author.objects.filter(bibcode=z)

        flag = 0
        for y in arts:
            if y.status.id == 3 or y.status.id == 2 or y.edited == False:
                flag = 1

        if flag == 0:
            thisart = NewArticle.objects.get(id=z)
            thisart.completed = True
            thisart.save()

    return HttpResponseRedirect(reverse("batch"))

# view an article by bibcode
def bibcode(request,bib):
    #single bibcode view
    #2023ApJS..269...13G

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    thisart = NewArticle.objects.get(bibcode=bib)
    auths = Author.objects.filter(bibcode__bibcode=bib)

    context = {
            "bib" : thisart,
            "bib_list": auths,
            }
    return render(request, "bibtool/bibcode.html", context)
    


## Legacy Article BibTool System
# needed for all work prior to Feb 2021
# Do not edit!

# list of article entries that need to be updated
def update(request, year, month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup

    articles = Article.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup)
    allmod = []
    allnot = []
    
    for y in articles:
        if y.created.strftime('%Y %m %d %H %M') == y.modified.strftime('%Y %m %d %H %M'):
            allnot.append(y)
        else:
            allmod.append(y)

    numod = len(allmod)
    numnot = len(allnot)
        
    context = {
        "articles": articles,
        "numod": numod,
        "numnot": numnot
        }

    return render(request, "bibtool/update.html", context)

# list of articles put into "unknown" becuase we dont know what to do with them
def unknown(request,year, month):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    bibgroup = request.user.bibgroup
    
    articles = Article.objects.filter(created__year=year,created__month=month,inst_id=4,adminbibgroup=bibgroup)
    numunknown = len(articles)

    totart = Article.objects.filter(created__year=year,created__month=month,adminbibgroup=bibgroup)

    numtotal = len(totart)
    numknown = numtotal-numunknown

    context = {
        "articles": articles,
        "numunknown": numunknown,
        "numknown": numknown
    }
    return render(request, "bibtool/unknown.html", context)

# post request to update an article entry
def post_update(request):

    upbib = request.POST["bibcode"]

    cfastatus = request.POST["cfastatus"]
    span_val = request.POST["span_value"]

    if span_val == "unknown":
        #print ("unknown")
        bibstatus = 2
        cfastatus = 4
    else:

        # if the cfastatus is 5, that means this is NOT a CfA record
        if int(cfastatus) == 5:
            #print ("not cfa")
            bibstatus = 2
        elif int(cfastatus) == 4:
            bibstatus = 1
        # every other status means that this is a CfA record
        else:
            #print ("yes cfa")
            bibstatus = 1

    new = Article.objects.get(id=upbib)

    new.status_id = bibstatus
    new.inst_id = cfastatus
    new.save()

    userid = request.user.id

    newwork =  Work.objects.create(username_id=userid,bibcode_id=upbib)
    newwork.save()

    return HttpResponseRedirect(reverse("batch"))