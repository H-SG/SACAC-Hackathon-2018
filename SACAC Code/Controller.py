def Controller(L, AMW, ABW, HU, GU):
    """AMW, ABW, HU, GU refering to previous time step values"""

    # Set relevant model parameters -------------------------------------------
    MWmax = 0.18
    BWmax = 0.1
    Lmax = 2.155
    Lmin = 0
    ## Set setpoint -----------------------------------------------------------
    sp = {"Emptier": 0.2, "Half-full": 0.5, "Fuller": 0.8}
    level = "Emptier"

    Lsp = sp[level] * Lmax

    ## Very simple controller -------------------------------------------------
    # If level too low: If AMW==1; MW = MWmax; Else BW = BWmax
    if L[0] < Lsp:
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
