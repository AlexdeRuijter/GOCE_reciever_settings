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

from datetime import datetime

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


def idxfinder(day, inher):
    if inher:
        if inher[0]:
            startTime = inher[0][0][0]
        else:
            startTime = list(it.islice(day.process(), 1))[0][0]
    else:
        startTime = list(it.islice(day.process(), 1))[0][0]

    return tuple(FO.findOffset(allOrbit.process(), startTime))


def Parse():
    ## The starting value of the first match:
    #totalidx = 10801

    # This is indeed the first time we start:
    first = True

    # There is no previous attendence:
    Att = None

    # There is no previous inheritance:
    inher = None
    
    for day in GPSdays:
        found, totalidx = idxfinder(day, inher)

        print(totalidx, day.filename)
                
        for value in findPosition(allOrbit.process(), day.countLosses(prevAtt = Att, noPrev = first, inheritance = inher), totalidx):
            yield value

        # Collect the Attendence schedule for the next day:
        Att = day.Att

        # It is simply not the first time anymore:
        first = False
        
        # Collect the inheritance for the next day:
        inher = day.inheritance        
        ##totalidx += inher[0][0][1]

def count():
    ## The starting value of the first match:
    #totalidx = 10801

    # This is indeed the first time we start:
    first = True

    # There is no previous attendence:
    Att = None

    # There is no previous inheritance:
    inher = None

    count = [0,0]
    
    for day in GPSdays:
        found, totalidx = idxfinder(day, inher)

        print(totalidx, day.filename)
                
        for value in day.countLosses(prevAtt = Att, noPrev = first, inheritance = inher):
            pass

        count[0] += day.nonzeroL1
        count[1] += day.nonzeroL2

        # Collect the Attendence schedule for the next day:
        Att = day.Att

        # It is simply not the first time anymore:
        first = False
        
        # Collect the inheritance for the next day:
        inher = day.inheritance        
        ##totalidx += inher[0][0][1]

    exp = [0,0]
    for L in range(2):
        for key in Att[L].keys():
            exp[L] += sum((end- begin + 1 for (begin, end) in Att[L][key]))

    print(" The nonzero values:  {}".format(count))
          
    print(" The unexpected losses: {}".format(exp))
    return count, exp

             


## The actual executed code!
# Load the orbitfiles:
allOrbit  = RO.AllFile()

# Load the GPSfiles:
path =  os.path.join(r"E:\GOCE", "GPS_nom")
GPSdays = [RG.GPSfile(filename, path) for filename in sorted(os.listdir(path))]

