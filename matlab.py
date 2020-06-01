from __future__ import print_function
from __future__ import division
import numpy as np
import scipy as sp
import scipy.integrate

f = lambda x: x ** 2
print(sp.integrate.quad(f, 0, 2))
print(sp.integrate.fixed_quad(f, 0, 2))
