def countLosses(self, 
                    prevAtt= None, 
                    noPrev = True,
                    inheritance = None,):
        """
        You should always count your losses. To chain days together, one can use the prevAtt and noPrev attributes
        :yield: [Timestamp, [Losses in L1], [Losses in L2]]
        """
        secondidx = 0

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
                                losses[L][key] = [idx, 0]
                                
                            
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
                yield losses[L], idx
                for K in range(2):
                    for key, loss in losses[K].items():
                        if loss[0] > loss[1] and loss[1]:
                            #print(loss, idx, secondidx, key, L)
                            pass

                        if not loss[0] and loss[1]:
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

                            if losses[L][key][0] == 0 and losses[L][key][1] > 3000:
                                # Something has gone haywire
                                print(key, "has gone haywire!", idx)
                                losses[0][key] = [0,0]

                            # If there is a end to the next loss:
                            elif losses[L][key][1]:
                                #print(losses[L][key], reserve[L][key])
                                
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
            prevtime, previdx, time, secondidx = 0, 0, 0, 0


            ## Yield all the losses that can be yielded:
            # This loop will keep spinning until there are no values left to yield,
            # or there is a condition that stops the running.
            condition = True
            while condition and len(toYield):

                # This will filter out all the time-doubles, if some may occur between switching dates.
                while prevtime == time and secondidx == previdx:
                    time, secondidx = toYield.popleft()

                # Save the time and index so we can use it for comparison next time in this while-loop.
                prevtime, previdx = time, secondidx

                # This tuple will contain the errors to be yielded.
                Errors = ([], []) # L1, L2
                
                # The checking of ends of losses should happen for both the bands:
                for L in range(2):

                    # Refresh the losses if possible:
                    for key in losses[L].keys():

                        # Collect the beginning and the end of the PRN pass:
                        begin, end = losses[L][key]

                        # If the loss has an end, and the current index is bigger or equal to that end  plus one:
                        if secondidx >= end + 1 and end:
                            
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
                            if secondidx < begin:
                                break

                            # If there is no end to the tracking pass and the index is equal to the beginning
                            # then the tracking pass might, or might not be an expected tracking loss, 
                            # so break the loop and put it back in the toYield-list, until we know more:
                            elif secondidx == begin and not end:

                                # Break the big old loop:
                                condition = False
                                # Put the entry back in to the bag!
                                toYield.appendleft([time, secondidx])
                            
                            # If there is a valid unexpected tracking loss however:
                            elif begin <= secondidx <= end:
                                
                                # Append the PRN to the error-list we're about to yield
                                Errors[L].append(key)

##                            # Hmmm:
##                            elif end < idx:
##                                condition = False
##                                losses[L][key] = [0,0]
##                                toYield.appendleft([time, idx])

                            # Now, if it is not within these options, something must have gone hayware, inform the user:    
                            else:
                                print(" Something went wrong: {}, {} | idx: {}, PRN: {}".format(begin, end, secondidx, key))
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
            self.idx = secondidx + 1
        self.Att = Att
        self.last = last

        ## Yay, done!