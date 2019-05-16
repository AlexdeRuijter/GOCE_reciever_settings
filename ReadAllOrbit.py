""""
This currently only works on Alex's laptop.
"""

# Import system modules
import itertools as it
import os

# Import selfmade modules
import ReadOrbit as RO

class AllFile:
    def __init__(self):
        self.setup()


    def setup(self):
        path = os.path.join(r"E:\GOCE", "GOCE_data")

        self.days = []
        filenames =[]
        for filename in sorted(os.listdir(path), key=lambda x: x[19:27]):
            filenames.append(filename)
            day = RO.orbitFile(filename, path)
            self.days.append(day)

        #    # Create an object to read the orbit files, and give it where the file is located.
        #    day1 = orbitFile("GO_CONS_SST_PRD_2I_20130901T205944_20130903T025943_0001.IDF", path)
 
        self.daystart = [list(it.islice(day.process(), 1))[0][0] for day in self.days] + [[1, 1]]
    

    def process(self):
        # Process the data in the file. It returns a generator object, so a for loop is the way to read it.
        for idx, day in enumerate(self.days):    
            for second in day.process():
                if second[0][2:] != self.daystart[idx+1][2:]:
                    yield second
                else:
                    break

if __name__ == "__main__":
    files = AllFile()
    for second in files.process():
        print(second)
    
