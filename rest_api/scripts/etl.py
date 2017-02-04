import os
# needed to run pandas locally
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

from sqlalchemy.sql import and_, or_, cast
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

import rest_api.sql_models as models
from rest_api.app import *

# disable warnings "A value is trying to be set on a copy of a slice from a DataFrame..."
pd.options.mode.chained_assignment = None

# classes used in processing
Evaluation = models.Evaluation
Site = models.Site
Geoposition = models.Geoposition
Evaluator = models.Evaluator
Evaluation = models.Evaluation
Person = models.Person
Consultation = models.Consultation
UserGarden = models.UserGarden
RegisteredWorkshop = models.RegisteredWorkshop
WorkshopSession = models.WorkshopSession

# utility functions:

def set_type(col, type, obj):
    """set column data type"""
    obj[col] = obj[col].astype(type)

def mk_dict(col, df):
    """df -> dictionary"""
    return df.to_dict()[col]

def rolling_count(val):
    if val == rolling_count.previous:
        rolling_count.count +=1
    else:
        rolling_count.previous = val
        rolling_count.count = 1
    return rolling_count.count

"""
ETL module for creating an analytical and db dataframes from MetroBlooms evaluation data

To run from interpreter you must first issue the commands:

import sys
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api/scripts')

---> to expose objects from this script:
from etl import *


"""
start = time.time()

"""
EXTRACT DATA


SQL Query:
---------
"""

def sql_object():

    # SQLAlchemy object -> Evaluation of a site
    qEvaluations = s.query(Site.address,
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
                    Evaluation.score.isnot(None)))

    # SQLAlchemy object -> site specific data
    qSites = s.query(Site.garden_id,
                             Site.address,
                             Site.city,
                             Site.zip,
                             Site.neighborhood,
                             Geoposition.latitude,
                             Geoposition.longitude,
                             Geoposition.accuracy,
                             Site.raingarden).\
        outerjoin(Geoposition, Geoposition.geo_id == Site.geo_id)

    # SQLAlchemy object -> site consultation
    qConsultations = s.query(Consultation.user_id,
                             Consultation.confirmed_date,
                             UserGarden.garden_id).\
        join(UserGarden, UserGarden.user_id == Consultation.user_id)

    # SQLAlchemy object -> workshop participant
    qWorkshops = s.query(RegisteredWorkshop.user_id,
                         #WorkshopSession.session_date,
                         UserGarden.garden_id).\
        join(UserGarden, UserGarden.user_id == RegisteredWorkshop.user_id)#.\
        #join(WorkshopSession, WorkshopSession.session_id == RegisteredWorkshop.session_id)

    """
        Criteria to restrict SQLA object. Instead, we grab whole dataset for use in manipulation in Pandas df:

        filter(and_(Evaluation.completed == 1,
                    Evaluation.scoresheet != None,
                    Site.raingarden == 1,
                    Geolocation.latitude != None,
                    Geolocation.latitude > 0))


    """

    # get php array object of scoresheets as list of dictionaries
    # by serializing SQLA query evaluations as list of dictionaries;
    # convert scoresheet from php array object to list of dictionaries
    # manipulate list of dictionaries as "horrible_mess"
    php_scores = [{'garden_id': result.garden_id,
              'ratingyear': result.ratingyear,
              'scoresheet': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}
             for result in qEvaluations]


    return qEvaluations, qSites, qConsultations, qWorkshops, php_scores


def sql_to_dataframe():

    qEvaluations, qSites, qConsultations, qWorkshops, php_scores = sql_object()
    # Pandas dataframes nourished by consuming SQLAlchemy objects:
    scoresheets= pd.DataFrame(php_scores)
    evaluations = pd.read_sql(qEvaluations.statement, qEvaluations.session.bind)#, columns = list('raingardenratingyear'))
    sites = pd.read_sql(qSites.statement, qSites.session.bind)#, columns = list('raingardenratingyear'))
    consultations = pd.read_sql(qConsultations.statement, qConsultations.session.bind)#, columns = list('raingardenratingyear'))
    workshops = pd.read_sql(qWorkshops.statement, qWorkshops.session.bind)#, columns = list('raingardenratingyear'))

    return evaluations, sites, consultations, workshops, scoresheets

# dataframes for consumption
evaluations, sites, consultations, workshops, scoresheets = sql_to_dataframe()

elapsed = (time.time() - start)
print 'Setup calls time elapsed -> ' + str(elapsed)

"""TRANSFORM DATA"""

start = time.time()

def get_core():

    # get number of evaluations per garden:
    # http://stackoverflow.com/questions/22320356/pandas-get-values-from-column-that-appear-more-than-x-times
    evaluations_sub = evaluations[['garden_id', 'ratingyear', 'score', 'raingarden']]
    vc = evaluations_sub.garden_id.value_counts()

    # need to filter out to only one garden per year
    # http://stackoverflow.com/questions/17995024/how-to-assign-a-name-to-the-a-size-column
    # issue with "A value is trying to be set on a copy of a slice from a DataFrame."
    # method with reset_index preferred, since it does not work on a copy of the object

    # set of garden_id had more than one evaluation:
    a = vc[vc >= 1].index.values
    # http://stackoverflow.com/questions/10373660/converting-a-pandas-groupby-object-to-dataframe with count
    b = evaluations_sub.groupby(['ratingyear', 'garden_id']).size().to_frame(name = 'count').reset_index()
    # set of garden_id with more than 1 evaluation in a year
    c = b[b['count'] > 1].garden_id.values

    # remove those garden_id with more than one eval in a year:
    d = np.setdiff1d(a, c)
    # filter df by numpy set difference and remap values accordingly:
    e = evaluations_sub[evaluations_sub['garden_id'].isin(d)].replace({True: 1, False: 0, None: 0})

    # add count of evaluations per garden_id:
    # see http://stackoverflow.com/questions/25119524/pandas-conditional-rolling-count

    # initialize
    rolling_count.count = 0 #static variable
    rolling_count.previous = None #static variable

    e['n'] = e['garden_id'].apply(rolling_count)

    # list of column names:
    header = list(e.columns.values)

    # get list of lists with all data
    data = [e.values.T.tolist()[x] for x in xrange(0, len(header))]

    # create dictionary with header as key:
    data_dict =  {header[x]: data[x] for x in xrange(0, len(header))}

    # write to dataframe:
    core_data = pd.DataFrame(data_dict)

    # set df column data type:
    map(set_type, header, repeat('int', len(header)), repeat(core_data, len(header)))

    # add scoresheet data from evals record set
    f = pd.merge(scoresheets, e, on = ('garden_id', 'ratingyear'), how = 'inner')

    return f, core_data


with_scoresheet, core_data = get_core()


def untangle_php_mess():
    # columns to map in dictionary
    keyed_items = ['ratingyear', 'garden_id', 'scoresheet']

    # Untangle php scoresheet object mess; group by scoresheet value
    # see http://stackoverflow.com/questions/39029939/how-to-best-extract-sub-dictionaries-by-value-in-this-object
    # get dictionary with scoresheet
    horrible_mess = mk_dict(keyed_items[2], with_scoresheet)

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

    # Remap scoresheet category values accordingly

    # set index for dataframe with grouped category,
    # return dataframe and use in list

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

    # write to df using category as name
    # see: http://stackoverflow.com/questions/31432201/assign-dataframes-in-a-list-to-a-list-of-names-pandas

    # initialize:
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

    #def set_id(category, column):
    #    """set index column for df"""
    #    x = pd.DataFrame(grouped[category]).set_index(column)
    #    return x

    # make list of grouped categories from scorecards,
    # using returned df's id column as each list's  unique id column
    cat_collection_idx = [pd.DataFrame(grouped[cat]).set_index('id') for cat in categories ]

    #cat_collection_idx = map(set_id, categories, repeat('id', len(categories)))

    # assign newly indexed list to category named list
    for x in range(len(cat_names)):
        cat_names[x] = cat_collection_idx[x]

    # remap df assigned column names accordingly:
    [x.rename(columns={'0': 'category', '1': 'score'}, inplace=True) for x in cat_names]

    return cat_names, keyed_items

cat_names, keyed_items = untangle_php_mess()

# make multi-column joinable df

def prepare_dual_key_join():
    # dictionary to remap categories:
    cat_dict =[{'visual_appeal': 'visual_impact'},
         {'plant_variety': 'plant_variety_and_health'},
         {'use_of_color': 'visual_impact'},
         {'color': 'visual_impact'}]

    # use nested comprehension to rename categories accordingly to dictionary:
    # condition for length greater than 0 means a match on the key exists
    [x['category'].replace(y, inplace=True) for x in cat_names for y in cat_dict if len(x[x['category'] == y.keys()[0]]) > 0]

    # once column names have been remapped we concatenate all lists:
    result = pd.concat(cat_names)

    # add joinable column using index created in function set_id()
    result['id'] = result.index

    # create data frames with missing dual keyed variables that map to index:

    # dictionary of key by id and value of ratingyear:
    ratingyear = mk_dict(keyed_items[0], with_scoresheet)

    # make list of dictionaries:
    out = [{'id': k, keyed_items[0]: v} for k, v in ratingyear.iteritems()]

    # list of dictionaries -> df:
    ratingyear = pd.DataFrame(out)

    # dictionary of key by id and value of garden_id:
    garden_id = mk_dict(keyed_items[1], with_scoresheet)

    # make list of dictionaries:
    out = [{'id': k, keyed_items[1]: v} for k, v in garden_id.iteritems()]

    # list of dictionaries -> df:
    garden_id = pd.DataFrame(out)

    # merge dual key on id created in set_id():
    keyed_values = pd.merge(garden_id, ratingyear, on = ('id'), how = 'inner')

    return keyed_values, result

keyed_values, result = prepare_dual_key_join()

def make_dual_key_join():

    # merge dual key with single column scoring
    # to make df with list of all categories and respective scores
    final = pd.merge(keyed_values, result, on = ('id'), how = 'inner').\
        sort_values(by = ['garden_id','ratingyear', 'category'],  ascending = [True, True, True])

    # filter out those with category = 'location':
    final_filtered = final[~final['garden_id'].isin(final[final['category'] == 'location'].garden_id)]

    # final_filtered['score'] = final_filtered['score'].astype(int)

    # set data type:
    header = ['score']
    map(set_type, header, repeat('int', len(header)), repeat(final_filtered, len(header)))

    filter_col = ['environmental_stewardship',
                  'maintenance',
                  'design',
                  'visual_impact',
                  'plant_variety_and_health']

    # make list of single column scorecard by category:
    scorecard_categories = [final_filtered[final_filtered['category'] == x] for x in filter_col if len(final_filtered[final_filtered['category'] == x]) > 0]


    # change data layout to multi-columns from single column:
    cols = ['garden_id', 'ratingyear', 'score']
    # in order of list of series
    category_score_prefix = ['es', 'me', 'dn', 'vi', 'pv']

    # first filter columns and then rename score column for each iterable list of pd series:
    for i in xrange(0, len(scorecard_categories)):
        scorecard_categories[i] = scorecard_categories[i][cols]
        # rename series score column per scorecard category
        scorecard_categories[i].rename(columns=lambda x: x.replace('score', category_score_prefix[i] + '_score'), inplace=True)

    # http://stackoverflow.com/questions/23668427/pandas-joining-multiple-dataframes-on-columns/23671390#23671390
    # transform list of series into dataframe via merge
    scorecard = reduce(lambda left,right: pd.merge(left, right, how='inner', on=('garden_id', 'ratingyear')), scorecard_categories)

    # Add total score as remapped category of pass/fail

    # set mask for pass/fail on overall score:
    well_maintained = (core_data['score'] > 8)

    # update according to mask
    core_data['pass'] = np.where(well_maintained, 1, 0)

    return scorecard

scorecard = make_dual_key_join()

elapsed = (time.time() - start)
print 'Transform calls time elapsed -> ' + str(elapsed)

"""LOAD DATA"""
start = time.time()
def data_out():

    # merge core data with remapped categorical scores to create analytical data set
    analytical_set = pd.merge(core_data, scorecard, on = ('garden_id', 'ratingyear'), how = 'inner')

    header = ['score', 'raingarden', 'ratingyear', 'garden_id', 'n']

    map(set_type, header, repeat('int', len(header)), repeat(analytical_set, len(header)))

    # set if garden_id was registered in workshop/consultation
    w_garden_id = set(workshops['garden_id'])
    c_garden_id = set(consultations['garden_id'])

    analytical_set['workshop'] = np.where(analytical_set.garden_id.isin(w_garden_id), 1, 0)
    analytical_set['consultation'] = np.where(analytical_set.garden_id.isin(c_garden_id), 1, 0)

    # site data for db design usage
    cols_to_keep = ['garden_id',
                    'address',
                    'city',
                    'zip',
                    'neighborhood',
                    'latitude',
                    'longitude',
                    'accuracy']


    full_set = pd.merge(analytical_set, sites[cols_to_keep] , how='left', on='garden_id')

    # write out data:
    analytical_set.to_csv('~/development/data/mb_analytical.csv')
    full_set.to_csv('~/development/data/mb_full.csv')

    return analytical_set, full_set

analytical_set, full_set = data_out()

elapsed = (time.time() - start)
print 'Load calls time elapsed -> ' + str(elapsed)
