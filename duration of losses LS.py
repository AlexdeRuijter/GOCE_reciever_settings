# [[Y, M, D, H, min, sec], [Errors in L1], [Errors in L2]] as input
# Calculates the duration of one loss, then the next etc.
# Stores the duration in L1/L2_durations and plots them with the average

import GPS_init as gi
import GPS_passSpan_v2 as ps2
import matplotlib.pyplot as plt
import csv
import GPS_filenames as fn


def loss_histogram_pt1(duration_dict1, duration_dict2):
    with open("Loss_durations.txt", "a+") as file:  #
        for L12 in range(2):
            if L12 == 0:
                durations_tosort = duration_dict1
                subplot_index = 211
                name = 'dict1'

            else:
                durations_tosort = duration_dict2
                subplot_index = 212
                name = 'dict2'

            sorter_list = []
            # for PRN in durations_tosort:
            #     # print(durations_tosort[PRN])
            #     for length in durations_tosort[PRN]:
            #         # if length > 250:
            #         #     print(name)
            #         #     print("Long loss!", PRN, durations_tosort[PRN].index(length))
            #
            #         if length not in counter_dict:
            #             counter_dict[length] = 1
            #         else:
            #             counter_dict[length] += 1

            # print(counter_dict)
            # durations = [key for key in counter_dict]
            # durations.sort()
            # print(durations)
            biglist = []
            for PRN in durations_tosort:
                biglist.extend(durations_tosort[PRN])

            print(len(biglist), biglist)
            biglist.sort()
            csvwriter = csv.writer(file, delimiter=',')
            csvwriter.writerow(biglist)
            csvwriter.writerow([])


def plotter(duration_dict1, duration_dict2,fname):
    fig = plt.figure(num=None, figsize=(15, 10), dpi=80, facecolor='w', edgecolor='k')
    fig.suptitle('Duration of Signal Losses due to Ionospheric Scintillation', fontsize=15)
    for L12 in range(2):
        if L12 == 0:
            durations_individual = duration_dict1
            subplot_index = 211

        else:
            durations_individual = duration_dict2
            subplot_index = 212

        biglist = []
        for PRN in durations_individual:
            biglist.extend(durations_individual[PRN])

        ax1 = fig.add_subplot(subplot_index)
        ax1.hist(biglist, bins=max(biglist), label='')
        average = sum(biglist) / len(biglist)
        print(average)
        ax1.axvline(average, linestyle='dashed', color = 'r')
        plt.xlabel('Duration of loss [s]')
        plt.ylabel('Frequency of occurence [ ]', )

    plt.savefig(fname, format="png")
    # frequencies = [counter_dict[key] for key in durations]
    # print(durations, frequencies)
    # ax1 = fig.add_subplot(subplot_index)
    # ax1.plot(durations,frequencies, label="Duration of single losses")
    # # ax1.plot(L1_number, len(L1_durations)*[L1_ave], label="Average duration of losses")
    # ax1.legend(loc='best')
    # ax1.set_title('Duration of Signal Losses on L1')

    # ax2 = fig.add_subplot(212)
    # ax2.plot(L2_number,L2_durations, label="Duration of single losses")
    # ax2.plot(L2_number, len(L2_durations)*[L2_ave], label="Average duration of losses")
    # ax2.legend(loc='best')
    # ax2.set_title('Duration of Signal Losses on L2')
    # plt.xlabel('Number of loss []')
    # plt.ylabel('Duration of loss [s]',)

    #plt.show()

filenames=fn.filenames_list()
counter = 245
output_start = ["fig_"," "]

for day in filenames:
    filename = str(counter).join(output_start)
    print(filename)

    ListTimestamp, PRNs, GL1_losses, GL2_losses = gi.P2_init(day[1])
    PRNstarts, PRNends, instances = gi.PRN_Bookmarker(ListTimestamp, PRNs)

    scintdict1, carryover1, durationdict1 = ps2.passSpan_v2(GL1_losses, PRNstarts, PRNends)
    scintdict2, carryover2, durationdict2 = ps2.passSpan_v2(GL2_losses, PRNstarts, PRNends)

    # loss_histogram_pt1(durationdict1, durationdict2)
    plotter(durationdict1,durationdict2,filename)

    counter += 1
