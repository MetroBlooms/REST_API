import tempfile
import time
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
                         Site.raingarden,
                         Geoposition.latitude,
                         Geoposition.longitude,
                         Geoposition.accuracy,
                         Evaluation.evaluation_id,
                         Evaluation.eval_type,
                         Evaluation.garden_id,
                         Evaluation.scoresheet,
                         Evaluation.score,
                         Evaluation.rating,
                         Evaluation.ratingyear,
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
print 'Script: ' + os.path.basename(__file__)
print 'DataSource: metroblo_website'
print 'RunDate: ' + time.strftime("%d-%B-%Y")
print 'RunBy: ' + os.environ['USER']

print '\n'
print '===================================='
print 'MetroBlooms Evaluation Data Summary:'
print '===================================='

# example Pandas queries:
print '\n'
print 'evaluation dataframe info:'
print '=========================='
print evaluations.info()
print '\n'
print 'sites dataframe info:'
print '====================='
print sites.info()

print '\n'
print 'Total Unique Sites'
print '=================='
print sites.garden_id.nunique()

print '\n'
print 'Total Unique Sites with Evaluation'
print '=================================='
print evaluations.garden_id.nunique()

print '\n'
#print sites[(sites.raingarden == 1)].groupby('raingarden').size()
print 'Total Unique Sites with BMP'
print '==========================='
print len(sites[(sites.raingarden == 1)].groupby('garden_id').size())

print '\n'
print 'Total BMP by City'
print '================='
headers = ['city','garden']
print tabulate(sites[(sites.raingarden == 1)].groupby('city').count()['raingarden'].to_frame(), headers, tablefmt="simple")

print '\n'
print 'Total Unique Evaluations'
print '========================'
print evaluations.evaluation_id.nunique()

# confounder: eval_type used for evaluations not consistent with raingarden flag
print '\n'
print 'Issue with Identifying Raingarden: '\
      'sites.raingarden versus evaluations.eval_type'
print '================================================================================'
print evaluations.pivot_table(index=["city"], columns=["eval_type"],values='raingarden',aggfunc=np.count_nonzero)

print '\n'
print 'Total Evaluators'
print '================'
print evaluations.evaluator_id.nunique()

print '\n'
print 'Total Mobile Evaluations'
print '========================'
test7 = evaluations[['comments']]
test7 = test7.replace({True: 1, False: 0})
print len(test7[(test7.comments.str.lower().str.contains('mobile') == 1)])

print '\n'
print 'Total BMP in City Evaluated by Year'
print '==================================='
test = evaluations[['raingarden','city','ratingyear']]
test = test.replace({True: 1, False: 0})
print test.pivot_table(index=["city"], columns="ratingyear",values='raingarden',aggfunc=np.sum)

print '\n'
print 'Total BMP Evaluated by Year'
print '==========================='
test2 = evaluations[['raingarden','ratingyear']]
test2 = test2.replace({True: 1, False: 0})
print test2.pivot_table(columns="ratingyear",values='raingarden',aggfunc=np.sum)

print '\n'
print 'Total BMP Evaluated'
print '==================='
test3 = evaluations[['raingarden','garden_id']]
test3 = test3.replace({True: 1, False: 0})
print len(test3[(test3.raingarden == 1)].groupby(['garden_id']).count())

print '\n'
print 'Total Unique Geocoordinates'
print '==========================='
print len(sites.groupby(['latitude','longitude']).size())

print '\n'
test8 = sites[['accuracy']]
print 'Geocoordinate Accuracies'
print '========================'
headers = ['accuracy','n']
print tabulate(test8.groupby('accuracy').size().to_frame(), headers, tablefmt="simple")

print '\n'
print 'Geocoordinates of Evaluations by Year'
print '====================================='
test4 = evaluations[['raingarden','latitude','longitude','ratingyear']]
test4 = test4.replace({True: 1, False: 0})
print test4.pivot_table(index=["latitude","longitude"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

# score by rating year
print '\n'
print 'Ratings by Year for BMP'
print '======================='
test5 = evaluations[['raingarden','score','ratingyear']]
test5 = test5.replace({True: 1, False: 0})
print test5.pivot_table(index=["score"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

print '\n'
print 'BMP Evaluations in Zipcode by Year'
print '=================================='
test6 = evaluations[['raingarden','zip','ratingyear']]
test6 = test6.replace({True: 1, False: 0})
print test6.pivot_table(index=["zip"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

print '\n'
print 'SQL evaluations:'
print '================'
print qEvaluations

print '\n'

print 'SQL sites:'
print '=========='
print qSites


#print evaluations[100:101]
#print evaluations[300:301]
#print evaluations[700:701]

# get data set as pandas data frame for manipulation

#frame = pd.read_sql(query.statement, query.session.bind)

#print frame

