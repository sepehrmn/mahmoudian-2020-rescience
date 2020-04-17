import numpy as np
import math
import itertools

def cal_mis(R, C, X, X__R, X__C, X__R_C, RCX):

    I_X_R__C = 0.0
    I_X_C__R = 0.0
    I_X_R_C = 0.0

    for x, r, c in itertools.product(X, R, C):

        val_rcx = RCX[(r, c, x)] + np.finfo(float).eps
        val_x__r_c = X__R_C[(x, r, c)] + np.finfo(float).eps
        val_x__c = X__C[(x, c)] + np.finfo(float).eps
        val_x__r = X__R[(x, r)] + np.finfo(float).eps
        val_x = X[x] + np.finfo(float).eps

        # I(X;R|C)
        I_X_R__C += val_rcx * math.log(val_x__r_c / val_x__c, 2)

        # I(X;C|R)
        I_X_C__R += val_rcx * math.log(val_x__r_c / val_x__r, 2)

        # I(X;R;C)
        I_X_R_C += val_rcx * math.log((val_x__r * val_x__c) / (val_x * val_x__r_c), 2)

    results = {'I_X_R__C': I_X_R__C,
               'I_X_C__R': I_X_C__R,
               'I_X_R_C': I_X_R_C}

    return results


def cal_fun_met(R, C, functions_X, functions_X__R, functions_X__C,
                      functions_X__R_C, functions_RCX):

    functions = list(functions_RCX.keys())
    results = {}

    for function in functions:

        X = functions_X[function]
        X__R = functions_X__R[function]
        X__C = functions_X__C[function]
        X__R_C = functions_X__R_C[function]
        RCX = functions_RCX[function]

        results[function] = cal_mis(R, C, X, X__R, X__C, X__R_C, RCX)

    return results
