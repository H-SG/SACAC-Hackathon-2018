import os
import pickle
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def get_integral_limits():
    return [-1, 1]

def getController(maximum_municipal_water):
    max_mw = 0.1 + 0.18

    # New Antecedent/Consequent objects hold universe variables and membership
    # functions
    # f_tank_level = ctrl.Antecedent(np.arange(0, 1, 0.01), 'level')
    integral_limits = get_integral_limits()

    f_tank_error = ctrl.Antecedent(np.arange(-0.2, 0.2, 0.01), 'level_error')
    f_tank_error_sum = ctrl.Antecedent(np.arange(integral_limits[0], integral_limits[1], 0.001), 'level_error_sum')

    # f_rain_water = ctrl.Antecedent(np.arange(0, limits['RW'][1], 0.001), 'rain_water')
    # f_house_usage = ctrl.Antecedent(np.arange(0, limits['HU'][1], 0.001), 'house_usage')
    # f_garden_usage = ctrl.Antecedent(np.arange(0, limits['GU'][1], 0.001), 'garden_usage')

    # f_municipal_water = ctrl.Consequent(np.arange(0, limits['MW'][1], 0.001), 'municipal_water')
    # f_bore_hole_water = ctrl.Consequent(np.arange(0, limits['BW'][1], 0.001), 'bore_hole_water')
    f_water_needed = ctrl.Consequent(np.arange(0, max_mw, 0.001), 'water_needed')

    # Auto-membership function population is possible with .automf(3, 5, or 7)
    # f_tank_level.automf(3)
    f_tank_error.automf(3)
    f_tank_error_sum.automf(3)

    # f_rain_water.automf(3)
    # f_house_usage.automf(3)
    # f_garden_usage.automf(3)
    # f_municipal_water.automf(3)
    # f_bore_hole_water.automf(3)

    # Special function to ensure better(?) action
    f_water_needed['poor'] = fuzz.gaussmf(f_water_needed.universe, 0, max_mw/500)
    f_water_needed['average'] = fuzz.gaussmf(f_water_needed.universe, max_mw/1.9, max_mw/8)
    f_water_needed['good'] = fuzz.gaussmf(f_water_needed.universe, max_mw, max_mw/5)
    f_water_needed['just_a_bit'] = fuzz.gaussmf(f_water_needed.universe, max_mw/1.2, max_mw/50)
    f_water_needed['very_high'] = fuzz.gaussmf(f_water_needed.universe, max_mw, max_mw/500)

    f_tank_error['poor'] = fuzz.gaussmf(f_tank_error.universe, -0.2, 0.02)
    f_tank_error['average'] = fuzz.gaussmf(f_tank_error.universe, 0, 0.05)
    f_tank_error['good'] = fuzz.gaussmf(f_tank_error.universe, 0.1, 0.02)
    f_tank_error['very_high'] = fuzz.gaussmf(f_tank_error.universe, 0.2, 0.02)

    # f_tank_error_sum['poor'] = fuzz.gaussmf(f_tank_error_sum.universe, integral_limits[0], integral_limits[1]/5)
    # f_tank_error_sum['average'] = fuzz.gaussmf(f_tank_error_sum.universe, 0, integral_limits[1]/5)
    # f_tank_error_sum['good'] = fuzz.gaussmf(f_tank_error_sum.universe, integral_limits[1], integral_limits[1]/5)

    neg_error = 'poor'
    pos_error = 'good'
    small_error = 'average'

    lo = 'poor'
    med = 'average'
    hi = 'good'

    # probable need input weighting based on available resource
    rule_highest_error = ctrl.Rule(f_tank_error['very_high'], f_water_needed[hi])
    rule_high_error = ctrl.Rule(f_tank_error[pos_error], f_water_needed['just_a_bit'])
    rule_low_error = ctrl.Rule(f_tank_error[neg_error], f_water_needed[lo])
    rule_slight_error = ctrl.Rule(f_tank_error[small_error], f_water_needed[lo])

    rule_for_integral_error_pos = ctrl.Rule(f_tank_error_sum[pos_error], f_water_needed[med])
    rule_for_integral_error_neg = ctrl.Rule(f_tank_error_sum[neg_error], f_water_needed[lo])
    rule_for_integral_error_small = ctrl.Rule(f_tank_error_sum[small_error], f_water_needed[lo])

    base_ctrl = ctrl.ControlSystem([
        rule_high_error, 
        # rule_low_error, 
        # rule_slight_error, 
        rule_for_integral_error_pos,
        # rule_for_integral_error_neg,
        # rule_for_integral_error_small,
        rule_highest_error
    ])

    base = ctrl.ControlSystemSimulation(base_ctrl)
    return base

def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
        
def load_object(filename):
    with open(filename, 'rb') as input:  # Overwrites any existing file.
        obj = pickle.load(input)
    return obj

def save_or_load(filename, max_ww):
    if os.path.exists(filename):
        obj = load_object(filename)
    else:
        obj = getController(max_ww)
        save_object(obj, filename)
    return obj


def Controller(L, AMW, ABW, HU, GU, counter=1):

    """AMW, ABW, HU, GU refering to previous time step values
    AMW     -> available municipal water
    ABW     -> available borehole water
    HU      -> house usage
    GU      -> garden usage
    """

    # Set relevant model parameters -------------------------------------------
    sp = {"Emptier": 0.2, "Half-full": 0.5, "Fuller": 0.8}
    level = "Fuller"
    Lsp = sp[level]
    Lsp = 0.4

    MWmax = 0.18
    BWmax = 0.1
    Lmax = 2.155
    Lmin = 0

    if False:
        if L[0]/Lmax < Lsp:
            if AMW[0] == 1:
                MWspec = MWmax
                BWspec = 0
            else:
                MWspec = 0
                BWspec = BWmax
        else:
            MWspec = 0
            BWspec = 0
        return MWspec, BWspec

    try:
        ## Set setpoint -----------------------------------------------------------
        sp = {"Emptier": 0.2, "Half-full": 0.5, "Fuller": 0.8}

        # if np.mean(HU) > 0.

        level_normalised = L[0]/Lmax * 1

        level_error = Lsp - level_normalised
        # print(level_error)

        base = save_or_load('my_fuzzy_controller.pkl', MWmax)
        # base = getController(MWmax)

        sum_error = 0
        for l in L[::-1]:
            sum_error += Lsp - l/Lmax
        # sum_error = sum_error if sum_error > -0.05 else -0.05
        # sum_error = sum_error if sum_error < 0.05 else 0.05

        base.input['level_error'] = level_error
        integral_limits = get_integral_limits()

        # print('Before: ', level_normalised, sum_error)
        sum_error = integral_limits[0] * 2 if sum_error < integral_limits[0] * 2 else sum_error
        sum_error = integral_limits[1] * 2 if sum_error > integral_limits[1] * 2 else sum_error
        # print('After: ', level_normalised, sum_error)
        # print('----------------')
        # print(L)
        # print('----------------')

        base.input['level_error_sum'] = sum_error
        # print(sum_error)
        base.compute()

        total_water_needed = base.output['water_needed']

        # add a bit for expected use
        # total_water_needed += np.mean(HU) * 0.3

        # silly assumption of availability
        avail_mw = np.mean(AMW) * BWmax
        avail_bw = np.mean(ABW) * MWmax

        if total_water_needed < avail_mw:
            MWspec = total_water_needed 
            BWspec = 0
        else:
            MWspec = MWmax
            BWspec = total_water_needed - MWmax

        # make everything less if we are above setpoint
        # print('Level erro: ', Lsp, L[0], level_error)
        if level_error < 0.05:
            MWspec *= 0
            BWspec *= 0

        V = (2.155*4.641)
        if L[0] * V < 0.05 * V:
            return MWmax, BWmax

        return MWspec, BWspec
    except Exception as e:
        if os.path.exists('my_fuzzy_controller.pkl'):
            os.remove('my_fuzzy_controller.pkl')
            raise e
