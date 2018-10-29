import numpy


def TanksMassBalance(Lnow, RW, AMW, ABW, MWspec, BWspec, HUreq, GUreq):
    # Set model parameters ----------------------------------------------------
    # Area of tanks
    A = 4.641
    MWmax = 0.18
    BWmax = 0.1
    Lmax = 2.155
    Lmin = 0
    
    ## Availability conditions ------------------------------------------------
    # If MW and BW are not available (AMV, ABW = 0) then the MW and BW flows
    # will be zero, otherwise MW and BW are as specified by the controller
    MW = AMW * MWspec
    BW = ABW * BWspec
    
    ## Maximum flow -----------------------------------------------------------
    # If MW and BW are set larger than physically possible, set to given
    # maximum and minimum values.
    MW = min(MW, MWmax)
    BW = min(BW, BWmax)
    
    ## Minimum flow -----------------------------------------------------------
    # MW and BW have to be positive values, i.e. larger than 0 as there cannot
    # be a negative flow from the tanks to the municipal or borehole line
    MW = max(MW, 0)
    BW = max(BW, 0)

    ## Try: Calculate new level with HUreq and GUreq --------------------------
    HU = HUreq
    GU = GUreq
    # Time step = 1 hour as flowrates are specified in m3/h -------------------
    Lnext_temp = Lnow + (1 / A) * (RW + MW + BW - HU - GU)
    
    # Check for overflow ------------------------------------------------------
    Lnext = min(Lnext_temp, Lmax)
    if Lnext != Lnext_temp:
        OF = A * (Lnext_temp - Lmax)  # Overflow rate, to waste water line
    else:
        OF = 0

    # Check for tank empty condition ------------------------------------------
    if Lnext < Lmin:
        # Allocate HU and GU in ratio of requirement
        fHU = HUreq / (HUreq + GUreq)
        fGU = 1 - fHU
        # Available water
        TU = (Lnow - Lmin) * A
        # Distribute
        HU = TU * fHU
        GU = TU * fGU
        # No water left over; tank empty
        Lnext = Lmin

    return Lnext, MW, BW, HU, GU, OF
