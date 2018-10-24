# Team Dapper Strategy tank model for SACAC Hackathon 2018
# Assuming linear level and valve responses

import numpy as np
import scipy.optimize as op

TANK_VOLUME = 5.0       # m³
LEVEL = 0.5             # initial tank level fraction
LEAK_CONST = 0.0        # leakrate = leakconst*level
TOTAL_OVERFLOW = 0.0    # historic waste total
TOTAL_CONSUMP = 0.0     # historical total consumption of sources
SHORTFALL = False       # did the tank experience a water shortfall in the last step
OVERFLOW = False        # did the tank overflow in the last step

def stepTank(MW=0, AMW=1, BW=0, ABW=1, RW=0, HU=0, GU=0, updateLevel=True):
    """Perform one timestep of tank simulation.

    This will return a level reading, other parameters
    will be stored in global module vars.

    Keyword arguments:
    MW -- municipal water valve setting         (fraction)
    AMW -- municipal water current max supply   (m³/h)
    BW -- borehole water valve setting          (fraction)
    ABW -- borehole water current max supply    (m³/h)
    RW -- rainwater flow into tank              (m³/h)
    HU -- home usage                            (m³/h)
    updateLevel -- update global level var      (bool)
    """
    global LEVEL, TOTAL_CONSUMP, TOTAL_OVERFLOW, SHORTFALL, OVERFLOW
    
    TOTAL_CONSUMP += HU + GU
    accumulation = (MW*AMW + BW*ABW + RW) -\
                   (TOTAL_CONSUMP + LEVEL*LEAK_CONST)
    newVolume = TANK_VOLUME*LEVEL + accumulation

    if newVolume > TANK_VOLUME:
        TOTAL_OVERFLOW += TANK_VOLUME - newVolume
        SHORTFALL = False
        OVERFLOW = True
        newLevel = 1        
    elif newVolume < 0:
        SHORTFALL = True
        OVERFLOW = True
        newLevel = 0
    else:
        SHORTFALL = False
        OVERFLOW = False
        newLevel = newVolume/TANK_VOLUME

    if updateLevel:
        LEVEL=newLevel

    return newLevel

def tankVolumeEstimator(HMW=[1], HBW=[1], HHU=[1], HGU=[1], HLEVEL=[0.5], updateVolume=True):
    """Estimate tank volume from Historical data.
    Assumes no underflow, overflow or leakage

    Assuming one set of values is from the last hour, i.e. flows for
    last hour and level at end

    Keyword arguments:
    HMW -- historical municipal water usage     (array m³/h)
    HBW -- historical borehole water usage      (array m³/h)
    HHU -- historical home water usage          (array m³/h)
    HGU -- historical garden water usage        (array m³/h)
    HLEVEL -- historical tank level             (array m³/h)
    updateVolume -- upgate global volume var    (bool)
    """

    global TANK_VOLUME
    volGuess = 5

    # estimate average disturbance for measurement
    supply = np.array(HMW) + np.array(HBW)
    consumption = np.array(HHU) + np.array(HGU)
    disturbance = (sum(supply) - sum(consumption))/len(HMW)

    # get relevant changes
    tankChange = (supply - consumption) + disturbance
    tankChange = tankChange[1:]
    levelChange = HLEVEL[1:] - HLEVEL[:-1]

    def tankFunc(V):
        output = []
        for i in len(tankChange):
            out = V - tankChange[i]/levelChange[i]
            output.append(out)
        return output

    newVolume = op.fsolve(tankFunc, volGuess)

    if updateVolume:
        TANK_VOLUME = newVolume

    return newVolume
