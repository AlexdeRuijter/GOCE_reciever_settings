"""
This file hosts an algorithm to find the offset in one of the iterables.
As long as a time is available and iterable[i][0] = timeStamp.
It returns (True, idx) if it found it, else it will return (False, 0)
"""


def findOffset(iterable, offsetTime):
    """
    This algorithm specializes in finding the offset of two iterables.
    It will return either (True, offset), or (False, 0)
    """

    # Iterate throug the file:
    for idx, iter in enumerate(iterable, 1):

        # The timestamp is always the first instance:
        time = iter[0]

        # Check whether the month is the same:
        if time[1] == offsetTime[1]:

            # Check whether the days are the same:
            if time[2] == offsetTime[2]:

                # Check whether the hours match up:
                if time[3] == offsetTime[3]:

                    # Check whether it is the right minute:
                    if time[4] == offsetTime[4]:
                                              
                        # Finally, check whether the seconds are in a one second range:
                        if time[5]< offsetTime[5]< time[5]+1:

                            return True, idx

    return False, 0 