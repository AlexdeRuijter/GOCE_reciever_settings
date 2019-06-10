## Imports:
# Import system modules:
import os
from matplotlib import pyplot as plt

# Import our own modules:
import ReadGPS as RG


## The functions we use:
def count():
    ## The starting value of the first match:
    #totalidx = 10801

    # This is indeed the first time we start:
    first = True

    # There is no previous attendence:
    Att = None

    # There is no previous inheritance:
    inher = None

    count = [0,0]
    
    for index, day in enumerate(GPSdays, 1):
        print("We are calculating day {}!".format(index))

        for value in day.countLosses(prevAtt = Att, noPrev = first, inheritance = inher):
            # We just need to iterate, no need to do anything:
            pass

        count[0] += day.nonzeroL1
        count[1] += day.nonzeroL2

        # Collect the Attendence schedule for the next day:
        Att = day.Att

        # It is simply not the first time anymore:
        first = False
        
        # Collect the inheritance for the next day:
        inher = day.inheritance
    
    # Collect all losses:
    All = inher[-1]

    # A variable to store the unexpected losses:
    unexp = [0,0]

    # For both the L1 and L2 bands:
    for L in range(2):

        # For every PRN documented in his band:
        for losses in All[L].values():
            print(losses)

            # If there actually is a record of that PRN:
            if losses:
                # Collect the unexpected losses:
                unexp[L] += sum(end- begin + 1 for (begin, end) in losses if begin and end)

    # Print our desired outcome:
    print(" The nonzero values:  {}".format(count))
          
    # And another one:
    print(" The unexpected losses: {}".format(unexp))
    
    # Return the dictionary of all losses to make a histogram:
    return All


def histogram(DictOfLosses, figname = "Duration_of_Losses",):
    """
    This function plots a histogram for a given dict of losses. 
    The 'dict' is actually a list of two dicts, corresponding to the L1 and L2 bands respectively.
    :return: A plotted histogram of the duration of the lossses.
    """
    # Specify the plot first:
    fig = plt.figure(num=None, figsize=(15, 10), dpi=80, facecolor='w', edgecolor='k')
    
    ## Give the figure a suptitle:
    #fig.suptitle('Duration of Signal Losses due to Ionospheric Scintillation', fontsize=15)

    # For both bands in the spectrum, L1 and L2:
    for L in range(2):

        # Set up the subplots:
        subplot_index = [212, 211][L]

        # Calculate every single duration in the specified L-band
        durations = [end - begin + 1 for losses in DictOfLosses[L].values() for (begin, end) in losses]

        # Plot the histogram:
        ax1 = fig.add_subplot(subplot_index)
        ax1.hist(durations, bins=max(durations), label='')

        # Calculate the average:
        alldurations = len(durations)
        average = sum(durations) / alldurations

        print("The total amount of losses for L{} is: {}".format(L+1, alldurations))

        # Plot the average
        ax1.axvline(average, linestyle='dashed', color = 'r')
        
        # Assign the labels to the graph
        plt.xlabel('Duration of loss [s]')
        plt.ylabel('Frequency of occurence [-]', )

    # Save the figure, and plot it
    plt.savefig(figname+".png", format="png")
    plt.show()


def writeFile():
    with open("dIcTOfONeDaY.txt", "w+") as f:
        for D in DictsOfDurations:
            for k, value in D.items():
                f.write("{}: {} \n".format(k, value))
            f.write("\n")

## The actual executed code!
# Load the GPSfiles:
path =  os.path.join(r"E:\GOCE_DATA", "GPS_red")
# path =  os.path.join(r"C:\Users\keike\Desktop\New folder")
GPSdays = [RG.GPSfile(filename, path) for filename in sorted(os.listdir(path))]

# Calculate the dict of durations:
DictsOfDurations = count()

# Plot the dict of durations:
histogram(DictsOfDurations, figname = "TestFigure")

writeFile()