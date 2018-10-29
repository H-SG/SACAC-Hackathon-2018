def Controller(L, AMW, ABW, HU, GU):
    MWmax = 0.18
    BWmax = 0.1
    global tStep, bigEnd
    tStep += 1

    V = (2.155*4.641)
    L = L/2.155
    SP = 0.4
    ER  = SP - L[0]

    retMW = 0
    retBW = 0

    if ER > 0.05:
        if L[0] == 0:
            retMW = MWmax
            retBW = BWmax
        else:
            retMW = MWmax
    
    if (tStep > 8400):
        if L[0] > 0.75:
            bigEnd = True
        if bigEnd & (L[0] > 0):
            return 0, 0
        else:
            return retMW, retBW
    
    return retMW, retBW

tStep = 0
bigEnd = False
