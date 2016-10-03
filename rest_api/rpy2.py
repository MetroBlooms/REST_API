from numpy import *
import scipy as sp
from pandas import *
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import pandas.rpy.common as com

# 8261 assignment 1

#2
ro.r('y = c(3, 10, 5, 9, 7, 12)')
ro.r('sum(y)')

#3
ro.r('x = c(10, 10, 10, 10)')
ro.r('sum(x)')

#5
ro.r('x = c(7, 4, 10)')
ro.r('y = sum(x)')
ro.r('10*y')

#6
ro.r('y = 10*x')
ro.r('sum(y)')

#8
ro.r('z=c(2,7,4)')
ro.r('sum(z^2)')

#10
ro.r('sum(z*x)')

#11
ro.r('sum(z^2*x^2)')

#12
ro.r('N = length(y)')
ro.r('y.bar = sum(y)/N')
ro.r('mean(y)')

#15
ro.r('y.diff = y-y.bar')
ro.r('sum(y.diff)')

#18
ro.r('y')
ro.r('mean(r)')
ro.r('sum((y-mean(y))^2)')
ro.r('sum((y-mean(y))^2)/(length(y)-1)')

#20

ro.r('x = c(7, 4, 10)')
ro.r('z = c(2, 7, 4)')
ro.r('sum(x)*sum(z)')
ro.r('sum(x*z)')