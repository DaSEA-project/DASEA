# How to contribute to this project

All changes, submissions or suggestions happens through github pull requests. Please read below about branching.

1. Make a fork of the repository and create a branch from `main`
2. Add your changes, features etc. but only 1 feature pr. PR
3. State explicitly in the PR what your fix or feature does and how to test it.

## Adding a new package manager

If you want to extend DASEA to support a new package manager, you can do so by adding a new file in the `dasea` directory with the name of the package manager. Inside, you write an individual miner for the package manager. Your miner needs to transform the data from the package manager into a format that DASEA can use. All the models are located in `dasea.common.datamodel.py`. The required models for the csv export are `Package`, `Version` and `Dependency`.

Once you are done transforming your data to the respective format, you can call the function `_serialize_data` in the `dasea.common.utils.py` file. It will write the data to a csv file, given the array and the file to write to. The file path should be `data/out/<package_manager>/<package_manager>_[packages|versions|dependencies]_<date>.csv`

Note: The mapping of the IDs is done, for now, individually in the miners. This is because the package managers are not consistent in their way of mapping the IDs. This will be fixed in the future.

## Updating the generate csv command

Go inside `main.py` and update the `main` function to support your package manager.

## Releasing a new version of the dataset

Add a ZENODO_API_KEY in your .env file to enable the release of the dataset.

Publish the dataset by running:

```bash
  bash bin/create_dataset.sh
```
