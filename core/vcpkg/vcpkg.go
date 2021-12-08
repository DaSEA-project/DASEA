package vcpkg

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"reflect"
	"time"

	"github.com/heyjoakim/DASEA/common/helpers"
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
	Homepage       string        `json:"Homepage"`
	Maintainer     string        `json:"Maintainers"`
	License        string        `json:"License"`
	Dependencies   []interface{} `json:"Dependencies"`
}

type dependency struct {
	Name string `json:"name",mapstructure:"name"`
}

const (
	VCPKG_PACKAGES_OUTPUT = "https://vcpkg.io/output.json"
)

var (
	PKGS_MAP              = make(map[string]int64)
	PKG_ID                = int64(1)
	VERSION_ID            = int64(1)
	DEPENDENCY_ID         = int64(1)
	date                  = time.Now().Format("01-02-2006")
	VCPKG_PACKAGE_DATA    = fmt.Sprintf("data/vcpkg/vcpkg_packages-%s.csv", date)
	VCPKG_VERSION_DATA    = fmt.Sprintf("data/vcpkg/vcpkg_versions-%s.csv", date)
	VCPKG_DEPENDENCY_DATA = fmt.Sprintf("data/vcpkg/vcpkg_dependencies-%s.csv", date)
)

// Start Helper Functions

func unmarshalResponse(data []byte) (response, error) {
	var r response
	err := json.Unmarshal(data, &r)
	return r, err
}

func handleError(err error) {
	if err != nil {
		panic(err)
	}
}

func createNameIdPackageMap(packages []pkg) {
	for _, p := range packages {
		PKGS_MAP[p.Name] = PKG_ID
		PKG_ID++
	}
}

func formatAndExport(packages []pkg) {
	for _, p := range packages {

		var pckg models.Package
		pckg.ID = PKGS_MAP[p.Name]
		pckg.Name = p.Name

		// Write package data to CSV
		helpers.WriteToCsv(pckg.GetKeys(), pckg.GetValues(), VCPKG_PACKAGE_DATA)

		var version models.Version

		version.ID = VERSION_ID
		version.PackageID = PKGS_MAP[p.Name]
		version.Version = p.Version
		version.PackageManager = "Vcpkg"
		version.Description = p.Description
		version.HomepageURL = p.Homepage
		version.Maintainer = p.Maintainer
		version.License = p.License

		// write version data to CSV
		helpers.WriteToCsv(version.GetKeys(), version.GetValues(), VCPKG_VERSION_DATA)

		if len(p.Dependencies) > 0 {
			writeDependencies(p.Dependencies, version.ID)
		}
		VERSION_ID++
	}
}

func writeDependencies(dependencies []interface{}, VERSION_ID int64) {
	for _, dep := range dependencies {
		var formattedDep models.Dependency
		formattedDep.ID = DEPENDENCY_ID
		formattedDep.SourceID = VERSION_ID
		// formattedDep.Constraints = ""

		if reflect.TypeOf(dep).Kind() == reflect.String {
			formattedDep.TargetID = PKGS_MAP[dep.(string)]
		} else {
			var tempDep dependency
			mapstructure.Decode(dep, &tempDep)
			formattedDep.TargetID = PKGS_MAP[tempDep.Name]
		}
		helpers.WriteToCsv(formattedDep.GetKeys(), formattedDep.GetValues(), VCPKG_DEPENDENCY_DATA)
		DEPENDENCY_ID++
	}
}

// End Helper Functions

func Traverse() {
	response, err := http.Get(VCPKG_PACKAGES_OUTPUT)
	handleError(err)
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	handleError(err)
	res, _ := unmarshalResponse(data)
	createNameIdPackageMap(res.Packages)
	formatAndExport(res.Packages)
	fmt.Println("Vcpkg Package Data Exported")
}
