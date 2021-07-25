"""
    Test script for cantonese examples
"""

import io
import os
import glob
import datetime

starttime = datetime.datetime.now()
file_list = []
# Get all the file names under examples
for f in glob.glob(os.path.join('..\examples\*', '*.cantonese')):
    file_list.append(f)

i = 0
print("==============START TEST================")
while i < len(file_list) - 3:
    print("Running:" + file_list[i] +  "......")
    os.system("python cantonese.py " + file_list[i])
    print("End")
    i += 1
print("=============END=======================")
endtime = datetime.datetime.now()
# Count and Output the runtime
print("Finished in " + str((endtime - starttime).seconds) + "s!")