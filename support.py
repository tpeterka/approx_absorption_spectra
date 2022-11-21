import diy
import mfa
import csv
import numpy as np

import os

ORIGINAL_DATA_PATH='datasets/'
MFA_DATA_PATH='MFA/'
IDX_MAX=200


Cases={}
Cases['1']={'varext':'001','nctrl':450,'geom_degree':1,'vars_degree':2}
Cases['2']={'varext':'002','nctrl':0,'geom_degree':1,'vars_degree':3}

def ReadAllFilesToMFA(FILE_PATH,Case,options=None):
    FILE_LIST=[]
    INPUT_FILE_LIST=[]

    variant=Case['varext']
    options={}
    options['nctrl']=Case['nctrl']
    options['geom_degree']=Case['geom_degree']
    options['vars_degree']=Case['vars_degree']

    if(FILE_PATH is None):
        dir_list = os.listdir(MFA_DATA_PATH)
        if(variant==''):
            varext=".mfa"
        else:
            varext="-"+variant+".mfa"
        MFA_FILES=[]
        ORIGINAL_FILES=[]
        lv=len(varext)
        for k in range(len(dir_list)):
            fn=dir_list[k]
            tot_fn=len(fn)

            #print('fn ({:}): {:}; {:}=={:} :> {:} [{:}]'.format(lv,fn,fn[-lv:-1]+fn[-1],varext,fn[-lv:-1]+fn[-1]==varext,fn[0:(tot_fn-lv)]))

            if(fn[-lv:-1]+fn[-1]==varext):
                MFA_FILES.append(MFA_DATA_PATH+fn)
                ORIGINAL_FILES.append(ORIGINAL_DATA_PATH+fn[0:(tot_fn-lv)]+'.csv')
                #print(ORIGINAL_DATA_PATH+fn[0:(tot_fn-lv)]+'.csv')
        return MFA_FILES, ORIGINAL_FILES



    dir_list = os.listdir(FILE_PATH)
    for fn in dir_list:
        ext=fn[-3:-1]+fn[-1]
        if(ext=='csv'):
            FILE_LIST.append(fn[0:-4])
            INPUT_FILE_LIST.append(FILE_PATH+fn[0:-4]+'.'+ext)



    for k in range(len(FILE_LIST)):
        if(variant==''):
            varext=".mfa"
        else:
            varext="-"+variant+".mfa"
        print('Reading {:} and saving to {:}'.format(INPUT_FILE_LIST[k],MFA_DATA_PATH+FILE_LIST[k]+varext))
        ReadFileToMFA(INPUT_FILE_LIST[k],MFA_DATA_PATH+FILE_LIST[k]+varext,options=options)

def ReadFileToMFA(INPUT_FILE,OUTPUT_FILE,options=None):
    if options is None:
        options={}
        options['nctrl']=0       #"number of control points", default = 0
        options['geom_degree']=1 #"polynomial degree for geometry (domain)", default = 1
        options["vars_degree"]=3 #"polynomial degree for science variable (range)", default = 3

    # read one csv file
    with open(INPUT_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        input_pts = np.empty((0,2), dtype='f8')
        for row in reader:
            try:
                input_pts = np.append(input_pts, [ [float(row[0]), float(row[1]) ] ], axis=0)
            except:
                pass
        # sort rows by first column
        input_pts = input_pts[input_pts[:, 0].argsort()]
        

        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        #input_pts = input_pts[0:IDX_MAX, :]
        print(np.asarray(input_pts).shape)
        print(input_pts[0,:])
        
        #input_pts_truncated=np.zeros(np.asarray(input_pts).shape)
        #input_pts_truncated[0:IDX_MAX,0] = input_pts[0:IDX_MAX,0]
        #input_pts_truncated[0:IDX_MAX,1] = input_pts[0:IDX_MAX,1]
        #input_pts = input_pts_truncated.tolist()
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')


    # default program arguments
    error               = True
    dom_dim             = 1
    ndom_pts, pt_dim    = input_pts.shape
    geom_nctrl_pts      = options["geom_degree"] + 1
    if (options['nctrl'] > 0):
        vars_nctrl_pts  = options['nctrl']
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
    d_args.geom_p           = [options['geom_degree']]
    d_args.vars_p           = [[options['vars_degree']]]
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
    diy.write_blocks(OUTPUT_FILE, m, save = mfa.save_block)

def ReadOriginalFile(fn):
    IDX_MAX=200
    spec_unit_list=[]
    with open(fn, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        cnt=0
        for row in spamreader:
            if(len(row)==3 and cnt>=2):
                #print('{:} {:}'.format(row[0],row[1]))
                spec_unit_list.append([np.float64(row[0]),np.float64(row[1])])
            cnt+=1
    
    spec_unit_list=np.asarray(spec_unit_list)

    freq=spec_unit_list[:,0]
    power=spec_unit_list[:,1]
    idx=np.argsort(freq)
    freq=freq[idx]
    power=power[idx]
    freq=freq[0:IDX_MAX]
    power=power[0:IDX_MAX]
    power_original = power.copy()
    power=power-np.min(power)

    spec_unit_list=np.zeros((IDX_MAX,8))

    # 0 is original frequency (actually wavelength)
    spec_unit_list[0:IDX_MAX,0]=freq
    # 1 is original power, shifted by min
    spec_unit_list[0:IDX_MAX,1]=power

    # 8 is original power, not shifted by min
    spec_unit_list[0:IDX_MAX,1]=power_original

    # 2 is scale of wavelength between 0 and 1
    spec_unit_list[0:IDX_MAX,2]=np.linspace(0,1,IDX_MAX)

    # 3 is the power scaled to integrate to one => a PDF
    dx=np.diff(spec_unit_list[0:IDX_MAX,2])[0]
    scale=(dx/2)* power[0] + dx/2 * power[IDX_MAX-1] + dx*np.sum(power[1:IDX_MAX-1])
    spec_unit_list[0:IDX_MAX,3]=power/scale

    # 4 is the CDF
    pdf=spec_unit_list[0:IDX_MAX,3]
    cdf=np.zeros((IDX_MAX,))
    cdf[0]=pdf[0]*dx/2.
    for i in range(1,IDX_MAX-1):
        cdf[i]=cdf[i-1]+pdf[i]*dx
    cdf[IDX_MAX-1]=cdf[IDX_MAX-2]+pdf[IDX_MAX-1]*dx/2.

    spec_unit_list[0:IDX_MAX,4]=cdf

    # 5 is the inverse CDF coords
    spec_unit_list[0:IDX_MAX,5]=cdf
    # 6 is the inverse CDF
    spec_unit_list[0:IDX_MAX,6]=spec_unit_list[0:IDX_MAX,2]
    
    return spec_unit_list

def W_cdf(coord_cdf1, cdf1, coord_cdf2, cdf2, p=2, NP=1000):
    
    interp_grid=np.linspace(0,1,NP)
    dx=interp_grid[1]-interp_grid[0]
    
    cdf1_interp=np.interp(interp_grid, coord_cdf1, cdf1)
    cdf2_interp=np.interp(interp_grid, coord_cdf2, cdf2)
    
    int_val=(dx/2.)*np.abs(cdf1_interp[0]-cdf2_interp[0])**p
    for i in range(1,NP-1):
        int_val+=dx*np.abs(cdf1_interp[i]-cdf2_interp[i])**p
    int_val+=(dx/2.)*np.abs(cdf1_interp[NP-1]-cdf2_interp[NP-1])**p
    
    int_val=int_val**(1./p)
    return int_val
