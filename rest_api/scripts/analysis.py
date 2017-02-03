import sys
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')
from rest_api.scripts.etl import *

import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import pandas as pd
pd.set_option('display.width', 1000)
import numpy as np

from tabulate import tabulate

print 'data:'
print evals
print len(evals)

table = pd.DataFrame(evals)
count = table.garden_id.nunique()

"""
To print:
python extract.py > out
printed to PDF using postscript
"""

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
print 'Issue with Identifying Raingarden: ' \
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

# get summary statistics on categorical score

summary = final_filtered[['category', 'score', 'garden_id']]
summary[(summary.category == 'environmental_stewardship')].groupby('garden_id').describe()
summary[(summary.category == 'plant_variety_and_health')].groupby('garden_id').describe()
summary[(summary.category == 'maintenance')].groupby('garden_id').describe()
summary[(summary.category == 'design')].groupby('garden_id').describe()
summary[(summary.category == 'visual_impact')].groupby('garden_id').describe()

# summary statistics on total score
summary = df[['score', 'garden_id']]
summary.groupby('garden_id').describe()

# as per http://blog.yhat.com/posts/logistic-regression-and-python.html




dummy_es = pd.get_dummies(analytical_set['es_score'], prefix='es')
dummy_es.head()
dummy_pv = pd.get_dummies(analytical_set['pv_score'], prefix='pv')
dummy_me = pd.get_dummies(analytical_set['me_score'], prefix='me')

data = analytical_set[['pass','raingarden','n']]
data = data.join(dummy_es.ix[:,[0,1,2,3]])
data = data.join(dummy_pv.ix[:,[0,1,2,3]])
data = data.join(dummy_me.ix[:,[0,1,2,3]])

data['intercept'] = 1.0

train_cols = data.columns[1:]
import statsmodels.api as sm
logit = sm.Logit(data['pass'], data[train_cols])

result = logit.fit()
print result.summary()
# look at the confidence interval of each coefficient
print result.conf_int()
# odds ratio
np.exp(result.params)

# combined
params = result.params
conf = result.conf_int()
conf['OR'] = params
conf.columns = ['2.5%', '97.5%', 'OR']
np.exp(conf)

# simulate
combos = pd.DataFrame(cartesian([[1, 2, 3, 4, 5, 6, 7], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4], [0, 1, 2, 3, 4], [0, 1], [1.]]))
combos.columns = ['n', 'es_score', 'me_score', 'pv_score', 'raingarden', 'intercept']

dummy_es = pd.get_dummies(combos['es_score'], prefix='es')
dummy_es.head()
dummy_pv = pd.get_dummies(combos['pv_score'], prefix='pv')
dummy_me = pd.get_dummies(combos['me_score'], prefix='me')
dummy_rg = pd.get_dummies(combos['raingarden'], prefix='rg')

dummy_es.columns = ['es_0', 'es_1', 'es_2', 'es_3', 'es_4']
dummy_me.columns = ['me_0', 'me_1', 'me_2', 'me_3', 'me_4']
dummy_pv.columns = ['pv_0', 'pv_1', 'pv_2', 'pv_3', 'pv_4']
dummy_rg.columns = ['rg_0', 'rg_1']
cols_to_keep = ['n', 'es_score', 'me_score', 'pv_score', 'raingarden', 'intercept']

combos = combos[cols_to_keep]
combos = combos.join(dummy_es.ix[:,[0,1,2,3]])
combos = combos.join(dummy_pv.ix[:,[0,1,2,3]])
combos = combos.join(dummy_me.ix[:,[0,1,2,3]])
combos = combos.join(dummy_rg.ix[:,[1]])

combos['pass_pred'] = result.predict(combos[train_cols])
import matplotlib.pylab as pl

def isolate_and_plot(variable):
    # isolate gre and class rank
    grouped = pd.pivot_table(combos, values=['pass_pred'], index=[variable, 'raingarden'],
                             aggfunc=np.mean)

    # in case you're curious as to what this looks like
    # print grouped.head()
    #                      admit_pred
    # gre        prestige
    # 220.000000 1           0.282462
    #            2           0.169987
    #            3           0.096544
    #            4           0.079859
    # 284.444444 1           0.311718

    # make a plot
    colors = 'rbgyrbgy'
    for col in combos.raingarden.unique():
        plt_data = grouped.ix[grouped.index.get_level_values(1) == col]
        pl.plot(plt_data.index.get_level_values(0), plt_data['pass_pred'],
                color=colors[int(col)])

    pl.xlabel(variable)
    pl.ylabel("P(pass=1)")
    pl.legend(['0', '1'], loc='upper left', title='rg')
    pl.title("Prob(pass=1) isolating " + variable + " and rg")
    pl.show()

#isolate_and_plot('es_score')
#isolate_and_plot('raingarden')
#isolate_and_plot('pv_score')
#isolate_and_plot('es_score')

#move analysis over to R
#import pandas.rpy.common as com

##### NEW!!!!! #####

from rest_api.scripts.rpy2 import pandas2ri
from rest_api.scripts import rpy2 as ro

R = ro.r
pandas2ri.activate()

r_analytical_set = pandas2ri.py2ri(analytical_set)
print r_analytical_set
print type(r_analytical_set)

# get summary
print R.table(r_analytical_set.rx('pass'))
print R.table(r_analytical_set.rx('raingarden'))
print R.table(r_analytical_set.rx('score'))
print R.table(r_analytical_set.rx('es_score'))
print R.table(r_analytical_set.rx('me_score'))
print R.table(r_analytical_set.rx('dn_score'))
print R.table(r_analytical_set.rx('vi_score'))
print R.table(r_analytical_set.rx('pv_score'))

# http://stackoverflow.com/questions/36582505/r-x-must-be-atomic-for-sort-list
print R.table(R.unlist(r_analytical_set.rx('pass')), R.unlist(r_analytical_set.rx('raingarden')))

print R.summary(r_analytical_set)

# firgure out how to do in R
analytical_set.describe()
pd.crosstab(analytical_set['pass'], analytical_set['es_score'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['me_score'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['pv_score'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['raingarden'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['n'], rownames=['pass'])
pd.crosstab(analytical_set['raingarden'], analytical_set['es_score'], rownames=['raingarden'])
pd.crosstab(analytical_set['raingarden'], analytical_set['me_score'], rownames=['raingarden'])
pd.crosstab(analytical_set['raingarden'], analytical_set['pv_score'], rownames=['raingarden'])
pd.crosstab(analytical_set['raingarden'], analytical_set['raingarden'], rownames=['raingarden'])
pd.crosstab(analytical_set['raingarden'], analytical_set['n'], rownames=['raingarden'])
pd.crosstab(analytical_set['pass'], analytical_set['raingarden'], rownames=['pass'])

import matplotlib
matplotlib.use('TkAgg')

# do in R? see http://stackoverflow.com/questions/13035834/plot-every-column-in-a-data-frame-as-a-histogram-on-one-page-using-ggplot
analytical_set[['es_score', 'me_score', 'pv_score', 'vi_score', 'dn_score', 'score', 'raingarden', 'n', 'pass']].hist()

import rest_api.scripts.rpy2.robjects.lib.ggplot2 as ggplot2

gp = ggplot2.ggplot(r_analytical_set)
pp = gp + \
     ggplot2.aes_string(x='factor(garden_id)', y='score') + \
     ggplot2.geom_boxplot()

pp.plot()

pp = gp + \
     ggplot2.aes_string(x='score') + \
     ggplot2.geom_histogram()

pp.plot()

#### TODO: scatterplots? Other qualitative?


# -----> logistic stuffs
R('p <- 846/5062')
R('odds <- p/(1 - p)')
R('logit <- log(p/(1 - p))')
R('invlogit <- function(x){ exp(x)/(1 + exp(x)) }')
R('invlogit(logit)')

#formula = 'pass~n'

from rest_api.scripts.rpy2 import Formula
formula = Formula('pass~n')
formula.getenvironment()['pass'] = r_analytical_set.rx2('pass')
formula.getenvironment()['n'] = r_analytical_set.rx2('n')

#fit = R.glm(formula=formula, data=r_analytical_set,   family=R('binomial(link="logit")'))
import rest_api.scripts.rpy2.robjects.packages as rpacks
stats = rpacks.importr("stats")
fit = stats.glm(formula = formula,
                family = stats.binomial(link = "logit"),
                data=r_analytical_set)

s = R.summary(fit)
print(fit)
print(R.summary(fit))

R.plot(formula,
       data=r_analytical_set,
       ylab = 'P(outcome =  1 | pass)',
       xlab = 'N: number of times evaluated',
       xaxp = R.c(0, 5, 10))
#R.plot('''{0}, data={1}, ylab = "P(outcome =  1 | pass)", xlab = "N: number of times evaluated", xaxp = R.c(0, 5, 10)''').format(formula, r_analytical_set)
t s
#with open('/Users/gregsilverman//development/python/rest_api/rest_api/utils.r', 'r') as f:
#    string = f.read()

#from rpy2.robjects.packages import STAP
#invlogit = STAP(string, "invlogit")

R('invlogit <- function(x){ exp(x)/(1 + exp(x)) }')
R('curve(invlogit({0} + {1}*x), add = TRUE)'.format(R.coef(fit)[0],R.coef(fit)[1]))

v = -1*R.coef(fit)[0]/R.coef(fit)[1]
R.lines(R.c(-1, v), R.c(0.5, 0.5), col = "red", lty = "dashed")
R.lines(R.c(v, v), R.c(-0.1, 0.5), col = "red", lty = "dashed")

print R.table(r_analytical_set.rx('pass'))
z2 = fit.rx2('linear.predictors')

#c1 = R.curve(invlogit(R.coef(fit)[0] + R.coef(fit)[1]*R.x), add = True)
#R(c1)

'''
formula = 'pass ~ raingarden + n'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n + factor(es_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n + factor(me_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n + factor(pv_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))


formula = 'pass ~ raingarden + n + factor(me_score) + factor(pv_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n + factor(me_score) + factor(es_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n + factor(pv_score) + factor(es_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

formula = 'pass ~ raingarden + n + factor(me_score) + factor(pv_score) + factor(es_score)'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))
'''

# comparison to rpy2
rdata = analytical_set[['pass','n']]
rdata['intercept'] = 1.0
train_cols = rdata.columns[1:]
logit = sm.Logit(rdata['pass'], rdata[train_cols])
result = logit.fit()
print result.summary()

# extract summary object values ->
# http://stackoverflow.com/questions/16110715/getting-part-of-r-object-from-python-using-rpy2
print fit.names
z1 = s.rx2('deviance')[0]
z2 = s.rx2('null.deviance')[0]


