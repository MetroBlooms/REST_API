import os
# needed to run pandas locally
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

from sqlalchemy.sql import and_, or_
import pandas as pd
pd.set_option('display.width', 1000)
import numpy as np
from phpserialize import unserialize
import simplejson as json
from ast import literal_eval
from collections import defaultdict
# needed to map extra parameter
from itertools import repeat
import time

import mb_models as models
from mb_models import db
# disable warnings "A value is trying to be set on a copy of a slice from a DataFrame..."
pd.options.mode.chained_assignment = None

# Classes used in testing
Evaluation = models.Evaluation
Site = models.Site
Geoposition = models.Geoposition
Evaluator = models.Evaluator
Evaluation = models.Evaluation
Person = models.Person

"""
ETL module for creating and analytical dataframe from MEtroBloom evaluation data

To run from interpreter you must first issue the commands:

import sys
sys.path.append('absolute path to this file')
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')

---> to expose objects from this script:
import sys
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')
from extract import *

SQL Query:
---------

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


raingarden designation:
    Evaluation.eval_type = 'raingarden'
    Site.raingarden = 1
    Evaluation.comments search for raingarden
"""

# SQLAlchemy query objects:
start = time.time()

"""EXTRACT DATA"""

# SQLAlchemy object -> Evaluation of a site
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

# SQLAlchemy object -> site specific data
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


"""
    Criteria to restrict SQLA object. Instead, we grab whole dataset for use in manipulation in Pandas df:

    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                Site.raingarden == 1,
                Geolocation.latitude != None,
                Geolocation.latitude > 0))


# serialize SQLA query evaluations as list of dictionaries;
# convert scoresheet from php array object to list of dictionaries

"""

# get php array object of scoresheets as list of dictionaries
#evals = []
#for result in qEvaluations:
#            data = {'garden_id': result.garden_id,
#                    'ratingyear': result.ratingyear,
#                    'scoresheet': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}

#            evals.append(data)


evals = [{'garden_id': result.garden_id,
          'ratingyear': result.ratingyear,
          'scoresheet': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}
         for result in qEvaluations]

#print 'data:'
#print evals
#print len(evals)

table = pd.DataFrame(evals)
#count = table.garden_id.nunique()

# Pandas dataframe nourished by consuming SQLAlchemy object:

#evaluations = pd.read_sql(qEvaluations.statement, qEvaluations.session.bind, columns = list('raingardenratingyear'))
#sites = pd.read_sql(qSites.statement, qSites.session.bind, columns = list('raingardenratingyear'))
evaluations = pd.read_sql(qEvaluations.statement, qEvaluations.session.bind, columns = list('raingardenratingyear'))
sites = pd.read_sql(qSites.statement, qSites.session.bind, columns = list('raingardenratingyear'))

elapsed = (time.time() - start)
print 'Setup calls time elapsed -> ' + str(elapsed)

"""TRANSFORM DATA"""

start = time.time()

# get number of evaluations per garden:
# http://stackoverflow.com/questions/22320356/pandas-get-values-from-column-that-appear-more-than-x-times
evaluations_sub = evaluations[['garden_id', 'ratingyear', 'score', 'raingarden']]
vc = evaluations_sub.garden_id.value_counts()

#filter those with 6 evaluations:

#df = test[test['garden_id'].isin(vc[vc >= 4].index.values)]
#df.values.T.tolist()

# need to filter out to only one garden per year
# http://stackoverflow.com/questions/17995024/how-to-assign-a-name-to-the-a-size-column
# issue with "A value is trying to be set on a copy of a slice from a DataFrame."
# method with reset_index preferred, since it does not work on a copy of the object
#df['n'] = df.groupby(['garden_id','ratingyear']).transform(np.size)
#t = test
#u = df[df['size'] > 1].garden_id


# set of garden_id had more than one evaluation:
a = vc[vc >= 1].index.values
# http://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-object-to-dataframe with count
t = evaluations_sub.groupby(['ratingyear', 'garden_id']).size().to_frame(name = 'count').reset_index()
# set of garden_id with more than 1 evaluation in a year
b = t[t['count'] > 1].garden_id.values

# remove those garden_id with more than one eval in a year:
c = np.setdiff1d(a, b)
# filter df by numpy set difference and remap values accordingly:
d = evaluations_sub[evaluations_sub['garden_id'].isin(c)].replace({True: 1, False: 0, None: 0})

# add count of evaluations per garden_id:

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
#import matplotlib
#matplotlib.use('TkAgg')

# write df elements to list for plotting
#garden_id = d.values.T.tolist()[0]
#ratingyear = d.values.T.tolist()[1]
#score = d.values.T.tolist()[2]
#raingarden = d.values.T.tolist()[3]
#n = d.values.T.tolist()[4]

# list of column names:
header = list(d.columns.values)

#for x in xrange(0, len(test)):
#    test[x] = d.values.T.tolist()[x]

# get list of lists with all data
data = [d.values.T.tolist()[x] for x in xrange(0, len(header))]

#test_dict = {test_vals[0]: test[0], test_vals[1]: test[1], test_vals[2]: test[2], test_vals[3]: test[3], test_vals[4]: test[4] }

# create dictionary with header as key:
data_dict =  {header[x]: data[x] for x in xrange(0, len(header))}

#df = pd.DataFrame(dict(ratingyear = ratingyear, score = score, garden_id = garden_id, raingarden = raingarden, n = n))

# write to dataframe:
df = pd.DataFrame(data_dict)

#df['score'] = df['score'].astype(int)
#df['garden_id'] = df['garden_id'].astype(int)
#df['raingarden'] = df['raingarden'].astype(int)
#df['n'] = df['n'].astype(int)
#df['score'] = df['score'].astype(int)
#df['ratingyear'] = df['ratingyear'].astype(int)

def set_type(col, type, obj):
    """set column data type"""
    obj[col] = obj[col].astype(type)

# TODO: use test_vals
#df_col = ['score', 'garden_id', 'raingarden', 'n', 'score', 'ratingyear']

# set column data type:
map(set_type, header, repeat('int', len(header)), repeat(df, len(header)))

# add scoresheet data from evals record set
f = pd.merge(table, d, on = ('garden_id', 'ratingyear'), how = 'inner')
# f.to_dict()['scoresheet']

def mk_dict(col, df):
    """df -> dictionary"""
    return df.to_dict()[col]

keyed_items = ['ratingyear', 'garden_id', 'scoresheet']

#ratingyear = map(mk_dict, keyed_items[0], repeat(f, len(keyed_items[0:1])))

# Untangle php scoresheet object
# group by scoresheet value: http://stackoverflow.com/questions/39029939/how-to-best-extract-sub-dictionaries-by-value-in-this-object
# get dictionary with scoresheet
horrible_mess = mk_dict(keyed_items[2], f)
#horrible_mess = f.to_dict()['scoresheet']

# remap dictionary with id as key:
# literal_eval evaluates the statement and raises an exception if not a valid Python datatype
still_messy  = {k:literal_eval(v) for k,v in horrible_mess.items()}
# defaultdict uses default_factory to group key-value pairs
grouped = defaultdict(list)

# group by scoresheet category using key '0':
for k, v in still_messy.iteritems():
    for v1 in v.values():
        v1['id'] = k
        # group by key -> id
        grouped[v1['0']].append(v1)

#grouped['visual_appeal']
#grouped['visual_impact']
#grouped['environmental_stewardship']

#print len(test3[(test3.raingarden == 1)].groupby(['garden_id']).count())

# Remap scoresheet category values accordingly

# set index for dataframe with grouped category:
def set_df_id(category, column):
    """set index column for df"""
    x = pd.DataFrame(grouped[category]).set_index(column)
    return x

categories = ['visual_appeal',
              'visual_impact',
              'plant_variety',
              'plant_variety_and_health',
              'use_of_color',
              'color',
              'location',
              'sizing',
              'design',
              'maintenance',
              'environmental_stewardship']

map(set_df_id, categories, repeat('id', len(categories)))

# write to specific DF name: http://stackoverflow.com/questions/31432201/assign-dataframes-in-a-list-to-a-list-of-names-pandas
appeal,\
impact,\
plant_variety,\
plant_variety_and_health,\
use_of_color,\
color,\
location,\
sizing,\
design,\
maintenance,\
environmental_stewardship = \
    None,None,None,None,None,None,None,None,None,None,None

cat_names = [appeal,
             impact,
             plant_variety,
             plant_variety_and_health,
             use_of_color,
             color,location,
             sizing,
             design,
             maintenance,
             environmental_stewardship]

# make indexed df:
df_idx = map(set_df_id, categories, repeat('id', len(categories)))

# get category names:
for x in range(len(cat_names)):
    cat_names[x] = df_idx[x]
#cat_names

#[cat_names[x] == df[x] for x in cat_names]

#cat_names[x] = df[x for x in range(len(cat_names)]

# remap column names:
[x.rename(columns={'0': 'category', '1': 'score'}, inplace=True) for x in cat_names]

# remap categories:
di =[{'visual_appeal': 'visual_impact'},
     {'plant_variety': 'plant_variety_and_health'},
     {'use_of_color': 'visual_impact'},
     {'color': 'visual_impact'}]

# def remap_cat(di, df):
#    x = df['category'].replace(di, inplace=True)
#    return x


#search for value in df

#for i in range(0, len(cat_names)):
#    if len(cat_names[i][cat_names[i]['category'] == 'visual_impact']) > 0:
#        print di[i]

#for i in xrange(0, len(cat_names)):
#    for j in xrange(0, len(di)):
#        if len(cat_names[i][cat_names[i]['category'] == di[j].keys()[0]]) > 0:
#            print '{}{}'.format(di[j], j)


#for x in cat_names:
#    for y in di:
#        if len(x[x['category'] == y.keys()[0]]) > 0:
#            x['category'].replace(y, inplace=True)
#            print y
#            print x

# use nested comprehension to rename categories accordingly to dictionary:
[x['category'].replace(y, inplace=True) for x in cat_names for y in di if len(x[x['category'] == y.keys()[0]]) > 0]

# once remapped -> concatenate:
result = pd.concat(cat_names)

# add joinable column:
result['id'] = result.index
# create data frames with missing dual keyed variables that map to index:

#def mk_dict(col, df):
#    return df.to_dict()[col]

#keyed_items = ['ratingyear', 'garden_id']

#ratingyear = map(mk_dict, keyed_items[0], repeat(f, len(keyed_items[0:1])))

# dictionary of key by id and value of ratingyear:
ratingyear = mk_dict(keyed_items[0], f)

#ratingyear = f.to_dict()['ratingyear']
#out = []
#for k, v in ratingyear.items():
# for k, v in map(mk_dict, repeat('ratingyear', len(f)), repeat(f, len(f))).items():
#    kv = {'id': k, 'ratingyear': v}
#    out.append(kv)

# make list of dictionaries:
out = [{'id': k, keyed_items[0]: v} for k, v in ratingyear.iteritems()]

# list of dictionaries -> df:
ratingyear = pd.DataFrame(out)

#garden_id = f.to_dict()['garden_id']
#garden_id = map(mk_dict, repeat('garden_id', len(f)), repeat(f, len(f)))

# dictionary of key by id and value of garden_id:
garden_id = mk_dict(keyed_items[1], f)

#out = []
#for k, v in garden_id.items():
#for k, v in map(mk_dict, repeat('garden_id', len(f)), repeat(f, len(f))).items():
#    kv = {'id': k, 'garden_id': v}
#    out.append(kv)

# make list of dictionaries:
out = [{'id': k, keyed_items[1]: v} for k, v in garden_id.iteritems()]

# list of dictionaries -> df:
garden_id = pd.DataFrame(out)

# merge dual key:
keyed_values = pd.merge(garden_id, ratingyear, on = ('id'), how = 'inner')

# merge dual key with single column scoring:
final = pd.merge(keyed_values, result, on = ('id'), how = 'inner').\
    sort_values(by = ['garden_id','ratingyear', 'category'],  ascending = [True, True, True])

# filter out those with category = 'location':
final_filtered = final[~final['garden_id'].isin(final[final['category'] == 'location'].garden_id)]

# final_filtered['score'] = final_filtered['score'].astype(int)

# set data type:
header = ['score']
map(set_type, header, repeat('int', len(header)), repeat(final_filtered, len(header)))

#es = final_filtered[final_filtered['category'] == 'environmental_stewardship']
#me = final_filtered[final_filtered['category'] == 'maintenance']
#dn = final_filtered[final_filtered['category'] == 'design']
#vi = final_filtered[final_filtered['category'] == 'visual_impact']
#pv = final_filtered[final_filtered['category'] == 'plant_variety_and_health']

filter_col = ['environmental_stewardship',
              'maintenance',
              'design',
              'visual_impact',
              'plant_variety_and_health']

# single column scorecard by category:
scorecard_categories = [final_filtered[final_filtered['category'] == x] for x in filter_col if len(final_filtered[final_filtered['category'] == x]) > 0]

# ????? not sure what this was supposed to do
#df1 = df[~df['garden_id'].isin(final[final['category'] == 'location'].garden_id)]

# prelim stuff

# n gardens with 7 evaluations, 1 per year
#final_filtered.groupby('garden_id').count()


# change data layout to multi-columns from single column:
cols = ['garden_id', 'ratingyear', 'score']
category_score_prefix = ['es', 'me', 'dn', 'vi', 'pv']

# first filter columns and then rename score column for each iterable df:
for i in xrange(0, len(scorecard_categories)):
    scorecard_categories[i] = scorecard_categories[i][cols]
    # rename score column per scorecard category
    scorecard_categories[i].rename(columns=lambda x: x.replace('score', category_score_prefix[i] + '_score'), inplace=True)


#dn = dn[['garden_id', 'ratingyear', 'score']]
#dn.columns = ['garden_id', 'ratingyear', 'dn_score']

#es = es[['garden_id', 'ratingyear', 'score']]
#es.columns = ['garden_id', 'ratingyear', 'es_score']

#me = me[['garden_id', 'ratingyear', 'score']]
#me.columns = ['garden_id', 'ratingyear', 'me_score']

#pv = pv[['garden_id', 'ratingyear', 'score']]
#pv.columns = ['garden_id', 'ratingyear', 'pv_score']

#vi = vi[['garden_id', 'ratingyear', 'score']]
#vi.columns = ['garden_id', 'ratingyear', 'vi_score']

# http://stackoverflow.com/questions/23668427/pandas-joining-multiple-dataframes-on-columns/23671390#23671390
scorecard = reduce(lambda left,right: pd.merge(left, right, how='inner', on=('garden_id', 'ratingyear')), scorecard_categories)

#scorecard = pd.merge(dn, es, on = ('garden_id', 'ratingyear'), how = 'inner')
#scorecard = pd.merge(scorecard, me, on = ('garden_id', 'ratingyear'), how = 'inner')
#scorecard = pd.merge(scorecard, pv, on = ('garden_id', 'ratingyear'), how = 'inner')
#scorecard = pd.merge(scorecard, vi, on = ('garden_id', 'ratingyear'), how = 'inner')
# covariate matrix by garden
#scorecard[['garden_id', 'dn_score', 'es_score', 'me_score', 'pv_score', 'vi_score']].groupby('garden_id').describe()

# covariate matrix across all evaluations
#scorecard[['dn_score', 'es_score', 'me_score', 'pv_score', 'vi_score']].describe()

# Add total score as remapped category of pass/fail

# set mask for pass/fail on overall score:
well_maintained = (df['score'] > 8)
df['pass'] = 0
# update those that passed
df['pass'][well_maintained] = 1

"""LOAD DATA"""

# merge with categorical scores:
analytical_set = pd.merge(df, scorecard, on = ('garden_id', 'ratingyear'), how = 'inner')
#analytical_set['score'] = analytical_set['score'].astype(int)
#analytical_set['raingarden'] = analytical_set['raingarden'].astype(int)
#analytical_set['ratingyear'] = analytical_set['ratingyear'].astype(int)
#analytical_set['garden_id'] = analytical_set['garden_id'].astype(int)
#analytical_set['n'] = analytical_set['n'].astype(int)


header = ['score', 'raingarden', 'ratingyear', 'garden_id', 'n']

map(set_type, header, repeat('int', len(header)), repeat(analytical_set, len(header)))

elapsed = (time.time() - start)
print 'Other calls time elapsed -> ' + str(elapsed)
