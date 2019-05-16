"""
Warning, this file is not finished yet!
Proceed on own risk.
"""

# Import system modules:
import os 
import collections as co
import itertools as it

# Import our own modules:
import ReadResiduals as RR
import GeneratorSkip as GS
import ReadOrbit as RO
import preciseInterpolation as PI
import FindOffset as FO

# The functions used in this file:
def findPosition(Orbit, Residual):
    # This function finds the exact interpolation for each value of the values of the residuals 
    # and yields those to be further used
    oldOrbit = []
    for orbits, residuals in zip(GS.skip(Orbit, index), Residual):
        if oldOrbit:
            new = PI.interpolate(oldOrbit, orbits, residuals[0])
            new.append(residuals[1])
            yield new
    
        # Save the latest entry
        oldOrbit = [list(i) for i in orbits]


# First part, loading the files:
# Where are the residuals:
residualpath = os.path.abspath(os.path.join("", os.pardir, "RES_nom"))
residualfile = "GOCE.13.246_RDOD24hr.res"

# Where are the orbit files:
orbitpath = os.path.abspath(os.path.join("", os.pardir, "Orbit_data"))
orbitfile = "orbitFile.IDF"

# Create the orbit and residual objects to load the respective files:
orbit = RO.orbitFile(orbitfile, orbitpath)
residual = RR.residualFile(residualfile, residualpath)


# Second part, find how many we have to skip to find matching seconds.
# Orbit = orbitData:
Orbit = orbit.process()

# Residual = residualData:
Residual = residual.averageSecond()
tResidual = list(it.islice(Residual, 1))[0][0]

# Check if theres overlap between the two files:
found, index = FO.findOffset(Orbit, tResidual)


# Finally, match the values found to each other and compute the actual location of the residual:
# Reset the value of Orbit:
Orbit = orbit.process()

# If there is overlap:
if found:
    # Compute the actual position on the globe:
    residualPosition = findPosition(Orbit, Residual)

# Else:
else:
    print("There is no overlap.")

