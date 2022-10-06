# example illustrating reading an MFA and evaluating a point from it
# assumes that a 1-d domain was previously modeled and saved as "approx.mfa"

import diy
import mfa
import numpy as np
import optparse

# parse arguments
parser = optparse.OptionParser()
parser.add_option("-i", "--infile", dest="infile", help="input data file", default = "approx.mfa")
parser.add_option("-p", "--param", dest="param", type=float, help="parameter value where to evaluate pt [0.0 - 1.0]", default = -1.0)
(options, args) = parser.parse_args()

if options.param < 0.0:
    print("Parameter where to evaluate point is a mandatory argument (-p <parameter in [0.0-1.0]> or --param <parameter in [0.0-1.0]>)")
    sys.exit()

# MPI, DIY world and master
w = diy.mpi.MPIComm()           # world
m = diy.Master(w)               # master

# load the results and print them out
print("\n\nLoading blocks and printing them out\n")
a = diy.ContiguousAssigner(w.size, -1)
diy.read_blocks(options.infile, a, m, load = mfa.load_block)
m.foreach(lambda b,cp: b.print_block(cp, False))

# evaluate a point
param   = np.array([options.param])               # input parameters where to decode the point
pt      = np.array([0.0, 0.0])          # assigning fake values defines shape and type
m.foreach(lambda b, cp: b.decode_point(cp, param, pt))
print("\nThe point at param", param, "=", pt)
