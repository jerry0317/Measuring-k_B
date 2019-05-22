# util.py - supporting modules for other scripts
#
# Note: This file is not intended to run independently.
#
# Created by Jerry Yan

# Module to securely prompt for a user input
def user_input(val_name, val_range = None, val_float = True):
    input_hold = True

    while(input_hold):
        try:
            val_d = input("Please enter the value of {}: ".format(val_name))
            if val_float is True:
                val_d = float(val_d)
                val_min = val_range[0]
                val_max = val_range[1]
                if val_d < val_min or val_d > val_max:
                    raise Exception("{} out of range.".format(val_name))
        except Exception as e:
            print(e)
            print("ERROR. Please try again.")
        else:
            input_hold = False
    print()
    print("{0} is set as {1}.".format(val_name, val_d))
    print()
    return val_d

# k_B calculation supporting modules
# Boltzmann constant (10^-23)
K_B = 1.38064852

# Avogadro constant (10^23)
N_A = 6.02214

# Experiment Constants
# DISTANCE = 1
MOLAR_MASS = 28.97 * 10 ** (-3)
GAMMA = 1.40

# Van der Waals Constants
VDW_A = 0
VDW_B = 0

# Experiment Error Constants
DIS_ERR_ABS = 0.0025
TT_ERR_ABS = 4.665306263360271e-07
TEMP_ERR_ABS = 0.125

def c_from_tt(tt, dis):
    c_sound = dis / tt
    return c_sound

def kb_from_tt(tt, temp, dis):
    c_sound = c_from_tt(tt, dis)
    kb = (c_sound ** 2) * MOLAR_MASS / (GAMMA * N_A * temp)
    return kb

# N2 VDW Approximation
def kb_from_tt_vdw_n2_aprx(tt, temp, dis):
    c_sound = c_from_tt(tt, dis)
    kb = ((c_sound ** 2) - 611) / (1.003 * 1.4 * temp) * (2.32586 * 2 * 10 ** -3)
    return kb

def err_from_tt_pct(tt, temp, dis):
    dis_err_pct = DIS_ERR_ABS / dis
    temp_err_pct = TEMP_ERR_ABS / temp
    tt_err_pct = TT_ERR_ABS / tt
    err_pct = 2 * (dis_err_pct + tt_err_pct) + temp_err_pct
    return err_pct

def err_from_tt_vdw_pct(tt, temp, pres, dis):
    dis_err_pct = DIS_ERR_ABS / dis
    temp_err_pct = TEMP_ERR_ABS / temp
    tt_err_pct = TT_ERR_ABS / tt
    err_pct = 2 * (dis_err_pct + tt_err_pct) + temp_err_pct
    return err_pct

def err_arr_gp(x_arr, data_arr, err_arr):
    if len(data_arr) != len(err_arr):
        return False
    else:
        up_arr = []
        low_arr = []
        seg_arr = []
        for i in range(0, len(data_arr)):
            x_p = x_arr[i]
            data_p = data_arr[i]
            err_p = err_arr[i]
            up_p = data_p + err_p
            low_p = data_p - err_p
            up_arr.append(up_p)
            low_arr.append(low_p)
            seg_arr.append([[x_p, low_p], [x_p, up_p]])

        return (low_arr, up_arr, seg_arr)
