## Data Directory

This directory is used to store shared functionality (data model, helper functions, etc. inside common) and the miners that collect data (miners folder).

### Directory Structure

```
DaSEA
├── data/
│   ├── common/ # Data model and reusable functionality
|   |   ├── helpers.py
│   ├── miners/ # Individual miners
|   |   |   └── main.py # Entry point
|   |   |   └── alire.py
|   |   |   └── npm.py
|   |   |   └── ...
```

### Miner Structure

Each miner has individual ways of retriveing and shaping the package manager metadate, but we try to have similar method names, see below.

```python
#
def _collect_pkg_registry():
  # Collects the data from the source
  return []

def _collect_packages():
  # Collects and creates the packages array to write to csv and creates a map of package id and name
  return [], {}

def _collect_versions():
  # Collects and creates the versions array to write to csv
  return []

def _collect_dependencies():
  # Collects and creates the dependencies array to write to csv
  return []

def _collect_versions_with_dependencies(metadata_dict, pkg_idx_map):
  # Collects and creates the versions with dependencies array to write to csv
  # Used in cases where the the versions with dependencies are mined together
  return [], []

```
