"""
This python file stores an algorithm to read .IDF-files, and outputs useful data.
This data is a second-based interpolated longitude and latitude in the format:
[[Y, M, D, H, min, sec], [lon, lat]]

This algorithm is made by Group AB-3 of the Faculty of Aerospace Engineering at TUD, 2018-2019
"""

# Import system modules:
import math as mt
import numpy as np
import os
import itertools as it

# Import our own modules: 
import GeneratorSkip as GS

class orbitFile:
    def __init__(self, filename, path):
        """
        This class-object handles the opening of .IDF-files.
        This class object only needs the filename and the location of the file to come to exist.
        It will return the values one by one if you enter: 
        
        day = orbitFile(filename)
        for second in day.process():
            do_something_with(second)

        The results you get from second are
        [[Y, M, D, H, min, sec], [lat, lon]]
        """
        self.filename = os.path.join(path, filename)

    
    def open(self):
        """
        Opens the file, reads it, and evaluates if the index of the line is below 29544, and if the line starts with * or P,
        Only then will it actually yield some values.
        """
        with open(self.filename, 'r') as file:
            for idx, line in enumerate(GS.skip(file, 22)):
                if (line.startswith("*") or line.startswith("P")): # and idx < 25945:
                    yield line.split()
                

    def process(self):
        """
        How are we going to process the file?
        1) Open it, read it line by line, only the lines 22 to 25994.
        2) Format the data in blocks of 1 second.
        3) Keep the data of 1 second ago in memory
        4) Interpolate if there is a previous second.
        5) Translate x,y,z to lon, lat 
        6) Profit!
        """
        # 1
        self.datapoints = self.open()
        
        self.measurements = []      
        listIndex = 0
        # 2
        for measurement in self.chainData():
            listIndex += 1

            # 3
            self.measurements.append(measurement)
            
            # 4.1
            if listIndex > 1:                
                # 4.2
                for [time, [x,y,z]] in self.interpolate():
                    self.x, self.y, self.z = x,y,z

                    # 5
                    self.translate()
                    
                    # 6
                    yield [time, [self.lon, self.lat]]
                
                # Delete the oldest second, so there are always just two in memory    
                self.measurements.pop(0)


    def interpolate(self):
        """
        This function interpolates between the two points in time 10 second apart. 
        It calculate the gradient of the ten steps to be taken and then one by one returns these values.
        """
        interList = self.measurements

        oldTime   = interList[0][0]
        oldPos    = np.array(interList[0][1])
        newPos    = np.array(interList[1][1])

        diffPos   = (newPos - oldPos)/10
        diffTime  = oldTime

        for i in range(10):
            Pos = list(oldPos + i* diffPos)

            yield [diffTime, Pos]
            
            diffTime[5] +=  1


    def chainData(self):
        """
        This function takes the seperate lines, and forms one second-blocks.
        Also it makes formats the time/ position stamps, it returns them one by one.
        """
        counter = 0

        for datapoint in self.datapoints:
            if datapoint:
                if not counter:
                    time = self.timeStamp(datapoint)
                else:
                    position = self.positionStamp(datapoint)
                counter += 1
                counter %= 2

                if counter == 0:
                    yield [time, position]

    
    def timeStamp(self, timeLine):
        """
        This is a function exlusively for formatting the timestamp.
        The function returns [Y, M, D, H, min, sec].
        """
        return [int(i) for i in timeLine[1:-1]]+ [float(timeLine[-1])] 
    
    
    def positionStamp(self, positionLine):
        """
        This function is exlusively for mapping the x,y,z positionstamp.
        It returns [x, y, z].
        """
        return [float(i) for i in positionLine[1:-1]]

    
    def translate(self):
        """
        This is a shorter version of the function written by Dimitri.
        It converts x,y,z to longitude and latitude.
        """
        # Convert the x, y, z from km to m and store them in the object.
        x, y, z = self.x * 10**3, self.y * 10**3, self.z * 10**3

        # Constants of the WGS84 model.
        a = 6378137;                                                                    
        f = 1/298.257223563                                                            
        e = mt.sqrt(1 - (1 - f) ** 2)

        # Constants calculated with these initial constants.
        b   = a**2 *(1 - e**2)
        ep  = mt.sqrt((a*a - b)/b)
        p   = mt.sqrt(x*x + y*y)
        th  = mt.atan2(a*z, mt.sqrt(b)*p)

        # Then calculate the lon and lat:
        self.lon = mt.atan2(y,x)                                               *(180/mt.pi)                                                              # Longitude (radians)
        self.lat = mt.atan2((z+ep**2*mt.sqrt(b)*mt.sin(th)**3),(p-e**2*a*mt.cos(th)**3))*(180/mt.pi)


# This will make sure it only runs when the file is run directly, not if it is imported.        
if __name__ == "__main__":
    orbit = orbitFile("Hay", "jlkdjo")
    orbit.x, orbit.y, orbit.z = [-5000, 1670, 3722]
    orbit.translate()
    
