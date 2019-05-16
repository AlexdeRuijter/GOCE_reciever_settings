"""
This file stores an algorithm to open and read GPS files.
It outputs searches for errors, notes down the PRNs of the sattelites which have erred, per second in the following format:
[[Y, M, D, H, min, sec], [Errors in L1], [Errors in L2]]

This algorithm is made by Group AB-3 of the Faculty of Aerospace Engineering at TUD, 2018-2019
"""

# Import system modules:
import re
import os
import collections as co

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

        self.nonzeroL1 = 0
        self.nonzeroL2 = 0


    @property
    def inheritance(self):
        """This property is the inheritance to pass to the next day!
              :returns: toYield, losses, reserve, idx. """
        return (self.toYield, self.losses, self.reserve, self.idx, self.last, self.All,)


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
            #print(second)

            # 4
            processed = self.FaultyPRN(second)
            #print(processed)
            
            # 5
            yield processed
            

    def countLosses(self, 
                    prevAtt= None, 
                    noPrev = True,
                    inheritance = None,):
        """
        You should always count your losses. To chain days together, one can use the prevAtt and noPrev attributes
        :yield: [Timestamp, [Losses in L1], [Losses in L2]]
        """

        # If there is no previous day passed down, it is every day for himself, so we need some empty variables:
        if not inheritance:
            
            # Keep track of the current loss:
            losses = [{str(key): [0,0] for key in range(33)} for _ in range(2)]

            # Keep track of the upcoming losses:
            reserve = [{str(key): co.deque() for key in range(33)} for _ in range(2)]

            # All past losses that have not yielded yet:
            toYield = co.deque()
        
            # Collect all losses for funny metrics
            self.All = [{str(key):[] for key in range(33)}, {str(key):[] for key in range(33)}]

            # Collect PRN data of the last second!
            last = [None , None]

            # The file should start at zero!
            idx = 0

        else: 
            toYield, losses, reserve, idx, last, self.All = inheritance
        
        # Start reading the data:
        for Att, timeStamp, lossL1, lossL2, setPRNs, leavers, joiners, idx in self.attendance(first=noPrev, Att = prevAtt, start = idx):

            # This will stay False when no loss has no end.
            noLock = False
            lossL1 = [str(i) for i in lossL1]
            lossL2 = [str(i) for i in lossL2]
            
            TrackLoss = [set(lossL1), set(lossL2)]

            # For each L-band, L1 and L2 (0, 1):
            for L in range(2):        

                # For every PRN, check whether it is connected and locked:
                for key, [çonnect, locked] in Att.items():
                    if çonnect and locked:
                        # Here must go code to collect the losses, and put them in the list 
                        # if the beginning and the end are know, if losses[key][0] is non-zero
                        # and if we want to start a new loss, append it to reserve[key].
                        begin, end = losses[L][key]
                        
                        # is there an error for this PRN?
                        if key in TrackLoss[L]:
                            # Is the losstracker started?
                            if not begin:
                                # No? Then start it:
                                losses[L][key][0] = idx
                            
                            # It is started:
                            else:
                                
                                # Is the first loss finished yet?
                                if end:

                                    # If so check whether there is a reserve loss running:
                                    if reserve[L][key]:
                                    
                                        # If that is the case, check whether the last reserve is finished yet:
                                        if reserve[L][key][-1][1]:
                                            
                                            # If that is the case, start a new reserve track with this index:
                                            reserve[L][key].append([idx, 0])

                                        # Else:
                                        else:
                                            # For now, do nothing.
                                            pass
                                    
                                    # If that is not the case:
                                    else:

                                        # Start a new reserve loss:
                                        reserve[L][key].append([idx, 0])
                                
                                # If the first error is still running, do nothing:
                                else:
                                    pass


                ## Now check for each key whether there is an end to the loss.
                # If there is a previous loss to compare with:
                if last[L]:

                    # The difference between the current and the previous second is:
                    difference = (i for i in last[L] if i not in TrackLoss[L])

                    # For every PRN, which acts as a key, in the difference:
                    for key in difference:

                        # If the key is in contact with the SAT and not leaving this round:
                        if key in setPRNs and key not in leavers:

                            # If there is a end to the next loss:
                            if losses[L][key][1]:
                                
                                # Then the last reserve loss must be closed.
                                reserve[L][key][-1][1] = idx - 1

                            # Else, the next loss must thus be closed.
                            else:
                                losses[L][key][1] = idx - 1

                        # If the connection will indeed be cut or it is not in effect anymore:
                        elif key in leavers or key not in setPRNs:

                            # If there is no reserve_losses:
                            if not reserve[L][key]:

                                # Then the "real" losses must be nullified.
                                losses[L][key] = [0, 0]

                            # Else:
                            else:
                                # Nullify the last reserve loss, we don't need to save the variable!
                                _ = reserve[L][key].pop()

                        # If there is anything slipping past by now, inform us.
                        else:
                            print("Something slipped passes: {}, {}".format(idx, key))
                            print(setPRNS)
                            raise ValueError("Oh no, you shallt not pass!")
                        
                # Update the last values:
                last[L] = TrackLoss[L]
            
            # The loss has to be yielded someday:
            loss = [timeStamp, idx]
            toYield.append(loss)

            # Set all the knowledge of previous values to zero!
            prevtime, previdx, time, idx = 0, 0, 0, 0


            ## Yield all the losses that can be yielded:
            # This loop will keep spinning until there are no values left to yield,
            # or there is a condition that stops the running.
            condition = True
            while condition and len(toYield):

                # This will filter out all the time-doubles, if some may occur between switching dates.
                while prevtime == time and idx == previdx:
                    time, idx = toYield.popleft()

                # Save the time and index so we can use it for comparison next time in this while-loop.
                prevtime, previdx = time, idx

                # This tuple will contain the errors to be yielded.
                Errors = ([], []) # L1, L2
                
                # The checking of ends of losses should happen for both the bands:
                for L in range(2):

                    # Refresh the losses if possible:
                    for key in losses[L].keys():

                        # Collect the beginning and the end of the PRN pass:
                        begin, end = losses[L][key]

                        # If the loss has an end, and the current index is bigger or equal to that end  plus one:
                        if idx >= end + 1 and end:
                            
                            # Collect the loss for funny metrics!
                            self.All[L][key].append(losses[L][key])

                            # Then delete it:
                            # Make sure to cycle through entries
                            losses[L][key] = [0,0]

                            # If there is however still a loss in the reserve:
                            if reserve[L][key]:
                                
                                # Use that loss instead
                                losses[L][key] = reserve[L][key].popleft()

                    # Make a sorted list ordered on start values:
                    lost = sorted(losses[L].items(), key= lambda values: values[1][0])
                    
                    #for key in reserve[L].keys():
                        #if reserve[L][key]:
                            #print(key, end = "")
                    #print()

                    # Now begin checking whether we need to add this to the errors:
                    for key, [begin, end] in lost:
                        # lost is a sorted list on start values.

                        # Filter out all the zeroes:
                        if begin:

                            # Because it is sorted on start value, if one beginning is higher than the index,
                            # everything after it is too, so we don't have to worry 'bout those PRNs and errors!
                            if idx < begin:
                                break

                            # If there is no end to the tracking pass and the index is equal to the beginning
                            # then the tracking pass might, or might not be an expected tracking loss, 
                            # so break the loop and put it back in the toYield-list, until we know more:
                            elif idx == begin and not end:

                                # Break the big old loop:
                                condition = False
                                # Put the entry back in to the bag!
                                toYield.appendleft([time, idx])
                            
                            # If there is a valid unexpected tracking loss however:
                            elif begin <= idx <= end:
                                
                                # Append the PRN to the error-list we're about to yield
                                Errors[L].append(key)

##                            # Hmmm:
##                            elif end < idx:
##                                condition = False
##                                losses[L][key] = [0,0]
##                                toYield.appendleft([time, idx])

                            # Now, if it is not within these options, something must have gone hayware, inform the user:    
                            else:
                                print(" Something went wrong: {}, {} | idx: {}, PRN: {}".format(begin, end, idx, key))
                                raise ValueError(" Some things slipped past your ultimate scheme! Oh, our villainness!")

                # Now extract the the particular errors we should yield:
                L1, L2 = Errors

                if condition:
                    # Yield the value if possible.
                    yield [time, L1, L2]

        ## If we're done cycling through the day, we should do a few last things:
        # Save some variables to the class namespace:
        self.toYield = toYield
        self.losses = losses
        self.reserve = reserve
        if toYield:
            self.idx = toYield[-1][1] + 1
        else: 
            self.idx = idx + 1
        self.Att = Att
        self.last = last

        ## Yay, done!


    def attendance(self, first = True, Att= None, start = None):
        """
        This function checks whether the PRNs are diligently clocking in.
        """
        if not Att:
            Att = dict()
            for i in range(33):
                Att[str(i)] = [0,0]

        
        for second in self.alphaOmega(idx = start):
            # Second consists of:
            timeStamp, lossL1, lossL2, setPRNs, leavers, joiners, idx = second

            # For the first time, assume PRNs in the PRN_list have just connected:
            if first:
                first = False
                for i in second[3]:
                    Att[i][0] = 1
            
            # If a key has connected but has not locked yet:
            for key, values in Att.items():
                if values[0] and not values[1]:
                    # Check whether they are in the lists of losses
                    if key not in lossL1 and key not in lossL2:
                        Att[key][1] = 1
            
            # Take out the leavers:
            if leavers:
                for i in leavers:
                    Att[i] = [0, 0]

            # Insert the joiners!
            if joiners:
                for i in joiners:
                    Att[i][0] = 1
                    
            yield Att, timeStamp, lossL1, lossL2, setPRNs, leavers, joiners, idx


    def alphaOmega(self,idx = None):
        """
        Function to include the starts and the ends to the second, still yields on a second to second basis.
        """
        # If there is no further index specified, then use this index:
        if not idx:
            idx=  0
            
        # Read the file.
        self.lines = self.open()

        # Prepare the setup for finding starts and ends.
        last = []
        old_joiners = set()

        # Chop up in blocks of one second.
        for idx, second in enumerate(self.linehandler(), idx):

            # Take whatever we need from the second of data:
            prns = list(second[1])
            processed = self.FaultyPRN(second)
            
            # If there is a previous datapoint.            
            if last:
                
                # Check the which PRN joins and which don't:
                joiners = self.alphaPRN(set(last[3]), set(prns))

                # Als check which prn leaves and which don't:
                leavers = self.omegaPRN(set(last[3]), set(prns))
                
                # Now yield the the readied data:
                yield last + [leavers] + [old_joiners] + [idx- 1]

                # Save the joiners
                old_joiners = joiners
                
            # And the last second
            last = [list(i) for i in processed] + [prns]

        # At long last, give the last line of data
        yield processed +[prns] + [set()] + [old_joiners] + [idx]

            
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
        # L1S = [int(i[0]) for i in secondData[1]]
        L2 = [int(i[0]) for i in zip(secondData[1], secondData[3]) if i[1]]

        # Returns: Date, Time, and the PRN in which the error occurs.
        # If  there is no such PRN,  return an empty set instead. []
        #print(L1)

        # KEI EDIT: Added secondData[1] (PRN list) to the result (now removed)
        # PRNlst = [int(i) for i in secondData[1]]
        return [secondData[0], L1, L2]
      
    
    def linehandler(self):
        """
        This function splits all the data in parts with the lenght of a second and returns these one after oneother.
        The data is returned in list form: 
        [ [Y, M, D, H, min, sec], [PRNs], [[L1, error]], [[L2, error]] ]
        """
        secondOfData  = [[], [], [], []]

        for line in self.lines:
            # Seperate the header from the rest
            if not '.' in line[0]:
                
                # Check whether we already have some data from the previous header to parse:
                # If so, do that before we go on.
                if secondOfData[0]:
                    for prn in secondOfData[1]:
                        if prn not in secondOfData[2]:
                            self.nonzeroL1 += 1
                        if prn not in secondOfData[3]:
                            self.nonzeroL2 += 1

                    yield secondOfData
                    secondOfData = [[], [], [], []]

                timeStamp, PRNs = self.header(line)
                secondOfData[0] = timeStamp
                secondOfData[1] = PRNs

                counter = 0

            else:
                # If the line is even, the line is long.
                # Else, just skip it, we only like the long guys.
                if not counter%2:
                    L1, L2 =self.frequencyLine(line)

                    # Append the fitting values to the second of data. 
                    # In the right place...
                    secondOfData[2].append(L1)
                    secondOfData[3].append(L2)
                
                # Add one to the counter:
                counter += 1

        # That was the last line, so let's return the final values.
        yield secondOfData


    def header(self, headerLine):
        """ 
        Chop up the headerline!
        This function does literally that.
        It converts the header into a list of PRNs and Timestamp.
        """

        # The date-time signaturer consists of the first 6 elements of the header.
        time = [int(x) for x in headerLine[:5]] + [float(headerLine[5])]

        # Were in 2013 after Christ, not 13.
        time[0] += 2000

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
        pattern = '0.0'+'<0>'+'1'

        # Well, let's search for it!
        if re.search(pattern, '<0>'.join(dataLine[:-3])):
            if re.search(pattern, '<0>'.join(dataLine[:2])):
                if re.search(pattern, '<0>'.join(dataLine[2:4])):
                    L1, L2 = [1], [1]
                else:
                    L1, L2 =  [1], []
            else:
                L1, L2 = [], [1]

        return L1, L2


    def alphaPRN(self, last, current):
        """
        This function finds whether any new PRN has joined the contact list.
        """
        return current.difference(last)


    def omegaPRN(self, current, next):
        """
        This fuction checks whether the satellite loses a PRN in the next second.
        """
        return current.difference(next)

    def test_Inherit(self, inheritance):
         """
         This function tests whether the inheritance for the next day works out fine: 
         """
         for i in inheritance:
             print(i)


# This will make sure it only runs when the file is run directly, not if it is imported.   
if __name__ == "__main__":
    # Change this to wherever the .13o files are located on the PC.
    # In the dropbox, this will work fine.
    path = os.path.abspath(os.path.join(os.path.realpath(""), os.pardir, "GPS_nom"))
    # target = os.path.abspath(os.path.join("", os.pardir, "Data"))

    # Create an object to read the file, and send it where the file is located.
    day1 = GPSfile("repro.goce2460.13o", path)

    for second in day1.countLosses():
        #print(second)
        pass
    
    print("Hayday!")

    #with open("generatedlosses.txt", "w+") as f:
    #    for L in day1.All:
    #        for PRN, value in L.items():
    #            f.write(" {}:    {} \n".format(PRN, value))
    #        f.write("\n")
    
    print("Done!")
                

    # Process the data, it is a generator object, so a for loop is the way to read it.
    #with open("GPSprns.txt", "w+") as f:
    #    for second in day1.process():
    #        f.write(str(second)+ "\n")
