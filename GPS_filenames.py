import numpy as np

def filenames_list():
    """
    Author: Sherman
    Provides a list of mini-lists for the .13o input file and output writing file. Can be easily
    extendable
    :return:
    """
    counter = 245
    output_start = "P1_GPSprns_"
    output_end = ".txt"
    input_start = "repro.goce"
    input_end = "0.13o"
    input_elements = [input_start, input_end]
    output_elements = [output_start, output_end]
    itemsList = []

    for i in range(29):
        output_path = str(counter).join(output_elements)
        input_path = str(counter).join(input_elements)
        counter += 1
        itemsList.append([input_path, output_path])

    # print(itemsList)
    return itemsList


# print(len(itemsList
# filename = filenames_list()
# print(filename)