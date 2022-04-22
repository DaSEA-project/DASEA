## Data Directory

This directory is used to store all miners CSV files. Each miner has a corresponding folder, that needs to be kept in git, but its contents ignored. Inside the folder of each miner, there are 3 files - for packages, versions and dependencies.

### Structure

```
DaSEA
├── data/
│   ├── out/
|   |   ├── alire/
|   |   |   └── alire_dependencies_01-26-2022.csv
|   |   |   └── alire_packages_01-26-2022.csv
|   |   |   └── alire_versions_01-26-2022.csv
|   ├── ├── cargo/
|   |   |   └── cargo_dependencies_01-26-2022.csv
|   |   |   └── cargo_packages_01-26-2022.csv
|   |   |   └── cargo_versions_01-26-2022.csv
|   └── ├── chromebrew/
|   |   |   └── ...
|   └── ├── ...
```
