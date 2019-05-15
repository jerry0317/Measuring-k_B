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
