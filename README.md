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

rm CMakeCache.txt

cmake .. \
-DCMAKE_INSTALL_PREFIX=/path/to/mfa/install \
-DBUILD_SHARED_LIBS=true \
-Dpython=true

make -j install
```
# Encode an MFA model and save it to disk

```
cd /path/to/approx
python3 encode-csv.py -i <input csv file, required> -g <geom_degree, default 1> -v <vars_degree, default 3> -n <nctrl_pts, default
ninput_pts>
```
# Load an MFA model from disk and evaluate a point

```
python3 evaluate-pt.py -i <input mfa file, default approx.mfa> -p <parameter where to evaluate [0.0 - 1.0], required>
```


