import numpy as np
import math
import itertools

def cal_mis(r, c, x, x__r, x__c, x__r_c, rcx):

    I_X_R__C = 0.0
    I_X_C__R = 0.0
    I_X_R_C = 0.0
    results = {}

    for letter_x, letter_r, letter_c in itertools.product(x, r, c):

        val_rcx = rcx[(letter_r, letter_c, letter_x)] + np.finfo(float).eps
        val_x__r_c = x__r_c[(letter_x, letter_r, letter_c)] + np.finfo(float).eps
        val_x__c = x__c[(letter_x, letter_c)] + np.finfo(float).eps
        val_x__r = x__r[(letter_x, letter_r)] + np.finfo(float).eps
        val_x = x[letter_x] + np.finfo(float).eps

        temp_I_X_R__C = 0.0
        try:  # for ValueError: math domain error
            temp_I_X_R__C = val_rcx * math.log(val_x__r_c / val_x__c, 2)
        except:
            pass

        if not math.isnan(temp_I_X_R__C):
            I_X_R__C += temp_I_X_R__C

        # I(X;C|R)
        temp_I_X_C__R = 0.0  # slightly below
        try:
            temp_I_X_C__R = val_rcx * math.log(val_x__r_c / val_x__r, 2)
        except:
            pass

        if not math.isnan(temp_I_X_C__R):
            I_X_C__R += temp_I_X_C__R

        # I(X;R;C)
        temp_I_X_R_C = 0.0
        try:
            temp_I_X_R_C = val_rcx * math.log((val_x__r * val_x__c) / (val_x * val_x__r_c), 2)
        except:
            pass

        if not math.isnan(temp_I_X_R_C):
            I_X_R_C += temp_I_X_R_C

    results = {'I_X_R__C': I_X_R__C,
               'I_X_C__R': I_X_C__R,
               'I_X_R_C': I_X_R_C}

    return results


def cal_fun_met(r, c, functions_x, functions_x__r, functions_x__c,
                      functions_x__r_c, functions_rcx):

    functions = list(functions_rcx.keys())
    results = {}

    for function in functions:

        x = functions_x[function]
        x__r = functions_x__r[function]
        x__c = functions_x__c[function]
        x__r_c = functions_x__r_c[function]
        rcx = functions_rcx[function]

        results[function] = cal_mis(r, c, x, x__r, x__c, x__r_c, rcx)

    return results
