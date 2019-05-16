# -*- coding: utf-8 -*-
"""
Spyder Editor

[[Y, M, D, H, min, sec], [Errors in L1], [Errors in L2]]

This is a temporary script file.
"""

file = open("GPSlosses")


for i in file:
    cont_sec = int((file[i][5]) + 1)
    cont_sec_next = int((file[i+1][5]))
    cont_min = int((file[i][4])+1)          #minutes of i +1 should be the same for the next loss as well if same loss
    cont_min_next = int((file[i+1][4]))
    
    m=0
    
    if cont_sec == cont_sec_next :
        m=m+1
    elif cont_min == cont_min_next and cont_sec_next == 0 :
        m=m+1
    else:
        print("["+ m +"]")
        m=0

    