import math
import numpy as np
import scipy.signal as signal

#reads two lists of velocities and cross-correlates:
def cross_correlate(j1, j2):
    j1_j2_sum = 0
    j1_avg = mu(j1, 0, len(j1))
    j2_avg = mu(j2, 0, len(j2))
    for i in range(len(j1)):
        j1_j2_sum = j1_j2_sum + (
            (j1[i]-j1_avg)*(j2[i]-j2_avg)
        )
    j1_j2_sum = (1/(len(j1)))*j1_j2_sum
    #--------------------------------
    j1_sum = 0 
    for i in range(len(j1)):
        j1_sum = j1_sum + (
            (j1[i]-j1_avg)**2
        )
    j1_sum = (1/(len(j1)))*j1_sum
    #--------------------------------
    j2_sum = 0 
    for i in range(len(j2)):
        j2_sum = j2_sum + (
            (j2[i]-j2_avg)**2
        )
    j2_sum = (1/(len(j2)))*j2_sum
    #--------------------------------
    r = j1_j2_sum/(math.sqrt(j1_sum*j2_sum))

    return r

#reads a list of xs,ys and zs for ONE JOINT. Returns list of velocities
def velocity(xs, ys, zs):
    distances = np.empty(1)
    for i in reversed(range(0,len(xs)-1)):
        #sqd = ( (xs[i]-xs[i-1])**2 ) + ( (ys[i]-ys[i-1])**2 ) + ( (zs[i]-zs[i-1])**2 )
        dist = math.dist([xs[i], ys[i], zs[i]], [xs[i-1], ys[i-1], zs[i-1]])
        #dist = math.sqrt(sqd)
        distances = np.append(distances, dist)

    return np.flip(distances[1:]) * 1000

#data is a list of velocities
def skewness_of_velocity(data):
    #last_frame = last_frame-1
    avg = mu(data, 0, len(data))
    std = sigma(data, 0, len(data))
    skew = 0
    for i in range(0, len(data)):
        skew = skew + (data[i]-avg)**3
    
    r = ((1/(len(data)-0)) * skew) / (std**3)
    return r


def mu(v, init, last):
    sum=0
    for i in range(init,last):
        sum = sum + v[i]

    r = (1/(last-init)) * sum
    return r


def sigma(v, init, last):
    sum = 0
    avg = mu(v,init,last)
    for i in range(init,last):
        sum = sum + ((v[i] - avg)**2)
    r = math.sqrt(((1/(last-init))*sum))
    return r
