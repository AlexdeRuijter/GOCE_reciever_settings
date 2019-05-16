import ast

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
        :param modifier: tuning addon. the current method has a weakness where it consistently marks a stop_PRN bookmark
        before it actually stops. For prev comparators, this is 0, for next comparators, this is 1.

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