"""
This file stores an algorithm to open and read GPS files.
It outputs searches for errors, notes down the PRNs of the sattelites which have erred, per second in the following format:
[[Y, M, D, H, min, sec], [Errors in L1], [Errors in L2]]

This algorithm is made by Group AB-3 of the Faculty of Aerospace Engineering at TUD, 2018-2019
"""

# Import system modules:
import re
import os

# Import our own modules:
import GeneratorSkip as GS


class GPSfile:
    def __init__(self, filename, path):
        """
        In this part of the class, you can declare initial values and stuff, like the filename.
        Note that every function inside the class gets the value 'self' so if you state 'self.varname = blablabla',
        'varname' can be accessed from every function in the class, by stating 'self.varname'...
        If you don't state self., the variable will stay inside the function.
        Also, functions must be called like: 'self.funcName()' because they are 'Class Functions'.
        
        This class handles the opening of .13o-files.
        This class only needs the user to input the filename and the location of the file to come to exist.
        It will return the [Timestamp, [Faults in L1],  [Faults in L2]] by doing the following:

        day = GPSfile(filename)
        for second in day.process():
            print(second)

        """
        self.filename = os.path.join(path, filename)

    def open(self):
        """
        Opens and reads the file, line by line, from the fifteenth line.
        As simple as that.
        """
        with open(self.filename, 'r') as file:
            for line in GS.skip(file, 15):
                yield line.split()

    def process(self):
        """
        Process the data! This happens in multiple steps:
        1) Read the file! (line by line)
        2) No disturbine the turbine.
        3) Format the data in 1-second blocks, with the format:
            [[Timestamp], [PRNs], [Data from L1], [Data from L2]]
        4)  ==> [[Timestamp], [Error PRN L1], [Error PRN L2]]
        5) Done!
        """
        # 1
        self.lines = self.open()

        # 3
        for second in self.linehandler():
            # print(second)

            # 4
            processed = self.FaultyPRN(second)
            print(processed)

            # 5
            yield processed

    def FaultyPRN(self, secondData):
        """ 
        This function calls out the error in the ways of the PRN.
        It does this for every second apart, where the second is encoded int the format given:
        [[Timestamp], [PRNs], [L1: 1/ null], [L2: 1/null]]
        The function outputs the following:
        [[Timestamp], [L1: Faulty PRNs], [L2: Faulty PRNs]]
        """
        # SHERMAN EDIT: Turned off L2 track as test case for L1 since L1 is more robust.
        L1 = [int(i[0]) for i in zip(secondData[1], secondData[2]) if i[1]]
        L1S = [int(i) for i in secondData[1]]
        # L2 = [int(i[0]) for i in zip(secondData[1], secondData[3]) if i[1]]

        # Returns: Date, Time, and the PRN in which the error occurs.
        # If  there is no such PRN,  return an empty set instead. []
        return [secondData[0], L1S, L1]

    def linehandler(self):
        """
        This function splits all the data in parts with the lenght of a second and returns these one after oneother.
        The data is returned in list form: 
        [ [Y, M, D, H, min, sec], [PRNs], [[L1, error]], [[L2, error]] ]
        """
        secondOfData = [[], [], [], []]

        for line in self.lines:
            # Seperate the header from the rest
            if not '.' in line[0]:

                # Check whether we already have some data from the previous header to parse:
                # If so, do that before we go on.
                if secondOfData[0]:
                    yield secondOfData
                    secondOfData = [[], [], [], []]

                timeStamp, PRNs = self.header(line)
                secondOfData[0] = timeStamp
                PRNs = [int(x) for x in PRNs]
                secondOfData[1] = PRNs

                counter = 0

            else:
                # If the line is even, the line is long.
                # Else, just skip it, we only like the long guys.
                if not counter % 2:
                    L1, L2 = self.frequencyLine(line)

                    # Append the fitting values to the second of data.
                    # In the right place...
                    secondOfData[2].append(L1)
                    secondOfData[3].append(L2)

                # Add one to the counter:
                counter += 1

        # That was the last line, so let's return the final values.
        print(secondOfData)
        yield secondOfData

    def header(self, headerLine):
        """ 
        Chop up the headerline!
        This function does literally that.
        It converts the header into a list of PRNs and Timestamp.
        """

        # The date-time signaturer consists of the first 6 elements of the header.
        time = [int(x) for x in headerLine[:5]] + [float(headerLine[5])]

        # The PRNs are actually only the values from 8 to the second last.
        # Sometimes, when more than 11 PRNs, the last one should be split
        # From that split, we append first part to the PRNs.

        PRNs = headerLine[8:-1]
        if '-' in headerLine[-1] and headerLine[-1][0] != '-':
            PRNs.append(headerLine[-1].split('-')[0])
        # And of course, we return this:
        return time, PRNs

    def frequencyLine(self, dataLine):
        """
        This function formats the actual data and the errors.
        It will use pattern-matching to find the errors.
        The output format will be: 
        L1 = [Metres, (0/1)]
        L2 = [Metres, (0/1)]
        """
        # Best Case:
        L1 = []
        L2 = []

        # We will search for the following pattern: 
        # Keep in mind that there should be something in the middle, 
        # otherwise 3798340.01 would also trigger it...
        pattern = '0.0' + '<0>' + '1'

        # Well, let's search for it!
        if re.search(pattern, '<0>'.join(dataLine[:-3])):
            if re.search(pattern, '<0>'.join(dataLine[:2])):
                if re.search(pattern, '<0>'.join(dataLine[2:4])):
                    L1, L2 = [1], [1]
                else:
                    L1, L2 = [1], []
            else:
                L1, L2 = [], [1]

        return L1, L2

    def trimmer(self, mid2):
        """

        """


# This will make sure it only runs when the file is run directly, not if it is imported.
if __name__ == "__main__":
    # Change this to wherever the .13o files are located on the PC.
    # In the dropbox, this will work fine.
    path = os.path.abspath(os.path.join(os.path.realpath(""), os.pardir, "GPS_nom"))
    # target = os.path.abspath(os.path.join("", os.pardir, "Data"))

    # Create an object to read the file, and send it where the file is located.
    day1 = GPSfile("repro.goce2460.13o", path)

    # Process the data, it is a generator object, so a for loop is the way to read it.
    with open("GPSprns_test.txt", "w+") as f:
        for second in day1.process():
            f.write(str(second) + "\n")
