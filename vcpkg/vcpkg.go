package main

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"reflect"

	"github.com/mitchellh/mapstructure"
)


type Response struct {
	GeneratedOn string                	`json:"Generated On"`
	Size int 														`json:"Size"`
	Packages []Package									`json:"Source"`
}

type Package struct {
	Name            string                 `json:"Name"`
	Version         string                 `json:"Version"`
	Description     string                 `json:"Description"`
	Supports        string                 `json:"Supports"`
	Features     	  []Feature              `json:"Features"`
	Dependencies    []interface{} `json:"Dependencies"`
}

type Feature struct {
	Name            string                 `json:"Name"`
	Description     string            	   `json:"Description"`
}

type Dependency struct {
	Name            string                 `json:"name"`
	Platform        string                 `json:"platform"`
}

type PackageWithFormattedDependency struct {
	Name            string                 `json:"name"`
	Version       	string                 `json:"Version"`
	Dependencies    []Dependency
}

const (
	VCPKG_PACKAGES_OUTPUT = "https://vcpkg.io/output.json"
)

func UnmarshalResponse(data []byte) (Response, error) {
	var r Response
	err := json.Unmarshal(data, &r)
	return r, err
}

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func getPackagesWithFormattedDependencies(packages []Package) []PackageWithFormattedDependency {
	formattedPackages := make([]PackageWithFormattedDependency, 0, len(packages));

	for _,p := range packages {
		var pckg PackageWithFormattedDependency
		pckg.Name = p.Name
		pckg.Version = p.Version
		if  len(p.Dependencies) > 0 {
			pckg.Dependencies = getDependencies(p.Dependencies)
		}
		formattedPackages = append(formattedPackages, pckg)
	}

	return formattedPackages
}

func getDependencies(dependencies []interface{}) []Dependency {
	formattedDependencies := make([]Dependency, 0, len(dependencies));

	for _, dep := range dependencies {
		var formattedDep Dependency
		if reflect.TypeOf(dep).Kind() == reflect.String {
			formattedDep.Name = dep.(string);
			formattedDep.Platform = ""
		}	else {
			mapstructure.Decode(dep, &formattedDep)
		}
		formattedDependencies = append(formattedDependencies, formattedDep)
	}
	return formattedDependencies
}

func traverse() {
	response, err := http.Get(VCPKG_PACKAGES_OUTPUT)
	handleError(err)
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	handleError(err)
	res, _ := UnmarshalResponse(data)
	deps := getPackagesWithFormattedDependencies(res.Packages)
	writeToFile(deps)
}

func writeToFile(data []PackageWithFormattedDependency) {
	file, _ := json.MarshalIndent(data, "", " ")
	_ = ioutil.WriteFile("./dependencies.json", file, 0644)
}

func main() {
	traverse()
}