from bibsearch.models import Report, Journal, Name, Summary, SummaryReport
from bibtool.models import Author, NewArticle
from celery import Celery
from cfabib.celery import app 

import json
import time
import requests
import urllib.parse


@app.task
def adsquery(namelist,daterange,bibgroup,devkey,reid):

    authorlist = namelist.splitlines()

    #get docs from ADS search
    def searchads(query,position,daterange,devkey):
        rows = 2000
        q = position+':%22'+ urllib.parse.quote(query) + '%22%20pubdate:%5B' + daterange + '%5D%20bibgroup:'+bibgroup+'&fl=bibcode&rows='+str(rows)
        headers = {'Authorization': 'Bearer '+devkey}
        content = requests.get('https://api.adsabs.harvard.edu/v1/search/query/?q=' + q, headers=headers)
        results = content.json()
        docs = results['response']['docs']
        
        bibcodelist = []
        for x in docs:
            bibcodelist.append(str(x['bibcode']))

        return bibcodelist

    #verify bibcodes are in database
    def verifybibcodes(query,bibcodes,devkey):
        namelist = query.split(',')
        bibcodelist = []
        for x in bibcodes:
            names = Author.objects.filter(bibcode__bibcode=x,name__contains=namelist[0], status_id=1)
            for y in names:
                bibcodelist.append(str(y.bibcode))

        return bibcodelist

    #send bibcodes to ADS bigquery
    #output: docs
    def adsbigquery(bibcodelist,devkey):
        bibcodes = "bibcode\n" + '\n'.join(bibcodelist)
        content = requests.post('https://api.adsabs.harvard.edu/v1/search/bigquery', params={'q':'*:*', 'wt':'json', 'fq':'{!bitset}', 'fl':'bibcode,property,citation_count,pub', 'rows':2000}, headers={'Authorization': 'Bearer:'+devkey}, data=bibcodes)
        results = content.json()

        return results['response']['docs']

    def get_stats(docs):

        journallist = []

        ref_cite = 0
        nonref_cite = 0
        ref_art = 0
        nonref_art = 0

        total_art = len(docs)

        for x in docs:                  

            try:
                journal = str(x['pub'])
                journallist.append(journal)
            except KeyError:
                journal = ""

            try:
                prop = x['property']
                propclean = (' | ').join(prop)
            except KeyError:
                propclean = ''

            try:
                citations = int(x['citation_count'])
            except KeyError:
                citations = 0

            if "not refereed" in propclean.lower():
                nonref_cite += citations
                nonref_art += 1
                
            elif "refereed" in propclean.lower():
                ref_cite += citations
                ref_art += 1

            else:
                pass

        return total_art, ref_art, nonref_art, ref_cite, nonref_cite, journallist

    authcount = 0
    alljournals = []

    for x in authorlist:
    
        authors = {}
        authors["name"] = x

        bibcodes = searchads(x,"author",daterange,devkey)
        verified_bibcodes = verifybibcodes(x,bibcodes,devkey)
        unverified_bibcodes = list(set(verified_bibcodes).symmetric_difference(set(bibcodes)))

        verified_docs = adsbigquery(verified_bibcodes,devkey)
        unverified_docs = adsbigquery(unverified_bibcodes,devkey)

        verified_total_art, verified_ref_art, verified_nonref_art, verified_ref_cite, verified_nonref_cite, verified_journalist = get_stats(verified_docs)
        alljournals += verified_journalist

        unverified_total_art, unverified_ref_art, unverified_nonref_art, unverified_ref_cite, unverified_nonref_cite, unverified_journalist = get_stats(unverified_docs)
        alljournals += unverified_journalist


        first_author_bibcodes = searchads(x,"first_author",daterange,devkey)
        first_author_verified_bibcodes = verifybibcodes(x,first_author_bibcodes,devkey)
        first_author_unverified_bibcodes = list(set(first_author_verified_bibcodes).symmetric_difference(set(first_author_bibcodes)))

        first_author_verified_docs = adsbigquery(first_author_verified_bibcodes,devkey)
        first_author_unverified_docs = adsbigquery(first_author_unverified_bibcodes,devkey)

        first_author_verified_total_art, first_author_verified_ref_art, first_author_verified_nonref_art, first_author_verified_ref_cite, first_author_verified_nonref_cite, first_author_verified_journalist = get_stats(first_author_verified_docs)

        first_author_unverified_total_art, first_author_unverified_ref_art, first_author_unverified_nonref_art, first_author_unverified_ref_cite, first_author_unverified_nonref_cite, first_author_unverified_journalist = get_stats(first_author_unverified_docs)

        total_art = verified_total_art + unverified_total_art


        if total_art > 0:
            newauthor = Name.objects.create(resultset_id=reid, aname=x,
                vrart=verified_ref_art,
                vnrart=verified_nonref_art,
                vrcite=verified_ref_cite,
                vnrcite=verified_nonref_cite,
                vrfirst=first_author_verified_ref_art,
                vnrfirst=first_author_verified_nonref_art,
                urart=unverified_ref_art,
                unrart=unverified_nonref_art,
                urcite=unverified_ref_cite,
                unrcite=unverified_nonref_cite,
                urfirst=first_author_unverified_ref_art,
                unrfirst=first_author_unverified_nonref_art)
            authcount += 1
            newauthor.save()

    #get the relevant result set
    resultset = Report.objects.get(id=reid)
    resultset.anum = authcount
    resultset.daterange = daterange
    uniquej = set(alljournals)
    resultset.jnum = len(uniquej)
    resultset.save()

    for y in uniquej:
        jours = {}
        total_art = alljournals.count(y)

        jours["journal"] = y
        jours["total_art"] = total_art

        newjournal = Journal.objects.create(resultset_id=reid,jname=y,articlenum=total_art)
        newjournal.save()


@app.task
def summaryquery(startyr, endyr,bibgroup,devkey,reid):

    pubrange = range(int(startyr),int(endyr)+1)

    for y in pubrange:

        citation = 0

        url = 'https://api.adsabs.harvard.edu/v1/search/query/?q=bibgroup:'+bibgroup+'&fq=pubdate:'+str(y)+'&fq=property:refereed'

        headers={'Authorization': 'Bearer '+devkey}
        content = requests.get(url, headers=headers)
        results=content.json()
        k = results['response']['docs'][0]

        total = results['response']['numFound']
        loop = total/2000
        startnum = 0

        #looping
        for i in range (1,int(loop+2)):
        #for i in range (1,3): #use this line instead of above for short testing
            url1 = url+'&start='+str(startnum)+'&rows=2000&fl=citation_count'
            
            headers = {'Authorization': 'Bearer '+devkey}
            content = requests.get(url1, headers=headers)
            results = content.json()

            docs = results['response']['docs']

            for x in docs:

                try:
                    citation_count = x['citation_count']
                except KeyError:
                    citation_count = 0   
                           
                citation += citation_count

            startnum += 200
            time.sleep(1)
                        
        newsummary = Summary.objects.create(resultset_id=reid,year=y,refart=total,refcite=citation)
        newsummary.save()

    daterange = str(startyr)+" TO "+str(endyr)
    resultset = SummaryReport.objects.get(id=reid)
    resultset.daterange = daterange
    resultset.save()