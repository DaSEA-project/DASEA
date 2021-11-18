package vcpkg

import (
	"encoding/json"
	"io/ioutil"
	"net/http"
	"reflect"

	"github.com/heyjoakim/DASEA/common/models"
	"github.com/mitchellh/mapstructure"
)

type response struct {
	GeneratedOn string `json:"Generated On"`
	Size        int    `json:"Size"`
	Packages    []pkg  `json:"Source"`
}

type pkg struct {
	Name           string `json:"Name"`
	Version        string `json:"Version"`
	PackageManager string
	Description    string        `json:"Description"`
	Supports       string        `json:"Supports"`
	Features       []feature     `json:"Features"`
	Dependencies   []interface{} `json:"Dependencies"`
}

type feature struct {
	Name        string `json:"Name"`
	Description string `json:"Description"`
}

type dependency struct {
	Name     string `json:"name"`
	Platform string `json:"platform"`
}

type PackageWithFormattedDependency struct {
	Name         string `json:"name"`
	Version      string `json:"Version"`
	Dependencies []dependency
}

const (
	VCPKG_PACKAGES_OUTPUT = "https://vcpkg.io/output.json"
)

func UnmarshalResponse(data []byte) (response, error) {
	var r response
	err := json.Unmarshal(data, &r)
	return r, err
}

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func getPackagesWithFormattedDependencies(packages []pkg) []models.Package {
	formattedPackages := make([]models.Package, 0, len(packages))

	for _, p := range packages {
		var pckg models.Package
		pckg.Name = p.Name
		pckg.PackageManager = "Vcpkg"
		pckg.Platform = "C/C++"
		if len(p.Dependencies) > 0 {
			// pckg.Dependencies = getDependencies(p.Dependencies)
		}
		formattedPackages = append(formattedPackages, pckg)
	}

	return formattedPackages
}

func getDependencies(dependencies []interface{}) []models.Dependency {
	formattedDependencies := make([]models.Dependency, 0, len(dependencies))

	for _, dep := range dependencies {
		var formattedDep models.Dependency
		if reflect.TypeOf(dep).Kind() == reflect.String {
			formattedDep.TargetName = dep.(string)
			formattedDep.Constraints = ""
		} else {
			mapstructure.Decode(dep, &formattedDep)
		}
		formattedDependencies = append(formattedDependencies, formattedDep)
	}
	return formattedDependencies
}

func Traverse() {
	response, err := http.Get(VCPKG_PACKAGES_OUTPUT)
	handleError(err)
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	handleError(err)
	res, _ := UnmarshalResponse(data)
	deps := getPackagesWithFormattedDependencies(res.Packages)
	writeToFile(deps)
}

func writeToFile(data []models.Package) {
	file, _ := json.MarshalIndent(data, "", " ")
	_ = ioutil.WriteFile("./dependencies.json", file, 0644)
}
