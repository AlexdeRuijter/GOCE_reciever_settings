import ast
import re
import datetime as DT

"""
****** README: *******
This file is the 2nd programme in the chain for Q1/Q2 analysis. It reads the output files from Alex's 1st Step programme
and provides these things in a list:
1) Timestamp
2) PRN numbers per timestamp
3) General Losses (including expected GPS losses and IS (ionospheric scintillation) losses)

All items should be retrievable with the same indexes
"""


def PRN_Bookmarker(ListTimestamp, ListPRNs):
    """
    Author: Sherman
    This function checks for PRN starts and ends by comparing with the entries before and after the current entry.
    :return: list of times PRN starts, list of times PRN ends, sanity check item.
    """
    prn_starts = []
    prn_ends = []
    prn_instances = [0, 0]      # this is a sanity check to see whether all instances of PRN starts & ends are recorded.

    def iterate():
        """
        Generator: Yields the current, previous and next PRN entry, including its timestep.

        :yield: (Current PRN entry, Previous PRN entry, Next PRN entry, timestep).
        """
        for t in range(len(ListPRNs)):
            curr_step = set(ListPRNs[t])
            curr_time = t
            prev_step = False       # initialise first so if conditional doesn't pass, it's an invalid timestep.
            next_step = False
            if t - 1 >= 0:
                prev_step = set(ListPRNs[t - 1])

            if t + 1 < len(ListPRNs):
                next_step = set(ListPRNs[t + 1])

            # NOTE: outside of this function, prev_step is comparatorPrev, next_step is comparatorNext, and
            # curr_step is current.
            yield curr_step, prev_step, next_step, curr_time

    def differenceFinder(comparator, state):
        """
        Uses set theory to find the difference of PRNs between the comparator and the current sets.
        :param comparator: Entry of previous or next timestep, denoted by comparatorPrev or comparatorNext. WARNING:
        does not raise any exception if the wrong comparator set is used.
        :param state: Either -1 or +1 (the difference of comparator timestep vs the current),
        writes into either the list prn_starts or prn_ends.

        """

        if bool(comparator):    # checks whether there is a valid comparator
            intersectPRN = current.difference(comparator)       # set theory, looks for difference between 2 sets.
            if bool(intersectPRN):
                if state == -1:         # see documentation
                    target_list = prn_starts
                    prn_instances[0] += len(intersectPRN)
                elif state == 1:        # see documentation
                    target_list = prn_ends
                    prn_instances[1] += len(intersectPRN)
                else:
                    raise ValueError("2nd argument, 'state' variable is incorrect. Give either +1 or -1.")

                for item in intersectPRN:       # appends every time there's a new PRN
                    target_list.append([ListTimestamp[t], item, t])

    lineIterate = iterate()     # initiate generator
    try:                        # normal operation
        while True:
            # takes the current scope from the iterate() generator.
            current, comparatorPrev, comparatorNext, t = next(lineIterate)
            # finds the difference between the comparators vs current and appends into prn_starts & prn_ends
            differenceFinder(comparatorPrev, -1)
            differenceFinder(comparatorNext, +1)
    except StopIteration:       # catches the end of generator (StopIteration)
        pass
    finally:                    # memory-saving procedure
        del lineIterate

    return prn_starts, prn_ends, prn_instances

def Non0_Bookmarker(ListPRNs, startPRNs, endPRNs):
    """
    This function aims to give the timestamp & PRN bookmark for the first nonzero reading after the startPRN bookmark.
    This essentially means the end of the lock losses, meaning losses after this bookmark are tracking losses.
    To do this, the PRN start is a start condition, in which for the specific PRN starting, the function will focus on
    that PRN and iterate till the start of a non-zero reading in L1/L2. Then with that, it'll append into list.
    For end of Non0 bookmarks, the iterator should read from back to front, using the endPRNs as activation switch until
    it hits the Non0 from the back end.
    :param ListTimestamp:
    :return:
    """
    def PRN_span():
        """
        Iterates through the startPRN list for the PRN_ON point, and matches the PRN_OFF point per PRN. Uses a general
        slice search for the endPRN after the timestep (since the PRN logically should not end before it starts),
        expanding the slice scope if a search is not found. Terminates when the last entry in the startPRN list is
        reached. (comment) Hmm should we do this across days?? Might yield clearer results but is extra work...
        Maybe should append the unfinished PRNs and add them to the front of the subsequent day epoch.
        :return:
        """
        # print('entering function')
        start_ends = []
        for i in range(len(startPRNs)):
            assoc_PRN = startPRNs[i][1]
            assoc_t = startPRNs[i][2]
            # print(assoc_PRN)
            iterate_t = assoc_t
            while bool(iterate_t):
                # print(iterate_t)
                check_item = endPRNs[iterate_t][1]
                # print(check_item, assoc_PRN)
                if check_item == assoc_PRN:
                    # yield print("I should do something here.")
                    # iterate_t = False
                    # print("Final", startPRNs[i][1], endPRNs[iterate_t][1])
                    start_ends.append([startPRNs[i],endPRNs[iterate_t]])
                    iterate_t = False
                else:
                    iterate_t += 1

            if i  == 15:
                break



    # def iterate_v2():
    #     i = 0
    #     for t in range(len(ListPRNs)):
    #         curr_step = set(ListPRNs)
    #         curr_time = t
    #         # prev_step = False
    #         # next_step = False
    #         for i in range(len(startPRNs)):
    #             if t == startPRNs[i][3]:
    #                 # initiate start read to yield?
    #
    #                 yield startPRNs[i][2]


    # def differenceFinder(comparator, state):
    #     if bool(comparator):    # checks whether there is a valid comparator
    #         intersectFaulty = current.difference(comparator)      # set theory, looks for difference between 2 sets.
    #         if bool(intersect):
    #             if state == -1:
    #                 target_list = firstFaulty
    #                 prn_instances[0] += len(intersectFaulty)
    #             elif state == 1:
    #                 target_list = lastFaulty
    #                 prn_instances[1] += len(intersectFaulty)
    #             else:
    #                 raise ValueError("2nd argument, 'state' variable is incorrect. Give either +1 or -1.")
    #
    #             for item in intersectFaulty:       # appends every time there's a new faulty PRN
    #                 target_list.append([ListTimestamp[t], item, t])
    #finds first and last faulty prn at ANY time (no relation with the first and last signal with satellites)
    # lineIterate = iterate_v2()

    # try:
    #     while True:
    #         current, comparatorPrev, comparatorNext, t = next(lineIterate)
    #         differenceFinder(comparatorPrev, -1)
    #         differenceFinder(comparatorNext, 1)
    # except StopIteration:
    #     pass
    # finally:
    #     del lineIterate

    #identify the timestamp
    
    #find timestamp for "first non-zero" i.e. when prn is no longer "faulty" ---> timestamp one after the last faulty
        
    #find timestamp for first faulty prn, and update until the satellite is out of sight

    #once satellite out of sight, the timestamp we found was the "last non-zero"
    PRN_span()
    return

def passSpan(startPRN, endPRN):
    spanMajor = []

    def passSpan_indiv(PRN): #with prn number (1-32) as an input, returns the time periods when the prn was in sight
        spanMinor = []
        passes = 0
        starttime = 0                   #ListTimestamp[0]
        endtime = len(ListTimestamp)-1  #ListTimestamp[-1]

        if PRN in prns[0]:
            spanMinor.append([starttime,endtime])
        for step in startPRN: #Looks for the start of contact
            if step[1] == PRN:
                spanMinor.append([step[-1],endtime])
                #print (timestamp[-1])
        for step in endPRN: #Looks for the end of contact
            if step[1] == PRN:
                spanMinor[passes][1] = step[-1]
                passes += 1
        return spanMinor

    def passSpan_v2():
        spanMinor = [[] for _ in range(32)]
        for i in range(len(startPRN)):
            assoc_PRN = startPRN[i][1]
            assoc_t = startPRN[i][2]
            # print(assoc_PRN)
            iterate_t = assoc_t
            while bool(iterate_t):
                # print(iterate_t)
                check_item = endPRN[iterate_t][1]
                # print(check_item, assoc_PRN)
                if check_item == assoc_PRN:
                    print("I should do something here.")
                    # iterate_t = False
                    # print("Final", startPRNs[i][1], endPRNs[iterate_t][1])
                    spanMinor[assoc_PRN].append([startPRN[i],endPRN[iterate_t]])
                    iterate_t = False

                elif iterate_t + 1 > len(startPRN):
                    # transfer the stuff from this instance onwards to a 'next day' du mp.
                    print("Transfer needed!")

                else:
                    iterate_t += 1

            if i == 15:
                break


    # for iter in range(32):
    #     # print(iter)
    #     spanMajor.append(passSpan_indiv(iter+1))

    return spanMajor


def duration_count(ListTimestamp):
    """
    Aims to count the duration of tracking losses for any PRN. Returns the start of loss and duration of loss (maybe
    end of loss too, without PRN identifier. (Note: May consider using Georg's code)
    :param readingLine:
    :return:
    """
    dates = []
    def timeRetrieve():
        for item in ListTimestamp:
            second = int(item[5])
            microsecond = round(int((item[5] - second) * 1E6), -3)
            # print(item[5], second, microsecond)
            date = DT.datetime(item[0], item[1], item[2], hour=item[3],minute=item[4],second=second,
                               microsecond=microsecond)
            dates.append(date)
        return
    timeRetrieve()
    return dates

def P2_init(filename):
    # init line:
    ListTimestamp = []
    prns = []
    GL1_losses = []  # G for General, unfiltered
    GL2_losses = []
    with open(filename, "r") as f:
        for line in f:
            listFromLine = ast.literal_eval(line)
            ListTimestamp.append(listFromLine[0])
            prns.append(listFromLine[1])
            GL1_losses.append(listFromLine[2])
            GL2_losses.append(listFromLine[3])

    print("Parsing Complete.")

    return ListTimestamp, prns, GL1_losses, GL2_losses
# print(prns[0])

ListTimestamp, prns, GL1_losses, GL2_losses = P2_init("GPS_PRNandFaulty.txt")
starts, ends, instances = PRN_Bookmarker(ListTimestamp, prns)
for start in starts[:19]:
    print(start)
#print(starts[:5], end= "\n\n")
#print(ends[:5])
# print(starts[0],ends[0],instances)
# print(len(starts), len(ends), instances)
# dates = duration_count(starts)
# print(dates)
# Non0_Bookmarker(prns,starts, ends)
# print(len(prns))
majorset = passSpan(starts,ends)
#print(majorset)
