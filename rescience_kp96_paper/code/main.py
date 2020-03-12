import itertools
import math
import random
import numpy as np
import scipy
from scipy.special import expit

import rescience_kp96_paper.code.params as params
import rescience_kp96_paper.code.analysis as analysis
import rescience_kp96_paper.code.plotting as plotting


# P(r|c)
def cal_x(x, r, c, rcx):

    for letter_x, letter_r, letter_c in itertools.product(x, r, c):
                x[letter_x] += rcx[(letter_r, letter_c, letter_x)]
    return x

# P(r|c)
def cal_r__c(r, c, rc):

    r__c = {}
    for letter_c, letter_r in itertools.product(c, r):
        r__c[(letter_r, letter_c)] = rc[(letter_r, letter_c)] / c[letter_c]
    return r__c

# P(c|r)
def cal_c__r(r, c, rc):

    c__r = {}
    for letter_r, letter_c in itertools.product(r, c):
            c__r[(letter_c, letter_r)] = rc[(letter_r, letter_c)] / r[letter_r]
    return c__r

# P(r,c,x)
def cal_rcx(r, c, x, rc, x__r_c):

    rcx = {}
    for letter_x, letter_c, letter_r in itertools.product(x, c, r):
        rcx[(letter_r, letter_c, letter_x)] = rc[(letter_r, letter_c)] * x__r_c[(letter_x, letter_r, letter_c)]
    functions_rcx[function] = rcx
    return rcx

# P(x|r)
def cal_x__r(r, x, rcx):
    xr = {}
    for letter_x, letter_r in itertools.product(x, r):
        xr[(letter_x, letter_r)] = rcx[(letter_r, 0, letter_x)] + rcx[(letter_r, 1, letter_x)]

    x__r = {}
    for letter_x, letter_r in itertools.product(x, r):
        x__r[(letter_x, letter_r)] = xr[(letter_x, letter_r)] / r[(letter_r)]

    return x__r


# P(x|c)
def cal_x__c(c, x, rcx):
    xc = {}
    for letter_x, letter_c in itertools.product(x, c):
        xc[(letter_x, letter_c)] = rcx[(0, letter_c, letter_x)] + rcx[(1, letter_c, letter_x)]

    x__c = {}
    for letter_x, letter_c in itertools.product(x, c):
        x__c[(letter_x, letter_c)] = xc[(letter_x, letter_c)] / c[(letter_c)]

    return x__c



if __name__ == '__main__':

    # number of results
    n_results = params.r_magnitudes.shape[0] * params.c_magnitudes.shape[0] * params.n_metrics * params.n_functions
    # It is OK to for convenience, put everything in one big structured array
    analytical_results = np.zeros(n_results, dtype=[('activation_function', 'S40'),
                                         ('information_metric', 'S40'),
                                         ('r', np.float),
                                         ('c', np.float),
                                         ('value', np.float)])

    # r_c, r_notc, notr_c, notr_not
    r_c = params.corr * params.c__r
    r_notc = params.corr * (1 - params.c__r)
    notr_c = params.corr * (1 - params.c__r)
    notr_notc = params.corr * params.c__r

    r = {0: notr_c + notr_notc, 1: r_c + r_notc}
    c = {0: r_notc + notr_notc, 1: r_c + notr_c}

    rc = {(0, 0): notr_notc, (0, 1): notr_c, (1, 0): r_notc, (1, 1): r_c}
    r__c = cal_r__c(r, c, rc)
    c__r = cal_c__r(r, c, rc)

    # looping over r and c magnitudes:
    idx = 0
    for rmag, cmag in itertools.product(params.r_magnitudes, params.c_magnitudes):

        # try:
        spiking_r = {0: params.not_firing_value * rmag, 1: params.firing_value * rmag}
        spiking_c = {0: params.not_firing_value * cmag, 1: params.firing_value * cmag}

        # Activation function 1: additive
        additive_x__r_c = {}
        for letter_rspike, val_rspike in spiking_r.items():
            for letter_cspike, val_cspike in spiking_c.items():

                val_additive = val_rspike + val_cspike
                additive_firing = expit(val_additive)
                additive_silent = 1 - additive_firing
                additive_x__r_c[(1, letter_rspike, letter_cspike)] = additive_firing
                additive_x__r_c[(0, letter_rspike, letter_cspike)] = additive_silent

        # Activation function 2: modulatory
        modulatory_x__r_c = {}
        for letter_rspike, val_rspike in spiking_r.items():
            for letter_cspike, val_cspike in spiking_c.items():

                #vals_modulatory = np.zeros(1,dtype=np.float128)
                vals_modulatory = 0.5 * val_rspike * (1 + np.exp(val_rspike * val_cspike))
                modulatory_firing = expit(vals_modulatory)
                modulatory_silent = 1 - modulatory_firing
                modulatory_x__r_c[(1, letter_rspike, letter_cspike)] = modulatory_firing
                modulatory_x__r_c[(0, letter_rspike, letter_cspike)] = modulatory_silent

        # Activation function 3: additive and modulatory
        both_x__r_c = {}
        for letter_rspike, val_rspike in spiking_r.items():
            for letter_cspike, val_cspike in spiking_c.items():

                vals_both = 0.5 * val_rspike * (1 + math.exp(val_rspike * val_cspike)) + val_cspike
                both_firing = expit(vals_both)
                both_silent = 1 - both_firing
                both_x__r_c[(1, letter_rspike, letter_cspike)] = both_firing
                both_x__r_c[(0, letter_rspike, letter_cspike)] = both_silent

        # Activation function 4: No Context
        nocontext_x__r_c = {}
        for letter_rspike, val_rspike in spiking_r.items():
            for letter_cspike, val_cspike in spiking_c.items():

                vals_nocontext = val_rspike
                nocontext_firing = expit(vals_nocontext)
                nocontext_silent = 1 - nocontext_firing
                nocontext_x__r_c[(1, letter_rspike, letter_cspike)] = nocontext_firing
                nocontext_x__r_c[(0, letter_rspike, letter_cspike)] = nocontext_silent

        # Generating probability distributions

        # P(x,r,c)
        functions_x__r_c = {'additive': additive_x__r_c,
                            'modulatory': modulatory_x__r_c,
                            'both': both_x__r_c,
                            'nocontext': nocontext_x__r_c}

        functions_x = {}  # P(x)
        functions_x__r = {}  # P(x|r)
        functions_x__c = {}  # P(x|c)

        functions_rcx = {}
        for function, x__r_c in functions_x__r_c.items():

            x = {0: 0, 1: 0}

            # P(r,c,x)
            rcx = cal_rcx(r, c, x, rc, x__r_c)

            # P(x)
            functions_x[function] = cal_x(x, r, c, rcx)

            # P(x|r)
            functions_x__r[function] = cal_x__r(r, x, rcx)

            # P(x|c)
            functions_x__c[function] = cal_x__c(c, x, rcx)

        # Calculating information theoretic metrics
        functions_metrics = analysis.cal_fun_met(r, c, functions_x, functions_x__r, functions_x__c,
                                                       functions_x__r_c, functions_rcx)

        for function, metrics in functions_metrics.items():
           for metric, value in metrics.items():
               analytical_results[idx] = (function, metric, rmag, cmag, value)
               idx += 1

    #plotting.plot_fig1(params.r_magnitudes, analytical_results)
    #plotting.plot_fig2(params.r_magnitudes, params.c_magnitudes, analytical_results)

    # FIGURE 3
    samples_array = np.arange(40, 1040, 40)

    simulation_results = {'I_X_R__C': np.zeros(samples_array.shape[0]),
                            'I_X_C__R': np.zeros(samples_array.shape[0]),
                            'I_X_R_C': np.zeros(samples_array.shape[0]),
                            'sd_I_X_R__C': np.zeros(samples_array.shape[0]),
                            'sd_I_X_C__R': np.zeros(samples_array.shape[0]),
                            'sd_I_X_R_C': np.zeros(samples_array.shape[0])}

    for steps_idx, n_steps in enumerate(samples_array):

        temp_I_X_R__C = np.zeros(params.n_trials)
        temp_I_X_C__R = np.zeros(params.n_trials)
        temp_I_X_R_C = np.zeros(params.n_trials)

        for trial_n in range(params.n_trials):

            r_seq = np.zeros((1, n_steps), dtype=np.int)[0]
            c_seq = np.zeros((1, n_steps), dtype=np.int)[0]
            x_seq = np.zeros((1, n_steps), dtype=np.int)[0]

            for i in range(n_steps):

                rn = np.random.rand()

                if rn < r_c:
                    r_seq[i] = 1
                    c_seq[i] = 1

                elif rn < (r_c + r_notc):
                    r_seq[i] = 1
                    c_seq[i] = -1

                elif rn < (r_c + r_notc + notr_c):
                    r_seq[i] = -1
                    c_seq[i] = 1

                else:
                    r_seq[i] = -1
                    c_seq[i] = -1

                # The magnitudes were set to 2 in the paper
                r_mag = 2.0 * r_seq[i]
                c_mag = 2.0 * c_seq[i]
                a_m = 0.5 * r_mag * (1 + np.exp(r_mag * c_mag))
                p_fir = expit(a_m)

                rn = np.random.rand()
                if p_fir > rn:
                    x_seq[i] = 1

            n = r_seq.shape[0]

            r = {0: np.where(r_seq == -1)[0].shape[0]/n,
                 1: np.where(r_seq == 1)[0].shape[0]/n}

            c = {0: np.where(c_seq == -1)[0].shape[0]/n,
                 1: np.where(c_seq == 1)[0].shape[0]/n}

            x = {0: 0, 1: 0}
            rcx = {}
            for letter_r, letter_c in itertools.product(r, c):

                alp_r = letter_r
                if alp_r == 0:
                    alp_r = -1

                alp_c = letter_c
                if alp_c == 0:
                    alp_c = -1

                rs = np.where(r_seq == alp_r)
                cs = np.where(c_seq == alp_c)
                xs = x_seq[np.intersect1d(rs, cs)]

                rcx[(letter_r, letter_c, 1)] = np.sum(xs == 1) / n
                rcx[(letter_r, letter_c, 0)] = np.sum(xs == 0) / n

            # P(r,c)
            for letter_r, letter_c in itertools.product(r, c):
                rc[(letter_r, letter_c)] = rcx[(letter_r, letter_c, 1)] + rcx[(letter_r, letter_c, 0)]

            #r__c = cal_r__c(r, c, rc)
            #c__r = cal_c__r(r, c, rc)

            # P(r,c,x)
            x__r_c = {}
            for letter_r, letter_c, letter_x in itertools.product(r, c, x):
                 x__r_c[(letter_x, letter_r, letter_c)] = rcx[(letter_r, letter_c, letter_x)] / rc[(letter_r, letter_c)]

            x = cal_x(x, r, c, rcx)

            # THE BELOW RESULT IS WRONG. FIND OUT WHY.
            x__r = cal_x__r(r, x, rcx)
            # P(x|c)
            x__c = cal_x__c(c, x, rcx)
            mis = analysis.cal_mis(r, c, x, x__r, x__c, x__r_c, rcx)
            temp_I_X_R__C[trial_n] = mis['I_X_R__C']
            temp_I_X_C__R[trial_n] = mis['I_X_C__R']
            temp_I_X_R_C[trial_n] = mis['I_X_R_C']

        simulation_results['I_X_R__C'][steps_idx] = np.average(temp_I_X_R__C)
        simulation_results['I_X_C__R'][steps_idx] = np.average(temp_I_X_C__R)
        simulation_results['I_X_R_C'][steps_idx] = np.average(temp_I_X_R_C)

        simulation_results['sd_I_X_R__C'][steps_idx] = np.std(temp_I_X_R__C)
        simulation_results['sd_I_X_C__R'][steps_idx] = np.std(temp_I_X_C__R)
        simulation_results['sd_I_X_R_C'][steps_idx] = np.std(temp_I_X_R_C)

    plotting.plot_fig3(samples_array, analytical_results, simulation_results)
