import sys
sys.path.append('/Users/gregsilverman/development/python/rest_api/rest_api')
from extract import *

import rpy2.interactive as r
%load_ext rpy2.ipython
%R library(plyr)

# load in python/pandas dataframe
%R -i analytical_set
%R names(analytical_set)
%R names(analytical_set)[names(analytical_set)=="pass"] <- "no_inspect"

%R table(analytical_set$'no_inspect')

%R formula <- 'no_inspect ~ raingarden + n'
%R fit <- glm(formula, data=analytical_set, family=(binomial(link="logit")))
%R print(fit)
%R s <- summary(fit)
%R print(summary(fit))


# get pointer to file
%R source('utils.r')

R.plot(formula, data=r_analytical_set, ylab = 'P(outcome =  1 | pass)', xlab = 'N: number of times evaluated', xaxp = R.c(0, 5, 10))
#%R plot(formula, data=analytical_set, ylab = 'P(outcome =  1 | pass)', xlab = 'N: number of times evaluated', xaxp = c(0, 5, 10))
%R curve(invlogit(coef(fit)[1] + coef(fit)[2]*x), add = True)


