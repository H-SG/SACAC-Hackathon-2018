import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio


from Controller import Controller
from TanksMassBalance import TanksMassBalance

## Load example, pre-allocate vectors
data = sio.loadmat("Example1")

ABW = data["ABW"][:, 0]
AMW = data["AMW"][:, 0]
GUreq = data["GUreq"][:, 0]
HUreq = data["HUreq"][:, 0]
RW = data["RW"][:, 0]
t = data["t"][:, 0]

N = 365 * 24

L = np.zeros(N + 1)
MWspec = np.zeros(N)
BWspec = np.zeros(N)
MW = np.zeros(N)
BW = np.zeros(N)
HU = np.zeros(N)
GU = np.zeros(N)
OF = np.zeros(N)

## Initialize model
# Tank is halfway full
L[:2] = 2.155 / 2
# No MW or BW specified or used
MW[0] = 0
BW[0] = 0
MWspec[0] = 0
BWspec[0] = 0

## Run model
def rotatein(ind, var, length):
    if ind <= length:
        retval = np.zeros(length)
        retval[:ind] = var[ind - 1 :: -1]
        return retval
    else:
        return var[ind - 1 : ind - length - 1 : -1]


history = 24
for ind in range(1, N):
    # Controller inputs
    Linput = rotatein(ind, L[1:], history)
    AMWinput = rotatein(ind, AMW, history)
    ABWinput = rotatein(ind, ABW, history)
    HUinput = rotatein(ind, HU, history)
    GUinput = rotatein(ind, GU, history)

    # Controller action
    MWspec[ind], BWspec[ind] = Controller(Linput, AMWinput, ABWinput, HUinput, GUinput)

    L[ind + 1], MW[ind], BW[ind], HU[ind], GU[ind], OF[ind] = TanksMassBalance(
        L[ind],
        RW[ind],
        AMW[ind],
        ABW[ind],
        MWspec[ind],
        BWspec[ind],
        HUreq[ind],
        GUreq[ind],
    )

# Trim level vector
L = L[:-1]

## Assess performance
cMW = 25
cBW = 60
cHU = 150
cGU = 70
J = (cMW * MW + cBW * BW + cHU * (HUreq - HU) + cGU * (GUreq - GU)).sum()

## Plots
# Disturbances
plt.figure()
plt.subplot(5, 1, 1)
plt.plot(RW)
plt.ylabel("RW")
plt.axis("tight")
plt.subplot(5, 1, 2)
plt.plot(HUreq)
plt.ylabel("HU_{req}")
plt.axis("tight")
plt.subplot(5, 1, 3)
plt.plot(GUreq)
plt.ylabel("GU_{req}")
plt.axis("tight")
plt.subplot(5, 1, 4)
plt.plot(AMW)
plt.ylabel("AMW")
plt.axis("tight")
plt.subplot(5, 1, 5)
plt.plot(ABW)
plt.ylabel("ABW")
plt.axis("tight")
plt.xlabel("Time step")

# Control results
plt.figure()
plt.subplot(5, 1, 1)
plt.plot(L)
plt.ylabel("L")
plt.axis("tight")
plt.subplot(5, 1, 2)
plt.plot(MW)
plt.ylabel("MW")
plt.axis("tight")
plt.subplot(5, 1, 3)
plt.plot(BW)
plt.ylabel("BW")
plt.axis("tight")
plt.subplot(5, 1, 4)
plt.plot(HUreq - HU)
plt.ylabel("\Delta HU")
plt.axis("tight")
plt.subplot(5, 1, 5)
plt.plot(GUreq - GU)
plt.ylabel("\Delta GU")
plt.axis("tight")
plt.xlabel("Time step")

print(J)
plt.show()
