<!-- # Welcome to the DaSEA documentation
 -->
![](images/logo.png)


## Using the DaSEA Dataset

### Downloading the Dataset

All versions of the DaSEA dataset can be obtained from Zenodo: https://zenodo.org/record/5781670

The dataset is distributed as a compressed (BZip2) archive (TAR).
The filename of the dataset follows the pattern `dasea_%m-%d-%Y.tar.bz2`.
That is, The file `dasea_01-14-2022.tar.bz2` corresponds to the dataset that was released in Jan. 14th 2022.

The dataset can be downloaded from Zenodo for example as in the following:

TODO: update the link to the most current dataset!
```bash
wget https://zenodo.org/record/5781670/files/dasea_01-14-2022.tar.bz2
```


To get an overview over which ecosystems are included in the respective dataset before decompression, the files of the dataset can be listed:

```
$ tar -tvjf dasea_01-14-2022.tar.bz2
-rw-r--r--  0 user   staff    5162 Jan 14 15:16 data/out/alire/alire_packages_01-14-2022.csv
-rw-r--r--  0 user   staff   94991 Jan 14 15:16 data/out/alire/alire_versions_01-14-2022.csv
-rw-r--r--  0 user   staff   27035 Jan 14 15:16 data/out/alire/alire_dependencies_01-14-2022.csv
-rw-r--r--  0 user   staff  133668 Jan 14 15:18 data/out/homebrew/homebrew_packages_01-14-2022.csv
-rw-r--r--  0 user   staff 1093756 Jan 14 15:18 data/out/homebrew/homebrew_versions_01-14-2022.csv
-rw-r--r--  0 user   staff  669156 Jan 14 15:18 data/out/homebrew/homebrew_dependencies_01-14-2022.csv
-rw-r--r--  0 user   staff    1954 Jan 14 15:17 data/out/fpm/fpm_dependencies_01-14-2022.csv
-rw-r--r--  0 user   staff     663 Jan 14 15:17 data/out/fpm/fpm_packages_01-14-2022.csv
-rw-r--r--  0 user   staff    7011 Jan 14 15:17 data/out/fpm/fpm_versions_01-14-2022.csv
-rw-r--r--  0 user   staff  262594 Jan 14 15:17 data/out/vcpkg/vcpkg_versions_01-14-2022.csv
-rw-r--r--  0 user   staff   37836 Jan 14 15:17 data/out/vcpkg/vcpkg_packages_01-14-2022.csv
-rw-r--r--  0 user   staff  296420 Jan 14 15:17 data/out/vcpkg/vcpkg_dependencies_01-14-2022.csv
-rw-r--r--  0 user   staff   60884 Jan 14 15:17 data/out/conan/conan_dependencies_01-14-2022.csv
-rw-r--r--  0 user   staff   21328 Jan 14 15:17 data/out/conan/conan_packages_01-14-2022.csv
-rw-r--r--  0 user   staff  455922 Jan 14 15:17 data/out/conan/conan_versions_01-14-2022.csv
```

The output shows that in this version of the dataset contains the package dependency networks from the ADA package manager Alire, the MacOS package manager Homebrew, the Fortran package manager FPM, and the C/C++ package managers Conan and VCPKG.

### Decompressing the Dataset

The entire dataset can be decompressed with the tar command:

```bash
tar xf dasea_01-14-2022.tar.bz2
```

To only extract the dependency networks of a single package manager, or to extract only package information etc., the respective files can be extracted separately.
For example, the dependency network from the Fortran packages in FPM can be extracted as in the following:

```bash
tar -jxf dasea_01-14-2022.tar.bz2 data/out/fpm/fpm_packages_01-14-2022.csv
tar -jxf dasea_01-14-2022.tar.bz2 data/out/fpm/fpm_versions_01-14-2022.csv
tar -jxf dasea_01-14-2022.tar.bz2 data/out/fpm/fpm_dependencies_01-14-2022.csv
```

### Example use cases of the dataset







```python
engine = create_engine('sqlite:///school.db', echo=True)
```