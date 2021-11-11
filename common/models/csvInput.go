package models

type CSVInput struct {
	Pkg          Package
	Versions     []Version
	Dependencies []Dependency
}