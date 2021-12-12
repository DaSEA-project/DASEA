# Dependencies in Conan c++ package manger ecosystem

### Prerequisites
Go, Conan, C++ Compiler(s), Python, Git, Bash / Powershell (Windows)

### Errors when a package is specified for a specific OS
Sometimes the Conan miner will throw an error when package information cannot be extracted due to the package targeting a different OS than the host is currently running.

In order to mititage missing data, we run the Conan miner two times. First with Windows as target OS and then Linux.

This is done by changing the default Conan profile:

```
[settings]
os=Linux <- keep when targeting Windows
os=Windows <- keep when targeting Linux
os_build=Linux
arch=x86_64
arch_build=x86_64
compiler=gcc
compiler.version=9
compiler.libcxx=libstdc++
build_type=Release
[options]
[build_requires]
[env]
```

The default profile is located at `~/.conan/profiles`

### 12-12-21 STATS
Packages = 1118
Versions = 2723
Dependencies = 2758

### 11-20-20-21 STATS
Packages = 1124 (We only collect 1071 due to conan info failing)
Versions = 1095
Dependencies = 1110 (666 has no dependencies, no. is remaning total dependencies)
