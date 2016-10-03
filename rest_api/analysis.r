import sys
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')
from extract import *

# as per http://blog.yhat.com/posts/logistic-regression-and-python.html
analytical_set.describe()
pd.crosstab(analytical_set['pass'], analytical_set['es_score'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['me_score'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['pv_score'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['raingarden'], rownames=['pass'])
pd.crosstab(analytical_set['pass'], analytical_set['n'], rownames=['pass'])
analytical_set[['es_score', 'me_score', 'pv_score', 'vi_score', 'dn_score', 'score', 'raingarden', 'n', 'pass']].hist()

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

# move analysis over to R
import pandas.rpy.common as com
import rpy2.robjects as ro
R = ro.r

r_analytical_set = com.convert_to_r_dataframe(analytical_set)
print r_analytical_set
print type(r_analytical_set)

formula = 'pass~raingarden'
fit = R.glm(formula=R(formula), data=r_analytical_set,   family=R('binomial(link="logit")'))
s = R.summary(fit)
print(fit)
print(R.summary(fit))

from rpy2.robjects import Formula
#rplot = R('plot')
formula = Formula('pass~raingarden')
formula.getenvironment()['pass'] = r_analytical_set.rx2('pass')
formula.getenvironment()['n'] = r_analytical_set.rx2('n')
R.plot(formula, data=r_analytical_set, ylab = 'P(outcome =  1 | pass)', xlab = 'N: number of times evaluated', xaxp = R.c(0, 5, 10))

#with open('/Users/gregsilverman//development/python/rest_api/rest_api/utils.r', 'r') as f:
#    string = f.read()

#from rpy2.robjects.packages import STAP
#invlogit = STAP(string, "invlogit")

R('invlogit <- function(x){ exp(x)/(1 + exp(x)) }')
R('curve(invlogit({0} + {1}*x), add = TRUE)'.format(R.coef(fit)[0],R.coef(fit)[1]))

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
rdata = analytical_set[['pass','raingarden','n']]
rdata['intercept'] = 1.0
train_cols = rdata.columns[1:]
logit = sm.Logit(data['pass'], rdata[train_cols])
result = logit.fit()
print result.summary()

# extract summary object values ->
# http://stackoverflow.com/questions/16110715/getting-part-of-r-object-from-python-using-rpy2
print fit.names
z1 = s.rx2('deviance')
z2 = s.rx2('null.deviance')


