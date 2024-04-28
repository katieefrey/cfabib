from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Criteria, Batch
from bibtool.models import Article, NewArticle, Author

import csv
import json
import requests
import urllib.parse
import time


# serve management index page
def bmindex(request):
    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    context = {}
    return render(request, "bibmanage/index.html", context)


# serve static info page, if logged in
def info(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup


    context = {"bibgroup": bibgroup}

    return render(request, "bibmanage/info.html", context)


# serve static tips page, if logged in
def tips(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup


    context = {"bibgroup": bibgroup}

    return render(request, "bibmanage/tips.html", context)


# list of bibcode batches
def batch(request):
    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup

    # create new batch
    # number of all CfA verified bibcodes not in a batch
    # view all bibcodes?

    # list all currently closed batches
    closed = Batch.objects.filter(bibgroup=bibgroup,closed=True)

    # list all bibcodes classified to the right bibgroup, that are NOT in a batch
    # old system
    oldbibs = Article.objects.filter(status_id=1,batch_id=None, adminbibgroup=bibgroup)
    # new system

    newbibs = NewArticle.objects.filter(batch_id=None, adminbibgroup=bibgroup,completed=True)
    
    cfanewbibs = []
    for x in newbibs:
        auths = Author.objects.filter(bibcode_id=x)
        flag = 0
        for y in auths:
            if y.status.id == 1:
                flag = 1
                break

        if flag == 1:
            cfanewbibs.append(x)


    context = {
        "closed":  closed,
        "newbibs" : cfanewbibs,
        "oldbibs" : oldbibs,
        "numnew" : len(cfanewbibs) + len(oldbibs),
        "err" : "",
    }

    try:
        # is ther a current open batch?
        openbatch = Batch.objects.get(bibgroup=bibgroup,closed=False)
        
        # bibcodes in current open batch
        # old system
        openbatart = Article.objects.filter(batch_id=openbatch.id)

        # new system
        openbatnewart = NewArticle.objects.filter(batch_id=openbatch.id)
        

        context["openbatch"] = openbatch
        context["num"] = len(openbatart) + len(openbatnewart)

    except Batch.DoesNotExist:
        context["openbatch"] = None

    return render(request, "bibmanage/batch.html", context)


# see all the bibcodes in a batch
def viewbatch(request,batchid):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup

    try:
        onebatch = Batch.objects.get(bibgroup=bibgroup,id=batchid)

        numbibs1 = Article.objects.filter(batch_id=batchid).count()

        numbibs = NewArticle.objects.filter(batch_id=batchid).count()

        context = {
            "err": "",
            "batch" : onebatch,
            "numbibs" : numbibs + numbibs1,
        }

        return render(request, "bibmanage/viewbatch.html", context)

    except Batch.DoesNotExist:

        return HttpResponseRedirect(reverse("batch"))


# export bibcode list from a batch
def export(request):
    batchid = request.POST["batchid"]
    bibs1 = Article.objects.filter(batch_id=batchid)
    bibs = NewArticle.objects.filter(batch_id=batchid)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="batch_'+batchid+'.txt"'

    writer = csv.writer(response)

    for x in bibs:
        writer.writerow([x.bibcode])

    for x in bibs1:
        writer.writerow([x.bibcode])

    return response


# post request to close a batch
def close_batch(request):
    batchid = request.POST["batchid"]

    curbatch = Batch.objects.get(id=batchid)

    curbatch.closed = True

    curbatch.save()

    #url = reverse('batch', kwargs={'batchid': batchid})
    #return HttpResponseRedirect(url)

    return HttpResponseRedirect('batch/%s' % batchid)
    #return HttpResponseRedirect(reverse("batch"))
    # http://127.0.0.1:8000/bibmanage/batch/2


# post request to open a new batch
def post_openbatch(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup

    # try to get an existing open batch...
    try:
        curopen = Batch.objects.get(bibgroup=bibgroup, closed=False)

    # if none found, then create a new one
    except Batch.DoesNotExist:

        created = Batch.objects.create(bibgroup=bibgroup, closed=False)

    # go back to the batch page
    return HttpResponseRedirect(reverse("batch"))


# post request to add new bibcodes to a batch
def post_addtobatch(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)
    
    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup

    newbibcodes = request.POST.getlist('newbibcodes')
    oldbibcodes = request.POST.getlist('oldbibcodes')

    print (newbibcodes)
    print (oldbibcodes)
    batchid = request.POST["batchid"]

    for bibid in oldbibcodes:
        try:
            curbib = Article.objects.get(id=bibid)
            curbib.batch_id = batchid
            curbib.save()
        except Article.DoesNotExist:
            pass

    for bibid in newbibcodes:
        try:
            curbib = NewArticle.objects.get(id=bibid)
            curbib.batch_id = batchid
            curbib.save()
        except NewArticle.DoesNotExist:
            pass

    # go back to the batch page
    return HttpResponseRedirect(reverse("batch"))





### NYI functions for handling search criteria
# the idea is to be able to add database content via the web interface, instead of via the importdata.py script

# add a new criteria set
def add(request):
    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup

    criteria = Criteria.objects.values_list('id', 'name', named=True).filter(bibgroup_id=bibgroup.id)

    context = {
        "bibgroup": bibgroup,
        "err": "",
        "criteria" : criteria
        }

    return render(request, "bibmanage/add.html", context)


# select a criteria set
def select_criteria(request):

    criteriaid = request.POST["criteriaid"]

    if criteriaid == "":
        data = {
            "instlist" : "",
            "authorlist" : "",
            "exclstem" : "",
            "exclvol" : "",
            "inclstem" : "",
            "inclvol" : "",
            }

    else:
        criteria = Criteria.objects.get(id=criteriaid)

        data = {
            "instlist" : criteria.instlist,
            "authorlist" : criteria.authorlist,
            "exclstem" : criteria.exclstem,
            "exclvol" : criteria.exclvol,
            "inclstem" : criteria.inclstem,
            "inclvol" : criteria.inclvol,
            }

    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")


# NYI, trying to turn the import script into an add function for the web interface
# def add_post(request):

#     username = request.user
#     devkey = username.devkey
#     bibgroup = username.bibgroup

#     criteriaid = request.POST["criteriaid"]
#     startdate = request.POST["startdate"]
#     enddate = request.POST["enddate"]

#     if criteriaid == "":
#         print ("nothing selected, should write an error thingy")
#         pass

#     else:
#         criteria = Criteria.objects.get(id=criteriaid)
#         print (criteria)
#         aff_list =  (criteria.instlist).splitlines()
#         print (aff_list)

#         auth_list = (criteria.authorlist).splitlines()
#         excluded_bibstems = (criteria.exclstem).splitlines()
#         excluded_volumes = (criteria.exclvol).splitlines()

#         pubdate = str(startdate)+" TO "+str(enddate)

#         url = 'https://api.adsabs.harvard.edu/v1/search/query/?q='


#         def add_Article(data1, data2, data3, data4, data5, data6, data7, data8):
#             d, created = Article.objects.get_or_create(bibcode=data1, guess_id=data2, query=data3, affils=data4, authnum=data5, status_id=data6, inst_id=data7, adminbibgroup=data8)

#             return d

#         def getloop(qtype,query,daterange,devkey):
#             q = qtype+':%22'+ urllib.parse.quote(query) + '%22%20pubdate:%5B' + daterange + '%5D'
#             headers = {'Authorization': 'Bearer '+devkey}
#             content = requests.get(url + q, headers=headers)
#             results = content.json()
#             num = results['response']['numFound']
#             return num

#         def adsquery(qtype,aff_list,query,daterange,devkey):

#             #rows max value is 200
#             rows = 100

#             total = getloop(qtype,query,pubdate,devkey)
#             loop = total/rows
#             print ("Looping script "+str(int(loop+1))+" times.")
#             startnum = 0
#             for i in range (0,int(loop+1)):

#                 q = qtype+':%22'+ urllib.parse.quote(query) + '%22%20pubdate:%5B' + daterange + '%5D' + '&fl=bibcode,author,aff,bibgroup&rows='+str(rows)+'&start='+str(startnum)    
                
#                 print (url + q)

#                 headers = {'Authorization': 'Bearer '+devkey}
#                 content = requests.get(url + q, headers=headers)
#                 results = content.json()
#                 docs = results['response']['docs']
                
#                 for x in docs:
#                     bibcode = x['bibcode']
#                     bibstem = bibcode[4:9]
#                     volume = bibcode[9:13]

#                     if bibstem in excluded_bibstems:
#                         pass

#                     elif volume in excluded_volumes:
#                         pass

#                     else:
#                         try:
#                             bibgroup1 = x['bibgroup']
#                             bibgroupclean = ('|').join(bibgroup1)
#                         except KeyError:
#                             bibgroupclean = ''

#                         if bibgroup.bibgroup in bibgroupclean:
#                             pass

#                         else:

#                             try:
#                                 check = Article.objects.get(bibcode=bibcode, adminbibgroup=bibgroup)
#                                 print (bibcode+" already in")
                                
#                             except Article.DoesNotExist:
#                                 print ("adding "+bibcode)

#                                 try:
#                                     auth = x['author']
#                                     num_auth = str(len(auth))

#                                 except KeyError:
#                                     auth = []
#                                     num_auth = "0"

#                                 try:
#                                     aff = x['aff']
#                                     affclean = (' | ').join(aff)
#                                 except KeyError:
#                                     aff = []
#                                     affclean = ''

#                                 pairedaff_list = []

#                                 guess = 2 # review
                                
#                                 if qtype == "aff":
#                                     for y in range(0,len(auth)):
#                                         if query in aff[y].lower():
#                                             guess = 1
#                                             pairedaff_list.append(aff[y])
#                                             aff_list = (" | ").join(pairedaff_list)
#                                         else:
#                                             pass

#                                     if "Visiting" in affclean:
#                                         guess = 3 # review-visiting
#                                     else:
#                                         pass

#                                     if guess == 2: #review
#                                         aff_list = affclean

#                                     # if guess == likely
#                                     if guess == 1 and aff == "smithsonian":
#                                         if "observatory" not in aff_list.lower():
#                                             guess = 4 # review-nonSAO
#                                         else:
#                                             pass

#                                     elif guess == "Keep" and aff == "cfa":
#                                         if "irfu" in aff_list.lower():
#                                             guess = 5 # review-nonCfA
#                                         elif "cfa-italia" in aff_list.lower():
#                                             guess = 5 # review-nonCfA
#                                         else:
#                                             pass                        

#                                     elif guess == 1: # likely
#                                         pass

#                                     else:
#                                         pass       

#                                 elif qtype == "author":

#                                     boo = 0

#                                     #print (aff_list)
#                                     for w in aff_list:
#                                         if w in affclean.lower():
#                                             boo = 1

#                                     if boo == 0:
#                                         guess = 6 # doubtful

#                                     elif boo == 1:
#                                         guess = 1 #likely

#                                     aff_list = affclean

#                                 add_Article(bibcode, guess, query, aff_list, num_auth, 3, 4, bibgroup)
#                                 # status 3 = maybe
#                                 # inst 4 = unknown

#                 startnum += rows
#             time.sleep(1)

#         for x in aff_list:
#             adsquery("aff",aff_list,x,pubdate,devkey)

#         for x in auth_list:
#             adsquery("author",aff_list,x,pubdate,devkey)


#     context = {}


#     #return render(request, "bibmanage/add.html", context)
#     return render(request, "bibmanage/add_post.html", context)


# delete a criteria set
def delete_post(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    #otherwise, if they are logged in...
    username = request.user
    bibgroup = username.bibgroup

    criteriaid = request.POST["criteriaid"]

    if criteriaid == "":
        print ("nothing selected, should write an error thingy")
        pass

        data = {}

    else:
        criteria_del = Criteria.objects.get(id=criteriaid)

        #must uncomment to actually delete the record
        criteria_del.delete()

        criteria = Criteria.objects.values_list('id', 'name', named=True).filter(bibgroup_id=bibgroup.id)

        print (criteria)

        crit_list = []
        for y in criteria:
            crit_dict = {}
            print (y)
            crit_dict["id"] = y.id
            crit_dict["name"] = y.name

            crit_list.append(crit_dict)

        data = {
                "critlist" : crit_list
                }

    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type="application/json")


# NYI
def submitads(request):

    #if they are NOT loggedin...
    if not request.user.is_authenticated:
        context = {
            "state": "home"
            }
        return render(request, "bibtool/index.html", context)

    context = {
        "err" : ""
        }

    return render(request, "bibmanage/submitads.html", context)