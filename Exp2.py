"""
This file currently only works on alex's laptop!

"""

# Import system modules:
import os
import collections as co
import itertools as it

# Import our own modules:
import ReadGPS as RG
import GeneratorSkip as GS
import ReadAllOrbit as RO
import preciseInterpolation as PI
import FindOffset as FO

# The functions used in this file:
def findPosition(Orbit, GPS_gen, index):
    # This function finds the exact interpolation for each value of the values of the residuals 
    # and yields those to be further used
    Orbit = GS.skip(Orbit, index)
    oldOrbit = [list(i) for i in next(Orbit)]
    print(oldOrbit[0], list(it.islice(GPS_gen, 1))[0][0])
    for orbits, GPS in zip(Orbit, GPS_gen):
        # Interpolate
        new = PI.interpolate(oldOrbit, orbits, GPS[0])
        
        # Add the extra necessary information
        new.append(GPS[1:])
        
        # And yield it!
        yield new
    
        # Save the latest entry
        oldOrbit = [list(i) for i in orbits]


def idxfinder(day):
    startTime = list(it.islice(day.process(), 1))[0][0]
    return tuple(FO.findOffset(allOrbit.process(), startTime))


def Parse():
    totalidx = 10801
    for day in GPSdays:
        print(totalidx, day.filename)
        for value in findPosition(allOrbit.process(), day.process(), totalidx):
            yield value
        totalidx += 86400


# The actual executed code!
# Load the orbitfiles:
allOrbit  = RO.AllFile()

# Load the GPSfiles:
path =  os.path.join(r"E:\GOCE", "GPS_nom")
GPSdays = [RG.GPSfile(filename, path) for filename in sorted(os.listdir(path))]

