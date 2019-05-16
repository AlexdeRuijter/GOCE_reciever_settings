import GPS_init as gi
import numpy as np
from timeit import default_timer as timer

ListTimestamp, prns, GL1_losses, GL2_losses = gi.P2_init("GPS_PRNandFaulty.txt")
PRNstarts, endPRNs, instances = gi.PRN_Bookmarker(ListTimestamp, prns)

# startTime = timer()
startPRNs = PRNstarts
spans_list = np.zeros((32, 10, 2), dtype=int)
PRN_counter = np.zeros(32, dtype=int)
extraColumn = np.zeros((32, 1, 2), dtype=int)
total_counter = 0
# iterations = 0
running = True
# print(spans)

# print(startPRNs)
# print(endPRNs)
# print(len(startPRNs),len(endPRNs))

for i in range(len(startPRNs)):
    PRN = startPRNs[i][1]  # identifies PRN number for matching
    for j in range(i + 1, len(endPRNs)):  # searches for match from index i onwards (as ends only occur AFTER start)
        if endPRNs[j][1] == PRN:  # PRN matching procedure based off Kei's
            size = np.shape(spans_list)  # checks on the current shape of the matrix, we need the #columns
            PRN_index = PRN - 1  # converts PRN to array index
            if PRN_counter[PRN_index] == size[1]:  # if a certain PRN is larger than the number of columns...
                spans_list = np.concatenate((spans_list, extraColumn),
                                            axis=1)  # ... add another column of zeros to write

            # write the actual instance t
            spans_list[PRN_index, PRN_counter[PRN_index]] = [startPRNs[i][2], endPRNs[j][2]]  # save actual instance t
            PRN_counter[PRN_index] += 1  # counting function for which column the values should be written
            break  # when an endPRN is found, move on to next i.

        # if the PRN cannot be matched after iterating till the back (which is true if the endPRN is in another
        #  day)
        elif j == len(endPRNs) - 1:
            # print(total_counter)
            running = False
            break

    if not running:
        total_counter = i  # records the number of indexes which have an endPRN in the same day.
        break

# loss-caching segment
"""Since the total_counter value is essentially a representation of how many entries from startPRNs that has an 
endPRN value that exists in the same day, we can use this to determine the slice we need to 'carry over' the 
unfinished startPRN values to the next day. The simplest solution I've thought of for now is to cache the entries 
temporarily to be used and keep it around until the analysis for next day is found. Maybe a conditional could be used 
to find if there is indeed a previous day or a next day (which is the case for the first and last files we're 
analysing). """
carryOver = startPRNs[total_counter:]
# implement cache to carry over items

# with open('GPS_write',"w+") as cache:
# pass
# post-op diagnostic segment
print(spans_list[0])
# print(PRN_counter)
# print(sum(PRN_counter))
# print(size[1])

List_spans = spans_list
losses = GL2_losses
PRN_instances = PRN_counter
step_list = instances
bigBadScintList = {x: 0 for x in range(1,33)}
# print(PRN_instances)

"""
Generator: Yields the current, previous and next PRN entry, including its timestep.

:yield: (Current PRN entry, Previous PRN entry, Next PRN entry, timestep).
"""
for PRN in range(32):
    spans_perPRN = List_spans[PRN]  # this returns a 2d array
    # (below) list of end losses (incl. cutoff and zeros). note: 0 values mean whole span has no nonzero value.
    endLoss = PRN_instances[PRN] * [0]
    index_counter = 0
    ScintList_spans = []
    # for i in range(len(List_spans)):  # i referring to every span in view
    if PRN_instances[PRN] != 0:
        PRN += 1  # conversion from PRN list index to actual PRN number
        for i in range(len(spans_perPRN)):
            # print(i, spans_perPRN)

            startPRN, endPRN = spans_perPRN[i]
            # startPRN, endPRN = spans_perPRN[i]
            retro_endPRN = endPRN - 1  # the function has issues if point endPRN is used. This is a cheap fix.

            if startPRN != 0:
                for instance in range(retro_endPRN, startPRN, -1):
                    # print(losses[retro_endPRN])
                    if PRN not in losses[instance]:
                        if instance == retro_endPRN and PRN not in losses[retro_endPRN - 1]:
                            stopInstance = instance + 1  # for hard-coded disconnects where no ending lock loss occurs

                        elif instance != retro_endPRN:
                            stopInstance = instance  # because after this instance the lock loss occurs

                        else:
                            stopInstance = 0
                        # elif instance == startPRN + :
                        #     stopInstance = 0
                        endLoss[i] = stopInstance
                        break

                if endLoss[i] != 0:
                    scintLoss = False
                    scintLoss_list = []
                    for instance in range(startPRN+1, endLoss[i]):
                        if scintLoss and PRN in losses[instance]:  # TRACKING LOSSES YAASSS
                            if PRN not in losses[instance - 1]:
                                # create list to append
                                scintLoss_list = [instance]

                            elif PRN not in losses[instance + 1]:
                                # scintloss ending
                                scintLoss_list.append(instance)
                                ScintList_spans.append(scintLoss_list)

                        elif PRN in losses[instance] and not scintLoss:
                            continue

                        elif PRN not in losses[instance] and not scintLoss:  # encountering first nonzero
                            # switch on scintLoss recording
                            scintLoss = True

    # print(major_list)
    print(len(ScintList_spans), ScintList_spans)

    # break

# print(carryOver)
# endTime = timer()

# print(endTime - startTime)