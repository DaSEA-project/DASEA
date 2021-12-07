# How to contribute to this project

All changes, submissions or suggestions happens through github pull requests. Please read below about branching.

1. Make a fork of the repository and create a branch from `main`
2. Add your changes, features etc. but only 1 feature pr. PR
3. State explicitly in the PR what your fix or feature does and how to test it.

## Adding a new package manager

If you want to extend DASEA to support a new package manager, you can do so by adding a new folder in core with the name of the package manager. Inside, you write an individual parser for the package manager. Your parser needs to transform the data from the package manager into a format that DASEA can use. All the models are located in the `helpers/models` folder. The required models for the csv export are `Package`, `Version` and `Dependency`.

Once you are done transforming your data to the respective format, you can call the function `writeToCSV` in the `helpers/fileHander.go` file. It will write the data to a csv file, given the model struct keys and values and the full path of the file. The file path should be `data/package_manager_name/package_manager_name_packages-current_date.csv`

Note: The mapping of the IDs is done, for now, individually in the parsers. This is because the package managers are not consistent in their way of mapping the IDs. This will be fixed in the future.

## Updating the generate csv command

Go inside `main.go` and update the `main` function to support your package manager.

## Releasing a new version of the dataset

Generate a new version of the dataset by running the following command for each package manager:

```bash
  go run main.go packageManagerName
```

Add a ZENODO_API_KEY in your .env file to enable the release of the dataset.

Publish the dataset by running:

```bash
  go run main.go release-dataset
```
