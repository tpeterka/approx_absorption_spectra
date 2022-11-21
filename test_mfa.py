import diy
import mfa
import csv
import numpy as np

import os

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_context("talk", font_scale=1.25) # "talk"

from support import ReadAllFilesToMFA,ReadFileToMFA,ReadOriginalFile,Cases,ORIGINAL_DATA_PATH,MFA_DATA_PATH

FileToLoad=1

options={}
options['nctrl']=0       #"number of control points", default = 0
options['geom_degree']=1 #"polynomial degree for geometry (domain)", default = 1
options["vars_degree"]=3 #"polynomial degree for science variable (range)", default = 3

FILE_PATH='datasets/'


################################################
import subprocess
from pathlib import Path
Path(MFA_DATA_PATH).mkdir(parents=True, exist_ok=True)
#subprocess.run(["python3", "generate_mfa.py"])
################################################

Case=Cases['1']
ReadAllFilesToMFA(ORIGINAL_DATA_PATH,Case)
MFA_INPUT_FILES_1,ORIGINAL_FILES=ReadAllFilesToMFA(None,Case)

Case=Cases['2']
ReadAllFilesToMFA(ORIGINAL_DATA_PATH,Case)
MFA_INPUT_FILES_2,_=ReadAllFilesToMFA(None,Case)

MFA_INPUT_FILES_1.sort()
ORIGINAL_FILES.sort()
MFA_INPUT_FILES_2.sort()

######### Files are converted to MFA

MFA_INPUT_FILE_1=MFA_INPUT_FILES_1[FileToLoad]
ORIGINAL_FILE=ORIGINAL_FILES[FileToLoad]
MFA_INPUT_FILE_2=MFA_INPUT_FILES_2[FileToLoad]


print("Original file: {:}".format(ORIGINAL_FILE))
print("MFA file 1   : {:}".format(MFA_INPUT_FILE_1))
print("MFA file 2   : {:}".format(MFA_INPUT_FILE_2))

spec_list=ReadOriginalFile(ORIGINAL_FILE)

# MPI, DIY world and master
w = diy.mpi.MPIComm()           # world
m = diy.Master(w)               # master

# load the results and print them out
print("\n\nLoading blocks and printing them out\n")
a = diy.ContiguousAssigner(w.size, -1)
diy.read_blocks(MFA_INPUT_FILE_1, a, m, load = mfa.load_block)
m.foreach(lambda b,cp: b.print_block(cp, False))


x_coord_1=[]
x_val_1=[]
for Point in np.linspace(0,1,100):
    # evaluate a point
    param   = np.array([Point])               # input parameters where to decode the point
    pt      = np.array([0.0, 0.0])          # assigning fake values defines shape and type
    m.foreach(lambda b, cp: b.decode_point(cp, param, pt))
    #print("\nThe point at param {:} = {:}".format(param,pt))
    x_coord_1.append(pt[0])
    x_val_1.append(pt[1])
    
    
    
# MPI, DIY world and master
w = diy.mpi.MPIComm()           # world
m = diy.Master(w)               # master

# load the results and print them out
print("\n\nLoading blocks and printing them out\n")
a = diy.ContiguousAssigner(w.size, -1)
diy.read_blocks(MFA_INPUT_FILE_2, a, m, load = mfa.load_block)
m.foreach(lambda b,cp: b.print_block(cp, False))


x_coord_2=[]
x_val_2=[]
for Point in np.linspace(0,1,100):
    # evaluate a point
    param   = np.array([Point])               # input parameters where to decode the point
    pt      = np.array([0.0, 0.0])          # assigning fake values defines shape and type
    m.foreach(lambda b, cp: b.decode_point(cp, param, pt))
    #print("\nThe point at param {:} = {:}".format(param,pt))
    x_coord_2.append(pt[0])
    x_val_2.append(pt[1])

print('Case 1 : {:}'.format(Cases['1']))
print('Case 2 : {:}'.format(Cases['2']))

fig = plt.figure(figsize=(15, 10))
plt.plot(x_coord_1,x_val_1,lw=1,label='MFA Case 1')
plt.plot(x_coord_2,x_val_2,lw=1,label='MFA Case 2')
plt.plot(spec_list[:,0],spec_list[:,1],lw=3,label='Original')

#plt.xlim(425,450)
#plt.ylim(0.3,0.45)
plt.xlabel(r'wavelength')
plt.ylabel(r'power')
plt.grid('both')
plt.legend()
#plt.title(r"Frequency points")
plt.tight_layout()
plt.show()