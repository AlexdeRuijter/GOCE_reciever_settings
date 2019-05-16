"""
This file hosts an function for precise interpolation. It takes in any two points, whether x, y, z or lon, lat:

The first two inputs have the format:
[[Y, M, D, H, min, sec], [position]]

The third only has the timeStamp as argument.

The return value is the timeStamp + the interpolated position
[[Y, M, D, H, min, sec], [Interpolated Position]]

This algorithm is made by Group AB-3 of the Faculty of Aerospace Engineering at TUD, 2018-2019
"""

import datetime

def dT(T1, T2):
    t1 = datetime.datetime(*T1)
    tdiff = datetime.datetime(*T2) - t1

    return tdiff.total_seconds()


def interpolate(Position_i1, Position_i2, inBetween):
    """
    This fuction takes 2 lon, lat, position vectors, a time in between those two, and returns the interpolated longitude and latitude.
    Both position vectors follow the format:
    [[Y, M, D, H, min, sec], [lon, lat]]
    
    The inBetween uses the format [Y, M, D, H, min, sec] too.
    The return value is formatted [timeStamp, [lon, lat]].
    """
    
    # Chain the timestamps together and calculate the delta t
    T1 = Position_i1[0][:5] + [int(Position_i1[0][5])] + [int((Position_i1[0][5]%1)*1000000)] 
    T2 = Position_i2[0][:5] + [int(Position_i2[0][5])] + [int((Position_i2[0][5]%1)*1000000)]
    dt = dT(T1, T2)

    # Do the same with longitude and latitude.
    ds = [i[1]- i[0] for i in zip(Position_i1[1], Position_i2[1])]
    
    # Calculate the "slope":
    ds_dt = [i/dt for i in ds]
    
    # Make the timeStamp for (inBetween) more precise:
    precise_Time = inBetween[:5] + [int(inBetween[5])] + [int((inBetween[5]%1)*1000000)]
    
    # Calculate the time since the first measurement passed till "inBetween"
    DeltaT = dT(T1, precise_Time)

    # Calculate the precise position at "inBetween":
    Position = [DeltaT* i[0] + i[1] for i in zip(ds_dt, Position_i1[1])]

    # Then return the [timeStamp, [lon, lat]]
    return [inBetween, Position]

if __name__ == "__main__":
    # Test case:
    T1 = [[2013, 9, 1, 21, 46, 27.0], [0, 0]]    
    T2 =[[2013, 9, 1, 21, 46, 28.0], [1, 1]]
    inBetween = [2013, 9, 2, 21, 46, 29.75]
    
    print(interpolate(T1, T2, inBetween))
    
