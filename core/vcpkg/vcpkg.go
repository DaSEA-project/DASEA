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
	GeneratedOn 		string 			 `json:"Generated On"`
	Size        		int    			 `json:"Size"`
	Packages    		[]pkg  			 `json:"Source"`
}

type pkg struct {
	Name         	  string        `json:"Name"`
	Version         string        `json:"Version"`
	PackageManager  string
	Description     string        `json:"Description"`
	Homepage 	      string 				`json:"Homepage"`
	Maintainer      string 				`json:"Maintainers"`
	License         string 				`json:"License"`
	Dependencies    []interface{} `json:"Dependencies"`
}

type dependency struct {
	Name     			 	string 				`json:"name",mapstructure:"name"`
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

func formatPackagesForCSVExport(packages []pkg) []models.CSVInput {
	formattedPackages := make([]models.CSVInput, 0, len(packages))

	for _, p := range packages {
		var csvInput models.CSVInput
		var pckg models.Package
		pckg.Name = p.Name
		pckg.PackageManager = "Vcpkg"
		pckg.Platform = "C/C++"
		pckg.Description = p.Description
		pckg.HomepageURL = p.Homepage
		pckg.SourceCodeURL = ""
		pckg.Maintainer = p.Maintainer
		pckg.License = p.License
		pckg.Author = ""
		csvInput.Pkg = pckg
		csvInput.Versions = []models.Version{ { Version: p.Version } }
		if len(p.Dependencies) > 0 {
			csvInput.Dependencies = getDependencies(p.Dependencies)
		}
		formattedPackages = append(formattedPackages, csvInput)
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
			var tempDep dependency;
			mapstructure.Decode(dep, &tempDep)
			formattedDep.TargetName = tempDep.Name
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
	deps := formatPackagesForCSVExport(res.Packages)
	writeToFile(deps)
}

func writeToFile(data []models.CSVInput) {
	file, _ := json.MarshalIndent(data, "", " ")
	_ = ioutil.WriteFile("./core/vcpkg/dependencies.json", file, 0644)
}
