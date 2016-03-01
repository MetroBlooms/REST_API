import tempfile
import os
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import pandas as pd
pd.set_option('display.width', 1000)
import numexpr

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from phpserialize import unserialize
import simplejson as json
import rest_api.mb_models as models
from rest_api.mb_models import db

# Classes used in testing
Evaluation = models.Evaluation
Site = models.Site
Geoposition = models.Geoposition
Evaluation = models.Evaluation

#from app import db
#app = Flask(__name__)
#app.config.from_object('rest_api.config')
#db = SQLAlchemy(app)

'''
SQL Query:

use metroblo_website;

SELECT  latitude,
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
FROM gardenevals_evaluations eval
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
                         Evaluation.scoresheet,
                         Evaluation.score,
                         Evaluation.rating,
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
    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                Site.raingarden == 1,
                Geolocation.latitude != None,
                Geolocation.latitude > 0))


# serialize query output as list of dictionaries; convert scoresheet from php array object to list of dictionaries
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

out = pd.read_sql(query.statement, query.session.bind)

# example queries:

out[(~out.city.str.lower().str.contains('minnea')) & ~out.city.str.lower().str.contains('mpls')]
out[~out.latitude.isnull() & out.latitude != 0]
out.groupby('city').size()
out.groupby('accuracy').size()


#print out

#print out[100:101]
#print out[300:301]
#print out[700:701]

# get data set as pandas data frame for manipulation

#frame = pd.read_sql(query.statement, query.session.bind)

#print frame
