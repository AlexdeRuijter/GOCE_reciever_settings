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
    prn_instances = [0, 0]  # this is a sanity check to see whether all instances of PRN starts & ends are recorded.

    def iterate():
        """
        Generator: Yields the current, previous and next PRN entry, including its timestep.

        :yield: (Current PRN entry, Previous PRN entry, Next PRN entry, timestep).
        """
        for t in range(len(ListPRNs)):
            curr_step = set(ListPRNs[t])
            curr_time = t
            prev_step = False  # initialise first so if conditional doesn't pass, it's an invalid timestep.
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

        if bool(comparator):  # checks whether there is a valid comparator
            intersectPRN = current.difference(comparator)  # set theory, looks for difference between 2 sets.
            if bool(intersectPRN):
                if state == -1:  # see documentation
                    target_list = prn_starts
                    prn_instances[0] += len(intersectPRN)
                elif state == 1:  # see documentation
                    target_list = prn_ends
                    prn_instances[1] += len(intersectPRN)
                else:
                    raise ValueError("2nd argument, 'state' variable is incorrect. Give either +1 or -1.")

                for item in intersectPRN:  # appends every time there's a new PRN
                    target_list.append([ListTimestamp[t], item, t])

    lineIterate = iterate()  # initiate generator
    try:  # normal operation
        while True:
            # takes the current scope from the iterate() generator.
            current, comparatorPrev, comparatorNext, t = next(lineIterate)
            # finds the difference between the comparators vs current and appends into prn_starts & prn_ends
            differenceFinder(comparatorPrev, -1)
            differenceFinder(comparatorNext, +1)
    except StopIteration:  # catches the end of generator (StopIteration)
        pass
    finally:  # memory-saving procedure
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
                    start_ends.append([startPRNs[i], endPRNs[iterate_t]])
                    iterate_t = False
                else:
                    iterate_t += 1

    PRN_span()
    return


def passSpan(PRN):
    """
    This function finds the time periods when they enter/exit the prn list within the 12 channels.
    This function uses the input from 1-32, so for each satellite, separately.
    The result is a list of another smaller list which consists of the starting instance and ending instance.
    Instead of timestamp, instance (line number) is used so that the later functions can handle more easily.
    """
    span = []
    passes = 0
    starttime = 0  # starttime and endtime specified so that the result remains coherent even when prn exists in the 12 channel at the very start/end of one data file
    endtime = len(ListTimestamp) - 1
    if PRN in prns[0]:  # If the prn already exist from the very first observation...
        span.append([starttime, endtime])
    for timestamp in PRN_Bookmarker(ListTimestamp, prns)[0]:  # Looks for the start of contact
        if timestamp[1] == PRN:
            span.append([timestamp[-1], endtime])
            # print (timestamp[-1])
    for timestamp in PRN_Bookmarker(ListTimestamp, prns)[1]:  # Looks for the end of contact
        if timestamp[1] == PRN:
            span[passes][1] = timestamp[-1]
            passes += 1
    return span


def lockDetection(Losses):
    """
    Author: Kei
    This function uses the list of faulty prns (losses e.g. GL2_losses) that has the same length as the
    number of epochs of the data. The result is a list of 32 lists, for each prn. The first list indicates the
    instances when the error detected was determined as an "expected" locking error. There are still lots of stuff to
    be improved. i.e: - optimizing in general - making it applicable to files of different days, not only 3 september
    - it probably cannot be added directly in this function, but the being able to connect the end of one data to the
    start of the data of the next day.
    """
    LockLosses = []
    for i in range(32):  # For each PRN 1-32,
        LockInstance = []
        print("working on PRN #", i + 1)
        for span in passSpan(i + 1):  # This looks at each starting instances
            t = 1  # starting from 1, not 0 because of the nature of the data. Most times when prn is first
            # introduced in a list it reads a non-zero value.
            # print(span)
            try:
                while i + 1 in Losses[span[0] + t]:  # Check if the prn is included in the "faulty list"
                    # print(Losses[span[0]+t])
                    LockInstance.append(
                        span[0] + t)  # the instance is added into the list of instances when locking losses are found
                    t += 1
            except:
                print("something wrong happened at instance", span[0] + t,
                      "while looking for start lock losses, at prn #", i + 1)
                pass
        for span in passSpan(i + 1):  # Analyzing backwards, starting from the last instance specific prn is in sight
            t = 1  # same story here, the very last instance when prn is in sight it reads a non-zero value
            # print(span)
            try:
                while i + 1 in Losses[span[1] - t]:  # Check if the prn is included in the "faulty list", now it is
                    # -t instead of +t, because we are checking them backwards.
                    # print(Losses[span[0]+t])
                    LockInstance.append(
                        span[1] - t)  # the instance is added into the list of instances when locking losses are found
                    t += 1
            except:
                print("something wrong happened at instance", span[1] - t,
                      "while looking for end lock losses, at prn #", i + 1)
                pass
        LockLosses.append(LockInstance)  # compiling the instances into a final list
        # print(LockInstance)
    return LockLosses


def carry_over():
    """
    Author: Sherman
    This program aims to collect the PRNs with missing ends which occur at the end of a day. The function will cache
    the continuing PRNs' number, start timestamp and lock history (L1, L2) into a separate file. Also, a sub-function
    is created to search for PRN ends in the next day, specifically the ones that do not have a PRN start on the new
    day (since they started before the day).
    :return:
    """


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
            date = DT.datetime(item[0], item[1], item[2], hour=item[3], minute=item[4], second=second,
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

    print("*** P1 File parsing completed ***")

    return ListTimestamp, prns, GL1_losses, GL2_losses


# print(prns[0])

#ListTimestamp, prns, GL1_losses, GL2_losses = P2_init("GPS_PRNandFaulty.txt")
#starts, ends, instances = PRN_Bookmarker(ListTimestamp, prns)
# print(starts)
# print(ends)
# print(starts[0],ends[0],instances)
# print(len(starts), len(ends), instances)
# dates = duration_count(starts)
# print(dates)
# Non0_Bookmarker(prns,starts, ends)
#L1_LockLosses = lockDetection(GL1_losses)
#L2_LockLosses = lockDetection(GL2_losses)
#print(L1_LockLosses)
