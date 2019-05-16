import GPS_init as gi
import numpy as np
from timeit import default_timer as timer


ListTimestamp, prns, GL1_losses, GL2_losses = gi.P2_init("GPS_PRNandFaulty.txt")
PRNstarts, PRNends, instances = gi.PRN_Bookmarker(ListTimestamp, prns)


def passSpan_v2(general_losses, startPRNs, endPRNs):
    """
    Takes the output from the PRN_bookmarker function and does these things:
    (Pt. 1)
    1) Matches the start and ends for every PRN into spans...
    2) ... and sorts them into a 32 x 10 extendable matrix (with each entry able to hold 2 values, start and end PRN)
    3) Extracts the startPRNs entries that only end on the next day as carryOver.

    (Pt. 2)
    1) Finds the last lock loss before the end of a span, if any.
    2) Identifies the start of a nonzero reading and switches on recording function...
    3) ... and starts collecting the losses before the lock loss, these are ScintLosses.
    4) Collects the starts and ends of individual ScintLosses into spans...
    5) ... and collects all these spans into PRN-specific dict entries. !!! NOTE: the dict uses PRNs as key, not PRN-1.
    :param general_losses:
    :param startPRNs:
    :param endPRNs:
    :return:
    """
    startTime = timer()  # Timer function for performance checking
    """
    *** Initialise items for collecting and counting. ***
    * (3D matrix dimensions: (rows, columns, depth))
    spans_list = creates a 3D matrix, 32 rows (PRNs), 2 depth (for startPRN and endPRN), 10 columns (for now)
    PRN_counter = 32-size array, counts the number of spans of losses per PRN.
    extraColumn =  prepares a column (32 rows, 2 depth) if spans_list overflows.
    running = boolean, if the endPRN is reached (and carrying over PRNs are needed), breaks for loop
    carryOver = List of startPRN entries that only have an endPRN on the next day.
    """
    spans_list = np.zeros((32, 10, 2), dtype=int)
    PRN_counter = np.zeros(32, dtype=int)
    extraColumn = np.zeros((32, 1, 2), dtype=int)
    running = True
    carryOver = []

    # PHASE 1: zipping the start and endPRNs into spans

    for i in range(len(startPRNs)):
        PRN = startPRNs[i][1]  # identifies PRN number for matching
        for j in range(i + 1, len(endPRNs)):  # searches for match from index i onwards (as ends only occur AFTER start)
            if endPRNs[j][1] == PRN:  # PRN matching procedure based off Kei's
                size = np.shape(spans_list)  # checks on the current shape of the matrix, we need the number of columns
                PRN_index = PRN - 1  # converts PRN to array index

                if PRN_counter[PRN_index] == size[1]:  # if a certain PRN is larger than the number of columns...
                    spans_list = np.concatenate((spans_list, extraColumn),
                                                axis=1)  # ... add another column of zeros to write

                # save the actual instance t into the spans_list matrix.
                # the PRN_counter entry gives the next write location.
                # span is saved as [startPRN, endPRN], using the depth of 2 defined earlier.
                spans_list[PRN_index, PRN_counter[PRN_index]] = [startPRNs[i][2], endPRNs[j][2]]
                PRN_counter[PRN_index] += 1  # counting function for which column the values should be written

                # if the PRN cannot be matched after iterating till the back (which is true if the endPRN is in another
                #  day)
                # secondary conditional: as the iteration approaches the end of the whole startPRN list
                # (usually, carryOver starts about 15 entries before the end of startPRN)
                if PRN == endPRNs[-1][1] and sum(PRN_counter) > len(startPRNs) - 15:
                    carryOver[:] = startPRNs[(i + 1):]  # extracts the startPRN entries to carryOver
                    running = False
                    carryOver_counter = i + 1  # because the next startPRN bookmark requires carrying over.
                    carryOver = (carryOver, carryOver_counter)  # save carryOver as tuple.
                break  # when an endPRN is found, move on to next i.

        if not running:
            break  # end whole for-loop

    # PHASE 2: finding the actual muddafocking losses.

    """
    *** Initialise the items for collecting actual losses. ***
    
    bigBadScintDict = a dictionary w/ 32 keys, each key containing a list of spans of scint losses.
    bigBadDurationDict = a dictionary w/ 32 keys, each key containing a list of durations .
    """
    bigBadScintDict = {x: [] for x in range(1, 33)}
    bigBadDurationDict = {x: [] for x in range(1, 33)}
    # print(startPRNs[carryOver_counter][1])
    # print(endPRNs[-1][1])
    # print(carryOver)

    # Iterates per PRN
    for PRN in range(32):
        """
        *** Initialise process ***
        spans_perPRN = returns a list of spans, [[startPRN,endPRN], etc...]
        endLoss = 
        ScintList_spans =  list containing scintillation loss spans.
        """
        spans_perPRN = spans_list[PRN]
        # (below) list of end losses (incl. cutoff and zeros). note: 0 values mean whole span has no nonzero value.
        endLoss = PRN_counter[PRN] * [0]
        ScintList_spans = []
        # for i in range(len(List_spans)):  # i referring to every span in view

        """
        **** Algorithm explanation, Pt.1: finding the end locking losses ***
        1) Iterates through the spans in the spans_perPRN list
        2) searches from last element, marching leftwards until non-zero element is found or if the code realises it's 
        a hardcoded endPRN (so no end losses)
        3) creates a new endPRN condition based on this, called endLoss... (cont'd)
        """
        if PRN_counter[PRN] != 0:
            PRN += 1  # conversion from PRN list index to actual PRN number
            for i in range(len(spans_perPRN)):
                # print(i, spans_perPRN)

                startPRN, endPRN = spans_perPRN[i]
                retro_endPRN = endPRN - 1  # the function has issues if the endPRN point is used. This is a cheap fix.

                if startPRN != 0:
                    for instance in range(retro_endPRN, startPRN, -1):
                        # print(losses[retro_endPRN])
                        if PRN not in general_losses[instance]:
                            if instance == retro_endPRN and PRN not in general_losses[retro_endPRN - 1]:
                                # for hard-coded disconnects where no ending lock loss occurs
                                stopInstance = instance + 1

                            elif instance != retro_endPRN:
                                stopInstance = instance  # because after this instance the lock loss occurs

                            else:
                                stopInstance = 0
                            endLoss[i] = stopInstance
                            break

                    """
                    *** Algorithm explanation, pt.2: finding the start lock losses and the Scint losses ***
                    1) Using endLoss, iterate from start of PRN span, finding the locking losses
                    2) When the start lock losses end (therefore start of non-zero), switch on conditional called 
                    scintLoss = True
                    3) when scintLoss = True and the code finds a line that's zero, it'll record the start and end
                    of the span of scintLoss, appending into scintLoss_list.
                    4) when all spans have been processed per PRN, transfer the list of loss spans into the dict entry.
                    5) REMEMBER: the dict keys follow exact PRN number, so bigBadScintDict[1] gives list for PRN 1.
                    6) the spans are in the format [startLoss, endLoss].
                    """
                    if endLoss[i] != 0:  # an endLoss of 0 means the whole span is defective, therefore ignored.
                        scintLoss = False
                        scintLoss_list = []
                        for instance in range(startPRN + 1, endLoss[i]):
                            if scintLoss and PRN in general_losses[instance]:  # TRACKING LOSSES YAASSS
                                if PRN not in general_losses[instance - 1]:
                                    # create list to append
                                    scintLoss_list = [instance]

                                elif PRN not in general_losses[instance + 1]:
                                    # scintloss ending
                                    scintLoss_list.append(instance)
                                    ScintList_spans.append(scintLoss_list)

                            elif PRN not in general_losses[instance] and not scintLoss:  # encountering first nonzero
                                # switch on scintLoss recording
                                scintLoss = True

        bigBadScintDict[PRN] = ScintList_spans
    # print(bigBadScintList[12])  # note: change this out for actual usage.

    """
    *** DurationDict processing ***
    1) Takes the loss span and does a very simple arithmetic process to find the total duration of the loss span.
    2) Records the list of durations into the dictionary, where the dict keys follows exact PRN number.
    """
    for ind in range(1, 33, 1):
        duration_PRNspan = []
        for span in bigBadScintDict[ind]:
            start, end = span
            duration = end - start + 1  # since the duration also includes the end of the span by 1 sec.
            duration_PRNspan.append(duration)
        bigBadDurationDict[ind] = duration_PRNspan

    endTime = timer()
    print("*** passSpan process completed in ", endTime - startTime, "seconds ***")
    return bigBadScintDict, carryOver, bigBadDurationDict

scintdict, carryover, durationdict = passSpan_v2(GL2_losses, PRNstarts, PRNends)

#duration_dict = duration_ripper(scintdict)

for key in scintdict.keys():
    print(key, scintdict[key])
