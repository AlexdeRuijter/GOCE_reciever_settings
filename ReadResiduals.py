"""
This file stores an algorithm to open and read Residual files.
It outputs
[[Y, M, D, H, min, sec], 

This algorithm is made by Group AB-3 of the Faculty of Aerospace Engineering at TUD, 2018-2019
"""

# Import system modules:
import os

# Import our own modules:
import GeneratorSkip as GS

class residualFile:
    def __init__(self, filename, path):
        """
        This class handles the opening of .res-files.
        This class only needs the user to input the filename and the location of the file to come to exist.
        it outputs the data in the following format:

        [[Y, M, D, H, min, sec], 
        """
        self.filename = os.path.join(path, filename)

    def open(self):
        """
        Opens and reads the file, line by line, from the fifteenth line.
        As simple as that.
        """
        with open(self.filename, "r") as file:
            for line in file:
                yield line.split()


    def process(self):
        """
        Process the data! Use the following steps:
        1) Open the file, read it line by line.
        2) format the time.
        3) Add the rest of the line back to the timeStamp.

        """
        self.datapoints = self.open()
        
        for datapoint in self.datapoints:
            timeStamp = self.convertTime(datapoint)
            yield [timeStamp] + datapoint[2:]


    def averageSecond(self):
        """
        This function averages the noise residuals per second and returns them in the following format:
        [[Y, M, D, H, min, sec], average_noise]
        """
        # Second is to store the timestamp, annotating in which second we work
        Second = []

        # Take a line from the file. The time is already formatted and is entry[0]:
        for datapoint in self.process():

            # If the time has been annotated earlier.
            if Second:
                # If the second is equal to the previous annotation.
                if Second[5] == datapoint[0][5]:
                    # Add one to the counter and add the absolute value of the noise to 'noise'.
                    noise += abs(float(datapoint[-3]))
                    counter += 1
                else:
                    # If it is not equals, yield the data of the previous second and start over.
                    yield [Second, noise/counter]
                    counter = 1
                    noise = abs(float(datapoint[-3]))
                    Second = datapoint[0]
            else:
                # There has been no second yet, so denote the initial values:
                Second = datapoint[0]

                # Noise will store the summed absolute value of the noise per second, 
                # counter will store the amount of summed channels. 
                noise = abs(float(datapoint[-3]))
                counter = 1

        # The data has been cycled through, let's return the last value:
        yield [Second, noise/counter]
                    
            
    def convertTime(self, timeLine):
        """
        This function extracts the data from a single line in a .res file, and returns that:
        It follows the 'universal' time format:
        [Y, M, D, H, min, sec]
        """
        # First take the slashes and the colons out, and convert the first five values in integers:
        timeStamp = [int(i) for i in timeLine[0].split('/')] + [int(i) for i in timeLine[1].split(':')[:2]]

        # Add the last float, the seconds to the timeStamp:
        timeStamp += [float(i) for i in timeLine[1].split(':')[2:]]

        # Return the timeStamp:
        return timeStamp
        


# This will make sure it only runs when the file is run directly, not if it is imported.  
if __name__ == "__main__":
    # Change this to wherever the .res files are located on the PC.
    # In the dropbox, this will work fine.
    path = os.path.abspath(os.path.join(os.path.realpath(""), os.pardir,  "RES_nom"))

    # Create an object to read the file:
    day1 = residualFile("GOCE.13.246_RDOD24hr.res", path)
    
    
    # These are just some random things to do:
    # Let's iterate throught the file and print everything!
    for second in day1.averageSecond():
        print(second)

    # What is the maximum? Let's print it!
    print(max(day1.averageSecond(), key= lambda x: x[1]))
        

