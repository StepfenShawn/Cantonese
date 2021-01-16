"""
    Test script for contonese examples
"""
import io
import os
import glob
import re
import datetime

starttime = datetime.datetime.now()
file_list = []
for f in glob.glob(os.path.join('..\examples', '*.contonese')):
    file_list.append(f)
i = 0
print("==============START TEST================")
while i < len(file_list):
    print("Running:" + file_list[i] +  "......")
    os.system("python contonese.py " + file_list[i])
    print("End")
    i += 1
print("=============END=======================")
endtime = datetime.datetime.now()
print("Finish in " + str((endtime - starttime).seconds) + "s!")