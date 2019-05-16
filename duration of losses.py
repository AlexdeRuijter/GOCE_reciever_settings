#[[Y, M, D, H, min, sec], [Errors in L1], [Errors in L2]] as input
#Calculates the duration of one loss, then the next etc.
#Stores the duration in L1/L2_durations and plots them with the average
from GPS_prnSlicer import *
import matplotlib.pyplot as plt
import GPS_init as gi
import GPS_passSpan_v2 as ps2

# ListTimestamp, prns, GL1_losses, GL2_losses = P2_init("GPS_PRNandFaulty.txt")
# INPUT: the bigBadScintDict
ListTimestamp, PRNs, GL1_losses, GL2_losses = gi.P2_init("GPS_PRNandFaulty.txt")
PRNstarts, PRNends, instances = gi.PRN_Bookmarker(ListTimestamp, PRNs)

scintdict1, carryover1, durationdict1 = ps2.passSpan_v2(GL1_losses, PRNstarts, PRNends)
scintdict2, carryover2, durationdict2 = ps2.passSpan_v2(GL2_losses, PRNstarts, PRNends)
print(scintdict1)

alloss1 = []
alloss2 = []
#key = prn
#value = length lines
for key, values in scintdict1.items():
    for [begin, end] in values:
        alloss1.append(range(begin, end + 1))

File = open("GPS_PRNandFaulty.txt")
with open("temporaryonlylosses.txt", "w+") as file:
    for idx, string in enumerate(File):
        for Range in alloss1:
            if idx in Range:
                file.write(string)
                break

File.close()
File = open("temporaryonlylosses.txt")
file = []
for line in File:
    lst = eval(line)
    file.append(lst)


L1_durations = []
L2_durations = []

L1_counter = 0
L2_counter = 0

L1 = file[0][1]
L2 = file[0][2]

for i in file:
    if len(i[1]) != 0:
        if i[1] != L1:
            L1_durations.append(L1_counter)
            L1_counter = 0

    if len(i[2]) != 0:
        if i[2] != L2:
            L2_durations.append(L2_counter)
            L2_counter = 0

    L1 = i[1]
    L2 = i[2]
    if len(i[1]) != 0:
        L1_counter = L1_counter + 1
    if len(i[2]) != 0:
        L2_counter = L2_counter + 1

L1_ave = sum(L1_durations)/len(L1_durations)
L2_ave = sum(L2_durations)/len(L2_durations)
L1_number= list(range(len(L1_durations)))
L2_number= list(range(len(L2_durations)))


fig = plt.figure(num=None, figsize=(15, 10), dpi=80, facecolor='w', edgecolor='k')

fig.suptitle('Duration of Signal Losses due to Ionospheric Scintillation', fontsize=15)

ax1 = fig.add_subplot(211)
ax1.plot(L1_number,L1_durations, label="Duration of single losses")
ax1.plot(L1_number, len(L1_durations)*[L1_ave], label="Average duration of losses")
ax1.legend(loc='best')
ax1.set_title('Duration of Signal Losses on L1')
plt.xlabel('Number of loss []')
plt.ylabel('Duration of loss [s]',)

ax2 = fig.add_subplot(212)
ax2.plot(L2_number,L2_durations, label="Duration of single losses")
ax2.plot(L2_number, len(L2_durations)*[L2_ave], label="Average duration of losses")
ax2.legend(loc='best')
ax2.set_title('Duration of Signal Losses on L2')
plt.xlabel('Number of loss []')
plt.ylabel('Duration of loss [s]',)

plt.show()

print(L1_durations)
print (L2_durations)
print (L1_ave, L2_ave)