import tempfile
import os
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import pandas as pd
pd.set_option('display.width', 1000)
import numpy as np

#from phpserialize import unserialize
#import simplejson as json
import mb_models as models
from mb_models import db
from tabulate import tabulate


'''
To run from interpreter you must first issue the commands:

import sys
sys.path.append('absolute path to this file')

'''
# Classes used in testing
Evaluation = models.Evaluation
Site = models.Site
Geoposition = models.Geoposition
Evaluation = models.Evaluation


'''
SQL Query:

use metroblo_website;

select  latitude,
    longitude,
    accuracy,
    address,
    city,
    zip,
    raingarden,
    scoresheet,
    score,
    eval_type,
    rating,
    comments,
    date_evaluated
from gardenevals_evaluations eval
left evaluationser join (gardenevals_gardens garden, geolocation geo)
on (garden.garden_id = eval.garden_id AND garden.geo_id = geo.geo_id)
where completed = 1 AND scoresheet is not null

'''

'''
raingarden designation:
    Evaluation.eval_type = 'raingarden'
    Site.raingarden = 1
    Evaluation.comments search for raingarden
'''

# create SQLAlchemy query objects

# Grabs all evaluation data tied to a site
qEvaluations = db.session.query(Site.address,
                         Site.city,
                         Site.zip,
                         Site.neighborhood,
                         Evaluation.garden_id,
                         Evaluation.scoresheet,
                         Evaluation.score,
                         Evaluation.rating,
                         Evaluation.ratingyear,
                         Geoposition.latitude,
                         Geoposition.longitude,
                         Geoposition.accuracy,
                         Site.raingarden,
                         Evaluation.eval_type,
                         Evaluation.comments,
                         Evaluation.date_evaluated,
                         Evaluation.evaluator_id).\
    outerjoin(Evaluation, Site.garden_id == Evaluation.garden_id).\
    outerjoin(Geoposition, Geoposition.geo_id == Site.geo_id)

# Grabs site specific data
qSites = db.session.query(Site.garden_id,
                         Site.address,
                         Site.city,
                         Site.zip,
                         Site.neighborhood,
                         Geoposition.latitude,
                         Geoposition.longitude,
                         Geoposition.accuracy,
                         Site.raingarden).\
    outerjoin(Geoposition, Geoposition.geo_id == Site.geo_id)

'''
    Criteria to restrict SQLA object. Instead, we grab whole dataset for use in manipulation in Pandas df:

    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                Site.raingarden == 1,
                Geolocation.latitude != None,
                Geolocation.latitude > 0))


# serialize SQLA query evaluationsput as list of dictionaries; convert scoresheet from php array object to list of dictionaries
# TODO: will need to extract individual elements from scoresheet for use in analysis
#

evaluations = []
for result in query:
            data = {'address': result.address,
                    'jsonified': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}

            evaluations.append(data)

print 'data:'
print evaluations
print len(evaluations)


table = pd.DataFrame(evaluations)
count = table.address.nunique()
'''


# grab SQLA query evaluationsput directly into Pandas dataframe
evaluations = pd.read_sql(qEvaluations.statement, qEvaluations.session.bind, columns = list('raingardenratingyear'))
sites = pd.read_sql(qSites.statement, qSites.session.bind, columns = list('raingardenratingyear'))

# example Pandas queries:
print evaluations.info()
print sites.info()

'''
sites[(~sites.city.str.lower().str.contains('minnea')) &
            (~sites.city.str.lower().str.contains('mpls')) &
            (~sites.city.str.lower().str.contains('poli'))].groupby('city').size()

sites[~sites.latitude.isnull() & sites.latitude != 0]

evaluations.groupby(['eval_type','raingarden']).size()
sites.groupby('city').size()
evaluations.groupby(['city','raingarden']).size()
evaluations.groupby(['zip','raingarden']).size()
sites.groupby('accuracy').size()
sites.groupby(['latitude','longitude']).size()
sites.groupby(['latitude','longitude','accuracy']).size()
evaluations.groupby(['latitude','longitude','accuracy','raingarden']).size()
evaluations.groupby(['garden_id','raingarden']).size()

'''

# basic analytics on data set:

# total sites
print 'Total Unique Sites'
print sites.garden_id.nunique()
print evaluations.garden_id.nunique()

print 'Total Sites with Identified BMP'
print sites[(sites.raingarden == 1)].groupby('raingarden').size()

# site w/ rain gardens
print len(sites[(sites.raingarden == 1)].groupby('garden_id').size())

# rain gardens by city
print 'Total BMP by City'
headers = ['city','garden']
s = (sites.groupby(['city','raingarden']).size(),headers)
print tabulate(sites.groupby('city').count()['raingarden'].to_frame(), headers, tablefmt="simple")
print tabulate(s, headers, tablefmt="simple")

# confounder: eval_type used for evaluations not consistent with raingarden flag
print 'Issue with Identifying Raingarden'
print evaluations.pivot_table(index=["city"], columns=["eval_type"],values='raingarden',aggfunc=np.count_nonzero)

# number of evaluators
print 'Total Evaluators'
print evaluations.evaluator_id.nunique()

# mobile evaluations:
print 'Total Mobile Evaluations'
test7 = evaluations[['comments']]
test7 = test7.replace({True: 1, False: 0})
print len(test7[(test7.comments.str.lower().str.contains('mobile') == 1)])

# city versus eval rating year for rain gardens
print 'Total BMP in City Evaluated by Year'
test = evaluations[['raingarden','city','ratingyear']]
test = test.replace({True: 1, False: 0})
print test.pivot_table(index=["city"], columns="ratingyear",values='raingarden',aggfunc=np.sum)

# rating year by rain garden
print 'Total BMP Evaluated by Year'
test2 = evaluations[['raingarden','ratingyear']]
test2 = test2.replace({True: 1, False: 0})
headers = ['year','n']
print tabulate(test2.pivot_table(columns="ratingyear",values='raingarden',aggfunc=np.sum), headers, tablefmt="simple")

# evaluated  with for rain gardens
print 'Total BMP Evaluated'
test3 = evaluations[['raingarden','garden_id']]
test3 = test3.replace({True: 1, False: 0})
print len(test3[(test3.raingarden == 1)].groupby(['garden_id']).count())

# unique geo
print 'Total Unique Geocoordinates'
print len(sites.groupby(['latitude','longitude']).size())

# accuracies
print 'Geocoordinate Accuracies'
test8 = sites[['accuracy']]
print test8.groupby('accuracy').size()
print 'Geocoordinate Accuracies'
headers = ['accuracy','n']
print tabulate(test8.groupby('accuracy').size().to_frame(), headers, tablefmt="simple")

# geo by rating year for rain garden
print 'Geocoordinates of Evaluations by Year'
test4 = evaluations[['raingarden','latitude','longitude','ratingyear']]
test4 = test4.replace({True: 1, False: 0})
print test4.pivot_table(index=["latitude","longitude"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

# score by rating year
print 'Ratings by Year for BMP'
test5 = evaluations[['raingarden','score','ratingyear']]
test5 = test5.replace({True: 1, False: 0})
print test5.pivot_table(index=["score"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

# zip by rating year for rain garden
print 'BMP Evaluations in Zipcode by Year'
test6 = evaluations[['raingarden','zip','ratingyear']]
test6 = test6.replace({True: 1, False: 0})
print test6.pivot_table(index=["zip"],columns="ratingyear",values='raingarden',aggfunc=np.sum)
#print evaluations

print 'SQL evaluations:'
print qEvaluations

print '\n'
print '\n'

print 'SQL sites:'
print qSites


#print evaluations[100:101]
#print evaluations[300:301]
#print evaluations[700:701]

# get data set as pandas data frame for manipulation

#frame = pd.read_sql(query.statement, query.session.bind)

#print frame

