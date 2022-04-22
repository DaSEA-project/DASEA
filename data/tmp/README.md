## Temp Directory

This directory is used to store temporary files from miners. For example, downloading a registry file and storing it locally in order to extract package information. Each miner has a corresponding folder, that needs to be kept in git, but its contents ignored.

### Structure

```
DaSEA
├── data/
│   ├── tmp/
|   |   ├── alire/
|   |   |   └── alire_registry_file.txt
|   ├── ├── cargo/
|   |   |   └── xyz
|   └── ├── pypi/
|   |   |   └── pkg_names.pkl
|   └── ├── ...
```
