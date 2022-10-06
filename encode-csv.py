# example illustrating reading data from a csv file and encoding
# hard-coded for a 1-d domain (ie, a curve)

import diy
import mfa
import math
import csv
import numpy as np
import sys
import optparse

# parse arguments
parser = optparse.OptionParser()
parser.add_option("-i", "--infile", dest="infile", help="input data file", default = "")
parser.add_option("-g", "--geom_degree", dest="geom_degree", type=int, help="polynomial degree for geometry (domain)", default = 1)
parser.add_option("-v", "--vars_degree", dest="vars_degree", type=int, help="polynomial degree for science variable (range)", default = 3)
parser.add_option("-n", "--nctrl", dest="nctrl", type=int, help="number of control points", default = 0)
(options, args) = parser.parse_args()

if (options.infile == ""):
    print("Input file name is a mandatory argument (-i <filename> or --infile <filename>)")
    sys.exit()

# read one csv file
with open(options.infile, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    input_pts = np.empty((0,2), dtype='f8')
    for row in reader:
        try:
            input_pts = np.append(input_pts, [ [float(row[0]), float(row[1]) ] ], axis=0)
        except:
            pass
    # sort rows by first column
    input_pts = input_pts[input_pts[:, 0].argsort()]

    # debug
#     print("sorted input_pts:")
#     print(input_pts)

# default program arguments
error               = True
dom_dim             = 1
ndom_pts, pt_dim    = input_pts.shape
geom_nctrl_pts      = options.geom_degree + 1
if (options.nctrl > 0):
    vars_nctrl_pts  = options.nctrl
else:
    vars_nctrl_pts  = ndom_pts

# dataset arguments
d_args                  = mfa.DomainArgs(dom_dim, pt_dim)
d_args.weighted         = 0
d_args.n                = 0.0
d_args.multiblock       = False
d_args.verbose          = 1
d_args.structured       = True;
# NB, arrays bound to STL vectors must be assigned wholesale, not modified elementwise
d_args.geom_p           = [options.geom_degree]
d_args.vars_p           = [[options.vars_degree]]
d_args.ndom_pts         = [ndom_pts]
d_args.geom_nctrl_pts   = [geom_nctrl_pts]
d_args.vars_nctrl_pts   = [[vars_nctrl_pts]]
d_args.min              = [input_pts[0][0]]
d_args.max              = [input_pts[ndom_pts - 1][0]]

# debug
print("Encoding parameters:\n",
        "ndom_pts", ndom_pts,
        "pt_dim", pt_dim,
        "geom_degree", d_args.geom_p,
        "vars_degree", d_args.vars_p,
        "geom_nctrl_pts", d_args.geom_nctrl_pts,
        "vars_nctrl_pts", d_args.vars_nctrl_pts)

# MPI, DIY world and master
w = diy.mpi.MPIComm()           # world
m = diy.Master(w)               # master
nblocks = w.size                # hard-code 1 block per MPI rank

# decompose domain using double precision bounds
domain = diy.DoubleContinuousBounds(d_args.min, d_args.max)
d = diy.DoubleContinuousDecomposer(dom_dim, domain, nblocks)
a = diy.ContiguousAssigner(w.size, nblocks)
d.decompose(w.rank, a, lambda gid, core, bounds, domain_, link: mfa.Block.add(gid, core, bounds, domain_, link, m, dom_dim, pt_dim))

# initialize input data
m.foreach(lambda b, cp: b.input_data(cp, input_pts, d_args))

# compute the MFA
m.foreach(lambda b, cp: b.fixed_encode_block(cp, d_args))

# optional: compute error field
if error:
    m.foreach(lambda b, cp: b.range_error(cp, 1, True, True))

# print results
m.foreach(lambda b, cp: b.print_block(cp, True))

# save the results
print("\n\nSaving blocks\n")
diy.write_blocks("approx.mfa", m, save = mfa.save_block)
