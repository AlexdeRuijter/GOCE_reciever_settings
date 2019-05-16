import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from math import*
from matplotlib.lines import Line2D
import mpl_toolkits.axes_grid1 
import mpl_toolkits.axisartist
from matplotlib import colors
import matplotlib.patches as patches
import matplotlib as mpl

plt.rcParams.update({'font.size': 17})

import Exp3 as EX3

def rawData():
    for line in EX3.Parse():
        if len(line) > 3:
            print(line)
        else:
            binfinder(line)
    
    with open("GPSmap.txt", "w+") as file:
        for A in bins:
            file.write(str(A)+ "\n")


def openFile():
    with open("GPSmap.txt", "r") as file:
        C = []
        for line in file:
            C.append(eval(line))
    return C


def binfinder(entry): #Making bins
    time,[lon, lat], [L1,L2] = entry
    if lon > 0:
        lon += 1.
    if lat > 0:
        lat += 1
    #if abs(lat) > 89 or abs(lon) > 179:
    #    print(time, lon, lat, L1, L2)
    bins[int(lat)+89][int(lon)+179].append([L1, L2,[0]])

print("hey")
#g = listFile('Nominal_Residuals_Locations_Matched_days_16-30')#Data file 2


#f and g contain the matched up locations and noise residuals.
#they have to be binned into bins of 1 by 1 degree bins (longitude and latitude)

bins = [[[]for i in range(-180,180)]for j in range(-90,90)]
#latitude    == g[i][2][0]
#longitude   == g[i][2][1]
#residuals   == g[i][1]
print("hi!")


#line = rawData()
bins = openFile()
print(':)')
print('50%')
#for i in range(len(g)):
 #   binfinder(g[i])
maximum = 0
minimum = 1
for idxi,A in enumerate(bins):
    for idxj,B in enumerate(A):
        if B:
            count=0
            for i in B:
                count+=len(i[0])
            #if count > 200:
             #   count = 200
            bins[idxi][idxj] = count
            if count > maximum:
                maximum = count
            elif count < minimum:
                minimum = count
        else:
            bins[idxi][idxj] = 0
x = []
y = []
for i in range(-180,181):
    x.append(i)
for i in range(-90,91):
    y.append(i)
x,y     = np.meshgrid(x,y)
bins    = np.array(bins)

Iter=[]

coastline_data= np.loadtxt('Coastline.txt',skiprows=1)
# print(coastline_data)
w, h = plt.figaspect(0.5)
fig = plt.figure(figsize=(w,h))
plt.xlim(-180,180)
plt.ylim(-90,90)
plt.yticks([-90,-80,-70,-60,-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90])
plt.xticks([-180,-150,-120,-90,-60,-30,0,30,60,90,120,150,180])
plt.plot(coastline_data[:,0],coastline_data[:,1],'k')
#plt.title('Tracking Losses locations on L1 nom frequency')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

plt.pcolormesh(x, y, bins,cmap = 'rainbow', vmax = 300)
plt.colorbar(orientation = "horizontal")
plt.show()
