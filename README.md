# Install DIY

Build dependencies

- C++11 or higher compiler
- [MPI](http://www.mpich.org)

```
git clone https://github.com/diatomic/diy
```

# Build DIY

```
cd diy
mkdir build
cd build

rm CMakeCache.txt           # ignore error if file does not exist
cmake .. -Dpython=true
make -j

```
# Install MFA

Build dependencies

- C++11 or higher compiler
- [MPI](http://www.mpich.org)

```
git clone https://github.com/tpeterka/mfa
```

# Build MFA

```
cd mfa
mkdir build
cd build

rm CMakeCache.txt               # ignore error if file does not exist
cmake .. -Dmfa_python=true
make -j
```
# Set up PYTHONPATH

```
export PYTHONPATH=/path/to/diy/build/lib    # change /path/to/diy to your actual path
export PYTHONPATH=/path/to/mfa/build/python:$PYTHONPATH     # change /path/to/mfa/to your actual path

```

# Encode an MFA model and save it to disk

```
python3 encode-csv.py -i <input csv file, required> -g <geom_degree, default 1> -v <vars_degree, default 3> -n <nctrl_pts, default
ninput_pts>
```
# Load an MFA model from disk and evaluate a point

```
python3 evaluate-pt.py -i <input mfa file, default approx.mfa> -p <parameter where to evaluate [0.0 - 1.0], required>
```


