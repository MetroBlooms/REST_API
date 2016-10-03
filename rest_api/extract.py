import tempfile
import time
import os
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

from sqlalchemy.sql import and_, or_, func

import pandas as pd
pd.set_option('display.width', 1000)
import numpy as np

from phpserialize import unserialize
import simplejson as json
import mb_models as models
from mb_models import db
from tabulate import tabulate

def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    m = n / arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out

'''
To run from interpreter you must first issue the commands:

import sys
sys.path.append('absolute path to this file')
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')

---> to expose objects from this script:
import sys
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')
from extract import *

To print:
python extract.py > out
printed to PDF using postscript
'''
# Classes used in testing
Evaluation = models.Evaluation
Site = models.Site
Geoposition = models.Geoposition
Evaluator = models.Evaluator
Evaluation = models.Evaluation
Person = models.Person


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
                                Person.firstname,
                                Person.lastname,
                                Evaluation.evaluation_id,
                                Evaluation.eval_type,
                                Evaluation.garden_id,
                                Evaluation.scoresheet,
                                Evaluation.score,
                                Evaluation.rating,
                                Evaluation.ratingyear,
                                Evaluation.comments,
                                Evaluation.date_evaluated,
                                Evaluation.evaluator_id). \
    outerjoin(Evaluation, Site.garden_id == Evaluation.garden_id). \
    outerjoin(Evaluator, Evaluator.evaluator_id == Evaluation.evaluator_id). \
    outerjoin(Person, Evaluator.user_id == Person.user_id). \
    outerjoin(Geoposition, Geoposition.geo_id == Site.geo_id). \
    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                #Site.raingarden == 1,
                Evaluation.score.isnot(None)))
#Evaluation.ratingyear == 2015))

'''
qEvaluations = db.session.query(Site.address,
                         Site.city,
                         Site.zip,
                         Site.neighborhood,
                         Site.raingarden,
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
    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                or_(Site.raingarden == 1,
                    Evaluation.eval_type == 'raingarden')))
                #Evaluation.ratingyear == 2015))
                #Person.firstname == None))
'''
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

'''

# get scoresheets
evals = []
for result in qEvaluations:
            data = {'garden_id': result.garden_id,
                    'ratingyear': result.ratingyear,
                    'scoresheet': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}

            evals.append(data)

print 'data:'
print evals
print len(evals)


table = pd.DataFrame(evals)
count = table.garden_id.nunique()



# grab SQLA query evaluationsput directly into Pandas dataframe
#evaluations = pd.read_sql(qEvaluations.statement, qEvaluations.session.bind, columns = list('raingardenratingyear'))
#sites = pd.read_sql(qSites.statement, qSites.session.bind, columns = list('raingardenratingyear'))
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
print 'Ratings by Year for BMP'
print '======================='
test7 = evaluations[['score','garden_id','ratingyear']]
test7 = test7.replace({True: 1, False: 0})
print test7.pivot_table(index=["ratingyear"],columns="garden_id",values='score')
print test7.groupby('garden_id').describe()

# Get summary statistics on total score for those having more than 3 evaluations
# http://stackoverflow.com/questions/37780949/pandas-filtering-on-describe-output-count
newframe = test7.groupby('garden_id').describe()
idx = pd.IndexSlice
mask = newframe.loc[idx[:,'count'],:] > 3
idx1 = mask[mask.values].index.get_level_values('garden_id')
print newframe.loc[idx[idx1,:],:]

# get number of evaluations per garden
# http://stackoverflow.com/questions/22320356/pandas-get-values-from-column-that-appear-more-than-x-times
test = evaluations[['garden_id', 'ratingyear', 'score', 'raingarden']]
vc = test.garden_id.value_counts()
#filter those with 6 evaluations
#df = test[test['garden_id'].isin(vc[vc >= 4].index.values)]
#df.values.T.tolist()

# need to filter out to only one garden per year
# http://stackoverflow.com/questions/17995024/how-to-assign-a-name-to-the-a-size-column
# issue with "A value is trying to be set on a copy of a slice from a DataFrame."
# method with reset_index preferred, since it does not work on a copy of the object
#df['n'] = df.groupby(['garden_id','ratingyear']).transform(np.size)
#t = test
#u = df[df['size'] > 1].garden_id

a = vc[vc >= 1].index.values
# http://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-object-to-dataframe
t = test.groupby(['ratingyear', 'garden_id']).size().to_frame(name = 'count').reset_index()
b = t[t['count'] > 1].garden_id.values

# remove those sites with more than one eval in a year
c = np.setdiff1d(a, b)
d = test[test['garden_id'].isin(c)]

d = d.replace({True: 1, False: 0, None: 0})

# add count of garden_id
# count TOTAL times across garden_id
# e = test.groupby(['garden_id']).size().to_frame(name = 'n').reset_index()

# see http://stackoverflow.com/questions/25119524/pandas-conditional-rolling-count
def rolling_count(val):
    if val == rolling_count.previous:
        rolling_count.count +=1
    else:
        rolling_count.previous = val
        rolling_count.count = 1
    return rolling_count.count
rolling_count.count = 0 #static variable
rolling_count.previous = None #static variable

#e = pd.DataFrame(d)
d['n'] = d['garden_id'].apply(rolling_count)


#d = pd.merge(e, d, on = ('garden_id'), how = 'inner')
# Issue wrt python shell: http://github.com/mwaskom/seaborn/issues/231
import matplotlib
matplotlib.use('TkAgg')
import seaborn as sns

# write df elements to list for plotting
garden_id = d.values.T.tolist()[0]
ratingyear = d.values.T.tolist()[1]
score = d.values.T.tolist()[2]
raingarden = d.values.T.tolist()[3]
n = d.values.T.tolist()[4]

# write to dictionary and new df
df = pd.DataFrame(dict(ratingyear = ratingyear, score = score, garden_id = garden_id, raingarden = raingarden,n = n))

df['score'] = df['score'].astype(int)
df['garden_id'] = df['garden_id'].astype(int)
df['raingarden'] = df['raingarden'].astype(int)
df['n'] = df['n'].astype(int)
df['score'] = df['score'].astype(int)
df['ratingyear'] = df['ratingyear'].astype(int)


# plot variables as scatter using assigned colors by category
#sns.lmplot('ratingyear', 'score', data=d, hue='garden_id', fit_reg=False)

# draw plots with multiple Axes where each Axes shows the same relationship conditioned on different levels of
# some variable
#g = sns.FacetGrid(df, hue='garden_id', size=8)
# scatter
#g.map(plt.scatter, 'ratingyear', 'score')
# line
#g.map(plt.plot, 'ratingyear', 'score')

#plt.scatter(df['ratingyear'], df['score'], s=100, c=df['garden_id'],label=df['garden_id'])
#plt.show()
#plt.close()

# add scoresheet data from evals record set
f = pd.merge(table, d, on = ('garden_id', 'ratingyear'), how = 'inner')
f.to_dict()['scoresheet']

# group by scoresheet value: http://stackoverflow.com/questions/39029939/how-to-best-extract-sub-dictionaries-by-value-in-this-object
horrible_mess = f.to_dict()['scoresheet']
from ast import literal_eval
from collections import defaultdict
still_messy  = {k:literal_eval(v) for k,v in horrible_mess.items()}
grouped = defaultdict(list)
#for sub in still_messy.values():
for k, v in still_messy.items():
    for d1 in v.values():
        d1['id'] = k
        # group by key -> id
        grouped[d1['0']].append(d1)

grouped['visual_appeal']
grouped['visual_impact']
grouped['environmental_stewardship']

print len(test3[(test3.raingarden == 1)].groupby(['garden_id']).count())

# Remap scoresheet category values accordingly

# visual_impact
appeal = pd.DataFrame(grouped['visual_appeal']).set_index('id')
appeal.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
di = {'visual_appeal': 'visual_impact'}
appeal['category'].replace(di, inplace=True)

impact = pd.DataFrame(grouped['visual_impact']).set_index('id')
impact.rename(columns={'0': 'category', '1': 'score'}, inplace=True)

# plant_variety_and_health
plant_variety = pd.DataFrame(grouped['plant_variety']).set_index('id')
plant_variety.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
di = {'plant_variety': 'plant_variety_and_health'}
plant_variety['category'].replace(di, inplace=True)

plant_variety_and_health = pd.DataFrame(grouped['plant_variety_and_health']).set_index('id')
plant_variety_and_health.rename(columns={'0': 'category', '1': 'score'}, inplace=True)

# color
use_of_color = pd.DataFrame(grouped['use_of_color']).set_index('id')
use_of_color.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
di = {'use_of_color': 'color'}
use_of_color['category'].replace(di, inplace=True)

color = pd.DataFrame(grouped['color']).set_index('id')
color.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
# NB: color -> visual_impact in 2013
di = {'color': 'visual_impact'}
color['category'].replace(di, inplace=True)
use_of_color['category'].replace(di, inplace=True)

location = pd.DataFrame(grouped['location']).set_index('id')
location.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
#di = {'location': 'design'}
#location['category'].replace(di, inplace=True)

sizing = pd.DataFrame(grouped['sizing']).set_index('id')
sizing.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
#di = {'sizing': 'design'}
#sizing['category'].replace(di, inplace=True)

# design
#visual_impact = pd.DataFrame(grouped['visual_impact']).set_index('id')
#visual_impact.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
#di = {'visual_impact': 'design'}
#visual_impact['category'].replace(di, inplace=True)

#visual_appeal = pd.DataFrame(grouped['visual_appeal']).set_index('id')
#visual_appeal.rename(columns={'0': 'category', '1': 'score'}, inplace=True)
#di = {'visual_appeal': 'design'}
#visual_appeal['category'].replace(di, inplace=True)

design = pd.DataFrame(grouped['design']).set_index('id')
design.rename(columns={'0': 'category', '1': 'score'}, inplace=True)

# maintenance
maintenance = pd.DataFrame(grouped['maintenance']).set_index('id')
maintenance.rename(columns={'0': 'category', '1': 'score'}, inplace=True)

# environmental_stewardship
environmental_stewardship = pd.DataFrame(grouped['environmental_stewardship']).set_index('id')
environmental_stewardship.rename(columns={'0': 'category', '1': 'score'}, inplace=True)

# once remapped -> concatenate
frames = [appeal,
          impact,
          plant_variety,
          location,
          sizing,
          plant_variety_and_health,
          use_of_color,
          color,
          design,
          environmental_stewardship,
          maintenance]

result = pd.concat(frames)
# make into joinable column
result['id'] = result.index
# create data frames with missing dual keyed variables that map to index:

ratingyear = f.to_dict()['ratingyear']
out = []
for k, v in ratingyear.items():
    kv = {'id': k, 'ratingyear': v}
    out.append(kv)

ratingyear = pd.DataFrame(out)

out = []
garden_id = f.to_dict()['garden_id']
for k, v in garden_id.items():
    kv = {'id': k, 'garden_id': v}
    out.append(kv)

garden_id = pd.DataFrame(out)

keyed_values = pd.merge(garden_id, ratingyear, on = ('id'), how = 'inner')

# kv = keyed_values.drop('id', 1)

# single column scoring
final = pd.merge(keyed_values, result, on = ('id'), how = 'inner').\
    sort_values(by = ['garden_id','ratingyear', 'category'],  ascending = [True, True, True])

# filter out those with category = 'location'
yesh = final[~final['garden_id'].isin(final[final['category'] == 'location'].garden_id)]

yesh['score'] = yesh['score'].astype(int)

es = yesh[yesh['category'] == 'environmental_stewardship']
me = yesh[yesh['category'] == 'maintenance']
dn = yesh[yesh['category'] == 'design']
vi = yesh[yesh['category'] == 'visual_impact']
pv = yesh[yesh['category'] == 'plant_variety_and_health']

# plot variables as scatter using assigned colors by category
#sns.lmplot('ratingyear', 'score', data=es, hue='garden_id', fit_reg=False)

# draw plots with multiple Axes where each Axes shows the same relationship conditioned on different levels of
# some variable
#g = sns.FacetGrid(es, hue='garden_id', size=8)
# scatter
#g.map(plt.scatter, 'ratingyear', 'score')
# line
#g.map(plt.plot, 'ratingyear', 'score')

# total scores, filter out 'location' (and sizing, since instrument is not same)
df1 = df[~df['garden_id'].isin(final[final['category'] == 'location'].garden_id)]

'''
bp_df = df[['garden_id','score']]
bp_df.boxplot(by='garden_id')
plt.title("Boxplot of total scores")
plt.suptitle("")

# by score sheet
bp_es = es[['garden_id','score']]
bp_es.boxplot(by='garden_id')
plt.title("Boxplot of evironmental stewardship")
plt.suptitle("")

bp_me = me[['garden_id','score']]
bp_me.boxplot(by='garden_id')

bp_dn = dn[['garden_id','score']]
bp_dn.boxplot(by='garden_id')

bp_vi = vi[['garden_id','score']]
bp_vi.boxplot(by='garden_id')

bp_pv = pv[['garden_id','score']]
bp_pv.boxplot(by='garden_id')


'''

# prelim stuff

# n gardens with 7 evaluations, 1 per year
yesh.groupby('garden_id').count()

# get summary statistics on categorical score
summary = yesh[['category', 'score', 'garden_id']]
summary[(summary.category == 'environmental_stewardship')].groupby('garden_id').describe()
summary[(summary.category == 'plant_variety_and_health')].groupby('garden_id').describe()
summary[(summary.category == 'maintenance')].groupby('garden_id').describe()
summary[(summary.category == 'design')].groupby('garden_id').describe()
summary[(summary.category == 'visual_impact')].groupby('garden_id').describe()

# summary statistics on total score
summary = df1[['score', 'garden_id']]
summary.groupby('garden_id').describe()

# change data layout to multi-columns from single column

dn = dn[['garden_id', 'ratingyear', 'score']]
dn.columns = ['garden_id', 'ratingyear', 'dn_score']

es = es[['garden_id', 'ratingyear', 'score']]
es.columns = ['garden_id', 'ratingyear', 'es_score']

me = me[['garden_id', 'ratingyear', 'score']]
me.columns = ['garden_id', 'ratingyear', 'me_score']

pv = pv[['garden_id', 'ratingyear', 'score']]
pv.columns = ['garden_id', 'ratingyear', 'pv_score']

vi = vi[['garden_id', 'ratingyear', 'score']]
vi.columns = ['garden_id', 'ratingyear', 'vi_score']

scorecard = pd.merge(dn, es, on = ('garden_id', 'ratingyear'), how = 'inner')
scorecard = pd.merge(scorecard, me, on = ('garden_id', 'ratingyear'), how = 'inner')
scorecard = pd.merge(scorecard, pv, on = ('garden_id', 'ratingyear'), how = 'inner')
scorecard = pd.merge(scorecard, vi, on = ('garden_id', 'ratingyear'), how = 'inner')
# covariate matrix by garden
scorecard[['garden_id', 'dn_score', 'es_score', 'me_score', 'pv_score', 'vi_score']].groupby('garden_id').describe()

# covariate matrix across all evaluations
scorecard[['dn_score', 'es_score', 'me_score', 'pv_score', 'vi_score']].describe()

# Add total score as remapped category

# set mask for pass/fail on overall score
well_maintained = (df1['score'] > 8)
df1['pass'] = 0
# update those that passed
df1['pass'][well_maintained] = 1

# merge with categorical scores
analytical_set = pd.merge(df1, scorecard, on = ('garden_id', 'ratingyear'), how = 'inner')
analytical_set['score'] = analytical_set['score'].astype(int)
analytical_set['raingarden'] = analytical_set['raingarden'].astype(int)
analytical_set['ratingyear'] = analytical_set['ratingyear'].astype(int)
analytical_set['garden_id'] = analytical_set['garden_id'].astype(int)
analytical_set['n'] = analytical_set['n'].astype(int)

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

print '\n'
print '\n'
print '\n'
print '============='
print 'ALL OUT:'
#test = evaluations[['firstname','lastname','address','city','zip','garden_id','evaluator_id','ratingyear','score','raingarden', 'comments']]
#print test

#print test.pivot_table(index=["evaluator_id"],columns="garden_id",values='score',aggfunc=np.sum)


#test.to_csv('test2.csv',sep='\t')
#test = evaluations[['firstname','lastname','evaluator_id']]
#print test



