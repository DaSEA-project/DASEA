package models

type CSVInput struct {
	Pkg          Package
	Versions     []Version
	Dependencies []Dependency
}

// []CSVInput --->  packages.csv, dependencies.csv, versions.csv
