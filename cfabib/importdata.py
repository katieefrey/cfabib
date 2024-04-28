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

from bibtool.models import Article, Author, NewArticle

# printing database settings so I know I'm connected to the right one
print (settings.DATABASES)

start = input("Query Start Date (YYYY or YYYY-MM): ")
end = input("Query End Date (YYYY or YYYY-MM): ")

######### Variables to Edit #########

#pubdate format  YYYY-MM-DD TO YYYY-MM-DD
#month and day optional
#examples:  2018-09 TO 2018-11
#           2018 TO 2019-03
#           2018-03 TO 2019
# pubdate = "2019-01 TO 2019-08"
pubdate = str(start)+" TO "+str(end)

#exclude all results that area already this bibgroup
bibgroup = "CfA"


######### Excluded Strings, Edit with Caution #########

# exclude the following bibstems, each must be exactly 5 characters long
excluded_bibstems = ["arXiv","ATel1","ATel.","yCat.","MPEC.","sptz.","Cosp.","DPS..","IAUC.","SPD..","AGUFM","AGUSM","APS..","IAUFM","AAS..","HEAD.","DDA..","zndo."]
# Verified bibstem codes to INCLUDE
# (i.e. do NOT write these into the above list)
# CBET.

#Always Include?
#ChNew  -- Chandra News?

# exclude the following volume codes, must be 4 characters long
excluded_volumes = ["prop",".tmp"]
# Verified volume codes to INCLUDE
# (i.e. do NOT write these into the above list)
# conf
# book

devkey = (open('dev_key.txt','r')).read()

# saerch on these affiliation strings
incafflist = (open('inc_aff_list.txt','r')).read()
inc_aff_list = incafflist.splitlines()

# search on theis lsit of authors
authorlist = (open('author_list.txt','r')).read()
auth_list = authorlist.splitlines()

# do not SEARCH on the broad or simple aff list, but use to narrow down author name results
broadafflist = (open('broad_aff_list.txt','r')).read()
broad_aff_list = broadafflist.splitlines()

simpleafflist = (open('simple_aff_list.txt','r')).read()
simple_aff_list = simpleafflist.splitlines()


# function to add data to the NewArticle table
def add_NewArticle(data1, data2, data3, data4):
    try:
        d, created = NewArticle.objects.get_or_create(bibcode=data1, title=data2, adminbibgroup_id=data3, authnum=data4)
        return d

    except django.db.utils.IntegrityError:
        print("check to make sure the database is set up")
        print("or something went wrong, new article")
        return

# function to add data to the Author table
def add_Author(data1, data2, data3, data4, data5, data6, data7, data8, data9):
    try:
        d, created = Author.objects.get_or_create(bibcode_id=data1, name=data2, affil=data3, guess_id=data4, query=data5, inst_id=data6, adminbibgroup_id=data7, status_id=data8, autoclass=data9)
        return d

    except django.db.utils.IntegrityError:
        print("something went wrong, author")
        return

# function to determine how many loops are needed to get all information for an author or affiliation
def getloop(qtype,query,daterange,url,devkey):
    q = qtype+':%22'+ urllib.parse.quote(query) + '%22%20pubdate:%5B' + daterange + '%5D'
    headers = {'Authorization': 'Bearer '+devkey}
    content = requests.get(url + q, headers=headers)
    results = content.json()
    num = results['response']['numFound']
    return num

# query ADS for a affiliation or author and add results to database
def newadsquery(qtype,query,daterange,url,devkey):

    #rows max value is 200
    rows = 200

    total = getloop(qtype,query,pubdate,url,devkey)
    loop = total/rows
    print ("Looping script "+str(int(loop+1))+" times.")
    startnum = 0

    for i in range (0,int(loop+1)):
        q = qtype+':%22'+ urllib.parse.quote(query) + '%22%20pubdate:%5B' + daterange + '%5D' + '&fl=bibcode,author,aff,bibgroup,database,title&fq_database=(database%3Aastronomy OR database%3Aphysics)&rows='+str(rows)+'&start='+str(startnum)    
        
        print (query)

        headers = {'Authorization': 'Bearer '+devkey}
        content = requests.get(url + q, headers=headers)
        results = content.json()

        docs = results['response']['docs']
        
        for x in docs:
            bibcode = x['bibcode']
            bibstem = bibcode[4:9]
            volume = bibcode[9:13]

            # if bibstem or volume are in an excluded set,
            # or if the article is not in the physics or astro database
            # then skip the rest of the function

            if "astronomy" not in x["database"] and "physics" not in x["database"]:
                pass

            elif bibstem in excluded_bibstems:
                pass

            elif volume in excluded_volumes:
                pass

            else:

                try:
                    bibgroup1 = x['bibgroup']
                    bibgroupclean = ('|').join(bibgroup1)
                except KeyError:
                    bibgroupclean = ''

                # # if the bibgroup is in the list of bibgroups,
                # # skip the rest of the function
                # if bibgroup in bibgroupclean:
                #     pass

                # # otherwise! it is time to get to work
                # else:

                try:
                    # was this article evaluated using the pre Feb 2021 system?
                    test = Article.objects.get(bibcode=bibcode)
                    print (bibcode+" already in old system")
                
                # if not, then continue
                except Article.DoesNotExist:

                    # list the authors, and how many there are
                    try:
                        auth = x['author']
                        num_auth = str(len(auth))
                    except KeyError:
                        auth = []
                        num_auth = "-"

                    # get the article title, include subtitle.
                    try:
                        title = x['title']
                        title1 = (('|').join(title))
                        if len(title1) > 249:
                            titleclean = title1[0:249]
                        else:
                            titleclean = title1
                    except KeyError:
                        titleclean = ''

                    # list the affiliations
                    try:
                        aff = x['aff']
                        affclean = (' | ').join(aff)
                    except KeyError:
                        aff = []
                        affclean = ''

                    # check to see if this paper is in the New Article database
                    try:
                        NewArticle.objects.get(bibcode=bibcode)
                    
                    # if it is not, then add it
                    except NewArticle.DoesNotExist:
                        print ("adding "+bibcode)
                        add_NewArticle(bibcode, titleclean, 1, num_auth)

                    # get the NewArticle object for this bibcode
                    bibsc = NewArticle.objects.get(bibcode=bibcode)

                    # auto assign the default "review" stauts to guess
                    guess = 2 # review
                    
                    # if this query was searching for an affiliation do the following
                    if qtype == "aff":
                        for y in range(0,len(auth)):

                            #check to see if the queried affiliation is in the list of article affiliations
                            if query in aff[y].lower():
                                
                                if Author.objects.filter(bibcode=bibsc.id, name=auth[y], affil=aff[y],adminbibgroup_id=1).exists():
                                    # an author with this name, affiliation, and bibcode are already in the datase
                                    pass
                                else:
                                    # since the query is in the list of article affiliations, set the guess to "likely"
                                    guess = 1 # likely

                                    # however if "visiting" or retirred appears anywhere, then set to status 3, "review-visiting"
                                    if "visiting" in aff[y].lower():
                                        guess = 3 # review-visiting

                                    elif "visit" in aff[y].lower():
                                        guess = 3 # review-visiting

                                    elif "retired" in aff[y].lower():
                                        guess = 3 # review-visiting
        
                                    # because there is another "cfa", if "cfa" was the query, set the paper to a review status
                                    if guess == 1 and query == "cfa":
                                        if "irfu" in aff[y].lower():
                                            guess = 5 # review-nonCfA
                                        elif "cfa-italia" in aff[y].lower():
                                            guess = 5 # review-nonCfA
                                        elif "cfai" in aff[y].lower():
                                            guess = 5 # review-nonCfA
                                        else:
                                            guess = 2 #review

                                    # set guess status to review if "northcott" appears in an "hco" affiliation
                                    elif guess == 1 and query == "hco":
                                        if "Northcott" in aff[y].lower():
                                            guess = 5 # review-nonCfA

                                    # depending on the end result of the "guess" status, set other statuses
                                    if guess == 1:
                                        autoclass = True
                                        status = 1
                                        inst = 6
                                    else:
                                        autoclass = False
                                        status = 3
                                        inst = 4

                                    # make an entry into that Author table
                                    add_Author(bibsc.id, auth[y], aff[y], guess, query, inst, 1, status, autoclass)

                    # otherwise, if this query was searching for an author do the following
                    elif qtype == "author":
                        flname = query.split(',')

                        # get last name and first initial only from the author query
                        namei = flname[0]+", "+flname[1][1]

                        for y in range(0,len(auth)):

                            #if the last name and first initial appears in the author list, then set statuses
                            if namei.lower() in auth[y].lower():
                                affs = aff[y].lower()

                                guess = 6
                                autoclass = True
                                status = 2
                                inst = 5

                                # if something from the broad list is in the affiliation than consider
                                for z in broad_aff_list:
                                    if z in affs:
                                        guess = 1 # likely

                                if guess == 1:
                                    autoclass = True
                                    status = 1
                                    inst = 6
                                else:

                                    if affs == '-':
                                        guess = 2
                                    else: 
                                        for z in simple_aff_list:
                                            if z in affs:
                                                guess = 2
                                    
                                    if guess == 2:
                                        autoclass = False
                                        status = 3
                                        inst = 4

                                # if this author, affiliation, and bibcode combo are in the database then pass
                                if Author.objects.filter(bibcode=bibsc.id, name=auth[y], affil=aff[y],adminbibgroup_id=1).exists():
                                        pass
                                else:                            
                                    # otherwise add to database
                                    add_Author(bibsc.id, auth[y], aff[y], guess, query, inst, 1, status, autoclass)

        startnum += rows
    time.sleep(1)


if __name__ == "__main__":

    url = 'https://api.adsabs.harvard.edu/v1/search/query/?q='

    for x in inc_aff_list:
        newadsquery("aff",x,pubdate,url,devkey)

    for x in auth_list:
        newadsquery("author",x,pubdate,url,devkey)

    print ("finished!")