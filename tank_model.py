# Team Dapper Strategy tank model for SACAC Hackathon 2018
# Assuming linear level and valve responses

TANK_VOLUME = 5.0       # m³
LEVEL = 0.5             # initial tank level fraction
LMIN = 0.05             # minimum level setting
LMAX = 0.95             # maximum level setting
LEAK_CONST = 0.0        # leakrate = leakconst*level
TOTAL_OVERFLOW = 0.0    # historical waste total
TOTAL_SHORTFAL = 0.0    # historical total water shortfall
TOTAL_CONSUMP = 0.0     # historical total consumption of sources
SHORTFALL = False       # did the tank experience a water shortfall in the last step
OVERFLOW = False        # did the tank overflow in the last step

def stepTank(MW=0, MWMax=1, BW=0, BWMax=1, RW=0, HU=0, GU=0, updateLevel=True):
    """Perform one timestep of tank simulation and return new level.

    Other parameters will be stored in global module vars.

    Keyword arguments:
    MW -- municipal water valve setting         (fraction)
    MWMax -- municipal water max supply         (m³/h)
    BW -- borehole water valve setting          (fraction)
    BWMax -- borehole water current max supply  (m³/h)
    RW -- rainwater flow into tank              (m³/h)
    HU -- home usage                            (m³/h)
    updateLevel -- update global level var      (bool)
    """
    global LEVEL, TOTAL_CONSUMP, TOTAL_OVERFLOW, TOTAL_SHORTFAL,\
           SHORTFALL, OVERFLOW

    consumption = HU + GU
    TOTAL_CONSUMP += consumption
    accumulation = (MW*MWMax + BW*BWMax + RW) -\
                   (consumption + LEVEL*LEAK_CONST)
    newVolume = TANK_VOLUME*LEVEL + accumulation

    if newVolume > TANK_VOLUME*LMAX:
        TOTAL_OVERFLOW += newVolume - TANK_VOLUME*LMAX
        SHORTFALL = False
        OVERFLOW = True
        newLevel = LMAX
    elif newVolume < TANK_VOLUME*LMIN:
        TOTAL_SHORTFAL += TANK_VOLUME*LMIN - newVolume
        SHORTFALL = True
        OVERFLOW = False
        newLevel = LMIN
    else:
        SHORTFALL = False
        OVERFLOW = False
        newLevel = newVolume/TANK_VOLUME

    if updateLevel:
        LEVEL=newLevel

    return newLevel

def simTank(MW=[1], BW=[1], HU=[1], GU=[1], RW=[1], LInit=0.5):
    """Calculate total waste and underflow volumes for specified data

    Keyword arguments:
    MW --  municipal water usage     (array m³/h)
    BW --  borehole water usage      (array m³/h)
    HU --  home water usage          (array m³/h)
    GU --  garden water usage        (array m³/h)
    RW --  rainwater                 (array m³/h)
    LInit -- initial tank level      (fraction)
    """

    totOverflow = 0
    totUnderflow = 0
    totConsumption = 0

    for i in range(0, len(MW)):
        totConsumption += MW[i] + BW[i]

        tankBal = (MW[i] + BW[i] + RW[i]) - (HU[i] + GU[i])

        if not i:
            currLevel = LInit
        
        newVolume = TANK_VOLUME*currLevel + tankBal

        if newVolume > TANK_VOLUME*LMAX:
            currLevel = LMAX
            totOverflow += newVolume - TANK_VOLUME*LMAX
        elif newVolume < TANK_VOLUME*LMIN:
            currLevel = LMIN
            totUnderflow += TANK_VOLUME*LMIN - newVolume
        else:
            currLevel = newVolume/TANK_VOLUME

    return totOverflow, totUnderflow, totConsumption
