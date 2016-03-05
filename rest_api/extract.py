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
left outer join (gardenevals_gardens garden, geolocation geo)
on (garden.garden_id = eval.garden_id AND garden.geo_id = geo.geo_id)
where completed = 1 AND scoresheet is not null

'''

'''
raingarden designation:
    Evaluation.eval_type = 'raingarden'
    Site.raingarden = 1
    Evaluation.comments search for raingarden
'''

# create SQLAlchemy query object
query = db.session.query(Site.address,
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
    join(Evaluation, Site.garden_id == Evaluation.garden_id).\
    outerjoin(Geoposition, Geoposition.geo_id == Site.geo_id)

'''
    Criteria to restrict SQLA object. Instead, we grab whole dataset for use in manipulation in Pandas df:

    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                Site.raingarden == 1,
                Geolocation.latitude != None,
                Geolocation.latitude > 0))


# serialize SQLA query output as list of dictionaries; convert scoresheet from php array object to list of dictionaries
# TODO: will need to extract individual elements from scoresheet for use in analysis
#

out = []
for result in query:
            data = {'address': result.address,
                    'jsonified': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}

            out.append(data)

print 'data:'
print out
print len(out)


table = pd.DataFrame(out)
count = table.address.nunique()
'''

# grab SQLA query output directly into Pandas dataframe
out = pd.read_sql(query.statement, query.session.bind, columns = list('raingardenratingyear'))

# example queries:
print out.info()
out[(~out.city.str.lower().str.contains('minnea')) & (~out.city.str.lower().str.contains('mpls')) & (~out.city.str.lower().str.contains('poli'))].groupby('city').size()
out[~out.latitude.isnull() & out.latitude != 0]

out.groupby(['eval_type','raingarden']).size()
out.groupby('city').size()
out.groupby(['city','raingarden']).size()
out.groupby(['zip','raingarden']).size()
out.groupby('accuracy').size()
out.groupby(['latitude','longitude']).size()
out.groupby(['latitude','longitude','accuracy']).size()
out.groupby(['latitude','longitude','accuracy','raingarden']).size()
out.groupby(['garden_id','raingarden']).size()

# basic analytics on data set:

# total sites
len(out.garden_id)
print out[(out.raingarden == 1)].groupby('raingarden').size()

# site w/ rain gardens
len(out[(out.raingarden == 1)].groupby('garden_id').size())

# rain gardens by city
headers = ['city','garden', 'n']
s = (out.groupby(['city','raingarden']).size(),headers)
print tabulate(out.groupby('city').count()['raingarden'].to_frame(), headers, tablefmt="simple")
#print tabulate(s, headers, tablefmt="simple")

# city versus eval ratingyear for rain gardens
test = out[['raingarden','city','ratingyear']]
test = test.replace({True: 1, False: 0})
print test.pivot_table(index=["city"], columns="ratingyear",values='raingarden',aggfunc=np.sum)

# rating year by rain garden
test2 = out[['raingarden','ratingyear']]
test2 = test2.replace({True: 1, False: 0})
print test2.pivot_table(columns="ratingyear",values='raingarden',aggfunc=np.sum)

# site versus eval ratingyear for rain gardens
test3 = out[['raingarden','ratingyear','garden_id']]
test3 = test3.replace({True: 1, False: 0})
print len(test3[(test3.raingarden == 1)].groupby('garden_id').count())

# unique geo
print len(out.groupby(['latitude','longitude']).size())
# accuracies
print out.groupby('accuracy').size()

# geo by rating year for rain garden
test4 = out[['raingarden','latitude','longitude','ratingyear']]
test4 = test4.replace({True: 1, False: 0})
print test4.pivot_table(index=["latitude","longitude"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

# score by rating year
test5 = out[['raingarden','score','ratingyear']]
test5 = test5.replace({True: 1, False: 0})
print test5.pivot_table(index=["score","score"],columns="ratingyear",values='raingarden',aggfunc=np.sum)

# geo by rating year for rain garden
test6 = out[['raingarden','zip','ratingyear']]
test6 = test6.replace({True: 1, False: 0})
print test6.pivot_table(index=["zip"],columns="ratingyear",values='raingarden',aggfunc=np.sum)
#print out

#print out[100:101]
#print out[300:301]
#print out[700:701]

# get data set as pandas data frame for manipulation

#frame = pd.read_sql(query.statement, query.session.bind)

#print frame
