#Importing things...
import ast
import re
import datetime as DT

#Importing our functions
from GPS_prnSlicer import PRN_Bookmarker
from GPS_prnSlicer import passSpan
from GPS_prnSlicer import lockDetection
from GPS_prnSlicer import duration_count
from GPS_prnSlicer import P2_init

#Using the function
ListTimestamp, prns, GL1_losses, GL2_losses = P2_init("GPS_PRNandFaulty.txt")
starts, ends, instances = PRN_Bookmarker(ListTimestamp, prns)
L1_LockLosses = lockDetection(GL1_losses)
L2_LockLosses = lockDetection(GL2_losses)
